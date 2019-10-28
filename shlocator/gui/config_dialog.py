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

import os
from qgis.PyQt.QtCore import Qt, pyqtSlot
from qgis.PyQt.QtWidgets import QDialog, QTableWidgetItem, QAbstractItemView
from qgis.PyQt.uic import loadUiType

from shlocator.qgis_setting_manager import SettingDialog, UpdateMode
from shlocator.qgis_setting_manager.widgets import TableWidgetStringListWidget, ComboStringWidget
from shlocator.core.settings import Settings

DialogUi, _ = loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/config.ui'))


class ConfigDialog(QDialog, DialogUi, SettingDialog):
    def __init__(self, parent=None):
        settings = Settings()
        QDialog.__init__(self, parent)
        SettingDialog.__init__(
            self, setting_manager=settings, mode=UpdateMode.DialogAccept)
        self.setupUi(self)

        self.keep_scale.toggled.connect(self.point_scale.setDisabled)
        self.keep_scale.toggled.connect(self.scale_label.setDisabled)

        self.settings = settings
        self.init_widgets()
