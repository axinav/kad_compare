# -*- coding: utf-8 -*-
"""
/***************************************************************************
 KadCompareDialog
                                 A QGIS plugin
 Kadastr Compartion
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-05-02
        git sha              : $Format:%H$
        copyright            : (C) 2022 by axinav
        email                : axinav@gmail.com
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
import csv
import math
from qgis.core import *
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtCore import pyqtSlot
from .PointsNames import *
from .Dist2Kadastr import *
from .MathFeatures import *

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'kad_compare_dialog_base.ui'))


class KadCompareDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(KadCompareDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.kadCB.setFilters(QgsMapLayerProxyModel.Filter.PolygonLayer)
        self.pointKadCB.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
        self.factCB.setFilters(QgsMapLayerProxyModel.Filter.PolygonLayer)
        self.pointFactCB.setFilters(QgsMapLayerProxyModel.Filter.PointLayer)
        self.pointKadNameFieldCB.setLayer(self.pointKadCB.currentLayer())
        self.pointFactNameFieldCB.setLayer(self.pointFactCB.currentLayer())
        self.browseBtn.clicked.connect(self.browseFile)
        self.pointKadCB.currentIndexChanged.connect(self.pointKLayerChanged)
        self.pointFactCB.currentIndexChanged.connect(self.pointFLayerChanged)
        self.button_box.accepted.connect(self.run)


    def browseFile(self):
        newname=QtWidgets.QFileDialog.getSaveFileName(self,"Output Compartion CSV File", self.fileName.displayText(), "CSV File (*.csv *.txt)")
        if newname !=None:
            self.fileName.setText(newname[0])

   # @pyqtSlot()
    def pointKLayerChanged(self):
        self.pointKadNameFieldCB.setLayer(self.pointKadCB.currentLayer())
    def pointFLayerChanged(self):
        self.pointFactNameFieldCB.setLayer(self.pointFactCB.currentLayer())

    def loR(self, lor):
        if lor<0:
            return 'Снаружи'
        else:
            return 'Внутри'

    def inverseGeoTask(self, pKad, pFact):
        geom = QgsGeometry().fromPolylineXY([pKad,pFact])
        dist = geom.length()
        angle = math.degrees(geom.angleAtVertex(0))
        return (dist,angle) 

    def run(self):
        matchingDict=MatchFeatures(self.kadCB.currentLayer(),self.factCB.currentLayer()).matchingByDist()
        try:
            csvFile=open(self.fileName.text(), 'w', encoding='utf-8')
        except:
            return "Failure opening "+self.fileName.text()
        header=['Номер точки фактической границы', 'Расстояние до кадастровой границы, м',
                'Номер точки кадастровой границы', 
                'Положение фактической точки относительно кадастровой границы']
        csvWriter=csv.writer(csvFile, delimiter=';')
        csvWriter.writerow(header)
        listCompartion=[]
        for key in matchingDict:
            csvWriter.writerow(['Факт - '+ str(matchingDict[key]),'', 'Кадастр - '+str(key),'']) 
            kGeom=self.kadCB.currentLayer().getFeature(key).geometry()
            fGeom=self.factCB.currentLayer().getFeature(matchingDict[key]).geometry()
            kPntsLayer=self.pointKadCB.currentLayer()
            kNameField=self.pointKadNameFieldCB.currentField()
            fPntsLayer=self.pointFactCB.currentLayer()
            fNameField=self.pointFactNameFieldCB.currentField()
            distList=Dist2Kadastr(kGeom,fGeom,kPntsLayer,kNameField,fPntsLayer,fNameField)
            if self.distToSegmentCheckBox.isChecked():
                for item in distList.listDistsWithName2():
                    item[3]=self.loR(item[3]) #change -/+int location to Снаружи/Внутри
                    csvWriter.writerow(item)
            else:
                for item in distList.listDistsP2PWithName2():
                    item[3]=self.loR(item[3]) #change -/+int location to Снаружи/Внутри
                    csvWriter.writerow(item)
                centKad = kGeom.centroid().asPoint()
                centFact = fGeom.centroid().asPoint()
                dist,angle = self.inverseGeoTask(centKad, centFact)
                row = ['центроид', round(dist, 2), 'центроид', f'Дир.угол: {round(angle, 4)}']
                csvWriter.writerow(row)
        csvFile.close()
