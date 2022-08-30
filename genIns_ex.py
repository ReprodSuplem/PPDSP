import sys
import math
import subprocess
import pandas as pd

#
#================================================
class PPDPS:
	mip = ''
	varID = 0
	constrID = 0
	adjMxCSV = ''
	coordCSV = ''
	reqstCSV = ''
	vehiCSV = ''
	
	adjMatrx = []
	coordinates = []
	lenOfCoord = 0
	locaList = []
	requestList = []
	lenOfRequest = 0
	vehicleList = []
	lenOfVehicle = 0
	costMatrices = []

	xVarList = []
	tVarList = []
	qVarList = []

	#+++++++++++++++++++++

	def __init__(self):
		self.mip = ''
		constrID = 0
		self.coordCSV = '2DNode_' + sys.argv[1] + '.csv'
		self.reqstCSV = 'requestInfo' + sys.argv[2] + '_' + sys.argv[1] + '.csv'
		self.vehiCSV = 'vehicleCap' + sys.argv[3] + '_' + sys.argv[1] + '.csv'
		self.adjMxCSV = 'adjMatrx' + sys.argv[4] + '_' + sys.argv[1] + '.csv'
		self.readCSV()

		tmpList1 = [[self.coordinates[-1][0], self.coordinates[-1][1], 0, 0, -1]]
		tmpList2 = []
		for i in range(self.lenOfRequest):
			tmpList1.append([self.coordinates[self.requestList[i][2]][0], self.coordinates[self.requestList[i][2]][1], self.requestList[i][0], self.requestList[i][1], self.requestList[i][2]])
			tmpList2.append([self.coordinates[self.requestList[i][3]][0], self.coordinates[self.requestList[i][3]][1], self.requestList[i][0], -1*self.requestList[i][1], self.requestList[i][3]])
		tmpList2.append([self.coordinates[-1][0], self.coordinates[-1][1], 0, 0, -1])
		# requestList = {[ x, y, w, s, idx]}
		self.requestList = tmpList1 + tmpList2
		print(self.requestList)
		self.lenOfRequest = len(self.requestList) # size = 2n+2

		# costMatrices
		for i in range(self.lenOfVehicle):
			tmpMatrix = []
			for j in range(self.lenOfRequest):
				tmpList = []
				for k in range(self.lenOfRequest):
					tmpList.append(self.my_round_int(self.vehicleList[i][1]*self.locaList[self.requestList[j][4]][self.requestList[k][4]]))
				#print(tmpList)
				tmpMatrix.append(tmpList)
			self.costMatrices.append(tmpMatrix)

		# initialize each list of variables
		self.xVarList = [[[0]*self.lenOfRequest for j in range(self.lenOfRequest)] for i in range(self.lenOfVehicle)]
		self.tVarList = [[0]*self.lenOfRequest for i in range(self.lenOfVehicle)]
		self.qVarList = [[0]*self.lenOfRequest for i in range(self.lenOfVehicle)]

		#+++++++++++++++++++++

	def readCSV(self):
		# adjacency matrix
		self.adjMatrx = pd.read_csv(self.adjMxCSV, header=None).values.tolist()

		# <x, y> of location
		self.coordinates = pd.read_csv(self.coordCSV, header=None).values.tolist()
		#print(self.coordinates)
		self.lenOfCoord = len(self.coordinates)

		for i in range(self.lenOfCoord):
			tmpList = []
			for j in range(self.lenOfCoord):
				if self.adjMatrx[i][j] == 0: # block
					tmpList.append(999999)
				if self.adjMatrx[i][j] == 2: # free
					tmpList.append(0)
				if self.adjMatrx[i][j] == 1: # edge
					tmpList.append(self.my_round_int(math.dist( (self.coordinates[i][0], self.coordinates[i][1]), (self.coordinates[j][0], self.coordinates[j][1]) )))
			#print(tmpList)
			self.locaList.append(tmpList)
		self.floyd(self.locaList)
		#print(self.locaList)

		# <profit, size, origin, destination> of request
		self.requestList = pd.read_csv(self.reqstCSV, header=None).values.tolist()
		#print(self.requestList)
		self.lenOfRequest = len(self.requestList)

		# <capacity, cost_coefficient> of vehicle
		self.vehicleList = pd.read_csv(self.vehiCSV, header=None).values.tolist()
		#print(self.vehicleList)
		self.lenOfVehicle = len(self.vehicleList)

	def my_round_int(self, x):
		return (x * 2 + 1) // 2

	def floyd(self, tmpMatrix):
		for i in range(len(tmpMatrix)):
			for j in range(len(tmpMatrix)):
				for k in range(len(tmpMatrix)):
					tmpMatrix[j][k] = min(tmpMatrix[j][k], tmpMatrix[j][i] + tmpMatrix[i][k])

	# costMatrix 'cost-matrix_{v}' ## v:=vehicle
	def printCostMatrices(self):
		for i in range(len(self.costMatrices)):
			print('cost-matrix_{{{0}}}'.format(i))
			for j in range(self.lenOfRequest):
				print(*self.costMatrices[i][j], sep='\t')

	def newVarID(self):
		self.varID += 1
		return self.varID

	# binary variable 'x^v_{od}' ## v:=vehicle, o:=origin, d:=destination
	def genXVarList(self):
		for i in range(len(self.xVarList)):
			for j in range(len(self.xVarList[i])):
				for k in range(len(self.xVarList[i][j])):
					self.xVarList[i][j][k] = self.newVarID()

	def printXVarList(self):
		for i in range(len(self.xVarList)):
			print('x_{{{0}}}{1}'.format(i,'od'))
			for j in range(len(self.xVarList[i])):
				print(self.xVarList[i][j])

	# [time window] integer variables 't^v_n' ## v:=vehicle, n:=node
	def genTVarList(self):
		for i in range(len(self.tVarList)):
			for j in range(len(self.tVarList[i])):
				self.tVarList[i][j] = self.newVarID()

	def printTVarList(self):
		for i in range(len(self.tVarList)):
			print('t^{{{0}}}{1}'.format(i,'n'))
			print(self.tVarList[i])

	# [capacity] integer variables 'q^v_n' ## v:=vehicle, n:=node
	def genQVarList(self):
		for i in range(len(self.qVarList)):
			for j in range(len(self.qVarList[i])):
				self.qVarList[i][j] = self.newVarID()

	def printQVarList(self):
		for i in range(len(self.qVarList)):
			print('q^{{{0}}}{1}'.format(i,'n'))
			print(self.qVarList[i])

	def newConstrID(self):
		self.constrID += 1
		return self.constrID

	def genMipObjFunc(self): # Eq1
		isFirst = True
		self.mip += 'Maximize z\n\nSubject to\n'
		for i in range(self.lenOfVehicle):
			for j in range(1,int(self.lenOfRequest/2)): # P\in [1, n+1)
				for k in range(self.lenOfRequest):
					if isFirst:
						self.mip += str(self.requestList[j][2]) + ' x' + str(self.xVarList[i][j][k])
						isFirst = False
					else:
						self.mip += ' + ' + str(self.requestList[j][2]) + ' x' + str(self.xVarList[i][j][k])
		for i in range(self.lenOfVehicle):
			for j in range(self.lenOfRequest):
				for k in range(self.lenOfRequest):
					self.mip += ' - ' + str(self.costMatrices[i][j][k]) + ' x' + str(self.xVarList[i][j][k])
		self.mip += ' - z = 0\n'

	def genMipForEq3(self):
		for i in range(self.lenOfVehicle):
			isFirst = True
			for j in range(self.lenOfRequest):
				if isFirst:
					self.mip += 'c' + str(self.newConstrID()) + ': x' + str(self.xVarList[i][0][j])
					isFirst = False
				else:
					self.mip += ' + x' + str(self.xVarList[i][0][j])
			self.mip += ' = 1\n'
		for i in range(self.lenOfVehicle):
			isFirst = True
			for j in range(self.lenOfRequest):
				if isFirst:
					self.mip += 'c' + str(self.newConstrID()) + ': x' + str(self.xVarList[i][j][self.lenOfRequest-1])
					isFirst = False
				else:
					self.mip += ' + x' + str(self.xVarList[i][j][self.lenOfRequest-1])
			self.mip += ' = 1\n'

	def genMipForEq4(self):
		for i in range(1,int(self.lenOfRequest/2)): # P\in [1, n+1)
			isFirst = True
			for j in range(self.lenOfVehicle):
				for k in range(self.lenOfRequest):
					if isFirst:
						self.mip += 'c' + str(self.newConstrID()) + ': x' + str(self.xVarList[j][k][i])
						isFirst = False
					else:
						self.mip += ' + x' + str(self.xVarList[j][k][i])
			self.mip += ' <= 1\n'

	def genMipForEq5(self):
		for i in range(self.lenOfVehicle):
			for j in range(1,int(self.lenOfRequest/2)): # P\in [1, n+1)
				isFirst = True
				for k in range(self.lenOfRequest):
					if isFirst:
						self.mip += 'c' + str(self.newConstrID()) + ': x' + str(self.xVarList[i][j][k]) + ' - x' + str(self.xVarList[i][j+int(self.lenOfRequest/2)-1][k])
						isFirst = False
					else:
						self.mip += ' + x' + str(self.xVarList[i][j][k]) + ' - x' + str(self.xVarList[i][j+int(self.lenOfRequest/2)-1][k])
				self.mip += ' = 0\n'

	def genMipForEq6(self):
		for i in range(self.lenOfVehicle):
			for j in range(1,self.lenOfRequest-1): # P\cup D\in [1, 2n+1)
				isFirst = True
				for k in range(self.lenOfRequest):
					if isFirst:
						self.mip += 'c' + str(self.newConstrID()) + ': x' + str(self.xVarList[i][j][k]) + ' - x' + str(self.xVarList[i][k][j])
						isFirst = False
					else:
						self.mip += ' + x' + str(self.xVarList[i][j][k]) + ' - x' + str(self.xVarList[i][k][j])
				self.mip += ' = 0\n'

	def genMipForEq7Modf(self):
		for i in range(self.lenOfVehicle):
			for j in range(self.lenOfRequest):
				for k in range(self.lenOfRequest):
					if k != j:
						self.mip += 'c' + str(self.newConstrID()) + ': t' + str(self.tVarList[i][j]) + ' - t' + str(self.tVarList[i][k]) + ' + ' + str(self.lenOfRequest) + ' x' + str(self.xVarList[i][j][k]) + ' <= ' + str(self.lenOfRequest-1) + '\n'

	def genMipForEq8Modf(self):
		for i in range(self.lenOfVehicle):
			for j in range(1,int(self.lenOfRequest/2)): # P\in [1, n+1)
				self.mip += 'c' + str(self.newConstrID()) + ': t' + str(self.tVarList[i][j+int(self.lenOfRequest/2)-1]) + ' - t' + str(self.tVarList[i][j]) + ' > 0\n'

	def genMipForEq11(self):
		for i in range(self.lenOfVehicle):
			for j in range(self.lenOfRequest):
				for k in range(self.lenOfRequest):
					if k != j:
						variantSize = self.requestList[k][3]
						if variantSize > self.vehicleList[i][0] or self.vehicleList[i][0]+variantSize < 0:
							self.mip += 'c' + str(self.newConstrID()) + ': x' + str(self.xVarList[i][j][k]) + ' = 0\n'
						else:
							self.mip += 'c' + str(self.newConstrID()) + ': q' + str(self.qVarList[i][j]) + ' - q' + str(self.qVarList[i][k]) + ' + ' + str(int(self.vehicleList[i][0])) + ' x' + str(self.xVarList[i][j][k]) + ' <= ' + str(int(self.vehicleList[i][0])-variantSize) + '\n'

	def genMipForEq12(self):
		for i in range(self.lenOfVehicle):
			for j in range(self.lenOfRequest):
				variantSize = self.requestList[j][3]
				if variantSize > 0:
					if variantSize > self.vehicleList[i][0]:
						for k in range(self.lenOfRequest):
							self.mip += 'x' + str(self.xVarList[i][k][j]) + ' = 0\n'
					else:
						self.mip += 'q' + str(self.qVarList[i][j]) + ' >= ' + str(variantSize) + '\n'
						self.mip += 'q' + str(self.qVarList[i][j]) + ' <= ' + str(int(self.vehicleList[i][0])) + '\n'
				elif self.vehicleList[i][0]+variantSize > 0:
					self.mip += 'q' + str(self.qVarList[i][j]) + ' <= ' + str(int(self.vehicleList[i][0])+variantSize) + '\n'
				else:
					for k in range(self.lenOfRequest):
						self.mip += 'x' + str(self.xVarList[i][k][j]) + ' = 0\n'

	def genMipForEq17(self):
		for i in range(self.lenOfVehicle):
			for j in range(self.lenOfRequest):
				self.mip += 'x' + str(self.xVarList[i][j][j]) + ' = 0\n'

	def genMipForEq18(self):
		for i in range(self.lenOfVehicle):
			for j in range(int(self.lenOfRequest/2),self.lenOfRequest-1): # D\in [n+1, 2n+1)
				self.mip += 'x' + str(self.xVarList[i][0][j]) + ' = 0\n'

	def genMipForEq19(self):
		for i in range(self.lenOfVehicle):
			for j in range(1,int(self.lenOfRequest/2)): # P\in [1, n+1)
				self.mip += 'x' + str(self.xVarList[i][j][self.lenOfRequest-1]) + ' = 0\n'

	def genMipForEq20(self):
		for i in range(self.lenOfVehicle):
			for j in range(1,self.lenOfRequest-1): # P\cup D\in [1, 2n+1)
				self.mip += 'x' + str(self.xVarList[i][j][0]) + ' = 0\n'

	def genMipForEq21(self):
		for i in range(self.lenOfVehicle):
			for j in range(1,self.lenOfRequest-1): # P\cup D\in [1, 2n+1)
				self.mip += 'x' + str(self.xVarList[i][self.lenOfRequest-1][j]) + ' = 0\n'	

	def declareBounds(self):
		self.mip += '\nBounds\n'
		self.genMipForEq12()
		self.genMipForEq17()
		self.genMipForEq18()
		self.genMipForEq19()
		self.genMipForEq20()
		self.genMipForEq21()

	def declareBooleanVar(self): # Eq2
		self.mip += '\nBinary\n'
		for i in range(1, self.tVarList[0][0]):
			self.mip += 'x' + str(i) + '\n'

	def declareIntVar(self):
		self.mip += '\nGeneral\n'
		for i in range(self.tVarList[0][0], self.qVarList[0][0]):
			self.mip += 't' + str(i) + '\n'
		for i in range(self.qVarList[0][0], 1+self.varID):
			self.mip += 'q' + str(i) + '\n'
		self.mip += 'z\n'

	def genTailOfMipFile(self):
		self.mip += 'End'

	def writeMipFile(self, mipFileName):
		lpFile = open(mipFileName+'.lp', 'w')
		lpFile.write(self.mip)
		lpFile.close()

	#+++++++++++++++++++++
	

#================================================
#

#===========================
if __name__ == '__main__':
	insName = 'ex_' + sys.argv[1] + '_r' + sys.argv[2] + 'v' + sys.argv[3] + 'c' + sys.argv[4]

	ppdps = PPDPS()
	ppdps.genXVarList()
	ppdps.genTVarList()
	ppdps.genQVarList()

	ppdps.printXVarList()
	ppdps.printTVarList()
	ppdps.printQVarList()
	ppdps.printCostMatrices()

	ppdps.genMipObjFunc()
	ppdps.genMipForEq3()
	ppdps.genMipForEq4()
	ppdps.genMipForEq5()
	ppdps.genMipForEq6()
	ppdps.genMipForEq7Modf()
	ppdps.genMipForEq8Modf()
	ppdps.genMipForEq11()

	ppdps.declareBounds()
	ppdps.declareBooleanVar()
	ppdps.declareIntVar()
	ppdps.genTailOfMipFile()
	ppdps.writeMipFile(insName)

	#+++++++++++++++++++++

	#============
	#subprocess.run(['ls', '-a'])









