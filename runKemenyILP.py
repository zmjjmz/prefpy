import sys
import prefpy
from prefpy import preference
from prefpy import profile
from prefpy import io

from prefpy.kemenyILP import MechanismKemenyILP
from prefpy.profile import Profile
from prefpy.preference import Preference
from outputFormatting import *

#=====================================================================================

def main(argv):
	if len(argv) == 1:
		filename = input("Enter name of election data file:   ").lower()
		solveFile(filename)
	else:
		for i in range(1, len(argv)):
			print("============================{}============================".format(argv[i]))
			solveFile(argv[i])
			print("------------------------end of {}------------------------\n".format(argv[i]))

#=====================================================================================

def solveFile(filename):
	data = Profile({},[])
	data.importPreflibFile(filename)
	print("Imported file '" + filename + "'")
	
	print("Candidates: ", data.candMap)
	print("WMG: ", getDictString(data.getWmg()), "\n")

	kemenyMech = MechanismKemenyILP()
	print("Created KemenyMechanismILP obj")

	kemWinners = kemenyMech.getWinners(data)
	print("Calculated ILP Winner(s)")
	
	# print precedence matrix
	print("Precedence matrix: ", kemenyMech.precMtx)

	# print variables
	print("Optimized Binary Variables: ")
	for v in kemenyMech.gModel.getVars():
		print(v.varName, v.x)

	print('Obj: ', kemenyMech.gModel.objVal)

	# individual winner
	kemWinners = kemenyMech.getWinners(data)
	kemWinnersNames = convertCandIntsToNames(kemWinners, data.candMap)

	# winning ranking(s)
	kemWinRanksBase = kemenyMech.winningRankings
	kemWinRanksNames = convertCandIntsToNames(kemWinRanksBase, data.candMap)

	# winning ranking(s) formatted as strings in the form "a > b > c"
	kemWinRankStrs = []
	for ranking in kemWinRanksNames:
		kemWinRankStrs.append( getRankingString(ranking) )

	winnerPrint = "W* = {ranking}\nWinner(s) = {w}"
	print( winnerPrint.format(ranking=kemWinRankStrs, w=kemWinnersNames) )

#=====================================================================================

def testVarSumScoreAndSortRanking():
	varList = [('a', -0.0),('b', 1.0),  ('a', -0.0),('c', 1.0),  ('a', 1.0),('d', 0.0),  ('b', -0.0),('c', 1.0),  ('b', 1.0),('d', 0.0),  ('c', 1.0),('d', 0.0)]
	candMap = [(1,"a"), (2,"b"), (3,"c"), (4,"d")]

	# sum binary variables
	candScoresMap = dict()
	for v,x in varList:
		if(v in candScoresMap.keys()):
			candScoresMap[v] += x
		else:
			candScoresMap[v] = x
	print("candScoresMap: ", candScoresMap)

	# sort solution scores to get ranking
	sortedDataWithScores = sorted(candScoresMap.items(), key=lambda tup: tup[1], reverse=True)
	print("sortedDataWithScores: ", sortedDataWithScores)

	sortedDataRanking = sorted(candScoresMap, key=candScoresMap.get, reverse=True)
	print("sortedDataRanking: ", sortedDataRanking)

	print("Winning Ranking: ", getRankingString(sortedDataRanking))

#=====================================================================================

if __name__ == '__main__':
	main(sys.argv)


