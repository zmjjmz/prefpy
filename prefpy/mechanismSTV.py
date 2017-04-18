import math
import io
import sys
from mechanism import Mechanism
from preference import Preference
from profile import Profile

class MechanismSTV(Mechanism):
	"""
	Goal is to return the winner of STV Voting (plurality each round, where loser
	drops out every round until there is a winner).
	Inherits from the general scoring mechanism.

	TODO:
	- Ensure voting is valid (no partial orders)
	- Test results
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
			# check = preference.getReverseRankMap()
			# print(check)
			rankMaps.append(preference.getReverseRankMap())
			counts.append(preference.count)

		if (len(rankMaps) != len(counts)):
			print("something is wrong")
			
		totals = dict()
		flag = 0
		for k in range(len(rankMaps)):
			flag = 0
            #  Ranks are listed starting from 1
			rank = rankMaps[k]
			# print (rank)
			for i in range(1, len(rank) + 1):
				# print rank[i][0]
				# new_rank = rank[i]
				for j in range(0, len(rank[i])):
					if (rank[i][j] not in droppedOut):
						# print totals
						# print counts[i]
						# print totals[rank[i][j]], counts[i]
						new_rank = rank[i][j]
						if (rank[i][j] in totals):
							totals[rank[i][j]] += counts[k]
						else:
							totals[rank[i][j]] = counts[k]
						flag = 1
						# print (k)
						# print ("rank[i][j]",rank[i][j]," total:", totals[rank[i][j]])
				if (flag == 1):
					break

					
					
		#	NEED TO EXCLUDE KEYS WHO HAVE BEEN DROPPED			
		
		voteTotals = totals.values()
		minVotes = sys.maxsize
		for i in range (0, len(voteTotals)):
			print (voteTotals[i])
			if (voteTotals[i] < minVotes):
				minVotes = voteTotals[i]

		losers = [key for key, value in totals.iteritems() if value == minVotes]
		print(losers)
		return losers

	def STVWinner(self, profile):
		"""
		Computes the winners (and losers) for STV voting

		Returns a list of lists of all candidates in winning order:
			[[winner, 2nd winner, ... , loser], [winner, 2nd winner, ... , loser] ... ]
		"""
		#create 2-D list of losers and dropouts for possibility of ties
		losers = [[]]
		dropouts = [[]]

		for i in range(profile.numCands - 1):
			j=0
			while j <len(losers):
				dropouts[j] = self.computeRoundLoser(profile, losers[j])
				# print ("Losers:", losers);
				# print ("Dropouts:",dropouts)
				print
				if (dropouts[j]):
					losers[j].append(dropouts[j][0])
					for k in range(1, len(dropouts[j])):
						# print ("j:",j);
						losers.append(list(losers[j]))
						losers[-1].pop() 						#we want this so we only add one element at a time to losers
						losers[-1].append(dropouts[j][k])
						dropouts.append([])
				# dropouts[j] = []
				j+=1

		# Now we should have a list of lists called 'losers' which contains all losers for different tiebreaks

		cands = profile.preferences[0].getRankMap().keys()
		for loser in losers:
			winner = set(cands) - set(loser)
			loser.append(list(winner)[0])
			loser.reverse()

		#returns a list of lists with full rankings of candidates in STV
		return losers

if __name__ == "__main__":

	candMap = dict()
	preferences = []
	p = Profile(candMap, preferences)

	p.importPreflibFile('ED-00018-00000004.toc')

	m = MechanismSTV()

	print (m.STVWinner(p))
