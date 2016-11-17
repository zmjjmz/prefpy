import math
import io
from mechanism import Mechanism
from preference import Preference
from profile import Profile

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

		Is this correct? It seems like there should be an 'or'
	"""

	def __init__(self):
		empty_list = []
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

		if(len(droppedOut) == len(profile.candMap) -1 ):
			return 

		rankMaps = []
		counts = [] #could use getPreferenceCounts
		for preference in profile.preferences:
			rankMaps.append(preference.getReverseRankMap())
			counts.append(preference.count)

		if (len(rankMaps) != len(counts)):
			print("something is wrong")

		totals = dict()
		for rank in rankMaps:
            #  Ranks are listed starting from 1
			for i in range(1, len(rank) + 1):
				# print rank[i][0]
				# new_rank = rank[i]
				if (rank[i][0] not in droppedOut):
					# print totals
					# print counts[i]
					# print totals[rank[i][0]], counts[i]
					new_rank = rank[i][0]
					if (rank[i][0] in totals):
						totals[rank[i][0]] += counts[i]
					else:
						totals[rank[i][0]] = counts[i]
					break

		minVotes = min(totals.values())
		
		#tiebreaker needs to be added here so this returns a single value each time
		count = 0
		
		#how to implement tiebreaker
		# if any value matches the minVotes then run another iteration with the option removed.
		# print out that value.
		for key, value in totals.iteritems():

			if value == minVotes:
				losers = [key for key, value in totals.iteritems() if value == minVotes]
				print losers  # in this print, i was printing out key and value... value seemed good 
				# however key seemed incorrect.
				droppedOut.extend(losers)
				losers = self.computeRoundLoser(profile, droppedOut)
				
				#return droppedOut

		return droppedOut	
		#return
		#return losers

	def STVWinner(self, profile):
		"""
		Computes the winner(s) for STV voting

		Returns a set of candidates in the original list of candidates minus the losers
		"""
		i =0
		losers=[]



		#while (i < profile.numCands-1):
		#losers.extend(self.computeRoundLoser(profile, losers)) #use append for single value, extend for a list
		#	i += 1


		losers = self.computeRoundLoser(profile, losers)
		cands = profile.preferences[0].getRankMap().keys()
		return set(cands) - set(losers)



if __name__ == "__main__":

	candMap = dict()
	preferences = []
	p = Profile(candMap, preferences)

	p.importPreflibFile('ED-00001-00000001.toc')

	m = MechanismSTV()

	print m.STVWinner(p)
