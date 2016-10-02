# -*- coding: utf-8 -*-

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore,uic
from qgis.core import *
from qgis.gui import QgsMessageBar

import constants

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
                 parent=None):
        """
        Brief:
        """
        super(GPS3DCapturePluginSavePointDialog, self).__init__(parent)
        self.setupUi(self)
        #self.setWindowTitle(title)

        #self.lst_nombre_clase = lst_nombre_clase # contenedor lista para almacenar parámetros tras salvar valores introducidos en el panel

        self.iface = iface # Save reference to the QGIS interface
        self.fileName = fileName
        self.crs = crs
        self.existsFieldName = existsFieldName
        self.existsFieldNumber = existsFieldNumber
        self.existsFieldCode = existsFieldCode
        self.existsFieldHeight = existsFieldHeight
        self.useGeoidModel = useGeoidModel
        self.geoidModelFileName = geoidModelFileName
        self.initialize()

    def initialize(self):
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
            if not self.useGeoidModel:
                self.heightGeoidLabel.setVisible(False)
                self.heightGeoidLineEdit.setVisible(False)
                self.heightFromGeoidLabel.setVisible(False)
                self.heightFromGeoidLineEdit.setVisible(False)
        self.adjustSize()
        QtCore.QObject.connect(self.namePushButton,QtCore.SIGNAL("clicked(bool)"),self.selectName)
        #QtCore.QObject.connect(self.numberPushButton,QtCore.SIGNAL("clicked(bool)"),self.selectNumber)
        #QtCore.QObject.connect(self.codePushButton,QtCore.SIGNAL("clicked(bool)"),self.selectCode)
        #QtCore.QObject.connect(self.namePushButton,QtCore.SIGNAL("clicked(bool)"),self.selectName)
        #QtCore.QObject.connect(self.namePushButton,QtCore.SIGNAL("clicked(bool)"),self.selectName)

    def selectName(self):
        oldText=self.nameLineEdit.text()
        label = "Input Point Name:"
        title = constants.CONST_GPS_3D_CAPTURE_PLUGIN_SAVE_POINT_WINDOW_TITLE
        [text,ok]= QInputDialog.getText(self,title,label, QLineEdit.Normal,oldText)
        if ok and text:
            text = text.strip()
            if not text == oldText:
                self.nameLineEdit.setText(text)
                #self.settings.setValue("documents/geoFtpIp",text)
