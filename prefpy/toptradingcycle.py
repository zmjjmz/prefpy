from . import aggregate


class TTCAggregator(aggregate.RankAggregator):
    '''
            Extended class for Top Trading Cycle (TTC) algorithm
            developed by Gale and published by Scarf and Shapley
            _ is used to keep private variables with public accessors
    '''

    def __init__(self, alts_list, id):
        if id > len(alts_list) or id < 0:
            raise ValueError(
                "id must be in range [1, n] where n is the number of alternatives")

        # Simple inheritance to extend RankAggregator class
        super().__init__(alts_list)
        self._id = id

        self._allocation = id       # alternative currently allocated to this aggregator
        self._reference = None      # id of aggregator allocated this aggregator's top choice

    # Accessor functions for private class variables
    def getId(self):
        return self._id

    def getAllocation(self):
        return self._allocation

    def getReference(self):
        return self._reference

    def setAllocation(self, val):
        self._allocation = val

    def setReference(self, val):
        self._reference = val


class TTCAggregatorContainer:
    '''
            Main class that holds a list of TTCAggregators 
            and performs operations on that list
    '''

    def __init__(self, aggregators):
        self._master_aggregators = {}
        self._aggregators = {}
        self._allocations = []
        for aggregator in aggregators:
            self._aggregators[aggregator.getId()] = aggregator
            self._allocations.append(aggregator.getAllocation())

    # Accessor functions for private class variables
    def getAggregators(self):
        return self._aggregators.values()

    def getNumAggregators(self):
        return len(self._aggregators)

    # Return a list of all final allocations of aggregators
    def getFinalAllocations(self):
        allocations = [None] * len(self._master_aggregators)
        for id, aggregator in self._master_aggregators.items():
            allocations[id - 1] = aggregator.getAllocation()
        return allocations

    # Remove an aggregator from the trade
    def removeAggregator(self, id):
        self._master_aggregators[id] = self._aggregators[id]
        self._allocations.remove(id)
        self._aggregators.pop(id)

    # Update each aggregator's reference
    def updateReferences(self):
        if len(self._aggregators) == 0:
            return
        for aggregator1 in self._aggregators.values():
            topChoice = [
                x for x in aggregator1.alts if x in self._allocations][0]
            for aggregator2 in self._aggregators.values():
                if aggregator2.getAllocation() == topChoice:
                    aggregator1.setReference(aggregator2.getId())
                    break

    # Update the allocations of all aggregators based on a given cycle
    def updateAllocations(self, cycle):
        if len(cycle) == 1:
            self.removeAggregator(cycle[0])
        else:
            firstAllocation = self._aggregators[cycle[0]].getAllocation()
            # set each aggregator's allocation to that of the next allocation
            # in the cycle and remove it
            for i in range(0, len(cycle) - 1):
                self._aggregators[cycle[i]].setAllocation(
                    self._aggregators[cycle[i + 1]].getAllocation())
                self.removeAggregator(cycle[i])
            self._aggregators[cycle[-1]].setAllocation(firstAllocation)
            self.removeAggregator(cycle[-1])
        self.updateReferences()

    # Returns a 2D array containing the cycles between aggregators in the
    # container
    def getCycles(self):
        # convert the array of aggregators into a more usable graph form
        G = {}
        for aggregator in self._aggregators.values():
            G[aggregator.getId()] = aggregator.getReference()

        cycles = []
        cycle = []
        next = list(G.keys())[0]
        # parse the graph looking for cycles
        # the graph only contains vertices that have not been visited
        while True:
            if next not in G:
                if current == next:
                    cycles.append([next])
                elif cycle[0] == next:
                    cycles.append(cycle)
                if len(G) == 0:
                    break
                cycle = []
                next = list(G.keys())[0]

            current = next
            cycle.append(current)
            next = G[current]
            G.pop(current)

        return cycles


def topTradingCycle(preferences):
    '''
        preferences: 2D array of preferences for each agent
    '''

    # create TTCAggregator objects and container from preferences
    aggregators = []
    n = len(preferences)
    for profile in preferences:
        id = len(aggregators) + 1
        aggregator = TTCAggregator(profile, id)
        aggregators.append(aggregator)

    aggregators = TTCAggregatorContainer(aggregators)

    # main algorithm
    k = 0
    while aggregators.getNumAggregators() > 0:
        k += 1
        aggregators.updateReferences()
        TTCPrinter(k, aggregators)
        cycles = aggregators.getCycles()
        for cycle in cycles:
            aggregators.updateAllocations(cycle)

    return aggregators.getFinalAllocations()


def TTCPrinter(k, aggregators):
    print("Iteration {}:".format(k))
    for aggregator in aggregators.getAggregators():
        print("  {} @ {} ---> {}".format(aggregator.getId(),
                                         aggregator.getAllocation(), aggregator.getReference()))


def main():
    print("Executing tests")

    assert_message = "Test %i failed, allocation does not match expected result"

    print("Testing TTC...")
    print()

    # Test 1
    print("Test Case 1:")
    agents = [
        [3, 2, 1],
        [1, 2, 3],
        [2, 3, 1]
    ]
    for agent in agents:
        print(agent)

    print()
    result = [3, 1, 2]
    ttc = topTradingCycle(agents)
    print("Test Case 1 result:", ttc)
    print()
    assert (ttc == result), assert_message % 1

    # Test 2
    print("Test Case 2:")
    agents = [
        [4, 3, 2, 1, 5],
        [4, 1, 2, 3, 5],
        [1, 4, 3, 2, 5],
        [3, 2, 1, 4, 5],
        [1, 5, 2, 4, 3]
    ]
    for agent in agents:
        print(agent)

    print()
    result = [4, 2, 1, 3, 5]
    ttc = topTradingCycle(agents)
    print("Test Case 2 result:", ttc)
    print()
    assert (ttc == result), assert_message % 2

    # Test 3
    print("Test Case 3:")
    agents = [
        [3, 2, 4, 1, 5, 6],
        [3, 5, 6, 1, 2, 4],
        [3, 1, 2, 4, 5, 6],
        [2, 5, 6, 4, 1, 3],
        [1, 3, 2, 4, 5, 6],
        [2, 4, 5, 6, 1, 3]
    ]
    for agent in agents:
        print(agent)

    print()
    result = [2, 5, 3, 6, 1, 4]
    ttc = topTradingCycle(agents)
    print("Test Case 3 result:", ttc)
    print()
    assert (ttc == result), assert_message % 3

    # Test 4
    print("Test Case 4:")
    agents = []
    for agent in agents:
        print(agent)

    print()
    result = []
    ttc = topTradingCycle(agents)
    print("Test Case 4 result:", ttc)
    print()
    assert (ttc == result), assert_message % 4

    print("TTC passed all tests!")

if __name__ == "__main__":
    main()
