"""
Project: Multi-Winner Voting Algorithms
File:    MultiWinner.py
Authors: Nick Sirano, Parker Hamren
Date:    12/11/2016

Description:
    Multi-Winner approximation algorithms as described in 'Achieving fully
    proportional representation: Approximability results.'

Source:
    P. Skowron, P. Faliszewski, A. Slinko, 'Achieving fully proportional
    representation: Approximability results', Artificial Intelligence, Vol.222,
    Pages 67-103
"""

import copy
import math
import operator
import sys

from scipy.special import lambertw
from preference import Preference

def usage():
    """
    Prints usage information.
    """
    print("Usage: python MultiWinner.py <data.txt> <comm_size>")

def check_arguments():
    """
    Checks to see if enough arguments are passed to MultiWinner.py.
    """
    if len(sys.argv) < 2:
        print("ERROR: Not enough arguments.")
        usage()
        sys.exit(1)

def sign(n):
    """
    Checks the sign of a number 'n'.
    Returns  1 if positive.
    Returns -1 if negative.
    """
    return int(n > 0) - int(n < 0)

def create_wmgMap(ranking):
    """
    Create a weighted majority graph mapping from a voter's preference rankings.
    Each wmgMap is a dictionary of candidates that each maps to another
    dictionary of candidates, excluding the first candidate. The second
    dictionary then maps to '1' if the first candidate is ranked higher than the
    second and maps to '-1' if the first candidate is ranked lower.
    Returns wmgMap.

    Input:
        ranking - 1 dimensional list of preferences
    """
    wmgMap = dict()
    alternatives = sorted(ranking)

    # For each alternative as the first candidate,
    for a in alternatives:
        wmgMap[a] = dict()

        # For each alternative that is not the first candidate
        for alt in alternatives:
            if alt != a:
                alt_index = ranking.index(alt)
                a_index   = ranking.index(a)
                wmgMap[a][alt] = sign(alt_index - a_index)

    return wmgMap

def parse_data(filename, agents=[], alternatives=[]):
    """
    Parses voter data from input file.
    """
    f = open(sys.argv[1], "r")
    for line in f:
        ranking = line.rstrip().split(',')
        if len(ranking) > len(alternatives):
            alternatives = sorted(ranking)

        wmgMap = create_wmgMap(ranking)
        agents.append(Preference(wmgMap))

    return agents, alternatives

def borda(alternative, ranking):
    """
    Returns the borda score of an alternative in a given ranking defined as a
    two-dimensional list of alternatives.

    Input:
        alternative - string
        ranking     - 2-dimensional list of strings

    Output:
        integer
    """
    for tier in range(len(ranking)):
        if alternative in ranking[tier]:
            return len(ranking) - tier

    return 0

def getTopKAlt(alts, agents, K):
    """
    Function that returns the id of one of the candidate alternative that appears in the
    top K positions of the provided agent's rankings

    Input:
        alts   - list of strings ([str])
        agents - list of PrefPy Preference Objects ([Preference])
        K      - integer

    Output:
        string
    """
    # Default topKAlt is the first alternative in the list, but has a topKScore of 0
    #  until it is actually computed
    topKAlt = alts[0]
    topKAltScore = 0
    tmpScore = 0

    # Loop through alternatives, incrementing the score for every agent that
    #  ranks them in one of the top K positions
    for alt in alts:
        for ag in agents:
            if (ag.getRankMap()[alt] <= K):
                tmpScore += 1
        if (tmpScore > topKAltScore):
            topKAlt = alt
            topKAltScore = tmpScore
        tmpScore = 0

    # Returns the agent with the greatest topKScore (or one of them in case of a tie)
    return topKAlt

