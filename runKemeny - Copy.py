import sys
import prefpy
from prefpy import preference
from prefpy import profile
from prefpy import io

from prefpy.kemeny import MechanismKemeny
from prefpy.profile import Profile
from prefpy.preference import Preference

from gurobipy import *
import numpy as np
#=====================================================================================

def preferenceMatrix(preferences, counts):
	n, m = sum(counts), len(preferences[0])    # n preferences, m candidates
	print("m is", m)
	Q = np.zeros((m,m))
	for k in range(len(preferences)):
		vote = preferences[k]
		for i in range(len(vote) - 1):
			for j in range(i + 1, len(vote)):
				Q[vote[i][0]-1][vote[j][0]-1] += 1*counts[k] #Q[vote[i]][vote[j]] += 1
	return Q / n


def main():

	data = Profile({},[])


	# filename = "input1"
	filename = input("Enter name of election data file:   ").lower()
	data.importPreflibFile(filename)
	print("Imported file")

	kemenyMech = MechanismKemeny()
	#print("Created KemenyMechanism obj")

	kemWinner1 = kemenyMech.getWinners(data)
	kemWinRank1 = kemenyMech.getWinningRankings()
	print("W* = " + str(kemWinRank1) + ",  winner = " + str(kemWinner1))


	print(data.getPreferenceCounts())
	print(data.getOrderVectors())
	print(preferenceMatrix(data.getOrderVectors(), data.getPreferenceCounts()))
	print(data.candMap)

	try:
		# Create a new model
		m = Model("kemeny")

		binaryMap = {}
		candMap = data.candMap
		keys = candMap.keys()
		print(keys)
		precedence = preferenceMatrix(data.getOrderVectors(), data.getPreferenceCounts())
		obj = LinExpr()
		for i in range(len(keys)-1):
			for j in range(i+1, len(keys)):

				# Create variables
				binaryMap[(i,j)] = m.addVar(vtype=GRB.BINARY, name=candMap[i+1]+candMap[j+1])
				binaryMap[(j,i)] = m.addVar(vtype=GRB.BINARY, name=candMap[j+1]+candMap[i+1])
				# Integrate new variables
				m.update()

				# Add constraint: X_ab + X_ba = 1
				m.addConstr(binaryMap[(i,j)] + binaryMap[(j,i)] == 1)
				obj += precedence[i][j]*binaryMap[(j,i)] + precedence[j][i]*binaryMap[(i,j)]
				obj += precedence[j][i]*binaryMap[(i,j)] + precedence[i][j]*binaryMap[(j,i)]


		for i in range(len(keys)-2):
			for j in range(i+1, len(keys)-1):
				for k in range(j+1, len(keys)):
					m.addConstr(binaryMap[(i,j)] + binaryMap[(j,k)] + binaryMap[k, i] >= 1)

		# Set objective
		m.setObjective(obj, GRB.MINIMIZE)

		m.optimize()

		print(precedence)

		for v in m.getVars():
			print(v.varName, v.x)

		print('Obj:', m.objVal)

	except GurobiError:
		print('Error reported')


	# data.exportPreflibFile(filename + "-output")
	# print("Created output file")

	# myList = [(4, 'a', 'b'), (3, 'b', 'c'), (3, 'c', 'd'), (2, 'd', 'b'), (2, 'c', 'a'), (4, 'd', 'a')]
	# #print(rankpairMech.getWinners(edges = myList))
	# print(rankpairMech.getWinners(prof = data))
	# print(rankpairMech.getOneWinner(data))
	# edgeList=rankpairMech.getSortedEdges(data)
	# rankpairMech.createNXGraph(edgeList)



#=====================================================================================

if __name__ == '__main__':
	main()


