import sys
import random
import itertools
import prefpy
from prefpy import preference
from prefpy import profile
from prefpy import io

from prefpy.profile import Profile
from prefpy.preference import Preference
from outputFormatting import *

#=====================================================================================

def main(argv):
	filename, numCands, numUniqueRankings, maxVotesPerRanking = handleInput(argv)
	
	candOptions = "0abcdefghijklmnopqrstuvwxyz"
	candMap = dict()
	for i in range(1, numCands+1):
		candMap[i] = candOptions[i]

	preferencesList = []

	allRankingOptions = []
	for ranking in itertools.permutations(candMap.keys()):
		allRankingOptions.append(ranking)

	for i in range(numUniqueRankings):
		rankNum = random.randint(0, len(allRankingOptions))
		ranking = allRankingOptions[rankNum]
		wmgMap = genWmgMapFromRankMap( convertRankingToRankMap(ranking) )

		voteCount = random.randint(0, maxVotesPerRanking)

		newPref = Preference(wmgMap,voteCount)
		preferencesList.append(newPref)

	generatedProfile = Profile(candMap, preferencesList)
	generatedProfile.exportPreflibFile(filename)
	print("Generated file '" + filename + "'")

#=====================================================================================

def handleInput(argv):
	if len(argv) >= 2:
		filename = argv[1].lower()
	else:
		filename = input("Enter name of file to generate: ").lower()
	if len(argv) >= 3:
		numCands = int(argv[2])
	else:
		numCands = int(input("Enter the number of candidates:  "))
	if len(argv) >= 4:
		numUniqueRankings = int(argv[3])
	else:
		numUniqueRankings = int(input("Enter the number of unique votes/rankings:  "))
	if len(argv) >= 5:
		maxVotesPerRanking = int(argv[4])
	else:
		maxVotesPerRanking = int(input("Enter the maximum number of votes for each ranking:  "))

	return filename, numCands, numUniqueRankings, maxVotesPerRanking

#=====================================================================================

def convertRankingToRankMap(ranking):
	rankMap = dict()
	for i, cand in enumerate(ranking):
		rankMap[cand] = i
	return rankMap

#=====================================================================================

def genWmgMapFromRankMap(rankMap):
	"""
	Converts a single rankMap into a weighted majorty graph (wmg). We return the wmg as a 
	two-dimensional dictionary that associates integer representations of each pair of candidates,
	cand1 and cand2, with the number of times cand1 is ranked above cand2 minus the number of times
	cand2 is ranked above cand1.

	:ivar dict<int,int> rankMap: Associates integer representations of each candidate with its
		ranking in a single vote.
	"""

	wmgMap = dict()
	for cand1, cand2 in itertools.combinations(rankMap.keys(), 2):

		# Check whether or not the candidates are already present in the dictionary.
		if cand1 not in wmgMap.keys():
			wmgMap[cand1] = dict()
		if cand2 not in wmgMap.keys():
			wmgMap[cand2] = dict()
			
		# Check which candidate is ranked above the other. Then assign 1 or -1 as appropriate.       
		if rankMap[cand1] < rankMap[cand2]:
			wmgMap[cand1][cand2] = 1
			wmgMap[cand2][cand1] = -1 
		elif rankMap[cand1] > rankMap[cand2]:
			wmgMap[cand1][cand2] = -1
			wmgMap[cand2][cand1] = 1

		# If the two candidates are tied, We make 0 the number of edges between them.
		elif rankMap[cand1] == rankMap[cand2]:
			wmgMap[cand1][cand2] = 0
			wmgMap[cand2][cand1] = 0

	return wmgMap

#=====================================================================================

if __name__ == '__main__':
	main(sys.argv)





