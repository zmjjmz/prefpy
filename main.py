import prefpy
from prefpy import preference
from prefpy import profile

from prefpy.rankedPairs import RankedPairs
from prefpy.profile import Profile

if __name__ == '__main__' :

	data=Profile({},[])

	#data.importPreflibFile("4candpartialorder.txt")
	data.importPreflibFile("input1.txt")
	
	rankpairMech=RankedPairs()
	myList = [(4, 'a', 'b'), (3, 'b', 'c'), (3, 'c', 'd'), (2, 'd', 'b'), (2, 'c', 'a'), (4, 'd', 'a')]
	myEdgePrefList = [('a', 'b'), ('a', 'c'), ('b', 'c'), ('c', 'b'), ('b', 'a'), ('c', 'a'), ]
	#print(rankpairMech.getWinners(edges = myList))
	#print(rankpairMech.getWinners(prof = data, edgePrefList = myEdgePrefList))
	print(rankpairMech.getWinners(prof = data))
	#print(rankpairMech.getOneWinner(prof = data))