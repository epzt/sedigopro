# -*- coding: utf-8 -*-
"""
/***************************************************************************
 sediGoProDialog
                                 A QGIS plugin
 Manage image remotly capture with a GoPro camera
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-04-06
        git sha              : $Format:%H$
        copyright            : (C) 2019 by E. Poizot / Cnam-Intechmer (France)
        email                : emmanuel.poizot@lecnam.net
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

from PyQt5 import uic, QtWidgets, QtGui, QtCore
from qgis.core import QgsApplication
from goprocam import GoProCamera, constants

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sedigopro_dialog_base.ui'))

GOPROVIEWHEIGHT = 300
GOPROVIEWWIDTH = 400
GOPROULVIEWPOS = QtCore.QPointF(4,4)
GOPROURVIEWPOS = QtCore.QPointF(GOPROVIEWWIDTH-4,4)
GOPROLLVIEWPOS = QtCore.QPointF(5,GOPROVIEWHEIGHT-4)
GOPROLRVIEWPOS = QtCore.QPointF(GOPROVIEWWIDTH-4,GOPROVIEWHEIGHT-4)
CENTER = QtCore.QPoint(200,150)
# Adapt this value to your GOPRO camera type
GOPROPREFIX = "100GOPRO-"

class sediGoProDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(sediGoProDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.parentApp = parent
        self.setupUi(self)

        self.gopro = False
        self.workingDir = os.path.expanduser("~")
        # Check if New path exists
        if os.path.exists(self.workingDir) :
            # Change the current working Directory    
            os.chdir(self.workingDir)
            self.currentDirectoryLabel.setText(self.workingDir)
        else:
            QtWidgets.QMessageBox.information(self,"Error",f'Can\'t change to {self.workingDir}')
        #self.prefixImageName = ""
        self.textTagColor = QtCore.Qt.black
        self.setTagTextColor(self.textTagColor)
        self.GPSInfo = False
        self.defaultPrefix = GOPROPREFIX
        self.currentPosition = [0.0,0.0]
        self.batteryProgressBar.setValue(0)

        self.setWorkingDirectoryButton.setEnabled(True)
        self.getGoProImageButton.setEnabled(False)
        self.tagImageButton.setEnabled(False)
        self.saveImageButton.setEnabled(False)
        self.setGoProOffButton.setEnabled(False)
        self.setGoProOnButton.setEnabled(False)
        self.defaultPrefixLineEdit.setText(self.defaultPrefix)
        
        self.connectGoProCameraButton.clicked.connect(self.connectGoProCamera)
        self.setWorkingDirectoryButton.clicked.connect(self.setWorkingDirectory)
        self.getGoProImageButton.clicked.connect(self.getGoProImage)
        self.setGoProOffButton.clicked.connect(self.setGoProOff)
        self.setGoProOnButton.clicked.connect(self.connectGoProCamera)
        self.tagImageButton.clicked.connect(self.setTagImage)
        self.whiteTagTextButton.clicked.connect(self.setTagTextColorWhite)
        self.blackTagTextButton.clicked.connect(self.setTagTextColorBlack)
        self.saveImageButton.clicked.connect(self.saveImage)
        self.defaultPrefixLineEdit.textEdited.connect(self.defaultPrefixChanged)
        self.otherColorButton.clicked.connect(self.setTextColor)
        self.currentPositionButton.clicked.connect(self.getCurrentPosition)
        self.numImageSpinBox.valueChanged.connect(self.numSpinBoxValueChanged)
        self.setImageFileNameButton.clicked.connect(self.setFileImageName)
    def connectGoProCamera(self):
        self.setCursor(QtCore.Qt.WaitCursor)
        try:
            self.gopro = GoProCamera.GoPro()
        except:
            QtWidgets.QMessageBox.warning(self,"GoPro information","Enable to connect to GoPro camera")
            return
        if self.gopro.getStatusRaw(): # Try to get something from the camera if connected fine
            self.connectionStatusLabel.setStyleSheet("QLabel {color: green}")
            self.connectionStatusLabel.setText("CONNECTED")
            self.gopro.mode(constants.Mode.PhotoMode)
            self.setWorkingDirectoryButton.setEnabled(True)
            self.getGoProImageButton.setEnabled(True)
            self.tagImageButton.setEnabled(True)
            self.saveImageButton.setEnabled(True)
            self.setGoProOffButton.setEnabled(True)
            self.setGoProOnButton.setEnabled(False)
            self.updateBatteryLevel()
        else:
            QtWidgets.QMessageBox.warning(self,"GoPro information","Enable to connect to GoPro camera")
        self.setCursor(QtCore.Qt.ArrowCursor)

    def setWorkingDirectory(self):
        self.workingDir = QtWidgets.QFileDialog.getExistingDirectory(self, self.workingDir, "Select working directory...", QtWidgets.QFileDialog.ShowDirsOnly)
        if self.workingDir:
            # Check if New path exists
            if os.path.exists(self.workingDir):
                # Change the current working Directory
                os.chdir(self.workingDir)
                self.currentDirectoryLabel.setText(self.workingDir)
            else:
                QtWidgets.QMessageBox.information(self, "Error", f'Can\'t change to {self.workingDir}')

    def getGoProImage(self):
        # Erase previous name if any
        lastImageName = ""
        self.prefixTextTagLineEdit.setText(lastImageName)
        # Take a picture and download it
        self.gopro.downloadLastMedia(self.gopro.take_photo())
        # Save the name of the last picture and update GUI
        imgName = self.gopro.getMediaInfo("file")
        # Construct the name of the file as it is download in current location (with default GOPRO prefix
        lastImageName = f'{GOPROPREFIX}{imgName}'
        # Rename the file with user defined prefix
        os.rename(lastImageName, f'{self.defaultPrefix}{imgName}')
        # Set the current file name with user prefix
        lastImageName = f'{self.defaultPrefix}{imgName}'
        # Update GUI for saving purpose
        self.prefixTextTagLineEdit.setText(lastImageName.split(".")[0])
        self.imageNameLineEdit.setText(lastImageName.split(".")[0])
        # Delete last picture from GoPro
        self.gopro.delete("last")
        # Get the battery level and update the GUI
        self.updateBatteryLevel()
        # Draw the image
        self.drawGoProImage(lastImageName)
        # Get GNSS info to tag position on the picture
        self.getCurrentPosition()
        '''
        connectionRegistry = QgsApplication.gpsConnectionRegistry()
        connectionList = connectionRegistry.connectionList()
        if len(connectionList) > 0:
            self.GPSInfo = connectionList[0].currentGPSInformation()
        else:
            QtWidgets.QMessageBox.warning(self, "GPS information", "Can\'t load GPS information")
        '''
    def setGoProOff(self):
        self.gopro.power_off()
        self.connectionStatusLabel.setStyleSheet("QLabel {color: red}")
        self.connectionStatusLabel.setText("NOT CONNECTED")
        self.getGoProImageButton.setEnabled(False)
        self.tagImageButton.setEnabled(False)
        self.saveImageButton.setEnabled(False)
        self.setGoProOnButton.setEnabled(True)
        self.batteryProgressBar.setValue(0)
    def setGoProOn(self):
        self.drawGoProImage("/home/epoizot/100GOPRO-GOPR2161.JPG")
        #self.gopro.power_on()
        #self.connectionStatusLabel.setText("CONNECTED")
        self.getGoProImageButton.setEnabled(True)
        self.tagImageButton.setEnabled(True)
        self.saveImageButton.setEnabled(True)
        # Get the battery level and update the GUI
        self.updateBatteryLevel()
      
    def getGoProCameraInfo(self):
        QtWidgets.QMessageBox.information(self,"GoPro information",self.gopro.overview())
    
    def getImageName(self):
        if self.imageNameLineEdit != self.prefixTextTagLineEdit.text():
            return

    def drawGoProImage(self,fname):
        scene = QtWidgets.QGraphicsScene()
        pixmap = QtGui.QPixmap(fname)
        pixmap = pixmap.scaled(GOPROVIEWWIDTH,GOPROVIEWHEIGHT,QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        scene.addPixmap(pixmap)
        self.imageGoProViewer.setScene(scene)

    def setTagTextColor(self, _color):
        self.textTagColor = _color
        palette = self.currentColorButton.palette()
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(_color))
        self.currentColorButton.setPalette(palette)

    def setTagTextColorWhite(self):
        self.textTagColor = QtCore.Qt.white
        self.setTagTextColor(self.textTagColor)

    def setTagTextColorBlack(self):
        self.textTagColor = QtCore.Qt.black
        self.setTagTextColor(self.textTagColor)

    def getNewFileNameImage(self,prefix):
        # get the number at the spinbox and construc the new name
        retText = "{}-{:04d}".format(prefix,self.numImageSPinBox.value())
        return retText

    def isNewFileNameImageExist(self,newfname):
        return os.path.isfile(newfname)

    def setTagImage(self):
        # Get text to print on image
        texttag = self.prefixTextTagLineEdit.text()
        # Verification of the existence of the new file name
        if self.isNewFileNameImageExist(self.getNewFileNameImage(texttag)):
            QtWidgets.QMessageBox.critical(self,"Error",f'File {self.getNewFileNameImage(texttag)} exist.')
            return
        # Get image item, considering it's the only one on the centre of the view
        item = self.imageGoProViewer.itemAt(CENTER)
        scene = QtWidgets.QGraphicsScene()
        scene.setSceneRect(self.imageGoProViewer.sceneRect())
        # Add the image to the scene
        scene.addItem(item)
        self.imageGoProViewer.setScene(scene)
        textitem = QtWidgets.QGraphicsTextItem(self.getNewFileNameImage(texttag))
        textitem.setParent(self.imageGoProViewer)
        textitem.setDefaultTextColor(QtGui.QColor(self.textTagColor))
        # item for GNSS tag information
        print(f'G: {self.currentPosition[0]} L: {self.currentPosition[1]}')
        positionTag = 'G: {0:.6f}\n'.format(float(self.currentPosition[0]))
        positionTag += 'L: {0:.6f}'.format(float(self.currentPosition[1]))
        positionItem = QtWidgets.QGraphicsTextItem(positionTag)

        # Current text settings
        positionItem.setParent(self.imageGoProViewer)
        positionItem.setDefaultTextColor(QtGui.QColor(self.textTagColor))
        # Place the text at the define place
        textWidth = textitem.document().size().width()
        positionTextWidth = positionItem.document().size().width()
        textHeight = textitem.document().size().height()
        positionTextHeight = positionItem.document().size().height()
        if self.llRadioButton.isChecked():
            textitem.setPos(GOPROLLVIEWPOS-QtCore.QPointF(0,textHeight))
            positionItem.setPos(GOPROULVIEWPOS)
        elif self.lrRadioButton.isChecked():
            textitem.setPos(GOPROLRVIEWPOS-QtCore.QPointF(textWidth,textHeight))
            positionItem.setPos(GOPROURVIEWPOS-QtCore.QPointF(positionTextWidth,0))
        elif self.urRadioButton.isChecked():
            textitem.setPos(GOPROURVIEWPOS-QtCore.QPointF(textWidth,0))
            positionItem.setPos(GOPROLRVIEWPOS-QtCore.QPointF(positionTextWidth,positionTextHeight))
        elif self.ulRadioButton.isChecked():
            textitem.setPos(GOPROULVIEWPOS)
            positionItem.setPos(GOPROLLVIEWPOS-QtCore.QPointF(0,positionTextHeight))
        scene.addItem(textitem)
        scene.addItem(positionItem)
        # When tagged, proposal of a new file name
        self.imageNameLineEdit.setText(self.getNewFileNameImage(texttag))
        #textitem.setParent(self.imageGoProViewer)

    def setFileImageName(self):
        self.imageNameLineEdit.setText(self.prefixTextTagLineEdit.text())

    def saveImage(self):
        # Do some checking before saving the file
        if not self.imageNameLineEdit.text():
            QtWidgets.QMessageBox.critical(self,"Error","Enter a file name to save.")
            return
        if self.isNewFileNameImageExist(f'{self.imageNameLineEdit.text()}.JPG'):
            QtWidgets.QMessageBox.critical(self,"Error",f'File {self.imageNameLineEdit.text()}.JPG exist.')
            return
        # Get region of scene to capture.
        area = self.imageGoProViewer.sceneRect()
        # Create a QImage to render to and fix up a QPainter for it.
        image = QtGui.QImage(area.width(), area.height(), QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(image)
        # Render the region of interest to the QImage.
        self.imageGoProViewer.render(painter)
        painter.end()
        # Save the image to a file.
        image.save(f'{self.imageNameLineEdit.text()}.JPG', "jpg")

    def defaultPrefixChanged(self, newText):
        self.defaultPrefix = newText
        self.prefixTextChanged(newText)

    def prefixTextChanged(self, newText):
        self.prefixTextTagLineEdit.setText("{}{:04d}".format(newText, self.numImageSpinBox.value()))

    def numSpinBoxValueChanged(self, newValue):
        self.prefixTextTagLineEdit.setText("{}{:04d}".format(self.defaultPrefix, newValue))

    def setTextColor(self):
        colDiag = QtWidgets.QColorDialog(self)
        if colDiag.exec_():
            self.textTagColor = colDiag.currentColor()
            self.setTagTextColor(self.textTagColor)

    def updateBatteryLevel(self):
        # Get the battery level and update the GUI
        batteryLevel = self.gopro.getStatus(constants.Status.Status, constants.Status.STATUS.BatteryLevel)
        if batteryLevel:
            self.batteryProgressBar.setValue(int(batteryLevel * 100/3))
        else:
            self.batteryProgressBar.setValue(0)

    def getCurrentPosition(self):
        # Get GNSS info to tag position on the picture
        connectionRegistry = QgsApplication.gpsConnectionRegistry()
        connectionList = connectionRegistry.connectionList()
        if len(connectionList) > 0:
            self.GPSInfo = connectionList[0].currentGPSInformation()
            self.currentPosition = [self.GPSInfo.longitude, self.GPSInfo.latitude]
        else:
            QtWidgets.QMessageBox.warning(self, "GPS information", "Can\'t load GPS information")
        
