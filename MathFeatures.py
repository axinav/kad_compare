
from qgis.core import *

class MatchFeatures():
    '''Match features of layer to closest feature of another layer'''
    def __init__(self, kadLayer, factLayer):
        self.kadL=kadLayer
        self.factL=factLayer
        self.kadFeatNum=self.kadL.featureCount()
        self.factFeatNum=self.factL.featureCount()
        self.onlyOne=self.testOnlyOne()

    def testOnlyOne(self):
        if self.kadFeatNum==1 and self.factFeatNum==1:
            return True
        else:
            return False

    def matchingByDist(self):
        matchDict={} #{kFeat.id:closest fFeat.id}
        for kFeat in self.kadL.getFeatures():
            distDict={}
            for fFeat in self.factL.getFeatures():
                distDict[fFeat.id()]=fFeat.geometry().distance(kFeat.geometry())
            matchDict[kFeat.id()]=list(distDict)[list(distDict.values()).index(min(distDict.values()))]
        return matchDict
