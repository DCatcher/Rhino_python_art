import rhinoscriptsyntax as rs
import Rhino
import math
import Queue

dictPointByNum = {} #all the points,(0,0) is the start point
dictPointByCord = {}
cvBaseCurve = None
reRadius = 5
reBase = 5
reDist = 0.05
ltObjectPoint = []


def continue_or_not():
	items = ("Continue", "False", "True")
	results = rs.GetBoolean("Continue options", items, (True))

	if results:
		return results[0]
	else:
		return 1

def init():
	ptStartPoint = rs.GetObject("Select the point to start", rs.filter.point)
	ptcordStartPoint = rs.PointCoordinates(ptStartPoint)
	rs.AddTextDot("0,0",ptcordStartPoint)
	quePoint = Queue.Queue(maxsize=0)
	quePoint.put(ptcordStartPoint)
	dictPointByNum[(0,0)] = ptcordStartPoint
	dictPointByCord[ptcordStartPoint] = (0,0)
	cvBaseCurve = rs.GetObject("Select the baseline", rs.filter.curve)
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
				boolInOrNot = 0
				for ptcordPointTmpInOrOut in dictPointByCord:
					reDistForCompare = rs.Distance(ptcordPointTmpInOrOut,ptcordTmpPointInter)

					print ptcordPointTmpInOrOut
					print ptcordTmpPointInter
					print "this"
					if reDistForCompare < reDist:
						boolInOrNot = 1
						break
				print boolInOrNot
				if boolInOrNot == 0:
					quePoint.put(ptcordTmpPointInter)
					intTmpX = ltTmpCordNum[0]
					intTmpY = ltTmpCordNum[1]
					if ptcordTmpPointInter[0]<ptcordTmpPoint[0]:
						intTmpX -= 1
					else:
						intTmpX += 1
					ltTmpCordNumInter = (intTmpX,intTmpY)
					if (intTmpX % 5 == 0) and (intTmpY % 5 == 0):
						rs.AddTextDot(str(intTmpX)+","+str(intTmpY),ptcordTmpPointInter)
					dictPointByCord[ptcordTmpPointInter] = ltTmpCordNumInter
					dictPointByNum[ltTmpCordNumInter] = ptcordTmpPointInter
					ptTmpPoint = rs.AddPoint(ltIntersectionPoint[1])
					ltObjectPoint.append(ptTmpPoint)
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


def main():
	intInitReturn = init()
	if intInitReturn is not 0:
		return

#	intFinishReturn = finish()

if __name__ == "__main__":
	main()    
