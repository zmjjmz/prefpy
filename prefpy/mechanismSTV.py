import random
from .mechanism import Mechanism
from .preference import Preference
from .profile import Profile

class MechanismSTV(Mechanism):
    """
    The Single Transferable Vote Mechanism. This class is the parent class for
    several mechanisms and cannot be constructed directly. All child classes are
    expected to implement getScoringVector() method.
    """

    def __init__(self):
        self.maximizeCandScore = True
        self.seatsAvailable = 1

    def getWinningQuota(self, profile):
        """
        Returns an integer that is the minimum number of votes needed to
        definitively win using Droop quota

        :ivar Profile profile: A Profile object that represents an election profile.
        """

        return (profile.numVoters / (self.seatsAvailable + 1)) + 1

    def convRankingToTuple(self, ranking):
        """
        Returns a tuple of tuples that represents the ranking where the first inner
        tuple contains candidates that are ranked number 1 in original ranking and
        so on for each following inner tuple. e.g. {{4,}, {1,}, {3,}, {2,}} is a
        ranking where candidates are ranked in the order 4 > 1 > 3 > 2.

        :rtype tuple<tuple<int>>: will referred to as tupleRanking type.

        :ivar dict<int,list<int>> ranking: A mapping of ranking position number to
            list of candidates ranked at that position. e.g. {1:[2,3]} means
            candidates 2 and 3 are both ranked number 1 in the ranking.
        """

        return tuple(tuple(ranking[k+1]) for k in range(0,len(ranking)))

    def getInitialCandMaps(self, profile):
        """
        Returns a multi-part representation of the election profile referenced by
        profile.

        .. note:: tupleRanking is equal to tuple<tuple<int>> as returned by
            convRankingToTuple.
        :rtype dict<int,int> candScoreMap: A mapping of each candidate to their
            score, which starts out as the number of rankings with this candidate
            ranked first, or 0 if no rankings start out supporting this canddiate.
        :rtype dict<int,list<tupleRanking>> candPreferenceMap: A mapping of each
            candidate to a list all rankings, represented as tuple of tuples, that
            contribute to their score, which starts out empty.
        :rtype dict<tupleRanking, int> rankingCount: A mapping of rankings in tuple
            form to their corresponding count as given by profile.
        :rtype dict<tupleRanking, int> rankingOffset: A mapping of rankings in tuple
            form to the their own offset, which shows which candidate the ranking is
            currently supporting. Each ranking starts off supporting its first ranked
            candidate.

        :ivar Profile profile: A Profile object that represents an election profile.
        """

        allCands = list(profile.candMap.keys())
        rankMaps = profile.getReverseRankMaps()
        rankMapCounts = profile.getPreferenceCounts()

        # initialize all cands to have 0 score and [] supporting rankings
        candScoreMap, candPreferenceMap = {},{}
        for cand in allCands:
            candScoreMap[cand] = 0
            candPreferenceMap[cand] = []
        rankingOffset = {}
        rankingCount = {}

        for ranking,count in zip(rankMaps,rankMapCounts):
            tupleRanking = self.convRankingToTuple(ranking)
            rankingCount[tupleRanking] = count
            # find top ranked candidate and add to his score and supporint rankings
            candScoreMap[tupleRanking[0][0]] += rankingCount[tupleRanking]
            candPreferenceMap[tupleRanking[0][0]].append(tupleRanking)
            if tupleRanking not in rankingOffset:
                rankingOffset[tupleRanking] = 0

        return candScoreMap, candPreferenceMap, rankingCount, rankingOffset

    def getWinLoseCandidates(self, candScoreMap, winningQuota):
        """
        Returns candidates who gained at least winningQuota worth of votes and
        those with the least positive number of votes.

        :rtype set<int> winners: The set of candidates who has winningQuota worth
            of votes this round.
        :rtype set<int> losers: The set of candidates who has the least positive
            amount of votes.

        :ivar dict<int, int> candScoremap: A mapping of candidates to their score.
        :ivar int winningQuota: the amount of votes needed to win a seat
        """
        winners, losers = set(), set()
        lowestScore = winningQuota
        for cand,score in candScoreMap.items():
            if score >= winningQuota:
                winners.add(cand)
            elif score < lowestScore and score > 0:
                lowestScore = score
                losers = set([cand])
            elif score == lowestScore:
                losers.add(cand)
        return winners, losers



    def reallocLoserVotes(self, candScoreMap, candPreferenceMap, rankingCount,
                          rankingOffset, loser, noMoreVotesHere, deltaCandScores):
        """
        Modifies rankingOffset so that the rankings supporting the just eliminated
        candidate will support the next non-winning-or-eliminated candidate, or
        no one if offset reaches the end of the ranking. Also updates candScoreMap,
        candPreferenceMap, and deltaCandScores to reflect the new scores, and
        supporting rankings due to one candidate being eliminated. A ranking that
        supports no candidate is removed from all lists in candPreferenceMap, but
        not from rankingOffset, and rankingCount.

        .. note:: tupleRanking is equal to tuple<tuple<int>> as returned by
            convRankingToTuple.
        :ivar dict<int,int> candScoreMap: A mapping of candidates to their score.
        :ivar dict<int,list<tupleRanking>> candPreferenceMap: A mapping of each
            candidate to a list of supporting rankings in tuple form
        :ivar dict<tupleRanking, int> rankingCount: A mapping of rankings in tuple
            form to their corresponding count as given by profile.
        :ivar dict<tupleRanking, int> rankingOffset: A mapping of rankings in tuple
            form to the their own offset to the currently supproted candidate.
        """
        deltaCandScore = {}
        for ranking in candPreferenceMap[loser]:
            curOffset = rankingOffset[ranking]
            oldCand = ranking[curOffset][0]
            while(curOffset < len(ranking) and \
                  ranking[curOffset][0] in noMoreVotesHere):
                curOffset += 1
            rankingOffset[ranking] = curOffset
            if curOffset < len(ranking):
                newCand = ranking[curOffset][0]
                candPreferenceMap[newCand].append(ranking)
                candScoreMap[newCand] += rankingCount[ranking]
                if newCand not in deltaCandScore:
                    deltaCandScore[newCand] = 0
                deltaCandScore[newCand] += rankingCount[ranking]
            candScoreMap[oldCand] -= rankingCount[ranking]
            if oldCand not in deltaCandScore:
                deltaCandScore[oldCand] = 0
            deltaCandScore[oldCand] -= rankingCount[ranking]
        candPreferenceMap[loser] = []
        deltaCandScores.append(deltaCandScore)


    def getCandScoresMap(self, profile):
        """
        Returns a dictionary that associates integer representations of each
        candidate with their frequency as top ranked candidate or 0 if they were
        eliminated.

        This function assumes that breakLoserTie(self, losers, deltaCandScores, profile)
        is implemented for the child MechanismSTV class.

        :ivar Profile profile: A Profile object that represents an election profile.
        """

        # Currently, we expect the profile to contain an ordering over candidates
        # with no ties.
        elecType = profile.getElecType()
        if elecType != "soc" and elecType != "soi":
            print("ERROR: unsupported election type")
            exit()

        winningQuota = self.getWinningQuota(profile)
        numCandidates = profile.numCands
        candScoreMap, candPreferenceMap, rankingCount, rankingOffset = \
            self.getInitialCandMaps(profile)
        roundNum = 0

        deltaCandScores = []
        victoriousCands, eliminatedCands = set(), set()
        while(len(victoriousCands) < self.seatsAvailable and \
              len(victoriousCands) + len(eliminatedCands) + 1 < numCandidates):
            for cand in eliminatedCands:
                candScoreMap[cand] -= 1
            winners, losers = self.getWinLoseCandidates(candScoreMap, winningQuota)
            loser = self.breakLoserTie(losers, deltaCandScores, profile)
            victoriousCands = victoriousCands | winners
            eliminatedCands = eliminatedCands | {loser}
            #print('[round %d]'%roundNum,'prefMap:-',candPreferenceMap)
            #print('[round %d]'%roundNum,'scores:-',candScoreMap,'loser:-',loser,
            #      'w&l:-',victoriousCands, eliminatedCands)
            self.reallocLoserVotes(candScoreMap, candPreferenceMap, rankingCount, \
                                   rankingOffset,loser, \
                                   victoriousCands | eliminatedCands, deltaCandScores)
            roundNum+= 1
        return candScoreMap