class SingleAssignment:
    """
    Object that pairs the preference ranking of a voting agent with a candidate
    alternative's identifier, the default of which is '<none>'.

    Attributes:
        self.pref - PrefPy Preference Object
        self.alt  - string
    """

    def __init__(self, prefObj, altID="<none>"):
        self.pref = prefObj
        self.alt = altID

    # Function that returns the satisfaction score of the agent
    #  with their assigned alternative. Default scoring method
    #  is Borda.
    def getSatScore(self, scoreType="borda"):
        scoreType = scoreType.lower()

        if (scoreType == "borda"):
            return borda(self.alt, self.pref.getOrderVector())

        else:
            print("Error: unknown scoring method.")
            sys.exit(1)

class FullAssignment:
    """
    Object that pairs a list of SingleAssignments with a list of unmatched alternatives.
    Initially, all alternatives will be unmatched, however, and any matched alternatives
    should appear in the SingleAssignment list with the preference(s) they are matched with.

    Attributes:
        self.assignments = list of SingleAssignment Objects ([SingleAssignment])
        self.unmatchedAlts = list of strings ([str])
    """

    def __init__(self, assignmentObjList=[], unmatchedAltList=[]):
        self.assignments = assignmentObjList
        self.unmatchedAlts = unmatchedAltList

    # Function that returns the total satisfaction score of all
    #  assignments contained within. Default scoring method is Borda.
    def getSatScore(self, scoreType="borda"):
        scoreType = scoreType.lower()

        if (scoreType == "borda"):
            totalScore = 0
            for a in self.assignments:
                totalScore += a.getSatScore(scoreType)
            return totalScore

        else:
            print("Error: Unknown scoring method.")
            sys.exit(1)

# Approximation Algorithms
def algoA_M(comm_size, alts, agents):
    """
    Algorithm A as described on pages 76-77 of 'Achieving fully proportional
    representation: Approximability results' for the Monroe approximation
    algorithm.

    The solution is built iteratively. In each step, we pick some
    not-yet-assigned alternative 'a' and assign it to those agents that are not
    assigned to any other alternative yet, and whose satisfaction of being
    matched with 'a' is maximal. Satisfiabiltiy is based on the Borda score of
    each alternative for each agent.

    Input:
        comm_size - integer
        alts      - list of strings ([str])
        agents    - list of PrefPy Preference Objects ([Preference])
        d         - integer

    Output:
        phi - list of strings

    """
    num_assigned = len(agents)/comm_size

    alts_left = alts

    current_agents = [a.getOrderVector() for a in agents]

    phi = list()

    # For each committee member
    for i in range(1, comm_size + 1):
        score = dict()
        bests = dict()

        # For each alternative in each rank,
        alt_bests = []
        for alt in alts_left:
            def flat_rank(alt, order_vector):
                """
                Compresses ranking into 1-dimensional vector and returns the
                index of the alternative in the new vector.
                """
                yield (a for a in tier for tier in order_vector).index(alt)

            # Sort the agents by ranking of given alt, most preferred first
            agents_left = list(sorted(current_agents,
                                      key=lambda agent:
                                        flat_rank(alt, agent)))

            # Add the first n/K agents to the best fit for the given alternative
            alt_bests = []
            for n in range(int(num_assigned)):
                if agents_left:
                    alt_bests.append(agents_left.pop(0))

            bests[alt] = list(alt_bests)

            # For each alternative relative to each agent,
            score[alt] = 0
            for j in alt_bests:
                # Add the borda score
                score[alt] += borda(alt, j)

        best_alt = max(score.iteritems(), key=operator.itemgetter(1))[0]
        for j in bests[best_alt]:
            if best_alt not in phi:
                phi.append(best_alt)

            current_agents.remove(j)

        alts_left.remove(best_alt)

    return phi

