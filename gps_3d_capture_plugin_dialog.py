# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GPS3DCapturePluginDialog
                                 A QGIS plugin
 A plugin for capture 3D points from GPS
                             -------------------
        begin                : 2016-09-27
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Universidad de Castilla-La Mancha
        email                : david.hernandez@uclm.es
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
import os,sys
reload(sys)
sys.setdefaultencoding("utf-8")

from PyQt4 import QtCore,QtGui,uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.gui import QgsGenericProjectionSelector
from qgis.core import QgsApplication

import constants

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'gps_3d_capture_plugin_dialog_base.ui'))


class GPS3DCapturePluginDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GPS3DCapturePluginDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        self.path = QDir.currentPath()
        self.initializeGeoidComboBox()
        QtCore.QObject.connect(self.asciiFilePushButton,QtCore.SIGNAL("clicked(bool)"),self.selectAsciiFile)
        QtCore.QObject.connect(self.crsPushButton,QtCore.SIGNAL("clicked(bool)"),self.selectCrs)
        QtCore.QObject.connect(self.geoidCheckBox,QtCore.SIGNAL("clicked(bool)"),self.activateGeoid)

    def activateGeoid(self):
        if self.geoidCheckBox.isChecked():
            self.geoidLabel.setEnabled(True)
            self.geoidComboBox.setEnabled(True)
            self.geoidComboBox.setCurrentIndex(0)
        else:
            self.geoidLabel.setEnabled(False)
            self.geoidComboBox.setEnabled(False)
            self.geoidComboBox.setCurrentIndex(0)

    def initializeGeoidComboBox(self):
        self.geoidComboBox.addItem(constants.CONST_GPS_3D_CAPTURE_PLUGIN_COMBOBOX_NO_SELECT_OPTION)
        qgisAppPath=QgsApplication.prefixPath()
        qgisDir=QDir(qgisAppPath)
        qgisDir.cdUp()
        qgisDir.cdUp()
        qgisPath=qgisDir.absolutePath()
        shareDir=QDir(qgisPath+constants.CONST_GPS_3D_CAPTURE_PLUGIN_GEOIDS_RELATIVE_PATH)
        geoidFileNames = shareDir.entryList([constants.CONST_GPS_3D_CAPTURE_PLUGIN_GEOIDS_FILTER_1], QtCore.QDir.Files) #,QtCore.QDir.Name)
        for geoidFileName in geoidFileNames:
            geoidFileInfo=QFileInfo(geoidFileName)
            self.geoidComboBox.addItem(geoidFileInfo.baseName())

    def selectAsciiFile(self):
        oldFileName=self.asciiFileLineEdit.text
        title="Select ASCII file"
        filters="Files (*.txt)"
        fileName = QFileDialog.getOpenFileName(self,title,self.path,filters)
        fileInfo = QFileInfo(fileName)
        if fileInfo.isFile():
            self.path=fileInfo.absolutePath()
            self.selectFileLineEdit.setText(fileName)

    def selectCrs(self):
        projSelector = QgsGenericProjectionSelector()
        projSelector.exec_()
        crsId=projSelector.selectedCrsId()
        crsAuthId=projSelector.selectedAuthId()
        self.crsLineEdit.setText(crsAuthId)