class MechanismSTVForward(MechanismSTV):
    """
    The Single Transferable Vote Mechanism with Forward Tie Breaking.
    """

    def __init__(self):
        self.maximizeCandScore = True
        self.seatsAvailable = 1

    def breakLoserTie(self, losers, deltaCandScores, profile):
        """
        Returns one candidate to be eliminated by foward tie breaking.

        :rtype int loser: the candidate to be eliminated this round.

        :ivar set<int> losers: A set of candidates who are tied for being eliminated.
        :ivar list<dict<int,int>> deltaCandScores: A list of the score change for
            each candidate each round. Candidates whose score did not change for a
            round would not appear in the dictionary for that round.
        :ivar Profile profile: A Profile object that represents an election profile.
        """

        curCandScores = self.getInitialCandMaps(profile)[0]
        curRound = 0
        while(len(losers)>1 and curRound < len(deltaCandScores)):
            lowestScore = -1
            newLosers = set()
            for loser in losers:
                score = curCandScores[loser]
                if score < lowestScore or lowestScore == -1:
                    lowestScore = score
                    newLosers = {loser}
                elif score == lowestScore:
                    newLosers.add(loser)
            losers = newLosers

            for cand in losers:
                if cand not in deltaCandScores[curRound]:
                    continue
                curCandScores[cand] += deltaCandScores[curRound][cand]
            curRound += 1
        return random.choice(list(losers))

