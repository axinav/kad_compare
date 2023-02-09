from qgis.core import *
import collections

IdDistSid=collections.namedtuple('IdDistSid', ['id', 'dist', 'sid', 'LoR'])
IdDistNvLoR=collections.namedtuple('IdDistNvLoR', ['id', 'dist', 'nVert','LoR'])
class IdsDistStorage:
    def __init__(self, id, dist, sid=-1, lor=0, isSegment=False):
        self.id=id
        self.dist=dist
        self.sid=sid
        self.LoR=lor
        self.isSegment=isSegment

    def __eq__(self,other):
        return self.sid==other.sid
    def __lt__(self, other):
        return self.sid<other.sid
    def __gt__(self,other):
        return self.sid>other.sid
    def __repr__(self):
        return f'({self.id}, {self.dist}, {self.sid}, {self.LoR}, {self.isSegment})'
def prepereGeom(geom):
    '''create new ModGeometryWithNames where first vertex is north-westest'''
    bBox = geom.boundingBox()

    bBoxNWVert = QgsPointXY(bBox.xMinimum(), bBox.yMaximum())
    _,id0 = geom.closestVertexWithContext(bBoxNWVert)
    idList = list(range(id0, geom.constGet().nCoordinates()))
    lastIdList = list(range(1,id0+1))
    idList.extend(lastIdList)
    pnts = []
    for id in idList:
        pnt = QgsPointXY(geom.vertexAt(id).x(), geom.vertexAt(id).y())
        pnts.append(pnt)
    geomNWStart = QgsGeometry().fromPolygonXY([pnts])
    return geomNWStart
