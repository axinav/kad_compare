from qgis.core import *
import collections

IdDistSid=collections.namedtuple('IdDistSid', ['id', 'dist', 'sid'])
IdDistNvLoR=collections.namedtuple('IdDistNvLoR', ['id', 'dist', 'nVert','LoR'])
class ModGeometry(QgsGeometry):
    def __init__(self, geometry):
        super().__init__(geometry)


    def findClosestPoint(self,sameGeom):
        '''find distance from self vertices to similar geometry vertices. Returned [namedtuple IdDistSid(selfVert(id),(dist),similarVert(sid))].Paramter - similar QgsGeometry'''
        distIdsList=[]
        for i, pnt in enumerate(self.vertices()):
            pntXY=QgsPointXY(pnt.x(),pnt.y())
            dist=sameGeom.closestVertexWithContext(pntXY)
            distIdsList.append(IdDistSid._make([i,dist[0],dist[1]]))
        bubble_sort(distIdsList,'sid')
        return distIdsList

    def findClosestSegment(self,sameGeom):
        '''find distance from self vertices to similar geometry segment. Returned [namedtuple IdDistNvLor(selfVert(id),(dist),similarNextVertofSegment(nVert), leftOrRightOfSegment(LoR))].Paramter - similar QgsGeometry'''
        distIdsList=[]
        for i, pnt in enumerate(self.vertices()):
            pntXY=QgsPointXY(pnt.x(),pnt.y())
            dist=sameGeom.closestSegmentWithContext(pntXY)
            distIdsList.append(IdDistNvLoR._make([i,dist[0],dist[2],dist[3]]))
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



def bubble_sort(nums,field):
    '''sort list of namedtuples, arg: list, fieldname by was sorted'''
    iF=nums[0]._fields.index(field) #index of field
    # Устанавливаем swapped в True, чтобы цикл запустился хотя бы один раз
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(nums) - 1):
            if nums[i][iF] > nums[i + 1][iF]:
        # Меняем элементы
                nums[i], nums[i + 1] = nums[i + 1], nums[i]
    # Устанавливаем swapped в True для следующей итерации
                swapped = True