class MechanismSTVBackward(MechanismSTV):
    """
    The Single Transferable Vote Mechanism with Backwards Tie Breaking.
    """

    def __init__(self):
        self.maximizeCandScore = True
        self.seatsAvailable = 1

    def breakLoserTie(self, losers, deltaCandScores, profile):
        """
        Returns one candidate to be eliminated by backwards tie breaking.

        :rtype int loser: the candidate to be eliminated this round.

        :ivar set<int> losers: A set of candidates who are tied for being eliminated.
        :ivar list<dict<int,int>> deltaCandScores: A list of the score change for
            each candidate each round. Candidates whose score did not change for a
            round would not appear in the dictionary for that round.
        :ivar Profile profile: A Profile object that represents an election profile.
        """
        curRound = len(deltaCandScores) - 1
        while(len(losers) > 1 and curRound >= 0):
            highestChange = -1
            newLosers = set()
            for loser in losers:
                change = 0
                if loser in deltaCandScores[curRound]:
                    change = deltaCandScores[curRound][loser]
                if change > highestChange or highestChange == -1:
                    highestChange = change
                    newLosers = {loser}
                elif change == highestChange:
                    newLosers.add(loser)
            losers = newLosers
            curRound -= 1
        return random.choice(list(losers))

class MechanismSTVPosTieBreak(MechanismSTV):
    """
    The Single Transferable Vote Mechanism with Positional Tie Breaking.
    This is the parent class for several other mechanisms but can be constructed
    directly.  The child classes are expected to implement the getScoringVector()
    method.

    :ivar list<int> scoringVector: A list of integers (or floats that give the scores assigned to
    each position a ranking from first to last.
    """

    def __init__(self,scoringVector):
        self.maximizeCandScore = True
        self.seatsAvailable = 1
        self.scoringVector = scoringVector

    def getScoringVector(self,profile):
        """
        Returns the scoring vector. This function is called by breakLoserTie().

        :ivar Profile profile: A Profile object that represents an election profile.
        """
        if len(self.scoringVector) != profile.numCands:
            print("ERROR: scoring vector is not the correct length")
            exit()
        return self.scoringVector


    def breakLoserTie(self, losers, deltaCandScores, profile):
        """
        Returns one candiate to be eliminated by positional tie breaking.

        :rtype int loser: the candidate to be eliminated this round.

        :ivar set<int> losers: A set of candidates who are tied for being eliminated.
        :ivar list<dict<int,int>> deltaCandScores: A list of the score change for
            each candidate each round. Candidates whose score did not change for a
            round would not appear in the dictionary for that round.
        :ivar Profile profile: A Profile object that represents an election profile.
        """

        # Initialize our dictionary so all candidate have a score of zero.
        loserScoresMap = dict()
        for loser in losers:
            loserScoresMap[loser] = 0
        rankMaps = profile.getRankMaps()
        rankMapCounts = profile.getPreferenceCounts()
        scoringVector = self.getScoringVector(profile)
        # Go through the rankMaps of the profile and increment each candidates score appropriately
        for i in range(0, len(rankMaps)):
            rankMap = rankMaps[i]
            rankMapCount = rankMapCounts[i]
            for cand in rankMap.keys():
                if cand in losers:
                    loserScoresMap[cand] += scoringVector[rankMap[cand]-1]*rankMapCount
        #get a starting value for the lowest score, store losers with that value
        sampleLoser = losers.pop()
        loserScore = loserScoresMap[sampleLoser]
        actualLosers = set()
        actualLosers.add(sampleLoser)
        #find the lowest scored losers
        for loser in losers:
            currentScore = loserScoresMap[loser]
            if currentScore < loserScore:
                loserScore = currentScore
                actualLosers.clear()
                actualLosers.add(loser)
            elif currentScore == loserScore:
                actualLosers.add(loser)
        return random.choice(list(actualLosers))

