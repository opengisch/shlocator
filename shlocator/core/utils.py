# -*- coding: utf-8 -*-
"""
/***************************************************************************

 QGIS Schaffhausen Locator Plugin
 Copyright (C) 2019 Denis Rouzaud, OPENGIS.ch

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

from qgis.core import Qgis, QgsMessageLog
from qgis.utils import iface
from qgis.PyQt.QtCore import Qt, Q_ARG

DEBUG = True


def info(message: str, level: Qgis.MessageLevel = Qgis.MessageLevel.Info):
    QgsMessageLog.logMessage("{}: {}".format(
        'ShLocator', message), "Locator bar", level)
    meta = iface.messageBar().metaObject()
    if level == Qgis.MessageLevel.Warning:
        meta.invokeMethod(iface.messageBar(), 'pushWarning', Qt.ConnectionType.QueuedConnection, Q_ARG(
            str, 'ShLocator'), Q_ARG(str, message))
    elif level == Qgis.MessageLevel.Critical:
        meta.invokeMethod(iface.messageBar(), 'pushCritical', Qt.ConnectionType.QueuedConnection, Q_ARG(
            str, 'ShLocator'), Q_ARG(str, message))
    else:
        meta.invokeMethod(iface.messageBar(), 'pushInfo', Qt.ConnectionType.QueuedConnection, Q_ARG(
            str, 'ShLocator'), Q_ARG(str, message))


def dbg_info(message: str):
    if DEBUG:
        QgsMessageLog.logMessage("{}: {}".format(
            'ShLocator', message), "Locator bar", Qgis.MessageLevel.Info)
