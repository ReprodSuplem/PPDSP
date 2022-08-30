import sys
import math
import subprocess
import pandas as pd

#
#================================================
class ReForm:
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
	lenOfLocation = 0
	requestList = []
	lenOfRequest = 0
	vehicleList = []
	lenOfVehicle = 0

	xVarList = []
	yVarList = []
	uVarList = []
	hVarList = []

	def __init__(self):
		self.mip = ''
		constrID = 0
		self.coordCSV = '2DNode_' + sys.argv[1] + '.csv'
		self.reqstCSV = 'requestInfo' + sys.argv[2] + '_' + sys.argv[1] + '.csv'
		self.vehiCSV = 'vehicleCap' + sys.argv[3] + '_' + sys.argv[1] + '.csv'
		self.adjMxCSV = 'adjMatrx' + sys.argv[4] + '_' + sys.argv[1] + '.csv'
		self.readCSV()

		self.xVarList = [[[0]*(1+self.lenOfLocation) for j in range(1+self.lenOfLocation)] for i in range(self.lenOfVehicle)]
		self.yVarList = [[0]*self.lenOfVehicle for i in range(self.lenOfRequest)]
		self.uVarList = [[0]*self.lenOfLocation for i in range(self.lenOfVehicle)]
		self.hVarList = [[0]*self.lenOfLocation for i in range(self.lenOfVehicle)]

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
		self.lenOfLocation = len(self.locaList)-1
		#print(self.lenOfLocation)

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

	def newVarID(self):
		self.varID += 1
		return self.varID

	# Variable 'x^t_{od}'
	def genXVarList(self):
		for i in range(len(self.xVarList)):
			for j in range(len(self.xVarList[i])):
				for k in range(len(self.xVarList[i][j])):
					self.xVarList[i][j][k] = self.newVarID()

	def printXVarList(self):
		for i in range(len(self.xVarList)):
			print('x^{{{0}}}{1}'.format(i,'od'))
			for j in range(len(self.xVarList[i])):
				print(self.xVarList[i][j])

	# Variable 'y^t_r'
	def genYVarList(self):
		for i in range(len(self.yVarList)):
			for j in range(len(self.yVarList[i])):
				self.yVarList[i][j] = self.newVarID()

	def printYVarList(self):
		print('y^t_r')
		for i in range(len(self.yVarList)):
			print(self.yVarList[i])

	# Variable 'u^t_v'
	def genUVarList(self):
		for i in range(len(self.uVarList)):
			for j in range(len(self.uVarList[i])):
				self.uVarList[i][j] = self.newVarID()

	def printUVarList(self):
		for i in range(len(self.uVarList)):
			print('u^{{{0}}}{1}'.format(i,'v'))
			print(self.uVarList[i])

	# Variable 'h^t_v'
	def genHVarList(self):
		for i in range(len(self.hVarList)):
			for j in range(len(self.hVarList[i])):
				self.hVarList[i][j] = self.newVarID()

	def printHVarList(self):
		for i in range(len(self.hVarList)):
			print('h^{{{0}}}{1}'.format(i,'v'))
			print(self.hVarList[i])

	def newConstrID(self):
		self.constrID += 1
		return self.constrID

	def genMipObjFunc(self):
		isFirst = True
		self.mip += 'Maximize z\n\nSubject to\n'
		for i in range(self.lenOfRequest):
			for j in range(self.lenOfVehicle):
				if isFirst:
					self.mip += str(self.requestList[i][0]) + ' y' + str(self.yVarList[i][j])
					isFirst = False
				else:
					self.mip += ' + ' + str(self.requestList[i][0]) + ' y' + str(self.yVarList[i][j])
		for i in range(self.lenOfVehicle):
			for j in range(1+self.lenOfLocation):
				for k in range(1+self.lenOfLocation):
					#if k != j:
					self.mip += ' - ' + str(self.my_round_int(self.vehicleList[i][1]*self.locaList[j][k])) + ' x' + str(self.xVarList[i][j][k])
		self.mip += ' - z = 0\n'

	def genMipForEq3(self):
		for i in range(self.lenOfRequest):
			isFirst = True
			for j in range(self.lenOfVehicle):
				if isFirst:
					self.mip += 'c' + str(self.newConstrID()) + ': y' + str(self.yVarList[i][j])
					isFirst = False
				else:
					self.mip += ' + y' + str(self.yVarList[i][j])
			self.mip  += ' <= 1\n'	

	def genMipForEq4(self):
		for i in range(self.lenOfRequest):
			for j in range(self.lenOfVehicle):
				isFirst = True
				for k in range(1+self.lenOfLocation):
					if k != self.requestList[i][2] and k != self.requestList[i][3]:
						if isFirst:
							self.mip += 'c' + str(self.newConstrID()) + ': x' + str(self.xVarList[j][k][self.requestList[i][2]])
							isFirst = False
						else:
							self.mip += ' + x' + str(self.xVarList[j][k][self.requestList[i][2]])
				self.mip += ' - y' + str(self.yVarList[i][j]) + ' >= 0\n'

	def genMipForEq5(self):
		for i in range(self.lenOfRequest):
			for j in range(self.lenOfVehicle):
				isFirst = True
				for k in range(self.lenOfLocation):
					if k != self.requestList[i][3]:
						if isFirst:
							self.mip += 'c' + str(self.newConstrID()) + ': x' + str(self.xVarList[j][k][self.requestList[i][3]])
							isFirst = False
						else:
							self.mip += ' + x' + str(self.xVarList[j][k][self.requestList[i][3]])
				self.mip += ' - y' + str(self.yVarList[i][j]) + ' >= 0\n'

	def genMipForEq6(self):
		for i in range(self.lenOfVehicle):
			for j in range(1+self.lenOfLocation):
				isFirst = True
				for k in range(1+self.lenOfLocation):
					if isFirst:
						self.mip += 'c' + str(self.newConstrID()) + ': x' + str(self.xVarList[i][j][k]) + ' - x' + str(self.xVarList[i][k][j])
						isFirst = False
					else:
						self.mip += ' + x' + str(self.xVarList[i][j][k]) + ' - x' + str(self.xVarList[i][k][j])
				self.mip += ' = 0\n'

	def genMipForEq7(self):
		for i in range(self.lenOfVehicle):
			for j in range(1+self.lenOfLocation):
				isFirst = True
				for k in range(1+self.lenOfLocation):
					if k != j:
						if isFirst:
							self.mip += 'c' + str(self.newConstrID()) + ': x' + str(self.xVarList[i][j][k])
							isFirst = False
						else:
							self.mip += ' + x' + str(self.xVarList[i][j][k])
				self.mip += ' <= 1\n'

	# MTZ-SEC
	def genMipForEq8(self):
		for i in range(self.lenOfVehicle):
			for j in range(self.lenOfLocation):
				for k in range(self.lenOfLocation):
					if k != j:
						self.mip += 'c' + str(self.newConstrID()) + ': u' + str(self.uVarList[i][j]) + ' - u' + str(self.uVarList[i][k]) + ' + ' + str(self.lenOfLocation) + ' x' + str(self.xVarList[i][j][k]) + ' <= ' + str(self.lenOfLocation-1) + '\n'

	def genMipForEq9(self):
		for i in range(self.lenOfRequest):
			for j in range(self.lenOfVehicle):
				self.mip += 'c' + str(self.newConstrID()) + ': u' + str(self.uVarList[j][self.requestList[i][2]]) + ' - u' + str(self.uVarList[j][self.requestList[i][3]]) + ' + ' + str(self.lenOfLocation) + ' y' + str(self.yVarList[i][j]) + ' < ' + str(self.lenOfLocation) + '\n'

	def genMipForEq10(self):
		bigMInEq10 = 0
		for i in range(self.lenOfVehicle):
			if self.vehicleList[i][0] > bigMInEq10:
				bigMInEq10 = self.vehicleList[i][0]
		for i in range(self.lenOfRequest):
			bigMInEq10 += self.requestList[i][1]
		print('bigM @ Eq.10: {0}'.format(bigMInEq10))
		for i in range(self.lenOfVehicle):
			for j in range(self.lenOfLocation): # j is 'o'
				for k in range(self.lenOfLocation): # k is 'd'
					if k != j:
						Gamma = ''
						tmpList1 = []
						tmpList2 = []
						for l in range(self.lenOfRequest):
							if self.requestList[l][2] == k:
								tmpList1.append(l)
							if self.requestList[l][3] == k:
								tmpList2.append(l)
						for l in range(len(tmpList1)):
							Gamma += ' + ' + str(self.requestList[tmpList1[l]][1]) + ' y' + str(self.yVarList[tmpList1[l]][i])
						for l in range(len(tmpList2)):
							Gamma += ' - ' + str(self.requestList[tmpList2[l]][1]) + ' y' + str(self.yVarList[tmpList2[l]][i])
						# for the leftside of Eq.10
						self.mip += 'c' + str(self.newConstrID()) + ': h' + str(self.hVarList[i][j]) + ' - h' + str(self.hVarList[i][k]) + ' + ' + str(bigMInEq10) + ' x' + str(self.xVarList[i][j][k]) + Gamma + ' <= ' + str(int(bigMInEq10)) + '\n'
						# for the rightside of Eq.10
						self.mip += 'c' + str(self.newConstrID()) + ': h' + str(self.hVarList[i][j]) + ' - h' + str(self.hVarList[i][k]) + ' - ' + str(bigMInEq10) + ' x' + str(self.xVarList[i][j][k]) + Gamma + ' >= ' + str(-1*int(bigMInEq10)) + '\n'

	def genMipForEq11(self):
		for i in range(self.lenOfVehicle):
			for j in range(self.lenOfLocation):
				self.mip += 'h' + str(self.hVarList[i][j]) + ' <= ' + str(int(self.vehicleList[i][0])) + '\n'

	def genMipForEq12(self):
		for i in range(self.lenOfVehicle):
			for j in range(self.lenOfLocation):
				self.mip += 'u' + str(self.uVarList[i][j]) + ' <= ' + str(self.lenOfLocation-1) + '\n'

	def declareBounds(self):
		self.mip += '\nBounds\n'
		self.genMipForEq11()
		self.genMipForEq12()

	def declareBooleanVar(self): # Eq.2
		self.mip += '\nBinary\n'
		for i in range(1, self.yVarList[0][0]):
			self.mip += 'x' + str(i) + '\n'
		for i in range(self.yVarList[0][0], self.uVarList[0][0]):
			self.mip += 'y' + str(i) + '\n'

	def declareIntVar(self):
		self.mip += '\nGeneral\n'
		for i in range(self.uVarList[0][0], self.hVarList[0][0]):
			self.mip += 'u' + str(i) + '\n'
		for i in range(self.hVarList[0][0], 1+self.varID):
			self.mip += 'h' + str(i) + '\n'
		self.mip += 'z\n'

	def genTailOfIPFile(self):
		self.mip += 'End'

	def writeMipFile(self, mipFileName):
		lpFile = open(mipFileName+'.lp', 'w')
		lpFile.write(self.mip)
		lpFile.close()

#================================================
#

#===========================
if __name__ == '__main__':
	insName = 'p1_' + sys.argv[1] + '_r' + sys.argv[2] + 'v' + sys.argv[3] + 'c' + sys.argv[4]

	reform = ReForm()
	reform.genXVarList()
	reform.printXVarList()
	reform.genYVarList()
	reform.printYVarList()
	reform.genUVarList()
	reform.printUVarList()
	reform.genHVarList()
	reform.printHVarList()

	reform.genMipObjFunc()
	reform.genMipForEq3()
	reform.genMipForEq4()
	reform.genMipForEq5()
	reform.genMipForEq6()
	reform.genMipForEq7()
	reform.genMipForEq8()
	reform.genMipForEq9()
	reform.genMipForEq10()
	
	reform.declareBounds()
	reform.declareBooleanVar()
	reform.declareIntVar()
	reform.genTailOfIPFile()
	reform.writeMipFile(insName)









