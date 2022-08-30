import sys
import tsplib95
import math
import random
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
#from itertools import combinations, groupby
import itertools

def gnp_random_connected_graph(n, p, t, s):
	"""
	Generates a random undirected graph, similarly to an Erdős-Rényi 
	graph, but enforcing that the resulting graph is conneted
	"""
	GList = []
	#if p <= 0:
	#	return G
	#if p >= 1:
	#	return nx.complete_graph(n, create_using=G)
	for i in range(t):
		if i == 0:
			G = nx.Graph()
			G.add_nodes_from(range(n))
			edgesItr1 = itertools.combinations(random.sample(list(range(n)), n), 2)
			for _, node_edges in itertools.groupby(edgesItr1, key=lambda x: x[0]):
				random_edge = random.choice(list(node_edges))
				G.add_edge(*random_edge)
		else:
			G = GList[i-1].copy()
		edgesItr2 = itertools.combinations(range(n), 2)
		for e in edgesItr2:
			if i == 0 and (not G.has_edge(*e)) and random.random() > (1-p)/(1-2*(n-1)/(n**2-n)):
				G.add_edge(*e)
			if i != 0 and (not G.has_edge(*e)) and random.random() > (1-(p+i*s))/(1-(p+(i-1)*s)):
				G.add_edge(*e)
		#print(list(G.edges))
		GList.append(G.copy())
	return GList

