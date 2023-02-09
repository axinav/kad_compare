
from qgis.core import *

class PointsNames():
    def __init__(self,polyLayer,pointLayer,pointNameField):
        self.ptsLayer=pointLayer
        self.plnLayer=polyLayer
        self.ptsNameField=pointNameField

    def findPointName(self):
        '''match vertices of features in plnLayer to point in ptsLayer. return dict{featId:[(idVertex,pointName),]}'''
        featDict={}
        for feat in self.plnLayer.getFeatures():
            vIdNameList=[]
            for idp, v in enumerate(feat.verices()):
                pntgeom=QgsGeometry.fromPointXY(v.x(),v.y())
                pntName=''
                for pFeat in self.ptsLayer.getFeatures():
                    if pFeat.geometry().isGeosEqual(pntgeom):
                        pntName=pFeat.attrubute(self.ptsNameField)
                vIdNameList.append((idp,pntName))
            featDict[feat.id()]=vIdNameList
        return featDict
