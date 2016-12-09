import sys
import prefpy
from prefpy import preference
from prefpy import profile
from prefpy import io

from prefpy.kemeny import MechanismKemeny
from prefpy.profile import Profile
from prefpy.preference import Preference
from outputFormatting import *

#=====================================================================================

def main(argv):
	if len(argv) > 1:
		filename = argv[1]
	else:
		filename = input("Enter name of election data file:   ").lower()

	data = Profile({},[])
	data.importPreflibFile(filename)
	print("Imported file '" + filename + "'")
	
	# print("Candidates: ", data.candMap)
	# print("WMG: ", getDictString(data.getWmg()), "\n")
	
	kemenyMech = MechanismKemeny()
	# print("Created KemenyMechanism obj")

	kemWinners = kemenyMech.getWinners(data)
	kemWinnersNames = convertCandIntsToNames(kemWinners, data.candMap)

	kemWinRanksBase = kemenyMech.winningRankings
	kemWinRanksNames = convertCandIntsToNames(kemWinRanksBase, data.candMap)

	kemWinRankStrs = []
	for ranking in kemWinRanksNames:
		kemWinRankStrs.append( getRankingString(ranking) )
	winnerPrint = "W* = {ranking},  winner(s) = {w}"
	print( winnerPrint.format(ranking=kemWinRankStrs, w=kemWinnersNames) )

	candScoresMap = kemenyMech.getCandScoresMap(data)
	print("candScores: ", candScoresMap)
	# sortedData = sorted(candScoresMap.items(), key=lambda tup: tup[1])
	# print("sortedData: ", sortedData)
	sortedData2 = sorted(candScoresMap, key=candScoresMap.get)
	print("sortedData2: ", sortedData2)
	# winningRanking = []
	# for i in range(len(sortedData)):
	# 	winningRanking.append(sortedData[i][0])
	# print("winningRanking: ", winningRanking)

	varList = [('a', -0.0),('b', 1.0),  ('a', -0.0),('c', 1.0),  ('a', 1.0),('d', 0.0),  ('b', -0.0),('c', 1.0),  ('b', 1.0),('d', 0.0),  ('c', 1.0),('d', 0.0)]

	candScoresMap2 = dict()
	for v,x in varList:
		if(v in candScoresMap2.keys()):
			candScoresMap2[v] += x
		else:
			candScoresMap2[v] = x

	print("candScores2: ", candScoresMap2)

	sortedData3 = sorted(candScoresMap2, key=candScoresMap2.get, reverse=True)
	print("sortedData3: ", sortedData3)

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
	main(sys.argv)


