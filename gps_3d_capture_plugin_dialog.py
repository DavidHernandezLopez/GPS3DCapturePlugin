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
import shutil
reload(sys)
sys.setdefaultencoding("utf-8")

from PyQt4 import QtCore,QtGui,uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.gui import QgsGenericProjectionSelector
from qgis.core import QgsApplication,QgsCoordinateReferenceSystem

from gps_3d_capture_plugin_save_point_dialog import * #panel nueva camara

import constants

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'gps_3d_capture_plugin_dialog_base.ui'))


class GPS3DCapturePluginDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self,
                 iface,
                 parent=None):
        """Constructor."""
        super(GPS3DCapturePluginDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface
        self.initialize()

    def initialize(self):
        aux_path_plugin = 'python/plugins/' + constants.CONST_GPS_3D_CAPTURE_PLUGIN_NAME
        self.path_plugin = os.path.join(QtCore.QFileInfo(QgsApplication.qgisUserDbFilePath()).path(),aux_path_plugin)
        path_file_qsettings = self.path_plugin + '/' +constants.CONST_GPS_3D_CAPTURE_SETTINGS_FILE_NAME
        self.settings = QtCore.QSettings(path_file_qsettings,QtCore.QSettings.IniFormat)
        self.path = self.settings.value("last_path")
        if not self.path:
            self.path = QDir.currentPath()
            self.settings.setValue("last_path",self.path)
            self.settings.sync()
        self.crsAuthId=self.settings.value("crsAuthId")
        if not self.crsAuthId:
            self.crsAuthId = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
            self.settings.setValue("crsAuthId",self.crsAuthId)
            self.settings.sync()
        self.crs=QgsCoordinateReferenceSystem()
        self.crs.createFromUserInput(self.crsAuthId)
        if self.crs.geographicFlag():
            self.firstCoordinateFieldCheckBox.setText("Longitude")
            self.secondCoordinateFieldCheckBox.setText("Latitude")
        else:
            self.firstCoordinateFieldCheckBox.setText("Easting")
            self.secondCoordinateFieldCheckBox.setText("Northing")
        self.iface.mapCanvas().mapRenderer().setProjectionsEnabled(True)
        self.crsLineEdit.setText(self.crsAuthId)
        self.initializeGeoidComboBox()
        self.savePointPushButton.setEnabled(False)
        self.finishPushButton.setEnabled(False)
        QtCore.QObject.connect(self.csvFilePushButton,QtCore.SIGNAL("clicked(bool)"),self.selectCsvFile)
        QtCore.QObject.connect(self.crsPushButton,QtCore.SIGNAL("clicked(bool)"),self.selectCrs)
        QtCore.QObject.connect(self.geoidCheckBox,QtCore.SIGNAL("clicked(bool)"),self.activateGeoid)
        QtCore.QObject.connect(self.startPushButton,QtCore.SIGNAL("clicked(bool)"),self.startProcess)
        QtCore.QObject.connect(self.finishPushButton,QtCore.SIGNAL("clicked(bool)"),self.finishProcess)
        QtCore.QObject.connect(self.savePointPushButton,QtCore.SIGNAL("clicked(bool)"),self.savePoint)
        self.pointNumbers = []
        self.antennaHeight = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_ANTENNA_HEIGHT_DEFAULT_VALUE

    def activateGeoid(self):
        if self.geoidCheckBox.isChecked():
            self.geoidLabel.setEnabled(True)
            self.geoidComboBox.setEnabled(True)
            self.geoidComboBox.setCurrentIndex(0)
        else:
            self.geoidLabel.setEnabled(False)
            self.geoidComboBox.setEnabled(False)
            self.geoidComboBox.setCurrentIndex(0)

    def finishProcess(self):
        self.savePointPushButton.setEnabled(False)
        self.finishPushButton.setEnabled(False)
        self.csvFilePushButton.setEnabled(True)
        self.geoidCheckBox.setEnabled(True)
        self.geoidComboBox.setEnabled(True)
        self.crsPushButton.setEnabled(True)
        self.fieldsGroupBox.setEnabled(True)
        self.startPushButton.setEnabled(True)

    def initializeGeoidComboBox(self):
        self.geoidComboBox.addItem(constants.CONST_GPS_3D_CAPTURE_PLUGIN_COMBOBOX_NO_SELECT_OPTION)
        qgisAppPath=QgsApplication.prefixPath()
        qgisDir=QDir(qgisAppPath)
        qgisDir.cdUp()
        qgisDir.cdUp()
        qgisPath=qgisDir.absolutePath()
        shareDir=QDir(qgisPath+constants.CONST_GPS_3D_CAPTURE_PLUGIN_GEOIDS_RELATIVE_PATH)
        self.GeoidsPath = qgisPath+constants.CONST_GPS_3D_CAPTURE_PLUGIN_GEOIDS_RELATIVE_PATH
        geoidFileNames = shareDir.entryList([constants.CONST_GPS_3D_CAPTURE_PLUGIN_GEOIDS_FILTER_1], QtCore.QDir.Files) #,QtCore.QDir.Name)
        for geoidFileName in geoidFileNames:
            geoidFileInfo=QFileInfo(geoidFileName)
            self.geoidComboBox.addItem(geoidFileInfo.baseName())

    def savePoint(self):
        fileName=self.csvFileLineEdit.text()
        geoidFileName = ""
        if self.geoidCheckBox.isChecked():
            geoidFileBasename = self.geoidComboBox.currentText()
            geoidFileName = self.GeoidsPath + "/" + geoidFileBasename + constants.CONST_GPS_3D_CAPTURE_PLUGIN_GEOIDS_FILE_EXTENSION
        dlg = GPS3DCapturePluginSavePointDialog(self.iface,
                                                fileName,
                                                self.crs,
                                                self.nameFieldCheckBox.isChecked(),
                                                self.numberFieldCheckBox.isChecked(),
                                                self.codeFieldCheckBox.isChecked(),
                                                self.heightFieldCheckBox.isChecked(),
                                                self.geoidCheckBox.isChecked(),
                                                geoidFileName,
                                                self.pointNumbers,
                                                self.antennaHeight)
        isValidDlg = dlg.isValid
        if not isValidDlg:
            return
        dlg.show() # show the dialog
        result = dlg.exec_() # Run the dialog
        self.antennaHeight = dlg.getAntennaHeight()

    def selectCrs(self):
        projSelector = QgsGenericProjectionSelector()
        ret = projSelector.exec_()
        if ret == 1: #QMessageBox.Ok:
            crsId=projSelector.selectedCrsId()
            self.crsAuthId=projSelector.selectedAuthId()
            self.crsLineEdit.setText(self.crsAuthId)
            self.crs.createFromUserInput(self.crsAuthId)
            if self.crs.geographicFlag():
                self.firstCoordinateFieldCheckBox.setText("Longitude")
                self.secondCoordinateFieldCheckBox.setText("Latitude")
            else:
                self.firstCoordinateFieldCheckBox.setText("Easting")
                self.secondCoordinateFieldCheckBox.setText("Northing")
            self.settings.setValue("crsAuthId",self.crsAuthId)
            self.settings.sync()

    def selectCsvFile(self):
        oldFileName=self.csvFileLineEdit.text()
        title="Select CSV file"
        filters="Files (*.csv)"
        fileName = QFileDialog.getSaveFileName(self,title,self.path,filters)
        if fileName:
            fileInfo = QFileInfo(fileName)
            self.path=fileInfo.absolutePath()
            self.csvFileLineEdit.setText(fileName)
            self.settings.setValue("last_path",self.path)
            self.settings.sync()

    def startProcess(self):
        fileName=self.csvFileLineEdit.text()
        if not fileName:
            msgBox=QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
            msgBox.setText("You must select CSV file")
            msgBox.exec_()
            return
        if QFile.exists(fileName):
            msgBox=QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
            text="Exists CSV file:\n"+fileName
            msgBox.setText(text)
            msgBox.setInformativeText("Do you want to rename it with current date an time?")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Ok)
            ret = msgBox.exec_()
            if ret == QMessageBox.Ok:
                dateTime =QDateTime.currentDateTime()
                strDateTime=dateTime.toString("yyyy-MM-dd_HH-mm-ss")
                fileInfo=QFileInfo(fileName)
                filePath=fileInfo.absolutePath()
                fileNameWithoutExtension=fileInfo.completeBaseName()
                fileExtension=fileInfo.completeSuffix()
                newFileName=filePath+"/"+fileNameWithoutExtension+"_"+strDateTime+"."+fileExtension
                if not QFile.copy(fileName,newFileName):
                    msgBox=QMessageBox(self)
                    msgBox.setIcon(QMessageBox.Warning)
                    msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
                    msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
                    msgBox.setText("Error copying existing file:\n"+fileName+"\n"+newFileName)
                    msgBox.exec_()
                    return
        strCrs=self.crsLineEdit.text()
        if not strCrs:
            msgBox=QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
            msgBox.setText("You must select the output CRS")
            msgBox.exec_()
            return
        applyGeoid=self.geoidCheckBox.isChecked()
        geoidModel=self.geoidComboBox.currentText()
        if applyGeoid and geoidModel == constants.CONST_GPS_3D_CAPTURE_PLUGIN_COMBOBOX_NO_SELECT_OPTION:
            msgBox=QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
            msgBox.setText("If you select substract geoide height \n you must select a geoid model")
            msgBox.exec_()
            return
        csvFile=QFile(fileName)
        if not csvFile.open(QIODevice.WriteOnly | QIODevice.Text):
            msgBox=QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
            msgBox.setText("Error opening for writting file:\n"+fileName)
            msgBox.exec_()
            return
        csvTextStream = QTextStream(csvFile)
        firstField=True
        if self.nameFieldCheckBox.isChecked():
            csvTextStream<<"Name"
            firstField=False
        if self.numberFieldCheckBox.isChecked():
            if not firstField:
                csvTextStream<<","
            else:
                firstField=False
            csvTextStream<<"Number"
        if not firstField:
            csvTextStream<<","
        else:
            firstField=False
        csvTextStream<<"Easting"
        csvTextStream<<","<<"Northing"
        if self.heightFieldCheckBox.isChecked():
            csvTextStream<<","<<"Height"
        if self.codeFieldCheckBox.isChecked():
            csvTextStream<<","<<"Code"
        csvFile.close()
        self.savePointPushButton.setEnabled(True)
        self.finishPushButton.setEnabled(True)
        self.csvFilePushButton.setEnabled(False)
        self.crsPushButton.setEnabled(False)
        self.geoidCheckBox.setEnabled(False)
        self.geoidComboBox.setEnabled(False)
        self.fieldsGroupBox.setEnabled(False)
        self.startPushButton.setEnabled(False)


