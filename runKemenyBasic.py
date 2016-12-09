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

	# individual winner
	kemWinners = kemenyMech.getWinners(data)
	kemWinnersNames = convertCandIntsToNames(kemWinners, data.candMap)

	# winning ranking(s)
	kemWinRanksBase = kemenyMech.winningRanking
	kemWinRanksNames = convertCandIntsToNames(kemWinRanksBase, data.candMap)

	# winning ranking(s) formatted as strings in the form "a > b > c"
	kemWinRankStrs = []
	for ranking in kemWinRanksNames:
		kemWinRankStrs.append( getRankingString(ranking) )

	winnerPrint = "W* = {ranking},  winner(s) = {w}"
	print( winnerPrint.format(ranking=kemWinRankStrs, w=kemWinnersNames) )

#=====================================================================================

if __name__ == '__main__':
	main(sys.argv)


