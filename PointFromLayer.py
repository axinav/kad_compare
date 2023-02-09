from qgis.core import *
from .PointsNames import *

class PointFromLayer():
    def __init__(self, layer, fieldName):
        self.layer=layer
        self.field=fieldName
        self.point=None

    def setPoint(self, self.layer,self.field):

