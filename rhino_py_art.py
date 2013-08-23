import rhinoscriptsyntax as rs
import Rhino
import math
import Queue

dictPointByNum = {} #all the points,(0,0) is the start point
dictPointByCord = {}
cvBaseCurve = None
sfBaseSurface = None
reRadius = 5 #the length of the equal side
reBase = 5 #the length of the bottom side
reDist = 0.05
intMaxX = 0
ltObjectPoint = []

def InOrOut(ptcordTmpPointInter): #to judge whether I have added this point
	for ptcordPointTmpInOrOut in dictPointByCord:
		reDistForCompare = rs.Distance(ptcordPointTmpInOrOut,ptcordTmpPointInter)
		if reDistForCompare < reDist:
			return 1
	return 0

def AddPoint(ptcordTmpPointInter, ptcordTmpPoint, ltTmpCordNum, intWhich): #to add the point into the dict
	global intMaxX
	ltTmpCordNumInter = [ltTmpCordNum[0],ltTmpCordNum[1]]
	if ptcordTmpPointInter[intWhich]<ptcordTmpPoint[intWhich]:
		ltTmpCordNumInter[intWhich] -= 1
		if intWhich==1:
			ltTmpCordNumInter[0] += 1
	else:
		ltTmpCordNumInter[intWhich] += 1
	if ltTmpCordNumInter[0]>intMaxX:
		intMaxX = ltTmpCordNumInter[0]
	if ((ltTmpCordNumInter[0] % 5 == 0)):
		rs.AddTextDot(str(ltTmpCordNumInter[0])+","+str(ltTmpCordNumInter[1]),ptcordTmpPointInter)
	dictPointByCord[ptcordTmpPointInter] = ltTmpCordNumInter
	dictPointByNum[tuple(ltTmpCordNumInter)] = ptcordTmpPointInter
	ptTmpPoint = rs.AddPoint(ptcordTmpPointInter)
	ltObjectPoint.append(ptTmpPoint)


def continue_or_not():
	items = ("Continue", "False", "True")
	results = rs.GetBoolean("Continue options", items, (True))

	if results:
		return results[0]
	else:
		return 1

def init():
	global dictPointByNum #all the global vars
	global dictPointByCord
	global cvBaseCurve
	global sfBaseSurface
	global reRadius
	global reBase
	global reDist
	global ltObjectPoint
	ptStartPoint = rs.GetObject("Select the point to start", rs.filter.point)
	ptcordStartPoint = rs.PointCoordinates(ptStartPoint)
	rs.AddTextDot("0,0",ptcordStartPoint)
	quePoint = Queue.Queue(maxsize=0)
	quePoint.put(ptcordStartPoint)
	dictPointByNum[(0,0)] = ptcordStartPoint
	dictPointByCord[ptcordStartPoint] = (0,0)
	cvBaseCurve = rs.GetObject("Select the baseline", rs.filter.curve)
	sfBaseSurface = rs.GetObject("Select the base surface", rs.filter.surface)
	if sfBaseSurface is None:
		print "what the fuck"
		return -1
	while quePoint.qsize()>0:
		print quePoint.qsize()#debug output
		'''

		intContinueResult = continue_or_not()

		if intContinueResult is False:
			return -1
		rs.GetObject("Surface",rs.filter.surface)
		'''
		
		ptcordTmpPoint = quePoint.get()
		spTmpSphere = rs.AddSphere(ptcordTmpPoint,reBase)
		ltTmpIntersection = rs.CurveSurfaceIntersection(cvBaseCurve,spTmpSphere)
		if ltTmpIntersection is None:
			print "the start point should be on the baseline"
			return -1
		ltTmpCordNum = dictPointByCord[ptcordTmpPoint]
		for ltIntersectionPoint in ltTmpIntersection:
			if ltIntersectionPoint[0]==1:
				ptcordTmpPointInter = ltIntersectionPoint[1]
				boolInOrNot = InOrOut(ptcordTmpPointInter)
				if boolInOrNot == 0:
					quePoint.put(ptcordTmpPointInter)
					AddPoint(ptcordTmpPointInter, ptcordTmpPoint, ltTmpCordNum, 0)
			else:
				print "Impossible"
				return -1
		rs.DeleteObject(spTmpSphere)

	return 0

def finish():
	items = ("Points", "Reserve", "Delete")
	results = rs.GetBoolean("Delete options", items, (True))
	if results[0]:
		for object in ltObjectPoint:
			rs.DeleteObject(object)
	return 0

