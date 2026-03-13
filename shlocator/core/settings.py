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

from qgis.core import (
    QgsSettingsTree,
    QgsSettingsEntryString,
    QgsSettingsEntryBool,
    QgsSettingsEntryDouble,
    QgsSettingsEntryInteger,
)

PLUGIN_NAME = "shlocator"

class Settings:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Settings, cls).__new__(cls)

            settings_node = QgsSettingsTree.createPluginTreeNode(pluginName=PLUGIN_NAME)

            cls.point_scale = QgsSettingsEntryDouble("point_scale", settings_node, 1000)
            cls.service_url = QgsSettingsEntryString("service_url", settings_node, "https://api.geo.sh.ch/geo/searchbaseobjects/geojson/")
            cls.keep_scale = QgsSettingsEntryBool(
                "keep_scale", settings_node, False
            )
            cls.max_features = QgsSettingsEntryInteger(
                "max_features", settings_node, 20
            )

        return cls.instance