class MechanismSTVBorda(MechanismSTVPosTieBreak):
    """
    The Single Transferable Vote with Borda tie breaking mechanism.
    This inherits from the STV with positional tie breaking mechanism.
    """

    def __init__(self):
        self.maximizeCandScore = True
        self.seatsAvailable = 1

    def getScoringVector(self, profile):
        """
        Echos the function of the same name from MechanismBorda.
        Returns the scoring vector [m-1,m-2,m-3,...,0] where m is the number of candidates in the
election profile. This function is called by breakLoserTie() which is implemented in the
parent class.

        :ivar Profile profile: A Profile object that represents an election profile.
        """
        scoringVector = []
        score = profile.numCands-1
        for i in range(0,profile.numCands):
            scoringVector.append(score)
            score -= 1
        return scoringVector

class MechanismSTVCoombs(MechanismSTVPosTieBreak):
    """
    The Single Transferable Vote with Coombs tie breaking mechanism.
    This inherits from the STV with positional tie breaking mechanism.
    """

    def __init__(self):
        self.maximizeCandScore = True
        self.seatsAvailable = 1

    def getScoringVector(self, profile):
        """
        Echos the function of the same name from MechanismVeto.
        Returns the scoring vector [1,1,1,...,0]. This function is called by breakLoserTie()
        which is implemented in the parent class.

        :ivar Profile profile: a Profile object that represents an election profile.
        """
        numTiers = len(set(profile.getRankMaps()[0].values()))
        scoringVector = []
        for i in range(0, numTiers - 1):
            scoringVector.append(1)
        for i in range(numTiers - 1, profile.numCands):
            scoringVector.append(0)
        return scoringVector

