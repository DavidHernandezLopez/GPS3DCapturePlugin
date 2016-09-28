# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GPS3DCapturePlugin
                                 A QGIS plugin
 A plugin for capture 3D points from GPS
                             -------------------
        begin                : 2016-09-27
        copyright            : (C) 2016 by Universidad de Castilla-La Mancha
        email                : david.hernandez@uclm.es
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
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GPS3DCapturePlugin class from file GPS3DCapturePlugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .gps_3d_capture_plugin import GPS3DCapturePlugin
    return GPS3DCapturePlugin(iface)