def algoC_CC(comm_size, alts, agents, d):
    """
    Approximation algorithm for Chamberlin-Courant multi-winner elections, as described
    under Algorithm C (Chamberlin-Courant) in the paper 'Achieving fully proportional
    representation: Approximability results' by Piotr Skowron, Piotr Faliszewski, Arkadii Slinko.
    This algorithm takes in a desired committee size (comm_size), a list of candidate alternative ids (alts),
    a list of agent preferences (agents), and a integer for the number of saved partial commitee assignments (d).
    The returned output is a final list of winning alternatives to serve on the committee.

    Input:
        comm_size - integer
        alts      - list of strings ([str])
        agents    - list of PrefPy Preference Objects ([Preference])
        d         - integer

    Output:
        finalList - list of strings
    """

    # Store Preference objects (agents) in SingleAssignment objects
    assignments = []
    for a in agents:
        assignments.append(SingleAssignment(a))

    # List of partial assignments (i.e. incomplete committees)
    paList = []
    # Initial default partial assignment (none assigned)
    pa0 = FullAssignment(assignments, alts)
    paList.append(pa0)

    # Iteratively build up partial assignments by adding 1 alternative at a time
    for i in range(comm_size):
        # Temporary list for storing test versions of partial assignments
        tmpList = []
        # Extend every partial assignment to include 1 more alternative, trying every permutation
        for pa in paList:
            for alt in pa.unmatchedAlts:
                extendedPA = copy.deepcopy(pa)
                # Assign every agent to the current alternative if preferred
                #  regardles of previous assignments
                for a in extendedPA.assignments:
                    if (borda(alt, a.pref.getOrderVector()) > borda(a.alt, a.pref.getOrderVector())):
                        a.alt = alt
                # The alternative has now been matched, remove them from the
                #  list of unmatched alternatives
                extendedPA.unmatchedAlts.remove(alt)
                # Store the new extended partial assignment
                tmpList.append(extendedPA)
        # Sort the partial assignments by total satisfaction score provided
        tmpList = sorted(tmpList, key=lambda pa: pa.getSatScore(), reverse=True)
        # Keep only the top L partial assignments for use in the next iteration
        L = min(len(tmpList), d)
        paList = tmpList[:L]

    # Select the full assignment that provides the greatest total satisfaction
    finalAssignment = paList[0]
    # Convert to a simple list of alternatives and return
    finalSet = {}
    for sa in finalAssignment.assignments:
        finalSet[sa.alt] = None
    finalList = finalSet.keys()

    return finalList

def algoC_M(comm_size, alts, agents, d):
    """
    Approximation algorithm for Monroe multi-winner elections, as described
    under Algorithm C (Monroe) in the paper 'Achieving fully proportional representation:
    Approximability results' by Piotr Skowron, Piotr Faliszewski, Arkadii Slinko.
    This algorithm takes in a desired committee size (comm_size), a list of candidate alternative ids (alts),
    a list of agent preferences (agents), and a integer for the number of saved partial commitee assignments (d).
    The returned output is a final list of winning alternatives to serve on the committee.

    Input:
        comm_size - integer
        alts      - list of strings ([str])
        agents    - list of PrefPy Preference Objects ([Preference])
        d         - integer

    Output:
        finalList - list of strings
    """
    # Store the number of voting agents
    num_agents = len(agents)

    # Store Preference objects (agents) in SingleAssignment objects
    assignments = []
    for a in agents:
        assignments.append(SingleAssignment(a))

    # List of partial assignments (i.e. incomplete committees)
    paList = []
    # Initial default partial assignment (none assigned)
    pa0 = FullAssignment(assignments, alts)
    paList.append(pa0)

    # Iteratively build up partial assignments by adding 1 alternative at a time
    for i in range(comm_size):
        tmpList = []
        # Extend every partial assignment to include 1 more alternative, trying every permutation
        for pa in paList:
            for alt in pa.unmatchedAlts:
                extendedPA = copy.deepcopy(pa)
                # Sort the single assignments (agents) by their preference for the current alternative
                sortedAssignments = sorted(extendedPA.assignments, key=lambda a: a.pref.getRankMap()[alt])
                extendedPA.assignments = sortedAssignments
                # Assign the top (num_agents / comm_size) agents to the current alternative unless
                #  they have been previously assigned
                counter = 0
                for a in extendedPA.assignments:
                    if (a.alt == '<none>'):
                        a.alt = alt
                        counter += 1
                    if (counter == math.ceil(num_agents / comm_size)):
                        break

                # The alternative has now been matched
                extendedPA.unmatchedAlts.remove(alt)
                # Save the new extended partial assignment
                tmpList.append(extendedPA)

        # Sort the partial assignments by total satisfaction score
        tmpList = sorted(tmpList, key=lambda pa: pa.getSatScore(), reverse=True)
        # Keep the top L partial assignments for use in the next iteration
        L = min(len(tmpList), d)
        paList = tmpList[:L]

    # Select the full assignment that provides the greatest total satisfaction
    finalAssignment = paList[0]
    # Convert to a simple list of alternatives
    finalSet = {}
    for sa in finalAssignment.assignments:
        finalSet[sa.alt] = None
    finalList = finalSet.keys()

    return finalList

