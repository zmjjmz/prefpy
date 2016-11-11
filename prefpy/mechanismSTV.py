import math
import io
from preference import Preference
from profile import Profile
'''
if __name__ == "__main__":


	#profile is not defined?
	p = Profile()


	# need to make filename first
	#the designed file name is pretty confusing based on the read_election_file function

	# Preflib Election Data Format

	p.importPreflibFile("Basic Text Document.txt")
	mP = MechanismPlurality()
	scoreVect = mP.getScoringVector(p)
'''

class MechanismSTV(Mechanism):
	"""
	Goal is to return the winner of STV Voting (plurality each round, where loser
	drops out every round until there is a winner).
	Inherits from the general scoring mechanism (can change to positional if that
	works better).

	TODO:
	- STV with no tiebreaker
	- STV with ties broken alphabetically
	- STV with all alternatives returned
	- Ensure voting is valid (no partial orders)

	A few questions for the future:
	- Should the final result rank whoever dropped first as the last place?
	- Curious about line 97 in Mechanism.py:
		if elecType != "soc" and elecType != "toc":
            return False

		Is this correct? It seems like there should be an 'or'
	"""

	#def __init__(self):
		# add something here...



	# override getWinners eventually...
	# def getWinners(self, profile):

	# and possibly getRanking...
	# def getRanking(self, profile)

	def computeRoundLoser(self, profile, droppedOut):
		"""
		Computes who should drop out on a round

		profile - voting profile given
		droppedOut - list of candidates who have already dropped out
		"""

		rankMaps = []
		counts = [] #could use getPreferenceCounts
		for preference in profile.preferences:
			ranksMaps.append(preference.getReverseRankMap())
			counts.append(preferences.count)

		if (len(rankMaps) != len(counts)):
			print("something is wrong")

		totals = dict()
		for rank in rankMaps:
			for i in range(1, len(rank)):
				if (rank[i] not in droppedOut):
					if (rank[i] in totals):
						totals[rank[i]] += counts[i]
					else:
						totals[rank[i]] = counts[i]
					break

		minVotes = min(totals.values())
		losers = [key for key, value in totals.iteritems() if value == minVotes]
		#tiebreaker needs to be added here so this returns a single value each time
		return losers

	def STVWinner(self, profile):
		"""
		Computes the winner(s) for STV voting

		Returns a set of candidates in the original list of candidates minus the losers
		"""
		i =0
		losers=[]
		while (i < profile.numCands-1):
			losers.extend(computeRoundLoser(profile, losers)) #use append for single value, extend for a list
			i++
		
		cands = profile.preferences[0].getRankMap().keys()
		return set(keys) - set(losers)