class MechanismSTVAll(Mechanism):
    """
    The Single Transferable Vote Mechanism, returning all possible winners
    over all different tie-break combinations.
    """

    def __init__(self):
        self.maximizeCandScore = True
        self.seatsAvailable = 1

    def getWinningQuota(self, profile):
        """
        Returns an integer that is the minimum number of votes needed to
        definitively win using Droop quota

        :ivar Profile profile: A Profile object that represents an election profile.
        """

        return (profile.numVoters / (self.seatsAvailable + 1)) + 1

    def getInitialRankMaps(self, profile):
        """
        Returns a multi-part representation of the election profile referenced by
        profile.

        :ivar Profile profile: A Profile object that represents an election profile.
        """
        allCands = list(profile.candMap.keys())
        rankMaps = profile.getReverseRankMaps()
        rankMapCounts = profile.getPreferenceCounts()
        return rankMaps, rankMapCounts

    def getCandScoresMap(self, profile):
        """
        Returns a dictionary that associates integer representations of each
        candidate 1 if they win in some case or 0 if they were eliminated in
        every case.

        :ivar Profile profile: A Profile object that represents an election profile.
        """

        # Currently, we expect the profile to contain an ordering over candidates
        # with no ties.
        elecType = profile.getElecType()
        if elecType != "soc" and elecType != "soi":
            print("ERROR: unsupported election type")
            exit()

        winningQuota = self.getWinningQuota(profile)
        # print("Winning quota is %d votes" % winningQuota)
        numCandidates = profile.numCands
        rankMaps, rankMapCounts = self.getInitialRankMaps(profile)

        rankingOffset = [1 for i in rankMapCounts]
        roundNum = 1

        victoriousCands = set()
        eliminatedCandsList = [set()]
        rankingOffsets = [rankingOffset]
        while roundNum < numCandidates:
            # print("\n\nRound %d\t\t" % roundNum)
            newRankingOffsets = []
            newEliminatedCandsList = []
            for i in range(len(rankingOffsets)):
                rankingOffset = rankingOffsets[i]
                winners, losers = self.getWinLoseCandidates(rankMaps, rankMapCounts, rankingOffset, winningQuota)
                victoriousCands = victoriousCands | winners
                # print("\tWinners: %s" % victoriousCands)
                # print("\tEliminated so far: %s" % eliminatedCandsList[i])
                if len(winners) > 0:
                    continue

                # if len(losers) > 1:
                #     print("\t\t%s are tied" % losers)
                # else:
                #     print("\t\t%s is loser" % losers)
                for loser in losers:
                    newEliminatedCands = eliminatedCandsList[i] | {loser}
                    # print("\t\tCands eliminated: %s" % newEliminatedCands)
                    nextRankingOffset = self.reallocLoserVotes(rankMaps, rankMapCounts, rankingOffset, newEliminatedCands)
                    newEliminatedCandsList.append(newEliminatedCands)
                    newRankingOffsets.append(nextRankingOffset)
            rankingOffsets = newRankingOffsets
            eliminatedCandsList = newEliminatedCandsList
            roundNum+= 1
        allCands = set(profile.candMap.keys())

        candScoreMap = {}
        for eliminatedCands in eliminatedCandsList:
            for cand in eliminatedCands:
                candScoreMap[cand] = 0
            # Add candidates remaining in last round as victorious
            victoriousCands = victoriousCands | (allCands - eliminatedCands)
        for cand in victoriousCands:
            candScoreMap[cand] = 1
        return candScoreMap

    def getWinLoseCandidates(self, rankMaps, rankMapCounts, rankingOffset, winningQuota):
        """
        Returns all candidates who have won by passing the winning quota and all who have tied for lowest score.

        :ivar list<dict<int, list<int>>> rankMaps: List of rankings in dict form, where dict maps placement to list of candidates.
        :ivar list<int> rankMapCounts: Count of votes in corresponding entry of rankMaps
        :ivar list<int> rankingOffset: Index of top remaining candidate in corresponding entry of rankMaps
        :ivar int winningQuota: minimum value needed to be winner
        """
        candScores = {}
        # calculate scores
        for i in range(len(rankMaps)):
            ranking = rankMaps[i]
            offset = rankingOffset[i]
            cands = ranking[offset]
            for cand in cands:
                if cand not in candScores:
                    candScores[cand] = 0
                candScores[cand] += rankMapCounts[i]
        # print(candScores)
        # find winners and losers
        winners = set()
        losers = set()
        minScore = min(candScores.values())
        for cand in candScores:
            score = candScores[cand]
            if score >= winningQuota:
                winners.add(cand)
            if score == minScore:
                losers.add(cand)

        return winners, losers

    def reallocLoserVotes(self, rankMaps, rankMapCounts, rankingOffset, eliminatedCands):
        """
        Makes new rankingOffset based on who has been eliminated.

        :ivar list<dict<int, list<int>>> rankMaps: List of rankings in dict form, where dict maps placement to list of candidates.
        :ivar list<int> rankMapCounts: Count of votes in corresponding entry of rankMaps
        :ivar list<int> rankingOffset: Index of top remaining candidate in corresponding entry of rankMaps
        :ivar set<int> eliminatedCandidates: Set of candidates that have been eliminated
        """
        newRankingOffset = [i for i in rankingOffset]
        i = 0;
        while i < len(rankMaps):
            ranking = rankMaps[i]
            offset = newRankingOffset[i]
            cands = ranking[offset]
            nonLoserCands = []
            for cand in cands:
                if cand not in eliminatedCands:
                    nonLoserCands.append(cand)
            if len(nonLoserCands) == 0:
                newRankingOffset[i] = offset + 1
            else:
                i += 1
        return newRankingOffset