def algoP_CC(comm_size, alts, agents):
    """
    Approximation algorithm for Chamberlin-Courant multi-winner elections, as described
    under Algorithm P (Chamberlin-Courant) in the paper 'Achieving fully proportional representation:
    Approximability results' by Piotr Skowron, Piotr Faliszewski, Arkadii Slinko.
    This algorithm takes in a desired committee size (comm_size), a list of candidate alternative ids (alts), and
    a list of agent preferences (agents). The returned output is a final list of winning alternatives to serve on the committee.

    Input:
        comm_size - integer
        alts - list of strings ([str])
        agents - list of PrefPy Preference Objects ([Preference])

    Output:
        list of strings
    """
    # Calculate the bounding rank
    X = math.ceil(len(alts) * lambertw(comm_size)/comm_size)

    # Store Preference objects (agents) in SingleAssignment objects
    assignments = []
    for a in agents:
        assignments.append(SingleAssignment(a))

    # Full Assignment storage object to keep track of unassigned alts
    fa = FullAssignment(assignments, alts)
    # List of alternatives that have already been assigned
    assignedAlts = []

    # For each committee position
    for i in range(comm_size):
        # Collect a list of unassigned agents
        unmatchedAgents = []
        for a in assignments:
            if (a.alt =='<none>'):
                unmatchedAgents.append(a.pref)
		# Get the alternative that occurs in the top X positions of the most
		# unassigned agent's rankings
        alt = getTopKAlt(fa.unmatchedAlts, unmatchedAgents, X)
		# Note the alternative is now being assigned
        assignedAlts.append(alt)
        fa.unmatchedAlts.remove(alt)
		# Assign any unassigned agents who postion the alternative in
		#  their top X rankings to that alternative
        for a in unmatchedAgents:
            if (a.getRankMap()[alt] <= X):
                a.alt = alt
	# Assign any remaining unassigned agents to their most preferred
	#  alternatives of those selected to be on the committee
    for a in assignments:
        if (a.alt == '<none>'):
            for alt in assignedAlts:
                if (borda(alt, a.pref.getOrderVector()) > a.getSatScore()):
                    a.alt = alt

    # Convert to a simple list of alternatives
    finalSet = {}
    for sa in fa.assignments:
        finalSet[sa.alt] = None
    finalList = finalSet.keys()

    return finalList

def run():
    """
    Main function to run the program.
    """
    check_arguments()

    agents, alternatives = parse_data(sys.argv[1])

    if len(sys.argv) > 2:
        comm_size = int(sys.argv[2])

    else:
        comm_size = len(alternatives)

    winnersA = algoA_M(comm_size, alternatives, agents)
    print(winnersA)

    winners = winnersA
    return winners

# ============================================================================ #
if __name__ == "__main__":
	run()
