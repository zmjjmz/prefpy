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
	
	print("Candidates: ", data.candMap)
	print("WMG: ", getDictString(data.getWmg()), "\n")
	
	kemenyMech = MechanismKemeny()
	# print("Created KemenyMechanism obj")

	kemWinners = kemenyMech.getWinners(data)
	kemWinnersNames = convertCandIntsToNames(kemWinners, data.candMap)

	kemWinRanksBase = kemenyMech.getWinningRankings()
	kemWinRanksNames = convertCandIntsToNames(kemWinRanksBase, data.candMap)

	kemWinRankStrs = []
	for ranking in kemWinRanksNames:
		kemWinRankStrs.append( getRankingString(ranking) )
	winnerPrint = "W* = {ranking},  winner(s) = {w}"
	print( winnerPrint.format(ranking=kemWinRankStrs, w=kemWinnersNames) )

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


