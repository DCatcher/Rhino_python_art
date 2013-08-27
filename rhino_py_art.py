#zcx writes it
#2013/8/24
import rhinoscriptsyntax as rs
import Rhino
import math
import Queue

BOOLFORWHATISNOW = 1
BOOLFORSURFACE = 0

strPathExamine = "order.txt"
strPathOut = "result.txt"
fileTmp0 = open(strPathExamine,'w')
fileTmp1 = open(strPathOut,'w')
fileTmp0.close()
fileTmp1.close()
dictPointByNum = {} #all the points,(0,0) is the start point
dictPointByCord = {}
dictPointByCordGetRs = {}
dictPointByRealCord = {}
cvBaseCurve = None
sfBaseSurface = None
if BOOLFORWHATISNOW is 0:
	reRadius = 1500 #the length of the equal side
	reBase = 1000 #the length of the bottom side
	reDist = 700
	intInterval = 20
	intHashSize = 500
else:
	reRadius = 5 #the length of the equal side
	reBase = 5 #the length of the bottom side
	reDist = 0.5
	intInterval = 5
	intHashSize = 0.8
intMaxX = 0
intTestNum =5
intMaxY = 0
intPointNum = 0
ltObjectPoint = []

def GetHash(ptcordPoint):
	return (int(ptcordPoint[0]/intHashSize),int(ptcordPoint[1]/intHashSize),int(ptcordPoint[2]/intHashSize))

def InOrOut(ptcordTmpPointInter, ltTmpPointCord, intMaxDist=0): #to judge whether I have added this point
	global dictPointByRealCord
	ltDeltaX = range(-intTestNum,intTestNum+1)
	ltDeltaY = range(-intTestNum,intTestNum+1)
	ltDeltaZ = range(-intTestNum,intTestNum+1)
	ltHashCode = GetHash(ptcordTmpPointInter)
	for intDeltaX in ltDeltaX:
		for intDeltaY in ltDeltaY:
			for intDeltaZ in ltDeltaZ:
				ltTmpPointCordNear = (ltHashCode[0]+intDeltaX, ltHashCode[1]+intDeltaY, ltHashCode[2]+intDeltaZ)
				if ltTmpPointCordNear not in dictPointByRealCord:
					continue
				ptcordPointTmpInOrOut = dictPointByRealCord[ltTmpPointCordNear]
				reDistForCompare = rs.Distance(ptcordPointTmpInOrOut,ptcordTmpPointInter)
				if reDistForCompare < reDist+intMaxDist*reBase:
					return 1
	return 0

def AddPoint(ptcordTmpPointInter, ptcordTmpPoint, ptcordThirdPoint, ltTmpCordNum, intWhich): #to add the point into the dict
	global intMaxX
	global intMaxY
	global sfBaseSurface
	global intPointNum
	global dictPointByRealCord
	ptTmpPoint = rs.AddPoint(ptcordTmpPointInter)
	ltObjectPoint.append(ptTmpPoint)
	if not rs.IsPointOnSurface(sfBaseSurface,ptTmpPoint):
		rs.DeleteObject(ptTmpPoint)
		return
	ltTmpCordNumInter = [ltTmpCordNum[0],ltTmpCordNum[1]]
	if intWhich<2:
		if ptcordTmpPointInter[intWhich]<ptcordTmpPoint[intWhich]:
			ltTmpCordNumInter[intWhich] -= 1
			if intWhich==1:
				ltTmpCordNumInter[0] += 1
		else:
			ltTmpCordNumInter[intWhich] += 1
	elif intWhich==2:
		ltTmpCordNumInter[0]-=1
	elif intWhich==3:
		ltTmpCordNumInter[0]+=1

	if ltTmpCordNumInter[1]>intMaxY:
		intMaxY = ltTmpCordNumInter[1]
	if -ltTmpCordNumInter[1]>intMaxY:
		intMaxY = -ltTmpCordNumInter[1]
	if ltTmpCordNumInter[0]>intMaxX:
		intMaxX = ltTmpCordNumInter[0]
	if -ltTmpCordNumInter[0]>intMaxX:
		intMaxX = -ltTmpCordNumInter[0]
	if ((ltTmpCordNumInter[0] % intInterval == 0)):
		rs.AddTextDot(str(ltTmpCordNumInter[0])+","+str(ltTmpCordNumInter[1]),ptcordTmpPointInter)
