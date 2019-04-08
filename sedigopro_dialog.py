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

import time

from PyQt5 import uic
from PyQt5 import QtWidgets, QtGui, QtCore

from goprocam import GoProCamera, constants

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sedigopro_dialog_base.ui'))

GOPROVIEWHEIGHT = 300
GOPROVIEWWIDTH = 400
GOPROULVIEWPOS = QtCore.QPointF(5,4)
GOPROURVIEWPOS = QtCore.QPointF(GOPROVIEWWIDTH-90,4)
GOPROLLVIEWPOS = QtCore.QPointF(5,GOPROVIEWHEIGHT-24)
GOPROLRVIEWPOS = QtCore.QPointF(GOPROVIEWWIDTH-90,GOPROVIEWHEIGHT-24)
CENTER = QtCore.QPoint(200,150)
PREFIX100GOPRO = "100GOPRO-"

class sediGoProDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(sediGoProDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.gopro = False
        self.workingDir = os.path.expanduser("~")
        # Check if New path exists
        if os.path.exists(self.workingDir) :
            # Change the current working Directory    
            os.chdir(self.workingDir)
            self.currentDirectoryLabel.setText(self.workingDir)
        else:
            QtGui.QMessageBox.information(self,"Error",f'Can\'t change to {self.workingDir}')   
        #self.prefixImageName = ""
        self.textTagColor = "" 
        self.setTagTextColorBlack()

        self.setWorkingDirectoryButton.setEnabled(True)
        self.getGoProImageButton.setEnabled(False)
        self.tagImageButton.setEnabled(False)
        self.saveImageButton.setEnabled(False)
        self.setGoProOffButton.setEnabled(False)
        #self.setGoProOnButton.setEnabled(False)
        
        self.connectGoProCameraButton.clicked.connect(self.connectGoProCamera)
        self.setWorkingDirectoryButton.clicked.connect(self.setWorkingDirectory)
        self.getGoProImageButton.clicked.connect(self.getGoProImage)
        self.setGoProOffButton.clicked.connect(self.setGoProOff)
        #self.setGoProOnButton.clicked.connect(self.setGoProOn)
        self.tagImageButton.clicked.connect(self.setTagImage)
        self.whiteTagTextButton.clicked.connect(self.setTagTextColorWhite)
        self.blackTagTextButton.clicked.connect(self.setTagTextColorBlack)
        self.saveImageButton.clicked.connect(self.saveImage)

    def connectGoProCamera(self):
        self.gopro = GoProCamera.GoPro()
        if self.gopro:
            self.connectionStatusLabel.setStyleSheet("QLabel {color: green}")
            self.connectionStatusLabel.setText("CONNECTED")
            self.gopro.mode(constants.Mode.PhotoMode)
            self.setWorkingDirectoryButton.setEnabled(True)
            self.getGoProImageButton.setEnabled(True)
            self.tagImageButton.setEnabled(True)
            self.saveImageButton.setEnabled(True)
            self.setGoProOffButton.setEnabled(True)
            #self.setGoProOnButton.setEnabled(True)
    
    def setWorkingDirectory(self):
        self.workingDir = QtGui.QFileDialog.getExistingDirectory(self, self.workingDir, "Select working directory...", QtGui.QFileDialog.ShowDirsOnly)
        self.currentDirectoryLabel.setText(self.workingDir)
        # Check if New path exists
        if os.path.exists(self.workingDir) :
            # Change the current working Directory    
            os.chdir(self.workingDir)
        else:
            QtGui.QMessageBox.information(self,"Error",f'Can\'t change to {self.workingDir}')   

    def getGoProImage(self):
        # Erase previous name if any
        lastImageName = ""
        self.prefixTextTagLineEdit.setText(lastImageName)
        # Take a picture and download it
        self.gopro.downloadLastMedia(self.gopro.take_photo())
        # Save the name of the last picture and update GUI
        imgName = self.gopro.getMediaInfo("file")
        self.prefixTextTagLineEdit.setText("{}{}".format(PREFIX100GOPRO,imgName.split(".")[0]))
        lastImageName = "{}{}".format(PREFIX100GOPRO,imgName)
        # Update GUI for saving purpose
        self.imageNameLineEdit.setText("{}{}".format(PREFIX100GOPRO,imgName.split(".")[0]))
        # Delete last picture from GoPro
        self.gopro.delete("last")
        # Get the battery level and update the GUI
        batteryLevel = self.gopro.getStatus(constants.Status.Status, constants.Status.STATUS.BatteryLevel) 
        self.batterySlider.setValue(int(batteryLevel * 33.33))
        # Draw the image
        print(lastImageName)
        self.drawGoProImage(lastImageName)

    def setGoProOff(self):
        self.gopro.power_off()
        self.connectionStatusLabel.setStyleSheet("QLabel {color: red}")
        self.connectionStatusLabel.setText("NOT CONNECTED")
        self.getGoProImageButton.setEnabled(False)
        self.tagImageButton.setEnabled(False)
        self.saveImageButton.setEnabled(False)
        
    def setGoProOn(self):
        self.drawGoProImage("/home/epoizot/100GOPRO-GOPR2161.JPG")
        #self.gopro.power_on()
        #self.connectionStatusLabel.setText("CONNECTED")
        self.getGoProImageButton.setEnabled(True)
        self.tagImageButton.setEnabled(True)
        self.saveImageButton.setEnabled(True)
        # Get the battery level and update the GUI
        #batteryLevel = self.gopro.getStatus(constants.Status.Status, constants.Status.STATUS.BatteryLevel) 
        #self.batterySlider.setValue(int(batteryLevel * 33.33))
      
    def getGoProCameraInfo(self):
        QtGui.QMessageBox.information(self,"GoPro information",self.gopro.overview())
    
    def getImageName(self):
        if self.imageNameLineEdit != self.prefixTextTagLineEdit.text():
            return

    def drawGoProImage(self,fname):
        scene = QtGui.QGraphicsScene()
        pixmap = QtGui.QPixmap(fname)
        pixmap = pixmap.scaled(GOPROVIEWWIDTH,GOPROVIEWHEIGHT,QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        scene.addPixmap(pixmap)
        self.imageGoProViewer.setScene(scene)
    
    def setTagTextColorWhite(self):
        self.textTagColor = "white"
        self.textTagColorLabel.setText(f'Set text color: {self.textTagColor.upper()}')

    def setTagTextColorBlack(self):
        self.textTagColor = "black"
        self.textTagColorLabel.setText(f'Set text color: {self.textTagColor.upper()}')

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
            QtGui.QMessageBox.critical(self,"Error",f'File {self.getNewFileNameImage(texttag)} exist.')
            return
        # Get image item, considering it's the only one on the centre of the view
        item = self.imageGoProViewer.itemAt(CENTER)
        scene = QtGui.QGraphicsScene()
        scene.setSceneRect(self.imageGoProViewer.sceneRect())
        # Add the image to the scene
        scene.addItem(item)
        self.imageGoProViewer.setScene(scene)
        textitem = QtGui.QGraphicsTextItem(self.getNewFileNameImage(texttag))
        textitem.setParent(self.imageGoProViewer)
        textitem.setDefaultTextColor(QtGui.QColor(self.textTagColor))
        # Place the text at the define place
        if self.llRadioButton.isChecked():
            textitem.setPos(GOPROLLVIEWPOS)
        elif self.lrRadioButton.isChecked():
            textitem.setPos(GOPROLRVIEWPOS)
        elif self.urRadioButton.isChecked():
            textitem.setPos(GOPROURVIEWPOS)
        elif self.ulRadioButton.isChecked():
            textitem.setPos(GOPROULVIEWPOS)
        scene.addItem(textitem)
        # When tagged, proposal of a new file name
        self.imageNameLineEdit.setText(self.getNewFileNameImage(texttag))
        #textitem.setParent(self.imageGoProViewer)
        
    def saveImage(self):
        # Do some checking before saving the file
        if not self.imageNameLineEdit.text():
            QtGui.QMessageBox.critical(self,"Error","Enter a file name to save.")
            return
        if self.isNewFileNameImageExist(f'{self.imageNameLineEdit.text()}.JPG'):
            QtGui.QMessageBox.critical(self,"Error",f'File {self.imageNameLineEdit.text()}.JPG exist.')
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

        