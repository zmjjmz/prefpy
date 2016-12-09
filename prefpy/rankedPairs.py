'''
Authors: Bilal Salam, Levin Huang, Lucky Cho
'''
import io
import math
import itertools
from prefpy.profile import Profile
from prefpy.preference import Preference
from prefpy.mechanism import Mechanism
import networkx as nx
import matplotlib.pyplot as plt
import copy

def getWinningNodes(netxGraph):
	#function to find the winning nodes given a networkx graph
	topRanks = []
	for i in netxGraph.nodes():
		if netxGraph.in_edges(i) == []:
			topRanks.append(i)
	return topRanks

class branchedGraph():
	def __init__(self, rL, DG):
		self.remainingList = rL
		self.DG = DG
		
	def isDone(self):
	#function to check if the graph is done
		if len(self.remainingList) ==0:
			return True
		else:
			return False
	
	#currentWinners - list of string names of known winners
	#edgePrefList - [(node1, node2), (node2, node3)] list of edges sorted in decreasing order of preference, each tuple is an edge 
	def getNextEdge(self, currentWinners, edgePrefList = None):
	#function to progress through each 
		#list of graphs to branch to
		branchedGraphList = [] 
		branchedEdges, branchedRemEdges = self.findTies(edgePrefList)
		#iterate through each branch of the graph
		for i in range(len(branchedEdges)):
			tmpGraph = self.DG.copy()
			tmpEdge = branchedEdges[i]
			#add the edge
			self.addOneWayEdge(tmpGraph, tmpEdge)
			#pruning check to see if we have already found the possible winners
			if not set(getWinningNodes(tmpGraph)).issubset(set(currentWinners)):
				tmpBranchedGraph = branchedGraph(branchedRemEdges[i], tmpGraph)
				#add a new branched graph to the branchedGraphList
				branchedGraphList.append( tmpBranchedGraph)
		return branchedGraphList
		
	def addOneWayEdge(self, graph, edge):
	#function to check whether or not we want to add the edge in the case of the graph already having an opposite edge
		if not graph.has_edge(edge[2], edge[1]):
			graph.add_edge(edge[1], edge[2], weight=edge[0])
			try:
				nx.find_cycle(graph)
				graph.remove_edge(edge[1], edge[2])
			except:
				pass

	#edgePrefList - [(node1, node2), (node2, node3)] list of edges sorted in decreasing order of preference, each tuple is an edge 
	def findTies(self, edgePrefList = None):
	#function to find which edges are tied
		branchedRemEdges = [] #list of lists
		edges = self.remainingList 
		tmpList = [] #holds list of tied edges to branch out to
		tmpRemEdges = []
		
		if len(edges) > 0: #we know that we don't care about negative edge weights
			tmpWeight = edges[0][0]
			#loop through the list of edges
			for i in range(len(edges)):
				if edges[i][0] == tmpWeight: #we find tied edge that we want to use
					tmpList.append(copy.copy(edges[i])) #add the edge we are using to the list of edges to extend G`
		if edgePrefList is not None:
			if len(tmpList) > 0:
				tmpList = self.getBestEdge(tmpList, edgePrefList)
		for i in range(len(edges)):
			tmpRemEdges = copy.copy(edges) #deep copy edge list
			del tmpRemEdges[i] #remove tied edge from the remaining list
			branchedRemEdges.append(tmpRemEdges)
		return tmpList, branchedRemEdges
	
	def getBestEdge(self, edgeList, edgePrefList):
		bestIndex = None
		edgeListIndex = 0
		for i in range(0, len(edgeList)):
			edge = edgeList[i]
			try:
				tmpBestIndex = edgePrefList.index((edge[1], edge[2]))
				if bestIndex is None or bestIndex > tmpBestIndex:
					bestIndex = tmpBestIndex
					edgeListIndex = i
			except ValueError:
				print('edge does not exist in preference list, user did not give preference over all edges')
		return [edgeList[edgeListIndex]]
				
			
	
	