my_round_int = lambda x: int((x * 2 + 1) // 2)
tspFile = './' + sys.argv[1]
tspName = sys.argv[1][:-4]
problem = tsplib95.load(tspFile)
coordinates = []
for i in range(1,len(list(problem.get_nodes()))):
	coordinates.append(problem.node_coords[1+i])
coordinates.append(problem.node_coords[1]) # put the coordinate of depot into the tail of list
lenOfCoord = len(coordinates)

sumOfDistance = 0
for i in range(lenOfCoord):
	for j in range(1+i,lenOfCoord):
		sumOfDistance += my_round_int(math.dist( (coordinates[i][0], coordinates[i][1]), (coordinates[j][0], coordinates[j][1]) ))
avgDistance = my_round_int(sumOfDistance / (lenOfCoord*(lenOfCoord-1)/2))

repetRate = 3

# <profit, size, pickup_point, dropoff_point> of request
requestList = []
lenOfRequest = my_round_int((lenOfCoord-1)*repetRate/2)

## generate the decrementable list of <pickup_point, dropoff_point> for corresponding 'repetRate'
repetList = [1] * (lenOfCoord-1)
while sum(repetList) < 2*lenOfRequest:
	tmpRandIdx = my_round_int(random.uniform(0, lenOfCoord-2))
	repetList[tmpRandIdx] += 1
#print(repetList)

shuffList = []
for i in range(lenOfCoord-1):
	shuffList += [i] * repetList[i]
#print(shuffList)

reshuffle = True
pairList = []
while reshuffle:
	random.shuffle(shuffList)
	pairList.clear()
	for i in range(int(len(shuffList)/2)):
		if shuffList[2*i] == shuffList[1+2*i] or [shuffList[2*i], shuffList[1+2*i]] in pairList:
			break
		else:
			pairList.append([shuffList[2*i], shuffList[1+2*i]])
			if i == int(len(shuffList)/2)-1:
				reshuffle = False
#print(pairList)

headOfList = []
tailOfList = []
while len(pairList) > 0:
	### for the head of list
	i = 0
	while i < len(pairList):
		if repetList[pairList[i][0]] == 1 and repetList[pairList[i][1]] == 1:
			repetList[pairList[i][0]] -= 1
			repetList[pairList[i][1]] -= 1
			headOfList.insert(0, pairList.pop(i))
		elif repetList[pairList[i][0]] == 1 or repetList[pairList[i][1]] == 1:
			repetList[pairList[i][0]] -= 1
			repetList[pairList[i][1]] -= 1
			headOfList.append(pairList.pop(i))
		else:
			i += 1
	### for the tail of list
	maxIdx = -1
	tmpMax = 0
	for j in range(len(pairList)):
		if repetList[pairList[j][0]] + repetList[pairList[j][1]] > tmpMax:
			tmpMax = repetList[pairList[j][0]] + repetList[pairList[j][1]]
			maxIdx = j
	if maxIdx != -1:
		repetList[pairList[maxIdx][0]] -= 1
		repetList[pairList[maxIdx][1]] -= 1
		tailOfList.insert(0, pairList.pop(maxIdx))
sortedPairList = headOfList + tailOfList
#print(sortedPairList)

avgVol = 5
for i in range(lenOfRequest):
	lowerVol = 1
	upperVol = 2 * avgVol - lowerVol
	tmpRandVol = my_round_int(random.uniform(lowerVol, upperVol))
	requestList.append([my_round_int(2*avgDistance*tmpRandVol/avgVol), tmpRandVol])

for i in range(lenOfRequest):
	requestList[i].append(sortedPairList[i][0]) # pickup point
	requestList[i].append(sortedPairList[i][1]) # dropoff point

lenOfRequestList = [my_round_int((lenOfCoord-1)*repetRateList/2) for repetRateList in [3, 2.5, 2, 1.5, 1]]
#print(lenOfRequestList)

for cutEndIdx in lenOfRequestList:
	dfo = pd.DataFrame(requestList[:cutEndIdx])
	dfo.to_csv('requestInfo'+str(cutEndIdx)+'_'+tspName+'.csv', header=False, index=False)

	#dfi = pd.read_csv('requestInfo'+str(cutEndIdx)+'.csv', header=None) #, index_col=0)
	#print(dfi.to_string())





dfo = pd.DataFrame(coordinates)
dfo.to_csv('2DNode'+'_'+tspName+'.csv', header=False, index=False)

#dfi = pd.read_csv('2DNode.csv', header=None) #, index_col=0)
#print(dfi.to_string())





# adjacency matrix (size=lenOfCoord) where 0:=no_edge, 1:=edge, and 2:=free_edge
connectRatio = 1 # 0.6
sizeOfGList = 1 # 4
skip = 0.1
GList = gnp_random_connected_graph(lenOfCoord, connectRatio, sizeOfGList, skip)
edgesList = []
for i in range(sizeOfGList):
	edgesList.append(list(GList[i].edges))
	#print(edgesList[i])

#plt.figure(figsize=(8,5))
#nx.draw(GList[0], node_color='lightblue', with_labels=True, node_size=500)
#plt.show()

adjMatrix = [[0]*lenOfCoord for i in range(lenOfCoord)]
#for i in range(lenOfCoord):
#	adjMatrix[-1][i] = 2
#	adjMatrix[i][-1] = 2
#print(adjMatrix)
for i in range(lenOfCoord):
	adjMatrix[i][i] = 1

for i in range(sizeOfGList):
	for j in range(len(edgesList[i])):
		adjMatrix[edgesList[i][j][0]][edgesList[i][j][1]] = 1
		adjMatrix[edgesList[i][j][1]][edgesList[i][j][0]] = 1

	dfo = pd.DataFrame(adjMatrix)
	dfo.to_csv('adjMatrx'+str(int(10*(connectRatio+i*skip)))+'_'+tspName+'.csv', header=False, index=False)

	#dfi = pd.read_csv('adjMatrx'+str(int(10*connectRatio+i*skip))+'.csv', header=None) #, index_col=0)
	#print(dfi.to_string())





# <capacity, cost_coefficient> of vehicle
avgCap = 20
for lenOfVehicle in [2,4,6,8,10]:
#for lenOfVehicle in [my_round_int(avgVol*x/avgCap) for x in lenOfRequestList]:
	vehicleList = []
	for i in range(lenOfVehicle):
		capactCoeffi = [1, 0, -1]
		vehicleList.append([avgCap+5*capactCoeffi[i%3], 1+0.2*capactCoeffi[i%3]])

	dfo = pd.DataFrame(vehicleList)
	dfo.to_csv('vehicleCap'+str(lenOfVehicle)+'_'+tspName+'.csv', header=False, index=False)

	#dfi = pd.read_csv('vehicleCap'+str(lenOfVehicle)+'.csv', header=None) #, index_col=0)
	#print(dfi.to_string())












