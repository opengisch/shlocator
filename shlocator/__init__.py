# -*- coding: utf-8 -*-
"""
/***************************************************************************

                                 ShLocator

                             -------------------
        begin                : Oct 2019
        copyright            : (C) 2019 by Matthias Kuhn
        email                : matthias@opengis.ch
        git sha              : $Format:%H$
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


def classFactory(iface):
    """Load plugin.
    :param iface: A QGIS interface instance.
    """

    from .shlocator_plugin import ShLocatorPlugin
    return ShLocatorPlugin(iface)