class RankedPairs(Mechanism):
#Calculates winners using the RankedPairs voting mechanism

	#returns edges from the wmg sorted by weights
	def getSortedEdges(self,prof):
		#initialize the wmg from the given profile
		wmg = prof.getWmg()
		# empty array to hold the edges
		edges = []
		#add edges to the array
		for cand1 in prof.candMap.keys():
			for cand2 in prof.candMap.keys():
				if cand1 is not cand2:
					edges.append((wmg[cand1][cand2], prof.candMap[cand1], prof.candMap[cand2]))
		#sort the edges
		edges = sorted(edges, key=lambda weight: weight[0], reverse = True) 
		return edges
		
	def drawGraph(self, DG):
		#function to draw the given networkx graph.
		plt.figure()
		nodeLayout=nx.spring_layout(DG)
		nx.draw_networkx(DG,pos=nodeLayout,arrows=True)
		labels = nx.get_edge_attributes(DG, 'weight')
		nx.draw_networkx_edge_labels(DG, pos=nodeLayout, edge_labels=labels)
		#plt.show()

	def getOneWinner(self, prof = None, edgePrefList = None):
	#function to get one winner
		edges = self.getSortedEdges(prof)
		DG=self.initDG(edges)#get the networkx Directed Graph from the set of edges
		winners = [] #list to hold the winners
		doneList = [] #list of the graphs that have been completed
		newBranchedGraph = branchedGraph(edges, DG) #create the first branched graph
		graphs = newBranchedGraph.getNextEdge(winners, edgePrefList) #try to get the next edge from the new branched graph
		
		while(len(graphs) != 0):
		#Iterating through graphs, appending to tmp graphs list such that we arent modifying the list we are iterating over
			tmpGraphs = []
			graphs = graphs[0:1]
			graph=graphs.pop(0) #we've finished looking at this graph
			tmpNextEdgeList = graph.getNextEdge(winners, edgePrefList) #look at the next edge of the graph
			if tmpNextEdgeList == [] and graph.isDone(): #we know that the graph is complete if it satisfies these conditions
				doneList.append(graph)
				winners += getWinningNodes(graph.DG) #add the nodes returned by the getWinningNodes call
			else:
				graphs=tmpNextEdgeList+graphs
		print(len(doneList)) #debug statement to see how many graphs needed to be computed
		#loop to output each completed graph
		for winner in doneList:
			self.drawGraph(winner.DG)
		plt.show()
		return set(winners)
		
	def initDG(self, edges):
	#function to intialize the directed graph
		nodeSet=set()
		DG = nx.DiGraph()
		for i in range(len(edges)):
			nodeSet.add(edges[i][1])
		DG.add_nodes_from(nodeSet)
		return DG


	def getRanking(self, profile):

		raise NotImplementedError

	def getWinners(self, prof=None, edgePrefList=None):
		"""
		prof Profile
		edgePrefList- list of tuples representing a preference over wmg edges
		primary method to calculate multiple winners
		returns the set of winning nodes and then the linear orders justifying each
	    winner in the form of networkx objects

		"""

		edges = self.getSortedEdges(prof)
		
		DG=self.initDG(edges)#get the networkx Directed Graph from the set of edges
		winners = [] #list to hold the winners
		doneList = [] #list of the graphs that have been completed
		newBranchedGraph = branchedGraph(edges, DG) #create the first branched graph
		graphs = newBranchedGraph.getNextEdge(winners, edgePrefList) #try to get the next edge from the new branched graph
		
		while(len(graphs) != 0):
		#Iterating through graphs, appending to tmp graphs list such that we arent modifying the list we are iterating over
			tmpGraphs = []
			graph=graphs.pop(0) #we've finished looking at this graph
			tmpNextEdgeList = graph.getNextEdge(winners, edgePrefList) #look at the next edge of the graph
			if tmpNextEdgeList == [] and graph.isDone(): #we know that the graph is complete if it satisfies these conditions
				doneList.append(graph)
				winners += getWinningNodes(graph.DG) #add the nodes returned by the getWinningNodes call
			else:
				graphs=tmpNextEdgeList+graphs
		#print(len(doneList)) #debug statement to see how many graphs needed to be computed
		'''
		#loop to output each completed graph
		for winner in doneList:
			self.drawGraph(winner.DG)
		plt.show()'''
		
		return set(winners), [graph.DG for graph in doneList]
		#returns the set of winning nodes and then the linear orders justifying each winner in the form of networkx objects
		#uncomment the above loop for a visual representation





