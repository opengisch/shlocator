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
from PyQt5.QtCore import Qt, Q_ARG

DEBUG = True


def info(message: str, level: Qgis.MessageLevel = Qgis.Info):
    QgsMessageLog.logMessage("{}: {}".format(
        'ShLocator', message), "Locator bar", level)
    meta = iface.messageBar().metaObject()
    if level == Qgis.Warning:
        meta.invokeMethod(iface.messageBar(), 'pushWarning', Qt.QueuedConnection, Q_ARG(
            "QString", 'ShLocator'), Q_ARG("QString", message))
    elif level == Qgis.Critical:
        meta.invokeMethod(iface.messageBar(), 'pushCritical', Qt.QueuedConnection, Q_ARG(
            "QString", 'ShLocator'), Q_ARG("QString", message))
    else:
        meta.invokeMethod(iface.messageBar(), 'pushInfo', Qt.QueuedConnection, Q_ARG(
            "QString", 'ShLocator'), Q_ARG("QString", message))


def dbg_info(message: str):
    if DEBUG:
        QgsMessageLog.logMessage("{}: {}".format(
            'ShLocator', message), "Locator bar", Qgis.Info)
