# -*- coding: utf-8 -*-
"""
/***************************************************************************

 QGIS Schaffhausen Locator Plugin
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

from PyQt5.QtWidgets import QWidget
from qgis.core import Qgis
from qgis.gui import QgisInterface, QgsMessageBarItem
from shlocator.core.shlocator_filter import ShLocatorFilter


class ShLocatorPlugin:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.locator_filter = ShLocatorFilter(iface)
        self.iface.registerLocatorFilter(self.locator_filter)

    def initGui(self):
        pass

    def unload(self):
        self.iface.deregisterLocatorFilter(self.locator_filter)
