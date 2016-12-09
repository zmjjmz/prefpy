import sys
import prefpy
from prefpy import preference
from prefpy import profile
from prefpy import io
from prefpy import kemenyILP

from prefpy.kemeny import MechanismKemeny
from prefpy.kemenyILP import MechanismKemenyILP
from prefpy.profile import Profile
from prefpy.preference import Preference

#=====================================================================================

def main():

	data = Profile({},[])

	# filename = "input1"
	filename = input("Enter name of election data file:   ").lower()
	data.importPreflibFile(filename)
	print("Imported file")

	kemenyMechILP = MechanismKemenyILP()
	print("Created KemenyMechanismILP obj")

	kemWinner1 = kemenyMechILP.getWinners(data)
	print("Calculated ILP Winner(s)")
	
	# print(precedence)
	# for v in m.getVars():
	# 	print(v.varName, v.x)
	# print('Obj:', m.objVal)
	
	kemWinRank1 = kemenyMechILP.getWinningRankings()
	print("W* = " + str(kemWinRank1) + ",  winner = " + str(kemWinner1))

	
	
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
	main()


