from . import aggregate
import sys


class StableMatchingAggregator(aggregate.RankAggregator):
    '''
            Extended Class for Gale Shapley Algorithm Specifically
            _ is used to keep private variables with public accessors
    '''

    def __init__(self, alts_list, name):
        # Simple Inheritance to extend RankAggregator Class
        # Small check to handle None case with integer value
        if 'None' in alts_list:
            x = alts_list.index('None')
            alts_list[x] = '0'
        super().__init__(alts_list)
        self._name = name
        if self._name == "None":
            self._name = None
        self._unmatched = True
        self._matched_with = None
        self._tried = []

    # Accessor Functions for Private Class Variables
    def getName(self):
        return self._name

    def getUnmatched(self):
        return self._unmatched

    def getMatchedWith(self):
        return self._matched_with

    def getTried(self):
        return self._tried

    def setUnmatched(self, val):
        self._unmatched = val

    def setMatchedWith(self, val):
        self._matched_with = val

    def addToTried(self, val):
        self._tried.append(val)


class StableMatchingAggregatorContainer:
    '''
            Main Class for containing two lists of StableMatchingAggregators
            and perform operations on these two lists
    '''

    def __init__(self, dict1, dict2, proposer):
        self._dictWhole = {**dict1, **dict2}
        self._dictHalf1 = dict1  # Proposer
        self._dictHalf2 = dict2
        self._proposer = proposer
        self.matching = {}

    # Accessor Functions for Private Class Variables
    def getWholeDict(self):
        return self._dictWhole

    def getProposer(self):
        return self._proposer

    def getHalfDict(self, num):
        if num == 0:
            return self._dictHalf1
        elif num == 1:
            return self._dictHalf2
        else:
            raise ValueError("Incorrect Number Specified: Must use 0 or 1")

    # Breaks a matching between two alternatives
    def breakMatch(self, check):
        proposer = self._proposer
        matchToBreak = self.isMatchedWith(check)
        alt = self.getWholeDict()[check]
        if alt.getMatchedWith() is not None:
            alt.setMatchedWith(None)
            alt.setUnmatched(True)
            print("{} is breaking with {}.".format(
                check, matchToBreak))

    # Checks who an alternative is currently matched with
    def isMatchedWith(self, check):
        alt = self.getWholeDict()[check]
        return alt.getMatchedWith()

    # Checks if an alternative has a match
    def isMatched(self, check):
        alt = self.getWholeDict()[check]
        if alt.getMatchedWith() is not None:
            return True
        return False

    # Checks if c1 or c2 is higher on alternatives preference list
    def betterRanked(self, check, c1, c2):
        proposer = self._proposer
        alt = self.getWholeDict()[check]
        for x in range(0, len(self.getHalfDict(proposer))):
            if c1 == alt.alts[x]:
                return c1
            elif c2 == alt.alts[x]:
                return c2

    # Matching Function
    def createMatch(self, alt1, alt2):
        check1 = self.getWholeDict()[alt1]
        check1.setMatchedWith(alt2)
        check1.setUnmatched(False)
        check2 = self.getWholeDict()[alt2]
        check2.setMatchedWith(alt1)
        check2.setUnmatched(False)

    def betterThanNothing(self, c1, c2, proposer):
        alt = self.getWholeDict()[c2]
        for x in range(0, len(self.getHalfDict(proposer))):
            if c1 == alt.alts[x]:
                return True
            elif "0" == alt.alts[x] or None == alt.alts[x]:
                return False

    # Get name of preferred alternative at a certain index
    def getNameFromRank(self, check, rank):
        proposer = self._proposer
        if proposer not in [0, 1]:
            raise ValueError("Incorrect Number Specified: Must use 0 or 1")
        alt = self.getWholeDict()[check]
        return alt.alts[rank]

    def printResult(self):
        proposer = self._proposer
        print('Matching')
        for key, val in self.getHalfDict(proposer).items():
            one = key
            two = val.getMatchedWith()
            print("{} <---> {}".format(one, two))

    def storeMatching(self):
        proposer = self._proposer
        for key, val in self.getHalfDict(proposer).items():
            self.matching[key] = val.getMatchedWith()

    def checkStability(self):
        proposer = self._proposer
        side1 = self.getHalfDict(proposer)
        side2 = self.getHalfDict(int(not proposer))
        count = 0
        for key, val in side1.items():
            # if the current proposer is unmatched, see if we can find him/her a match
            if val.getUnmatched():
                for key2, val2 in side2.items():
                    # if current acceptor is less preferable to None
                    # skip ahead and look for another acceptor
                    if ("0" in val.alts) and (val.alts.index(key2)>val.alts.index("0")):
                        continue
                    elif (None in val.alts) and (val.alts.index(key2)>val.alts.index(None)):
                        continue
                    # if current proposer and current acceptor are both unmatched
                    # see if proposer is preferred by acceptor over None
                    if val2.getUnmatched():
                        if (None in val2.alts) and (val2.alts.index(key)<val2.alts.index(None)):
                            print("{} and {} should match".format(key, key2))
                            count+=1
                            break
                        elif ("0" in val2.alts) and (val2.alts.index(key)<val2.alts.index("0")):
                            print("{} and {} should match".format(key, key2))
                            count+=1
                            break
                        elif (not None in val2.alts) and (not "0" in val2.alts):
                            print("{} and {} should match".format(key, key2))
                            count+=1
                            break
                    # if acceptor matched, see if bachelor proposing is preferred
                    # over acceptor's current match
                    if val2.alts.index(key) < val2.alts.index(val2.getMatchedWith()):
                        print ("Proposer: {}, Acceptor: {}".format(key, key2))
                        print(val2.getMatchedWith())
                        print("{} should break to match with {}".format(key2, key))
                        count += 1
                        break
                continue
            # Finds the rank of its current match
            index = val.alts.index(val.getMatchedWith())
            # Store all options preferred to current match
            preferred = val.alts[: index]
            # If None is a preference, remove it and every alternative after it
            try:
                findNull = preferred.index("0")
                preferred = preferred[:findNull]
            except ValueError:
                try:
                    findNull = preferred.index(None)
                    preferred = preferred[:findNull]
                except ValueError:
                    pass
            # If preferred is empty, just skip to next
            if not preferred:
                continue
            # Dictionary of receiving side that is preferred
            reduced = {k: side2[k] for k in preferred}

            for key2, val2 in reduced.items():
                if (not val2.getUnmatched()) and val2.alts.index(key) < val2.alts.index(val2.getMatchedWith()):
                    print("Matching between {} and {} is unstable".format(key, key2))
                    count += 1
                    break
        if count == 0:
            return True
        else:
            return False