def expand(intStartY): #this function expands the points in the Y direction
	global dictPointByNum #all the global vars
	global dictPointByCord
	global cvBaseCurve
	global sfBaseSurface
	global reRadius
	global reBase
	global reDist
	global ltObjectPoint
	global intMaxX
	quePoint = Queue.Queue(maxsize=0) #get point from the queue until it is empty
	boolExPoint = 0
	for intX in range(intMaxX+1):
		ltStartXY = (intX,intStartY) #this is the point we start
		if ltStartXY in dictPointByNum:
			quePoint.put(dictPointByNum[ltStartXY])
			boolExPoint = 1
		if intX==0:
			continue
		ltStartXY = (-intX,intStartY)
		if ltStartXY in dictPointByNum:
			quePoint.put(dictPointByNum[ltStartXY])
			boolExPoint = 1

	if boolExPoint==0:
		return 1
	ltNeAndPo = (-1,1)

	while quePoint.qsize()>0:
		ptcordTmpPoint = quePoint.get() #this is the point we concern now, we also need the points near it
		ltTmpPointNum = dictPointByCord[ptcordTmpPoint]

		for intNeOrPo in ltNeAndPo:
			ltTmpPointNearNum = (ltTmpPointNum[0]+intNeOrPo,ltTmpPointNum[1])
			if ltTmpPointNearNum not in dictPointByNum:
				continue
			ptcordTmpPointNear = dictPointByNum[ltTmpPointNearNum] #get the cord of the near point

			planeXYPlane = rs.WorldXYPlane()
			planeTmpPlane0 = rs.MovePlane(planeXYPlane, ptcordTmpPoint)
			planeTmpPlane1 = rs.MovePlane(planeXYPlane, ptcordTmpPointNear)
			ltInterResults = rs.IntersectSpheres(planeTmpPlane0, reRadius, planeTmpPlane1, reRadius)
				#get the intersection results of two spheres
			if ltInterResults:
				cvInterCircle = rs.AddCircle(ltInterResults[1], ltInterResults[2])
			else:
				return
			ltTmpIntersection = rs.CurveSurfaceIntersection( cvInterCircle, sfBaseSurface) #get new points
			if ltTmpIntersection is None:
				continue
			for ltIntersectionPoint in ltTmpIntersection: #Add the points
				if ltIntersectionPoint[0]==1:
					ptcordTmpPointInter = ltIntersectionPoint[1]
					boolInOrNot = InOrOut(ptcordTmpPointInter)
					if boolInOrNot == 0:
						if intNeOrPo<0:
							AddPoint(ptcordTmpPointInter, ptcordTmpPoint, ltTmpPointNearNum, 1)
						else:
							AddPoint(ptcordTmpPointInter, ptcordTmpPoint, ltTmpPointNum, 1)
				else:
					print "Impossible"
					return -1
			rs.DeleteObject(cvInterCircle)
		'''
		for intNeOrPoHigh in ltNeAndPo:
			if (ltTmpPointNum[0]+intNeOrPoHigh,ltTmpPointNum[1]) not in dictPointByNum:
				for intNeOrPo in ltNeAndPo:
					if intNeOrPoHigh==1:
						ltTmpPointNearNum = (ltTmpPointNum[0]-intNeOrPoHigh,ltTmpPointNum[1]+intNeOrPo)
					else:
						ltTmpPointNearNum = (ltTmpPointNum[0],ltTmpPointNum[1]+intNeOrPo)

					if ltTmpPointNearNum not in dictPointByNum:
						continue
					ptcordTmpPointNear = dictPointByNum[ltTmpPointNearNum] #get the cord of the near point
					ptcordTmpPointDist = dictPointByNum[(ltTmpPointNum[0]-intNeOrPoHigh,ltTmpPointNum[1])]
					reDistanceTmp = rs.Distance(ptcordTmpPointDist,ptcordTmpPoint)

					planeXYPlane = rs.WorldXYPlane()
					planeTmpPlane0 = rs.MovePlane(planeXYPlane, ptcordTmpPoint)
					planeTmpPlane1 = rs.MovePlane(planeXYPlane, ptcordTmpPointNear)
					ltInterResults = rs.IntersectSpheres(planeTmpPlane0, reDistanceTmp, planeTmpPlane1, reRadius)
		'''

	return 0


def main():
	intInitReturn = init()
	if intInitReturn is not 0:
		return
	intNowY = 0
	while 1:
		if intNowY ==0:
			intExpandReturn = expand(0)
			if intExpandReturn is not 0:
				return
		else:
			intEx = 0
			intExpandReturn = expand(intNowY)
			if intExpandReturn is not 0:
				return
			if intExpandReturn is not 1:
				intEx = 1	
			intExpandReturn = expand(-intNowY)
			if intExpandReturn is not 0:
				return
			if intExpandReturn is not 1:
				intEx = 1	
			if intEx == 0:
				break
		intNowY += 1

#	intFinishReturn = finish()

if __name__ == "__main__":
	main()    
