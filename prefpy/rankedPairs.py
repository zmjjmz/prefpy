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

def getTopRank(netxGraph):
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
			
	def getNextEdge(self, currentWinners):
	#function to progress through each 
		#list of graphs to branch to
		branchedGraphList = [] 
		branchedEdges, branchedRemEdges = self.findTies()
		#iterate through each branch of the graph
		for i in range(len(branchedEdges)):
			tmpGraph = self.DG.copy()
			tmpEdge = branchedEdges[i]
			#add the edge
			self.addOneWayEdge(tmpGraph, tmpEdge)
			#pruning check to see if we have already found the possible winners
			if not set(getTopRank(tmpGraph)).issubset(set(currentWinners)):
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

	def findTies(self):
	#function to find which edges are tied
		branchedRemEdges = [] #list of lists
		edges = self.remainingList 
		tmpList = [] #holds list of edges to branch out to
		tmpRemEdges = []
		if len(edges) > 0: #we know that we don't care about negative edge weights
			tmpWeight = edges[0][0]
			#loop through the list of edges
			for i in range(len(edges)):
				if edges[i][0] == tmpWeight: #we find tied edge that we want to use
					tmpRemEdges = copy.copy(edges) #deep copy edge list
					del tmpRemEdges[i] #remove tied edge from the remaining list
					branchedRemEdges.append(tmpRemEdges)
					tmpList.append(copy.copy(edges[i])) #add the edge we are using to the list of edges to extend G`
		return tmpList, branchedRemEdges
	

class RankedPairs(Mechanism):
	def __init__(self):
		pass
	#returns a list of tuples(weight,label,label)
	def createNXGraph(self,edgeList):
		DG = nx.DiGraph()
		for edge in edgeList:
			DG.add_edge(edge[1], edge[2], weight=edge[0])
		#nx.draw(DG)
		#stuff for drawing the graph
		nodeLayout=nx.spring_layout(DG)
		nx.draw_networkx(DG,pos=nodeLayout,arrows=True)
		labels = nx.get_edge_attributes(DG, 'weight')
		nx.draw_networkx_edge_labels(DG, pos=nodeLayout, edge_labels=labels)
		plt.show()
		
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
		
		
	def getNewGraph(self,prof):
		#function to get the wmg and netx graph from the profile for the getOneWinner function
		wmg=prof.getWmg()
		DG=nx.DiGraph()
		newGraph=nx.DiGraph()
		edges=[]
		#initialize new graph to all zero edges
		edges=self.getSortedEdges(prof)
		for edge in edges:
			if edge[0]<0:
				break
			DG.add_edge(edge[1], edge[2], weight=edge[0])
			try:
				#if there is no cycle the method throws an exception
				nx.find_cycle(DG)
				DG.remove_edge(edge[1], edge[2])
				break
				# every edge is initialized to 0
				# may have to delete edge instead
			except:
				pass
		return DG

	def getOneWinner(self,prof):
	#function to get one winner
		newGraph=self.getNewGraph(prof)
		numCanidates=newGraph.number_of_nodes()
		winners = []
		for i in newGraph.nodes():
			inedges = newGraph.in_edges(i)
			if inedges == []:
				winners.append(i)
		return winners

	def getWinnerWithTieBreakingMech(self,prof,prefList):
		pass
		
	def getTopRank(self, graphList):
	#function to get the winners from the donelist
		topRanks = []
		for bGraph in graphList:
			newGraph = bGraph.DG
			for i in newGraph.nodes():
				#check if the node has any in-edges
				inedges = newGraph.in_edges(i)
				#if it has no in-edges, then we know that it is a winner
				if inedges == []:
					topRanks.append(i)
		return topRanks
		
	def initDG(self, edges):
	#function to intialize the directed graph
		nodeSet=set()
		DG = nx.DiGraph()
		for i in range(len(edges)):
			nodeSet.add(edges[i][1])
		DG.add_nodes_from(nodeSet)
		return DG

	def getWinners(self, prof=None, edges=None):
	#primary method to calculate multiple winners
		if edges is None:
			edges = self.getSortedEdges(prof)
		else:
			edges = sorted(edges, key=lambda weight: weight[0], reverse = True)
		print(edges)
		#DG = nx.DiGraph()
		
		#edges = self.getSortEdges(prof) #create the array of edges
		DG=self.initDG(edges)#get the networkx Directed Graph from the set of edges

		winners = [] #list to hold the winners
		doneList = [] #list of the graphs that have been completed
		newBranchedGraph = branchedGraph(edges, DG) #create the first branched graph
		graphs = newBranchedGraph.getNextEdge(winners) #try to get the next edge from the new branched graph
		while(len(graphs) != 0):
		#Iterating through graphs, appending to tmp graphs list such that we arent modifying the list we are iterating over
			tmpGraphs = []
			graph=graphs.pop(0) #we've finished looking at this graph
			tmpNextEdgeList = graph.getNextEdge(winners) #look at the next edge of the graph
			if tmpNextEdgeList == [] and graph.isDone(): #we know that the graph is complete if it satisfies these conditions
				doneList.append(graph)
				winners += self.getTopRank(doneList) #add the nodes returned by the getTopRank call
			else:
				graphs=tmpNextEdgeList+graphs
		print(len(doneList)) #debug statement to see how many graphs needed to be computed
		#loop to output each completed graph
		for winner in doneList:
			self.drawGraph(winner.DG)
		plt.show()
		
		return set(winners)


	def getRanking(self, prof):
		pass





