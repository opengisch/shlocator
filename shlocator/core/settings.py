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


from shlocator.qgis_setting_manager import SettingManager, Scope, Bool, Stringlist, Integer, Double, String

pluginName = "shlocator"


class Settings(SettingManager):
    def __init__(self):
        SettingManager.__init__(self, pluginName)

        self.add_setting(Integer('max_features', Scope.Global, 20))
        self.add_setting(Bool('keep_scale', Scope.Global, False))
        self.add_setting(Double('point_scale', Scope.Global, 1000))

        self.add_setting(String('service_url', Scope.Global,
                                'https://api.geo.sh.ch/geo/searchbaseobjects/geojson/'))
