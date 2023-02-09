from qgis.core import *
from .ModGeometryWithNames import *

class Dist2Kadastr():
    '''class make the table: name of fact vertix, dist to cad vert or segment,
    name of kad vert or segment, int negative - outside, positive -inside'''
    def __init__(self,kadGeom,factGeom,kpointLayer,knameField,fpointLayer,fnameField):
        self.kad=ModGeometryWithNames(kadGeom, kpointLayer, knameField)
        self.fact=ModGeometryWithNames(factGeom, fpointLayer,fnameField)
        self.dists2KadVerts=self.fact.dists2Vertexs(self.kad) #list of IdsDistStorage
        self.dists2KadSegments=self.fact.findClosestSegment(self.kad) #list of IdsDistStorage
        self.distToKad = self.fact.distToSameGeomList(self.kad)
        self.distFromKad = self.fact.distFromSameGeomList(self.kad)

    def findId(self,idS):
        '''func find index of line in self.dists2KadVerts by IdsDistStorage.id'''
        listIdV=[]
        for t in self.dists2KadVerts:
            listIdV.append(t.id)
        try:
            id=listIdV.index(idS)
        except ValueError:
            id=-1
        return id

    def listDists(self):
        '''func merges self.dists2KadSegments with self.dists2KadVerts
        line of self.dists2KadVerts inserts after line self.dists2KadSegments with same IdsDistStorage.id'''
        lD=[]
        for s in self.dists2KadSegments:
            lD.append(s)
            idV=self.findId(s.id)
            if idV>=0:
                lD.append(self.dists2KadVerts[idV])
        lD.sort(key=lambda item: item.id)
        return lD

    def areAllKadPnts(self):
        ''' Are there missing kad points'''
        return self.kad.constGet().nCoordinates()> self.fact.constGet().nCoordinates() 

    def findMissingKadPnts(self):
        ''' find missing kad points by its vertex number
        return set(vertex nuber)'''
        kadVertNumb=list(range(self.kad.constGet().nCoordinates()))
        usingKadVertNumb=[a.sid for a in self.dists2KadVerts]
        missingKadVert=set(kadVertNumb).difference(set(usingKadVertNumb))
        return missingKadVert
    def missingDistsWithName(self):
        '''create [factSegment, dist, kad name point, leftOrRight location]'''
        missingDists=[]
        for numb in self.findMissingKadPnts():
            pnt=self.kad.vertexAt(numb)
            pntXY=QgsPointXY(pnt.x(),pnt.y())
            dist=self.fact.closestSegmentWithContext(pntXY)
            f=str(self.fact.names[dist[2]])+'-'+str(self.fact.names[self.getPrevVert(self.fact,dist[2])])
            missingDists.append([f,round(dist[0]**0.5,2), self.kad.names[numb],-1*dist[3]])
        return missingDists
        

    def getPrevVert(self,geom, vertNumb):
        return geom.adjacentVertices(vertNumb)[0]
    def listDistsWithName(self):
        
        '''create [fact name point, dist, kad name point or segment, leftOrRight location]'''
        listDists=self.listDists()
        listDistsWName=[]
        for item in listDists:
            if item.isSegment:
                prev=self.getPrevVert(self.kad,item.sid)
                listDistsWName.append([self.fact.names[item.id], round(item.dist**0.5,2), str(self.kad.names[prev])+'-'+str(self.kad.names[item.sid]), item.LoR])
            else:
                listDistsWName.append([self.fact.names[item.id],round(item.dist**0.5,2),str(self.kad.names[item.sid]), item.LoR])
        if self.areAllKadPnts():
            listDistsWName=listDistsWName+self.missingDistsWithName()
        return listDistsWName

    def listDistsWithName2(self):
        listDistsWName = []
        for item in self.distToKad:
            if item.isSegment:
                prev=self.getPrevVert(self.kad,item.sid)
                listDistsWName.append([self.fact.names[item.id], round(item.dist**0.5,2), str(self.kad.names[prev])+'-'+str(self.kad.names[item.sid]), item.LoR])
            else:
                listDistsWName.append([self.fact.names[item.id],round(item.dist**0.5,2),str(self.kad.names[item.sid]), item.LoR])
        for item in self.distFromKad:
            if item.isSegment:
                prev=self.getPrevVert(self.fact,item.id)
                listDistsWName.append([str(self.fact.names[prev])+'-'+str(self.fact.names[item.id]), round(item.dist**0.5,2), self.kad.names[item.sid], item.LoR])
        return listDistsWName

    def listDistsP2PWithName2(self):
        listDistsWName = []
        for item in self.distToKad:
            if not item.isSegment:
                listDistsWName.append([self.fact.names[item.id],round(item.dist**0.5,2),str(self.kad.names[item.sid]), item.LoR])
        return listDistsWName
