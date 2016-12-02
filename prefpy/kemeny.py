'''
Authors: Tobe Ezekwenna, Sam Saks-Fithian, Aman Zargarpur
'''

import itertools
from prefpy.mechanism import Mechanism


#=====================================================================================
#=====================================================================================

class MechanismKemeny(Mechanism):
	"""
	The Kemeny mechanism.
	"""
	#=====================================================================================

	def __init__(self):
		self.maximizeCandScore = False

	#=====================================================================================

	def getCandScoresMap(self, profile):
		"""
		Returns a dictonary that associates the integer representation of each candidate with 
		their place in the winning ranking.

		:ivar Profile profile: A Profile object that represents an election profile.
		"""

		# Currently, we expect the profile to contain complete ordering over candidates.
		elecType = profile.getElecType()
		if elecType != "soc":
			print("ERROR: unsupported election type")
			exit()

		rankWeights = dict()
		wmgMap = profile.getWmg()
		for ranking in itertools.permutations(wmgMap.keys()):
			# Initialize inconsistent weight to 0
			rankWeights[ranking] = 0.0

			# For each pair of candidates in ranking, determine if edge/order in ranking
			# is inconsistent with corresponding edge/order in the WMG of the profile
			# Sum the weights of all such inconsistent edges
			for cand1, cand2 in itertools.combinations(rankMap.keys(), 2):
				# cand1 > cand2 in wmg
				wmgOrd = 1 if (wmgMap[cand1][cand2] > 0) else 0
				# cand1 > cand2 in ranking
				rankOrd = 1 if (ranking.index(cand1) < ranking.index(cand2)) else 0
				if wmgOrd != rankOrd:
					rankWeights[ranking] += abs(wmgMap[cand1][cand2])

		bestScore = min(rankWeights.values())
		winningRankings = []
		for ranking in rankWeights.keys():
			if rankWeights[ranking] == bestScore:
				winningRankings.append(ranking)

		if len(winningRankings) > 1:
			winRank = tiebreakRankings(winningRankings)
		else:
			winRank = winningRankings[0]

		return convertRankingToCandMap(winRank)

	#=====================================================================================

	def convertRankingToCandMap(self, ranking):
		"""
		Returns a dictonary that associates the integer representation of each candidate with 
		their place in the winning ranking.

		:ivar Tuple ranking: A tuple representing the winning order ranking of the canditates.
		"""
		candScoresMap = dict()
		for place, cand in enumerate(ranking):
			candScoresMap[cand] = place

		return candScoresMap

	#=====================================================================================

	def tiebreakRankings(self, winningRankings):
		"""
		Returns a tuple that is the winning ranking.

		:ivar List winningRankings: A list of tuples that represent preference rankings.
		"""
		return winningRankings[0]

#=====================================================================================
#=====================================================================================









