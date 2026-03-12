# -*- coding: utf-8 -*-
"""
/***************************************************************************

 QGIS Schaffhausen Locator Plugin
 Copyright (C) 2019 Matthias Kuhn, OPENGIS.ch

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

from qgis.core import Qgis
from qgis.gui import (
    QgsSettingsEditorWidgetWrapper,
    QgsSettingsBoolCheckBoxWrapper,
)
import os
from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtWidgets import QDialog

from shlocator.core.settings import Settings

DialogUi, _ = loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/config.ui'))


class ConfigDialog(QDialog, DialogUi):
    def __init__(self, parent=None):
        self.settings = Settings()
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.wrappers: list[QgsSettingsEditorWidgetWrapper] = []
        
        self.keep_scale.toggled.connect(self.point_scale.setDisabled)
        self.keep_scale.toggled.connect(self.scale_label.setDisabled)

        self.wrappers.append(
            QgsSettingsBoolCheckBoxWrapper(
                self.layers_include_opendataswiss,
                self.settings.layers_include_opendataswiss,
            )
        )
