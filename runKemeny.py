import prefpy
from prefpy import preference
from prefpy import profile
from prefpy import io

from prefpy.kemeny import MechanismKemeny
from prefpy.profile import Profile
from prefpy.preference import Preference

#=====================================================================================

def main():
	data = Profile({},[])

	data.importPreflibFile("input0")

	kemenyMech = MechanismKemeny()

	# myList = [(4, 'a', 'b'), (3, 'b', 'c'), (3, 'c', 'd'), (2, 'd', 'b'), (2, 'c', 'a'), (4, 'd', 'a')]
	# #print(rankpairMech.getWinners(edges = myList))
	# print(rankpairMech.getWinners(prof = data))
    # print(rankpairMech.getOneWinner(data))
    # edgeList=rankpairMech.getSortedEdges(data)
    # rankpairMech.createNXGraph(edgeList)



#=====================================================================================

if __name__ == '__main__':
	main()