def deferredAcceptance(list1, list2, proposer):
    '''
            list1 : alt:preferencees
            list2 : alt:preferencees
            proposer : side that is proposing
    '''
    if proposer not in [0, 1]:
        raise ValueError("Incorrect Number Specified: Must use 0 or 1")

    aggregators1 = {}
    aggregators2 = {}
    n = len(list2) if proposer == 0 else len(list1)
    count = 0
    for agg in list1:
        name = agg[0]
        preference = agg[1:len(agg)]
        aggregator = StableMatchingAggregator(preference, name)
        aggregators1[name] = aggregator
    for agg in list2:
        name = agg[0]
        preference = agg[1:len(agg)]
        aggregator = StableMatchingAggregator(preference, name)
        aggregators2[name] = aggregator
    container = StableMatchingAggregatorContainer(
        aggregators1, aggregators2, proposer)

    # Main Algorithm
    while(True):
        count = 0
        temp = container.getHalfDict(proposer)
        for key, val in temp.items():
            alt = val
            name = key
            for x in range(0, n):
                if (not container.isMatched(name)) and (not None in alt.getTried()) and (not "0" in alt.getTried()):
                    if x not in alt.getTried():
                        alt.addToTried(x)
                        name2 = container.getNameFromRank(name, x)
                        if (not name2) or name2 == None or name2 == "None" or name2 == "0":
                            break
                        if container.isMatched(name2):
                            curr = container.isMatchedWith(name2)
                            better = container.betterRanked(
                                name2, curr, name)
                            if proposer == 0:
                                container.createMatch(better, name2)
                            elif proposer == 1:
                                container.createMatch(name2, better)
                            if better != curr:
                                container.breakMatch(curr)
                        else:
                            if not container.betterThanNothing(name, name2, proposer):
                                print ("Bachelor {} rejects {}".format(name2, name))
                                continue
                            if proposer == 0:
                                container.createMatch(name, name2)
                            elif proposer == 1:
                                container.createMatch(name2, name)

        if container.checkStability():
            print('Finished')
            container.printResult()
            container.storeMatching()
            return container


