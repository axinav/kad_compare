from qgis.core import QgsPointXY

class QgsPointXYName(QgsPointXY):
    def __init__(self ):
        super().__init__()
        self.name=None

    def setFromFeat(self,feat, nameField):
        self.set(feat.geometry().asPoint().x(), feat.geometry().asPoint().y())     
        self.name=feat.attrubute(nameField)
