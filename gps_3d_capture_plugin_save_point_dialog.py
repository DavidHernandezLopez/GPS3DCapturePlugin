# -*- coding: utf-8 -*-

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, uic
from qgis.core import *
from qgis.core import (QgsGPSDetector, QgsGPSConnectionRegistry, QgsPoint, \
                        QgsCoordinateTransform, QgsCoordinateReferenceSystem, \
                        QgsGPSInformation)
from qgis.core import QgsRasterLayer
from qgis.core import QgsRaster
from qgis.gui import QgsMessageBar
import gdal
from gdalconst import *

import constants
import re

# codificación utf-8
import os
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'gps_3d_capture_plugin_save_point_dialog.ui'))


class GPS3DCapturePluginSavePointDialog(QDialog, FORM_CLASS):
    """
    Brief:
    """

    def __init__(self,
                 iface,
                 fileName,
                 crs,
                 existsFieldName,
                 existsFieldNumber,
                 existsFieldCode,
                 existsFieldHeight,
                 useGeoidModel,
                 geoidModelFileName,
                 pointNumbers,
                 antennaHeight,
                 parent=None):
        """
        Brief:
        """
        super(GPS3DCapturePluginSavePointDialog, self).__init__(parent)
        self.setupUi(self)
        # self.setWindowTitle(title)

        # self.lst_nombre_clase = lst_nombre_clase # contenedor lista para almacenar parámetros tras salvar valores introducidos en el panel

        self.iface = iface  # Save reference to the QGIS interface
        self.fileName = fileName
        self.crs = crs
        self.existsFieldName = existsFieldName
        self.existsFieldNumber = existsFieldNumber
        self.existsFieldCode = existsFieldCode
        self.existsFieldHeight = existsFieldHeight
        self.useGeoidModel = useGeoidModel
        self.geoidModelFileName = geoidModelFileName
        self.pointNumbers = pointNumbers
        self.antennaHeight = antennaHeight
        self.num_format = re.compile(r'^\-?[1-9][0-9]*\.?[0-9]*')
        self.initialize()
        self.updatePosition()

    def getAntennaHeight(self):
        return self.antennaHeight

    def initialize(self):
        self.isValid = True
        if self.crs.geographicFlag():
           self.firstCoordinateLabel.setText("Longitude")
           self.secondCoordinateLabel.setText("Latitude")
        else:
           self.firstCoordinateLabel.setText("Easting")
           self.secondCoordinateLabel.setText("Northing")
        if not self.existsFieldName:
            self.namePushButton.setVisible(False)
            self.nameLineEdit.setVisible(False)
        if not self.existsFieldNumber:
            self.numberPushButton.setVisible(False)
            self.numberLineEdit.setVisible(False)
        if not self.existsFieldCode:
            self.codePushButton.setVisible(False)
            self.codeLineEdit.setVisible(False)
        if not self.existsFieldHeight:
            self.heightAntennaPushButton.setVisible(False)
            self.heightAntennaLineEdit.setVisible(False)
            self.heightGpsLabel.setVisible(False)
            self.heightGpsLineEdit.setVisible(False)
            self.heightGroundLabel.setVisible(False)
            self.heightGroundLineEdit.setVisible(False)
            self.heightGeoidLabel.setVisible(False)
            self.heightGeoidLineEdit.setVisible(False)
            self.heightFromGeoidLabel.setVisible(False)
            self.heightFromGeoidLineEdit.setVisible(False)
        else:
            strAntennaHeigth=constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_ANTENNA_HEIGHT_PRECISION.format(self.antennaHeight)
            self.heightAntennaLineEdit.setText(strAntennaHeigth)
            if not self.useGeoidModel:
                self.heightGeoidLabel.setVisible(False)
                self.heightGeoidLineEdit.setVisible(False)
                self.heightFromGeoidLabel.setVisible(False)
                self.heightFromGeoidLineEdit.setVisible(False)
        candidateValue = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_FIRST_POINT_NUMBER
        if self.pointNumbers != []:
            candidateValue = self.pointNumbers(len(self.pointNumbers) - 1)
        self.numberLineEdit.setText(str(candidateValue))
        self.adjustSize()
        QtCore.QObject.connect(self.namePushButton, QtCore.SIGNAL("clicked(bool)"), self.selectName)
        QtCore.QObject.connect(self.numberPushButton,QtCore.SIGNAL("clicked(bool)"),self.selectNumber)
        QtCore.QObject.connect(self.codePushButton, QtCore.SIGNAL("clicked(bool)"), self.selectCode)
        QtCore.QObject.connect(self.heightAntennaPushButton,QtCore.SIGNAL("clicked(bool)"),self.selectAntennaHeight)
        QtCore.QObject.connect(self.updatePositionPushButton,QtCore.SIGNAL("clicked(bool)"),self.updatePosition)
        self.buttonBox.accepted.connect(self.selectAccept)
        epsgCodeGps = constants.CONST_GPS_3D_CAPTURE_PLUGIN_EPSG_CODE_GPS
        self.crsGps = QgsCoordinateReferenceSystem(epsgCodeGps)
        if not self.crsGps.isValid():
            msgBox=QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
            msgBox.setText("Error creating CRS by EPSG Code: "+str(epsgCodeGps))
            msgBox.exec_()
            self.isValid = False
            return
        self.crsOperationFromGps = QgsCoordinateTransform(self.crsGps,self.crs)
        if self.useGeoidModel:
            if not QFile.exists(self.geoidModelFileName):
                msgBox=QMessageBox(self)
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
                msgBox.setText("Geoid Model file not exists:\n"+self.geoidModelFileName)
                msgBox.exec_()
                self.isValid = False
                return
            # self.geoidDataset = gdal.Open( self.geoidModelFileName, GA_ReadOnly )
            # if self.geoidDataset is None:
            #     msgBox=QMessageBox(self)
            #     msgBox.setIcon(QMessageBox.Information)
            #     msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
            #     msgBox.setText("Error opening Geoid Model file:\n"+self.geoidModelFileName)
            #     msgBox.exec_()
            #     self.isValid = False
            #     return
            geoidModelFileInfo = QFileInfo(self.geoidModelFileName)
            geoidModelPath = geoidModelFileInfo.filePath()
            geoidModelBaseName = geoidModelFileInfo.baseName()
            self.geoidModel = QgsRasterLayer(geoidModelPath, geoidModelBaseName)
        #self.buttonBox.rejected.connect(self.selectReject)
        # QtCore.QObject.connect(self.namePushButton,QtCore.SIGNAL("clicked(bool)"),self.selectName)

    def isValid(self):
        return self.isValid

    def selectAccept(self):
        # msgBox=QMessageBox(self)
        # msgBox.setIcon(QMessageBox.Information)
        # msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
        # msgBox.setText("Accept button")
        # msgBox.exec_()
        connectionRegistry = QgsGPSConnectionRegistry().instance()
        connectionList = connectionRegistry.connectionList()
        if connectionList == []:
            msgBox=QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
            msgBox.setText("GPS connection not detected.\nConnect a GPS and try again")
            msgBox.exec_()
            return
        csvFile=QFile(self.fileName)
        if not csvFile.open(QIODevice.Append | QIODevice.Text):
            msgBox=QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
            msgBox.setText("Error opening for writting file:\n"+self.fileName)
            msgBox.exec_()
            return
        csvTextStream = QTextStream(csvFile)
        csvTextStream<<"\n"
        if self.existsFieldName:
            name = self.nameLineEdit.text()
            csvTextStream<<name<<","
        number = self.numberLineEdit.text()
        csvTextStream<<number<<","
        GPSInfo = connectionList[0].currentGPSInformation()
        firstCoordinate = GPSInfo.longitude
        secondCoordinate = GPSInfo.latitude
        pointCrsGps = QgsPoint(firstCoordinate,secondCoordinate)
        pointCrs = self.crsOperationFromGps.transform(pointCrsGps)
        firstCoordinate = pointCrs.x()
        secondCoordinate = pointCrs.y()
        if self.crs.geographicFlag():
            strFirstCoordinate = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_LONGITUDE_PRECISION.format(firstCoordinate)
            strSecondCoordinate = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_LATITUDE_PRECISION.format(secondCoordinate)
        else:
            strFirstCoordinate = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_EASTING_PRECISION.format(firstCoordinate)
            strSecondCoordinate = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_NORTHING_PRECISION.format(secondCoordinate)
        self.firstCoordinateLineEdit.setText(strFirstCoordinate)
        self.secondCoordinateLineEdit.setText(strSecondCoordinate)
        csvTextStream<<strFirstCoordinate<<","
        csvTextStream<<strSecondCoordinate
        if self.existsFieldHeight:
            height = GPSInfo.elevation
            strHeight=constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_HEIGHT_PRECISION.format(height)
            self.heightGpsLineEdit.setText(strHeight)
            csvTextStream<<","<<strHeight
            if self.useGeoidModel:
                geoidHeight = 50.0
                strGeoidHeight=constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_GEOID_HEIGHT_PRECISION.format(geoidHeight)
                heightFromGeoid = height - geoidHeight
                strHeightFromGeoid = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_HEIGHT_FROM_GEOID_PRECISION.format(geoidHeight)
                self.heightGeoidLineEdit.setText(strGeoidHeight)
                self.heightFromGeoidLineEdit.settText(strHeightFromGeoid)
        if self.existsFieldCode:
            code = self.codeLineEdit.text()
            csvTextStream<<","<<code
        csvFile.close()
        self.accept()

    def selectCode(self):
        oldText = self.codeLineEdit.text()
        label = "Input Point Code:"
        title = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_WINDOW_TITLE
        [text, ok] = QInputDialog.getText(self, title, label, QLineEdit.Normal, oldText)
        if ok and text:
            text = text.strip()
            if not text == oldText:
                self.codeLineEdit.setText(text)
                # self.settings.setValue("documents/geoFtpIp",text)

    def selectAntennaHeight(self):
        strCandidateValue = self.heightAntennaLineEdit.text()
        label = "Input Antenna Height:"
        title = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_WINDOW_TITLE
        ok = False
        while not ok:
            [text, ok] = QInputDialog.getText(self, title, label, QLineEdit.Normal, strCandidateValue)
            if ok and text:
                value = 0.0
                text = text.strip()
                if text.isdigit() or re.match(self.num_format,text):
                    value = float(text)
                    if (value < constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_ANTENNA_HEIGHT_MINIMUM_VALUE
                        or value > constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_ANTENNA_HEIGHT_MAXIMUM_VALUE):
                        ok = False
                else:
                    ok = False
                if ok:
                    strValue=constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_ANTENNA_HEIGHT_PRECISION.format(value)
                    self.heightAntennaLineEdit.setText(strValue)
                    self.updatePosition()
                    # self.settings.setValue("documents/geoFtpIp",text)
            else:
                if not ok:
                    ok = True

    def selectName(self):
        oldText = self.nameLineEdit.text()
        label = "Input Point Name:"
        title = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_WINDOW_TITLE
        [text, ok] = QInputDialog.getText(self, title, label, QLineEdit.Normal, oldText)
        if ok and text:
            text = text.strip()
            if not text == oldText:
                self.nameLineEdit.setText(text)
                # self.settings.setValue("documents/geoFtpIp",text)

    def selectNumber(self):
        if self.pointNumbers == []:
            candidateValue = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_FIRST_POINT_NUMBER
        else:
            candidateValue = self.pointNumbers(len(self.pointNumbers) - 1)
        label = "Input Point Number:"
        title = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_WINDOW_TITLE
        ok = False
        while not ok:
            [text, ok] = QInputDialog.getText(self, title, label, QLineEdit.Normal, str(candidateValue))
            if ok and text:
                text = text.strip()
                if not text.isdigit():
                    ok = False
                else:
                    value = int(text)
                    if (value < constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_POINT_NUMBER_MINIMUM_VALUE
                        or value > constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_POINT_NUMBER_MAXIMUM_VALUE):
                        ok = False
                if ok:
                    self.numberLineEdit.setText(text)
                    # self.settings.setValue("documents/geoFtpIp",text)
            else:
                if not ok:
                    ok = True

    def updatePosition(self):
        connectionRegistry = QgsGPSConnectionRegistry().instance()
        connectionList = connectionRegistry.connectionList()
        if connectionList == []:
            msgBox=QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(constants.CONST_GPS_3D_CAPTURE_PLUGIN_WINDOW_TITLE)
            msgBox.setText("GPS connection not detected.\nConnect a GPS and try again")
            msgBox.exec_()
            return
        GPSInfo = connectionList[0].currentGPSInformation()
        firstCoordinate = GPSInfo.longitude
        secondCoordinate = GPSInfo.latitude
        pointCrsGps = QgsPoint(firstCoordinate,secondCoordinate)
        pointCrs = self.crsOperationFromGps.transform(pointCrsGps)
        firstCoordinate = pointCrs.x()
        secondCoordinate = pointCrs.y()
        if self.crs.geographicFlag():
            strFirstCoordinate = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_LONGITUDE_PRECISION.format(firstCoordinate)
            strSecondCoordinate = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_LATITUDE_PRECISION.format(secondCoordinate)
        else:
            strFirstCoordinate = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_EASTING_PRECISION.format(firstCoordinate)
            strSecondCoordinate = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_NORTHING_PRECISION.format(secondCoordinate)
        self.firstCoordinateLineEdit.setText(strFirstCoordinate)
        self.secondCoordinateLineEdit.setText(strSecondCoordinate)
        antennaHeight = float(self.heightAntennaLineEdit.text())
        if self.existsFieldHeight:
            height = GPSInfo.elevation
            heightGround = height - antennaHeight
            strHeight=constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_HEIGHT_PRECISION.format(height)
            self.heightGpsLineEdit.setText(strHeight)
            strHeightGround = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_HEIGHT_PRECISION.format(heightGround)
            self.heightGroundLineEdit.setText(strHeightGround)
            if self.useGeoidModel:
                geoidFirstCoordinate = firstCoordinate
                geoidSecondCoordinate = secondCoordinate
                geoidPoint = QgsPoint(geoidFirstCoordinate,geoidSecondCoordinate)
                geoidHeight = self.geoidModel.geodataProvider().identify(geoidPoint,QgsRaster.IdentifyFormatValue)
                strGeoidHeight=constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_GEOID_HEIGHT_PRECISION.format(geoidHeight)
                heightFromGeoid = height - geoidHeight
                strHeightFromGeoid = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_HEIGHT_FROM_GEOID_PRECISION.format(geoidHeight)
                self.heightGeoidLineEdit.setText(strGeoidHeight)
                self.heightFromGeoidLineEdit.settText(strHeightFromGeoid)