class ModGeometryWithNames(QgsGeometry):
    def __init__(self, geometry,pointLayer,nameField):
        super().__init__(prepereGeom(geometry))
        self.names=self.matchNames(pointLayer,nameField)
        self.pointLayer = pointLayer
        self.nameField = nameField

    def matchNames(self,pLayer,nField):
        nameDict={}
        for vNumb,pnt in enumerate(self.vertices()):
            gXY=QgsGeometry().fromPointXY(QgsPointXY(pnt.x(),pnt.y()))
            for pFeat in pLayer.getFeatures():
                if gXY.equals(pFeat.geometry()):
                    nameDict[vNumb]=pFeat.attribute(nField)
        return nameDict

    def findSameVertices(self, poly2):
        '''find similar vertices in self.Geometry and poly2.Geometry
        return dict key=vertex num of self, value=vertex number of poly2
        dict contains only similar vertex '''
        kad = poly2
        fact = QgsGeometry(self)
        #rFact = self.northWestStartVert(fact) #уже переопределено
        #rKad = self.northWestStartVert(kad)
        kadCentroid = kad.centroid().asPoint()
        factCentroid = fact.centroid().asPoint()
        deltaX = kadCentroid.x() - factCentroid.x()
        deltaY = kadCentroid.y() - factCentroid.y()
        fact.translate(deltaX, deltaY)  #combine fact with kad by centroids

        dictIdPnts = {}
        for idF, pF in enumerate(fact.vertices()):
            pFXY = QgsPointXY(pF.x(), pF.y())
            pKXY,iK,_,_,dK = kad.closestVertex(pFXY)
            dF,iF = fact.closestVertexWithContext(pKXY)
            if dF==dK:
                dictIdPnts[idF] = iK
            else:
                dictIdPnts[iF] = iK
        return dictIdPnts

    def distToSameGeomList(self, sameGeom):
        '''создать лист расстояний точка-точка с использованием findSameVertices'''
        dictId = self.findSameVertices(sameGeom)
        fIdList = dictId.keys()
        distIdsList =[]
        for key  in dictId:
            val = dictId[key]
            fPnt = self.vertexAt(key)
            kPnt = sameGeom.vertexAt(val)
            line = QgsLineString(kPnt,fPnt)
            
            dist = line.length()**2
            fPntXY = QgsPointXY(fPnt.x(), fPnt.y())
            #dist,sId = sameGeom.closestVertexWithContext(fPntXY)
            isInner=0
            if sameGeom.contains(fPntXY):
                isInner=1
            else:
                isInner=-1
            distIdsList.append(IdsDistStorage(key,dist,val,isInner))
        for i, fPnt in enumerate(self.vertices()):
            if i not in fIdList:
                fPntXY = QgsPointXY(fPnt.x(), fPnt.y())
                dist,p,sId,lor = sameGeom.closestSegmentWithContext(fPntXY)
                distIdsList.append(IdsDistStorage(i,dist,sId,lor, True))
                


        distIdsList.sort(key=lambda item: item.id)
        return distIdsList

    def distFromSameGeomList(self, sameGeom):
        dictId = self.findSameVertices(sameGeom)
        kIdList = dictId.values()
        distIdsList =[]
        for i, kPnt in enumerate(sameGeom.vertices()):
            if i not in kIdList:
                kPntXY = QgsPointXY(kPnt.x(), kPnt.y())
                dist,p,sId,lor = self.closestSegmentWithContext(kPntXY)
                lor = -1 * lor
                distIdsList.append(IdsDistStorage(sId,dist,i,lor, True))
        distIdsList.sort(key=lambda item: item.id)
        return distIdsList

    def findClosestPoint(self,sameGeom):
        '''find distance from self vertices to similar geometry vertices. Returned [IdsDistStorage ].Paramter - similar QgsGeometry'''
        distIdsList=[]
        for i, pnt in enumerate(self.vertices()):
            pntXY=QgsPointXY(pnt.x(),pnt.y())
            dist=sameGeom.closestVertexWithContext(pntXY)
            isInner=0
            if sameGeom.contains(pntXY):
                isInner=1
            else:
                isInner=-1
            distIdsList.append(IdsDistStorage(i,dist[0],dist[1],isInner))
        distIdsList.sort(key=lambda item: item.sid)
        return distIdsList

    def findClosestSegment(self,sameGeom):
        '''find distance from self vertices to similar geometry segment. Returned [namedtuple IdDistNvLor(selfVert(id),(dist),similarNextVertofSegment(nVert), leftOrRightOfSegment(LoR))].Paramter - similar QgsGeometry'''
        distIdsList=[]
        for i, pnt in enumerate(self.vertices()):
            pntXY=QgsPointXY(pnt.x(),pnt.y())
            dist=sameGeom.closestSegmentWithContext(pntXY)
            distIdsList.append(IdsDistStorage(i,dist[0],dist[2],dist[3],True))
        return distIdsList

    def reduceIdList(self, idList):
        newList=[]
        i=0
        while i<len(idList):
            tempList=[]
            item=idList[i]
            tempList.append(item)
            #search same sid
            for it in range(i+1,len(idList)):
                if item.sid==idList[it].sid:
                    tempList.append(idList[it])
            #print(tempList)
            #search min dist in found
            minI=item
            for it in tempList:
                if it.dist<minI.dist:
                    minI=it
            newList.append(minI)
            i=i+len(tempList)
        return newList
    def dists2Vertexs(self,sGeom):

        allList=self.findClosestPoint(sGeom)
        idList=self.reduceIdList(allList)
        return idList
    
    def makeBorderSimilar(self,sGeom):
        allList=self.findClosestPoint(sGeom)
        idList=self.reduceIdList(allList)
        #print(allList)
        #print(idList)
        newGeom=QgsGeometry()
        pntList=[]
        for id in idList:
            pnt=self.vertexAt(id.id)
            pntXY=QgsPointXY(pnt.x(),pnt.y())
            pntList.append(pntXY)
        #poly=QgsPolygonXY(QgsLineString(pntList))
        return newGeom.fromPolygonXY([pntList])

    def northWestStartVert(self):
        '''create new ModGeometryWithNames where first vertex is north-westest'''
        bBox = self.boundingBox()

        bBoxNWVert = QgsPointXY(bBox.xMinimum(), bBox.yMaximum())
        _,id0 = self.closestVertexWithContext(bBoxNWVert)
        idList = list(range(id0, self.constGet().nCoordinates()))
        lastIdList = list(range(1,id0+1))
        idList.extend(lastIdList)
        pnts = []
        for id in idList:
            pnt = QgsPointXY(self.vertexAt(id).x(), self.vertexAt(id).y())
            pnts.append(pnt)
        geomNWStart = QgsGeometry().fromPolygonXY([pnts])
        return geomNWStart
    def northWestStartVertWithNames(self):
        '''create new ModGeometryWithNames where first vertex is north-westest'''
        bBox = self.boundingBox()

        bBoxNWVert = QgsPointXY(bBox.xMinimum(), bBox.yMaximum())
        _,id0 = self.closestVertexWithContext(bBoxNWVert)
        idList = list(range(id0, self.constGet().nCoordinates()))
        lastIdList = list(range(1,id0+1))
        idList.extend(lastIdList)
        pnts = []
        for id in idList:
            pnt = QgsPointXY(self.vertexAt(id).x(), self.vertexAt(id).y())
            pnts.append(pnt)
        geomNWStart = QgsGeometry().fromPolygonXY([pnts])
        return ModGeometryWithNames(geomNWStart, self.pointLayer, self.nameField)

    def simplifyGeom(self, tolerance = 0.5):
        '''simplify polygon: delete second vertex if 3 vertices lay on line
        return QgsGeometry'''
        def simpLine(p0, p1, p2, tolerance):
            lineGeom = QgsGeometry().fromPolyline([p0,p2])
            pGeom = QgsGeometry().fromPointXY(QgsPointXY(p1.x(),p1.y()))
            dist = lineGeom.distance(pGeom)
            if dist < tolerance:
                return True
            else:
                return False
        
        polygon = QgsGeometry(self)
        isNext = True
        id0 = 0
        while isNext:
            aGeom = polygon.constGet()
            id1 = id0 + 1
            id2 = id0 + 2
            if id2 < aGeom.nCoordinates():
                p0 = polygon.vertexAt(id0)
                p1 = polygon.vertexAt(id1)
                p2 = polygon.vertexAt(id2)
                isSimp = simpLine(p0, p1, p2, tolerance)
                if isSimp:
                    polygon.deleteVertex(id1)
                else:
                    id0 =id0 + 1
            else:
                isNext = False
        return polygon

    def simplifyGeomWithName(self, tolerance = 0.5):
        '''simplify polygon: delete second vertex if 3 vertices lay on line
        return ModGeometryWithNames'''
        def simpLine(p0, p1, p2, tolerance):
            lineGeom = QgsGeometry().fromPolyline([p0,p2])
            pGeom = QgsGeometry().fromPointXY(QgsPointXY(p1.x(),p1.y()))
            dist = lineGeom.distance(pGeom)
            if dist < tolerance:
                return True
            else:
                return False
        
        polygon = QgsGeometry(self)
        isNext = True
        id0 = 0
        while isNext:
            aGeom = polygon.constGet()
            id1 = id0 + 1
            id2 = id0 + 2
            if id2 < aGeom.nCoordinates():
                p0 = polygon.vertexAt(id0)
                p1 = polygon.vertexAt(id1)
                p2 = polygon.vertexAt(id2)
                isSimp = simpLine(p0, p1, p2, tolerance)
                if isSimp:
                    polygon.deleteVertex(id1)
                else:
                    id0 =id0 + 1
            else:
                isNext = False
        polygonWName = ModGeometryWithNames(polygon, self.pointLayer, self.nameField)
        return polygonWName
#def bubble_sort(nums):
#    '''sort list of IdsDistStorage objects, arg: list'''
#    # Устанавливаем swapped в True, чтобы цикл запустился хотя бы один раз
#    swapped = True
#    while swapped:
#        swapped = False
#        for i in range(len(nums) - 1):
#            if nums[i] > nums[i + 1]:
#        # Меняем элементы
#                nums[i], nums[i + 1] = nums[i + 1], nums[i]
#    # Устанавливаем swapped в True для следующей итерации
#                swapped = True