def main(argv):
    print("Executing tests")

    assert_message = "Test %i failed, allocation does not match expected result"

    print("Testing DA...\n")

    # Test 1
    print("Test Case 1\n")
    side1 = [[11, 1, 5, 3,  4, 6, 2, 7],
             [12, 3,  1, 4, 5, 6, 2, 7],
             [13, 5, 1, 4, 2, 6,  7, 3],
             [14, 6, 4, 7,  5, 2, 3, 1],
             [15, 4, 2, 3, 6, 5, 1, 7],
             [16, 2, 1, 4, 7, 5, 3, 6],
             [17, 7, 5,  2, 3, 1, 4, 6],
             [18, 1, 5,  6,  3, 2, 7, 4],
             [19, 3, 4, 7, 2, 1, 6, 5],
             [20, 1, 6, 7, 5, 2, 4, 3 ]]
    side2 = [[1, 12, 16, 20, 17, 19, 11, 14, 15, 13, 18],
             [2, 12, 11, 13, 16, 17, 14, 19, 15, 20, 18],
             [3, 16, 12, 15, 17, 18, 13, 19, 11, 14, 20],
             [4, 16, 20, 13, 11, 19, 18, 17, 14, 12, 15],
             [5, 20, 18, 16, 14, 11, 17, 13, 15, 19, 12],
             [6, 12, 11, 15, 19, 20, 14, 16, 17, 13, 18],
             [7, 20, 17, 18, 16, 12, 11, 13, 15, 14, 19]]

    print("Test Case 1 Result: \n")
    container = deferredAcceptance(side1, side2, 1)
    out = container.checkStability()
    assert(out is True), assert_message % 1

    # Test 2
    print("Test Case 2\n")
    side1 = [[11, 1, 5, 3, 9, 10, 4, 6, 2, 8, 7],
             [12, 3, 8, 1, 4, 5, 6, 2, 10, 9, 7],
             [13, 8, 5, 1, 4, 2, 6, 9, 7, 3, 10],
             [14, 9, 6, 4, 7, 8, 5, 10, 2, 3, 1],
             [15, 10, 4, 2, 3, 6, 5, 1, 9, 8, 7],
             [16, 2, 1, 4, 7, 5, 9, 3, 10, 8, 6],
             [17, 7, 5, 9, 2, 3, 1, 4, 8, 10, 6],
             [18, 1, 5, 8, 6, 9, 3, 10, 2, 7, 4],
             [19, 8, 3, 4, 7, 2, 1, 6, 9, 10, 5],
             [20, 1, 6, 10, 7, 5, 2, 4, 3, 9, 8]]
    side2 = [[1, 12, 16, 20, 17, 19, 11, 14, 15, 13, 18],
             [2, 12, 11, 13, 16, 17, 14, 19, 15, 20, 18],
             [3, 16, 12, 15, 17, 18, 13, 19, 11, 14, 20],
             [4, 16, 20, 13, 11, 19, 18, 17, 14, 12, 15],
             [5, 20, 18, 16, 14, 11, 17, 13, 15, 19, 12],
             [6, 12, 11, 15, 19, 20, 14, 16, 17, 13, 18],
             [7, 20, 17, 18, 16, 12, 11, 13, 15, 14, 19],
             [8, 17, 20, 12, 11, 19, 14, 18, 15, 13, 16],
             [9, 19, 13, 18, 17, 16, 12, 11, 15, 20, 14],
             [10, 15, 18, 17, 11, 12, 20, 13, 19, 16, 14]]

    print("Test Case 2 Result: \n")
    container = deferredAcceptance(side1, side2, 1)
    out = container.checkStability()
    assert(out is True), assert_message % 2

    # Test 3
    print("Test Case 3\n")
    side1 = [[10, None, 1, 2, 3, 5, 4, 6],
             [20, 3, 1, None, 2, 4, 5, 6],
             [30, 3, 1, 2, 4, 5, 6],
             [40, 1, 2, None, 3, 4, 5, 6],
             [50, 1, 2, 3, 5, 4, 6],
             [60, 2, 1, 3, 4, 6, 5]]
    side2 = [[1, None, 10, 20, 30, 40, 50, 60],
             [2, None, 20, 30, 50, 10, 40, 60],
             [3, None, 20, 30, 10, 50, 40, 60],
             [4, None, 20, 30, 10, 50, 40, 60],
             [5, 10, 30, 20, 50, 40, 60],
             [6, 20, 30, 10, 50, 40, 60]]

    print("Test Case 3 Result: \n")
    container = deferredAcceptance(side1, side2, 0)
    out = container.checkStability()
    assert(out is True), assert_message % 3

if __name__ == "__main__":
    main(sys.argv)