#	rs.AddTextDot(str(ltTmpCordNumInter[0])+","+str(ltTmpCordNumInter[1]),ptcordTmpPointInter)
	dictPointByCord[ptcordTmpPointInter] = ltTmpCordNumInter
	dictPointByCordGetRs[ptcordTmpPointInter] = ptTmpPoint
	dictPointByNum[tuple(ltTmpCordNumInter)] = ptcordTmpPointInter
	dictPointByRealCord[GetHash(ptcordTmpPointInter)] = ptcordTmpPointInter
	if (ptcordThirdPoint is not None) and (BOOLFORSURFACE==1):
		rs.AddSrfPt([ptTmpPoint,dictPointByCordGetRs[ptcordTmpPoint],dictPointByCordGetRs[ptcordThirdPoint]])
	intPointNum += 1
	if intPointNum%20==0:
		fileTmp0 = open(strPathExamine,'r')
		strOrder = fileTmp0.readline()
		fileTmp0.close()
		if strOrder=='exit':
			exit()
		fileTmp0 = open(strPathOut,'a')
		fileTmp0.write(str(intPointNum)+'\n')
		fileTmp0.close()
	

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
	global dictPointByRealCord
	global cvBaseCurve
	global sfBaseSurface
	global reRadius
	global reBase
	global reDist
	global ltObjectPoint
	ptStartPoint = rs.GetObject("Select the point to start", rs.filter.point)
	cvBaseCurve = rs.GetObject("Select the baseline", rs.filter.curve)
	sfBaseSurface = rs.GetObject("Select the base surface", rs.filter.surface)
	if sfBaseSurface is None:
		print "what the fuck"
		return -1
	ptcordStartPoint = rs.PointCoordinates(ptStartPoint)
	rs.AddTextDot("0,0",ptcordStartPoint)
	quePoint = Queue.Queue(maxsize=0)
	quePoint.put(ptcordStartPoint)
	dictPointByNum[(0,0)] = ptcordStartPoint
	dictPointByCord[ptcordStartPoint] = (0,0)
	dictPointByCordGetRs[ptcordStartPoint] = ptStartPoint
	dictPointByRealCord[GetHash(ptcordStartPoint)] = ptcordStartPoint

	print ptcordStartPoint
	print ptcordStartPoint[0]
	print ptcordStartPoint[1]
	print ptcordStartPoint[2]
	print GetHash(ptcordStartPoint)

	while quePoint.qsize()>0:
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
				boolInOrNot = InOrOut(ptcordTmpPointInter, ltTmpCordNum)
				if boolInOrNot == 0:
					quePoint.put(ptcordTmpPointInter)
					AddPoint(ptcordTmpPointInter, ptcordTmpPoint, None, ltTmpCordNum, 0)
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
	global dictPointByRealCord
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
	ltNeAndPoHigh = (-1,1)

	while quePoint.qsize()>0:
		ptcordTmpPoint = quePoint.get() #this is the point we concern now, we also need the points near it
		if ptcordTmpPoint not in dictPointByCord:
			continue
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
				continue
			ltTmpIntersection = rs.CurveSurfaceIntersection( cvInterCircle, sfBaseSurface) #get new points
			if ltTmpIntersection is None:
				continue
			for ltIntersectionPoint in ltTmpIntersection: #Add the points
				if ltIntersectionPoint[0]==1:
					ptcordTmpPointInter = ltIntersectionPoint[1]
					boolInOrNot = InOrOut(ptcordTmpPointInter, ltTmpPointNearNum)
					if boolInOrNot == 0:
						if intNeOrPo<0:
							AddPoint(ptcordTmpPointInter, ptcordTmpPoint,ptcordTmpPointNear, ltTmpPointNearNum, 1)
						else:
							AddPoint(ptcordTmpPointInter, ptcordTmpPoint,ptcordTmpPointNear, ltTmpPointNum, 1)
				else:
					print "Impossible"
					continue
			rs.DeleteObject(cvInterCircle)

		for intNeOrPoHigh in ltNeAndPoHigh:
			if (ltTmpPointNum[0]+intNeOrPoHigh,ltTmpPointNum[1]) not in dictPointByNum:
				for intNeOrPo in ltNeAndPo:
					if intNeOrPoHigh==1:
						ltTmpPointNearNum = (ltTmpPointNum[0]-intNeOrPoHigh,ltTmpPointNum[1]+intNeOrPo)
					else:
						ltTmpPointNearNum = (ltTmpPointNum[0],ltTmpPointNum[1]+intNeOrPo)

					if ltTmpPointNearNum not in dictPointByNum:
						continue
					ptcordTmpPointNear = dictPointByNum[ltTmpPointNearNum] #get the cord of the near point

					planeXYPlane = rs.WorldXYPlane()
					planeTmpPlane0 = rs.MovePlane(planeXYPlane, ptcordTmpPoint)
					planeTmpPlane1 = rs.MovePlane(planeXYPlane, ptcordTmpPointNear)
					ltInterResults = rs.IntersectSpheres(planeTmpPlane0, reRadius, planeTmpPlane1, reRadius)

					if ltInterResults:
						cvInterCircle = rs.AddCircle(ltInterResults[1], ltInterResults[2])
					else:
						continue
					ltTmpIntersection = rs.CurveSurfaceIntersection( cvInterCircle, sfBaseSurface) #get new points
					rs.DeleteObject(cvInterCircle)
					if ltTmpIntersection is None:
						continue
					for ltIntersectionPoint in ltTmpIntersection: #Add the points
						if ltIntersectionPoint[0]==1:
							ptcordTmpPointInter = ltIntersectionPoint[1]
							boolInOrNot = InOrOut(ptcordTmpPointInter,ltTmpPointNearNum, 0.6)
							if boolInOrNot == 0:
								if intNeOrPoHigh<0:
									AddPoint(ptcordTmpPointInter, ptcordTmpPoint,ptcordTmpPointNear, ltTmpPointNearNum, 2)
								else:
									AddPoint(ptcordTmpPointInter, ptcordTmpPoint,ptcordTmpPointNear, ltTmpPointNearNum, 3)

								planeXYPlane = rs.WorldXYPlane()
								planeTmpPlane0 = rs.MovePlane(planeXYPlane, ptcordTmpPoint)
								planeTmpPlane1 = rs.MovePlane(planeXYPlane, ptcordTmpPointInter)
								ltInterResults = rs.IntersectSpheres(planeTmpPlane0, reRadius, planeTmpPlane1, reRadius)

								if ltInterResults:
									cvInterCircle = rs.AddCircle(ltInterResults[1], ltInterResults[2])
								else:
									continue
								ltTmpIntersection = rs.CurveSurfaceIntersection( cvInterCircle, sfBaseSurface) #get new points
								rs.DeleteObject(cvInterCircle)
								if ltTmpIntersection is None:
									continue
								for ltIntersectionPoint in ltTmpIntersection: #Add the points
									if ltIntersectionPoint[0]==1:
										ptcordTmpPointInter = ltIntersectionPoint[1]
										boolInOrNot = InOrOut(ptcordTmpPointInter, ltTmpPointNum, 0.6)
										if boolInOrNot == 0:
											if intNeOrPoHigh<0:
												AddPoint(ptcordTmpPointInter, ptcordTmpPoint,ptcordTmpPointInter, ltTmpPointNum, 2)
											else:
												AddPoint(ptcordTmpPointInter, ptcordTmpPoint,ptcordTmpPointInter, ltTmpPointNum, 3)
											quePoint.put(ptcordTmpPointInter)
									else:
										print "Impossible"
										continue
						else:
							print "Impossible"
							continue

	return 0

def main():
	intInitReturn = init()
	if intInitReturn is not 0:
		return
	intNowY = 0
	while 1:
		if intNowY ==0:
			intExpandReturn = expand(0)
		else:
			intEx = 0
			intExpandReturn = expand(intNowY)
			if intExpandReturn is not 1:
				intEx = 1	
			intExpandReturn = expand(-intNowY)
			if intExpandReturn is not 1:
				intEx = 1	
			if intEx == 0:
				break
		intNowY += 1

#	intFinishReturn = finish()

if __name__ == "__main__":
	main()    
