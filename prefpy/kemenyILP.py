'''
Authors: Tobe Ezekwenna, Sam Saks-Fithian, Aman Zargarpur
'''

from prefpy.mechanism import Mechanism
from gurobipy import *
import numpy as np

#=====================================================================================
#=====================================================================================

def precedenceMatrix(preferences, counts):
	n, m = sum(counts), len(preferences[0])    # n preferences, m candidates
	#print("m is", m)
	Q = np.zeros((m,m))
	for k in range(len(preferences)):
		vote = preferences[k]
		for i in range(len(vote) - 1):
			for j in range(i + 1, len(vote)):
				Q[vote[i][0]-1][vote[j][0]-1] += 1*counts[k] #Q[vote[i]][vote[j]] += 1
	return Q / n

#=====================================================================================
#=====================================================================================

class MechanismKemenyILP(Mechanism):
	"""
	The Kemeny mechanism. Calculates winning ranking(s)/candidate(s) based on Gurobi
	optimization of ILP formula:

	Goal: minimize SUMMATION_a,b( Q_ab * X_ba + Q_ba * X_ab )
		where Q is the precedence matrix formed from profile
		i.e. Q_ab is the fraction of times a>b across all rankings in profile
	Constraints:
		X_ab in {0, 1}
		X_ab + X_ba = 1, for ALL a,b
		X_ab + X_bc + X_ca >= 1, for ALL a,b,c

	"""
	#=====================================================================================

	def __init__(self):
		self.maximizeCandScore = True
		self.winningRanking = []
		self.precMtx = []
		self.gModel = None

	#=====================================================================================

	def getCandScoresMap(self, profile):
		"""
		Returns a dictonary that associates the integer representation of each candidate 
		with their score from the ILP optimization. The score for each candidate is the 
		sum of all the binary variables that represent preference with respect to another 
		candidate after optimization.
		Sets/saves data variables for later use (self.winningRanking, self.precMtx, self.gModel)

		:ivar Profile profile: A Profile object that represents an election profile.
		"""
		# Currently, we expect the profile to contain complete ordering over candidates.
		elecType = profile.getElecType()
		if elecType != "soc":
			print("ERROR: unsupported election type")
			exit()

		try:
			# Create a new model
			m = Model("kemeny")

			binaryMap = {}
			candMap = profile.candMap
			keys = candMap.keys()
			# print(keys)
			
			precedence = precedenceMatrix(profile.getOrderVectors(), profile.getPreferenceCounts())
			
			# Begin constructing the objective
			obj = LinExpr()
			for i in range(len(keys)-1):
				for j in range(i+1, len(keys)):

					# Create variables (2, 3)
					binaryMap[(i,j)] = m.addVar(vtype=GRB.BINARY, name=candMap[i+1])
					binaryMap[(j,i)] = m.addVar(vtype=GRB.BINARY, name=candMap[j+1])
					# Integrate new variables
					m.update()

					# Add constraint: X_ab + X_ba = 1 (4)
					m.addConstr(binaryMap[(i,j)] + binaryMap[(j,i)] == 1)
					obj += precedence[i][j]*binaryMap[(j,i)] + precedence[j][i]*binaryMap[(i,j)]
					obj += precedence[j][i]*binaryMap[(i,j)] + precedence[i][j]*binaryMap[(j,i)]

			# Add transitivity constraint: X_ab + X_bc + X_ca >= 1 (5)
			for i in range(len(keys)):
				for j in range(len(keys)):
					for k in range(len(keys)):
						if(i == j or j == k or i == k):
							continue
						m.addConstr(binaryMap[(i,j)] + binaryMap[(j,k)] + binaryMap[k, i] >= 1)

			# Set objective
			m.setObjective(obj, GRB.MINIMIZE)
			m.optimize()

			# print(precedence)
			# for v in m.getVars():
				# print(v.varName, v.x)
			# print('Obj:', m.objVal)

			candScoresMap = self.convertBinVarsToCandMap(m.getVars())

			self.winningRanking = sorted(candScoresMap, key=candScoresMap.get, reverse=True)
			self.precMtx = precedence
			self.gModel = m

			return candScoresMap

		except GurobiError:
			print('Gurobi Error reported')

	#=====================================================================================

	def convertBinVarsToCandMap(self, varList):
		"""
		Returns a dictonary that associates the integer representation of each candidate 
		with their score from the ILP optimization. The score for each candidate is the 
		sum of all the binary variables that represent preference with respect to another 
		candidate after optimization.

		:ivar List varList: A list of the binary variables set by the optimization of a Gurobi model.
		"""
		candScoresMap = dict()
		for v in varList:
			if v.varName in candScoresMap.keys():
				candScoresMap[v.varName] += v.x
			else:
				candScoresMap[v.varName] = v.x
		return candScoresMap

#=====================================================================================
#=====================================================================================









