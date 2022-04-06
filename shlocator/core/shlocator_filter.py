# -*- coding: utf-8 -*-
"""
/***************************************************************************

 QGIS SH Locator Plugin
 Copyright (C) 2019 Matthias Kuhn

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


import json
import os
import sys
import traceback

from PyQt5.QtCore import (
    Qt,
    QTimer,
    QUrl,
    QUrlQuery,
    QVariant,
    QTextCodec,
    pyqtSignal
)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QApplication

from qgis.core import (
    Qgis,
    QgsLocatorFilter,
    QgsLocatorResult,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsGeometry,
    QgsWkbTypes,
    QgsPointXY,
    QgsLocatorContext,
    QgsFeedback,
    QgsFields,
    QgsField,
    QgsJsonUtils
)
from qgis.gui import (
    QgsRubberBand,
    QgisInterface,
    QgsMapCanvas,
    QgsFilterLineEdit
)

from shlocator.core.network_access_manager import NetworkAccessManager, RequestsException, RequestsExceptionUserAbort
from shlocator.core.settings import Settings
from shlocator.core.utils import dbg_info, info
from shlocator.gui.config_dialog import ConfigDialog


class FeatureResult:
    def __init__(self, feature):
        self.feature = feature

    def __repr__(self):
        return 'ShLocator Feature: {}/{}'.format(self.name, self.geometry)


class NoResult:
    pass


class ShLocatorFilter(QgsLocatorFilter):

    HEADERS = {b'User-Agent': b'Mozilla/5.0 QGIS ShLocator Filter'}

    message_emitted = pyqtSignal(str, str, Qgis.MessageLevel, QWidget)

    def __init__(self, iface: QgisInterface = None):
        """
        :param iface: QGIS interface, given when on the main thread (which will display/trigger results), None otherwise
        """
        super().__init__()

        self.iface = iface
        self.settings = Settings()

        #  following properties will only be used in main thread
        self.rubber_band = None
        self.map_canvas: QgsMapCanvas = None
        self.transform_ch = None
        self.current_timer = None
        self.result_found = False
        self.nam_fetch_feature = None

        if iface is not None:
            # happens only in main thread
            self.map_canvas = iface.mapCanvas()
            self.map_canvas.destinationCrsChanged.connect(
                self.create_transforms)

            self.rubber_band = QgsRubberBand(
                self.map_canvas, QgsWkbTypes.PolygonGeometry)
            self.rubber_band.setColor(QColor(255, 50, 50, 200))
            self.rubber_band.setFillColor(QColor(255, 255, 50, 160))
            self.rubber_band.setBrushStyle(Qt.SolidPattern)
            self.rubber_band.setLineStyle(Qt.SolidLine)
            self.rubber_band.setIcon(self.rubber_band.ICON_CIRCLE)
            self.rubber_band.setIconSize(15)
            self.rubber_band.setWidth(4)
            self.rubber_band.setBrushStyle(Qt.NoBrush)

            self.create_transforms()

    def name(self):
        return 'ShLocator'

    def clone(self):
        return ShLocatorFilter()

    def priority(self):
        return QgsLocatorFilter.Highest

    def displayName(self):
        return 'ShLocator'

    def prefix(self):
        return 'shl'

    def clearPreviousResults(self):
        if self.rubber_band:
            self.rubber_band.reset(QgsWkbTypes.PointGeometry)

        if self.current_timer is not None:
            self.current_timer.stop()
            self.current_timer.deleteLater()
            self.current_timer = None

    def hasConfigWidget(self):
        return True

    def openConfigWidget(self, parent=None):
        dlg = ConfigDialog(parent)
        dlg.exec_()

    def create_transforms(self):
        # this should happen in the main thread
        src_crs_ch = QgsCoordinateReferenceSystem('EPSG:2056')
        assert src_crs_ch.isValid()
        dst_crs = self.map_canvas.mapSettings().destinationCrs()
        self.transform_ch = QgsCoordinateTransform(
            src_crs_ch, dst_crs, QgsProject.instance())

    @staticmethod
    def url_with_param(url, params) -> str:
        url = QUrl(url)
        q = QUrlQuery(url)
        for key, value in params.items():
            q.addQueryItem(key, value)
        url.setQuery(q)
        return url.url()

    def fetchResults(self, search: str, context: QgsLocatorContext, feedback: QgsFeedback):
        try:
            dbg_info("start shlocator search...")

            if len(search) < 3:
                return

            self.result_found = False

            params = {
                'query': str(search),
                'maxfeatures': str(self.settings.value('max_features'))
            }

            nam = NetworkAccessManager()
            feedback.canceled.connect(nam.abort)
            url = self.url_with_param(
                self.settings.value('service_url'), params)
            dbg_info(url)
            try:
                (response, content) = nam.request(
                    url, headers=self.HEADERS, blocking=True)
                self.handle_response(response, search)
            except RequestsExceptionUserAbort:
                pass
            except RequestsException as err:
                info(err, Qgis.Info)

            if not self.result_found:
                result = QgsLocatorResult()
                result.filter = self
                result.displayString = self.tr('No result found.')
                result.userData = NoResult
                self.resultFetched.emit(result)

        except Exception as e:
            info(e, Qgis.Critical)
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            filename = os.path.split(
                exc_traceback.tb_frame.f_code.co_filename)[1]
            info('{} {} {}'.format(exc_type, filename,
                                   exc_traceback.tb_lineno), Qgis.Critical)
            info(traceback.print_exception(
                exc_type, exc_obj, exc_traceback), Qgis.Critical)

    def data_product_qgsresult(self, data: dict) -> QgsLocatorResult:
        result = QgsLocatorResult()
        result.filter = self
        result.displayString = data['display']
        result.group = 'Karten'
        result.userData = DataProductResult(
            type=data['type'],
            dataproduct_id=data['dataproduct_id'],
            display=data['display'],
            dset_info=data['dset_info'],
            sublayers=data.get('sublayers', None)
        )
        data_product = 'dataproduct'
        data_type = data['type']
        result.icon, result.description = dataproduct2icon_description(
            data_product, data_type)
        return result

    def handle_response(self, response, search_text: str):
        try:
            if response.status_code != 200:
                if not isinstance(response.exception, RequestsExceptionUserAbort):
                    info("Error in main response with status code: "
                         "{} from {}".format(response.status_code, response.url))
                return

            display_name_field = QgsField('display_name', QVariant.String)
            fields = QgsFields()
            fields.append(display_name_field)
            features = QgsJsonUtils.stringToFeatureList(response.content.decode('utf-8'), fields, QTextCodec.codecForName('UTF-8'))
            dbg_info('Found {} features'.format(len(features)))
            dbg_info('Data {}'.format(response.content.decode('utf-8')))

            for feature in features:
                dbg_info('Adding feature {}'.format(feature['display_name']))
                result = QgsLocatorResult()
                result.filter = self
                result.group = 'Objekte'
                result.displayString = feature['display_name']
                result.userData = FeatureResult(feature)
                self.resultFetched.emit(result)

                self.result_found = True

        except Exception as e:
            info(str(e), Qgis.Critical)
            exc_type, exc_obj, exc_traceback = sys.exc_info()
            filename = os.path.split(
                exc_traceback.tb_frame.f_code.co_filename)[1]
            info('{} {} {}'.format(exc_type, filename,
                                   exc_traceback.tb_lineno), Qgis.Critical)
            info(traceback.print_exception(
                exc_type, exc_obj, exc_traceback), Qgis.Critical)

    def triggerResult(self, result: QgsLocatorResult):
        # this is run in the main thread, i.e. map_canvas is not None
        self.clearPreviousResults()

        user_data = None
        if hasattr(result, 'getUserData'):
            user_data = result.getUserData()
        else:
            user_data = result.userData

        if type(user_data) == NoResult:
            pass
        elif type(user_data) == FeatureResult:
            self.highlight(user_data.feature.geometry())
        else:
            info('Incorrect result. Please contact support', Qgis.Critical)

    def highlight(self, geometry: QgsGeometry):
        self.rubber_band.reset(geometry.type())
        self.rubber_band.addGeometry(geometry, None)

        rect = geometry.boundingBox()
        if not self.settings.value('keep_scale'):
            if rect.isEmpty():
                current_extent = self.map_canvas.extent()
                rect = current_extent.scaled(self.settings.value(
                    'point_scale')/self.map_canvas.scale(), rect.center())
            else:
                rect.scale(4)
        self.map_canvas.setExtent(rect)
        self.map_canvas.refresh()

#        self.current_timer = QTimer()
#        self.current_timer.timeout.connect(self.clearPreviousResults)
#        self.current_timer.setSingleShot(True)
#        self.current_timer.start(5000)

    def parse_feature_response(self, response):
        if response.status_code != 200:
            if not isinstance(response.exception, RequestsExceptionUserAbort):
                info("Error in feature response with status code: "
                     "{} from {}".format(response.status_code, response.url))
            return

        data = json.loads(response.content.decode('utf-8'))

        geometry_type = data['geometry']['type']
        geometry = QgsGeometry()

        if geometry_type == 'Point':
            geometry = QgsGeometry.fromPointXY(QgsPointXY(data['geometry']['coordinates'][0],
                                                          data['geometry']['coordinates'][1]))

        elif geometry_type == 'Polygon':
            rings = data['geometry']['coordinates']
            for r in range(0, len(rings)):
                for p in range(0, len(rings[r])):
                    rings[r][p] = QgsPointXY(rings[r][p][0], rings[r][p][1])
            geometry = QgsGeometry.fromPolygonXY(rings)

        elif geometry_type == 'MultiPolygon':
            islands = data['geometry']['coordinates']
            for i in range(0, len(islands)):
                for r in range(0, len(islands[i])):
                    for p in range(0, len(islands[i][r])):
                        islands[i][r][p] = QgsPointXY(
                            islands[i][r][p][0], islands[i][r][p][1])
            geometry = QgsGeometry.fromMultiPolygonXY(islands)

        else:
            # ShLocator does not handle {geometry_type} yet. Please contact support
            info('ShLocator unterstützt den Geometrietyp {geometry_type} nicht.'
                 ' Bitte kontaktieren Sie den Support.'.format(geometry_type=geometry_type), Qgis.Warning)

        geometry.transform(self.transform_ch)
        self.highlight(geometry)
