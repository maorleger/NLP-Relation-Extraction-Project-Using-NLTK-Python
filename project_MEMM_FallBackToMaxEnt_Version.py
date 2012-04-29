"""
SYNOPSIS

    'project' [-h,--help] [-v,--verbose] [--version]

DESCRIPTION

    TODO This describes how to use this script. This docstring
    will be printed by the script if there is an error or
    if the user requests help (-h or --help).

EXAMPLES

    TODO: Show some examples of how to use this script.

EXIT STATUS

    TODO: List exit codes

AUTHOR

    Maor Leger

LICENSE

    project.py 
    Copyright (C) 2012  Maor Leger

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import numpy

__author__ = 'Maor Leger'

import sys, os, traceback, optparse
import time
import re
import subprocess as sub
import cPickle as pickle
#
#Some specs:
#first six columns are same as hw7.
#There is additional 7th column:
#Word    POS     BIO     TokenNumber     SentNumber      RoleLabel       ClassOfPredicate
#Role Label = {PRED, SUPPORT, ARG0, ARG1, ARG2, ARG3}
#ClassOfPredicate = {PARTITIVE-QUANT, PARTITIVE-PART, MERONYM, GROUP, SHARE, combination of these separated by /}
#
#Inventory of possible role labels (column 6) are dependent on the predicate class (column 7) - so column 7
#    is VERY important feature for predicting the possibilty of particular tags.
#
#There can be more than one of the same argument label for a given predicate.
#    - most common case: conjunction
#        - assumed that a conjoined phrase has 2 heads:
#        - ex: Time Warner/ARG0 's 50 %/ARG2 interest in Working Women/ARG1 and Working Mother/ARG1
#
#ARG3 is special - should also be treated as a dupe of ARG1:
#    - ex: Tiny next/ARG1 arteries of rats/ARG3
#    - for scoring - ARG1 and ARG3 should not be differentiated
#    - actually: ARG3 should not occur without an ARG1 => predicting an ARG1 is a necessary condition
#        for the occurence of ARG3
#
#
#Description of predicate classes:
#Partitive-Quant - same class as %
#    - Words represent multiple instances of an item, or a specific enumeration
#    - Includes over 200 distinct words: %, percent, 1/10, acre, array, jumble, quart, wave, watt, yen...
#    - Ex: newsstands are packed with a colorful array/PRED of magazines/ARG1
#Partitive-Part -
#    - ARG1 is a whole such that the whole phrase is a part of that whole
#    - Includes over 200 words: another, back, borough, component, ...
#    - Ex: Of the 11 components/PRED to the index/ARG1, only three others rose in September
#    - Includes meornyms:
#        - class = MERONYM/PARTITIVE-PART
#        - stronger roofs/PRED for light trucks/ARG1 and minivans/ARG1
#Group -
#    - PARTITIVE-QUANT except they have an ARG2 (approx: a leader of group)
#    - Over 60 words: army, association, bank, clan, troop,...
#    Ex: Robin/ARG2 's band/PRED of merry men/ARG1
#Share
#    - PARTITIVE-PART except they can have an ARG0 (owner) and an ARG2 (value)
#    - 13 words including: allotment, chunk, interest, niche, portion,...
#    - Ex: Time Warner/ARG0 's 50 %/ARG2 interest in Working Women/ARG1 and Working Mother/ARG1
#
#Argument definitions:
#ARG1 (or ARG3) possibilities:
#    - List of (i) set members or (ii) whole object that PRED is part of
#        - Ex:
#            - The 11 components/PRED to the index/ARG1
#            - The price/ARG1 rose/SUPPORT 5 %/PRED
#            - team of managers/ARG1
#            - team of editors/ARG1
#    - Description of a property of that set
#        - Ex:
#            - Management/ARG1 team
#            - editing/ARG1 team
#    - Possible to have both (a) and (b) simultaneously,
#        - In that case, mark one an ARG1 and the other an ARG3
#        - 5-editor/ARG1 management/ARG3 team
#
#ARG0 - Owner
#    - for SHARE nouns only
#    - ex: Mary/ARG0 's portion/PRED of the pizza/ARG1
#
#ARG2
#    - For SHARE nouns: Value (fraction, money, amount, etc) of share
#        - Ex: the largest/ARG2 chunk/PRED of Western Union/ARG1
#    - For GROUP nouns: Employer, leader or other pivotal entity
#        - Ex: California/ARG2 's assembly/PRED
#This list is NOT exhaustive!
#Sometimes idiosyncratic properties of particular words cause there to be additional argument types.
# From slides:
# ARG1: PARTITIVE-QUANT, GROUP, SHARE, PARTITIVE-PART
# ARG0: SHARE
# ARG2: SHARE, GROUP
# ARG3: Secondary theme ~~ ARG1
#
#
#Special labels: PRED and SUPPORT
#    - PRED marks the predicate of the relations. One example is generated for each predicate.
#    - SUPPORT marks words that connect the predicate with one or more of its arguments when they do not occur close by
#
#Choosing head of a phrase:
#    - For simple, common noun phrases and PPs with common NP objects:
#        - they choose the head noun
#        - ex: Dozens/PRED of travel books/ARG1
#    - For conjunctions, they mark each conjunct
#        - Ex: Dozens/PRED of tour books/ARG1 and travel magazines/ARG1
#    - For proper noun phrases and some similar cases
#        - they select the last "name" element of the phrase
#        - ex: The head/PRED of Anne Boleyn/ARG1
#    - There are rare cases when they choose head some other way. Limited effect on result.
#        - Ex: in a range expression, we use the word "to" as the head -
#            - Five percent/PRED of $374 to/ARG1 $375
#
#System guidelines:
#    - Many possible tasks
#    - May decide to simplify task in some way - make sure simplification is encoded in the scorer somehow
#        - Ex subtasks:
#            - Only predict ARG1s
#            - Limit to a particular subclass
#            - Use support tags in test for system output
#            - Predict your own support tags and don't use support tags in test etc
#    - Can write manual rule system, ML system, combination,etc
#    - provide clear description of whatever you do


fallBackCount = 0


class MaxEntRelationTagger():
    """The MaxEntRelationTagger class - contains everything needed to run a MaxEntRelationTagger tagger"""

    def __init__(self, devFileName, outFileName):
        """constructor for MaxEntRelationTagger"""
        self.trainingFileName = 'data/training'
        self.devFileName, self.outFileName = devFileName, outFileName
        self.testFileName, self.predictFileName = 'data/features.test', 'data/features.predictions'
        self.ARG0Classes = ['SHARE']
        self.ARG2Classes = ['SHARE', 'GROUP']
        self.ignoredClasses = ['PRED', 'SUPPORT']

    def readFile(self, fileName):
        """Reads a file and returns a list containing all the lines in the file"""
        inputFile = open(fileName, 'r')
        if not inputFile:
            print('error, input file cant be opened!')
            exit(1)
        return inputFile.readlines()


    def fixFileName(self, fileName):
        return os.path.join("data", re.sub(r'[/]', '_', fileName))

    def featureFileName(self, fileName):
        return self.fixFileName(fileName) + '.dat'

    def modelFileName(self, fileName):
        return self.fixFileName(fileName) + 'Model.txt'


    def TrainModel(self, numIterations, featureCutOff):
        """Trains the MaxEnt Model using Ang's MaxEnt wrapper"""
        print('Training model...\n')
        numIterations = str(numIterations)
        featureCutOff = str(featureCutOff)
        # TODO: REMOVE THIS BEFORE SUBMITTING!!!!!!!!
        try:
            self.taggedList = pickle.load(open("data/taggedList.pickle"))
            print('PICKLE successfully loaded')
        except IOError:
            print('Couldnt load PICKLE')
            raw = self.readFile(self.trainingFileName)
            self.taggedList = self.getTaggedList(raw)
            #self.taggedList = self.getTaggedList(raw)
        classNames = set([item[6] for item in self.taggedList if len(item) > 5 and item[5] == 'PRED'])
        openFiles = {}
        for item in classNames:
            openFiles[item] = open(self.featureFileName(item), 'w')
        oneSent = []
        #dataFile = open(self.featuresFileName, 'w')
        totalSents = 10263
        i = 0
        className = 'None'
        for item in self.taggedList:
            if item:
                oneSent.append(item)
                if item[5] == 'PRED':
                    className = item[6]
            else:
                i += 1
                #print('i={0} %completed={1}'.format(i, float(i) / totalSents))
                if className != 'None':
                    self.writeAllWordFeatures(oneSent, openFiles[className], True, True)
                oneSent = []
                className = 'None'
        for fileName, openFile in openFiles.iteritems():
            openFile.close()
            print(
                'Running java -jar -Xmx1024m MaxEntCreatModel.jar {0} {1} {2}'.format(self.featureFileName(fileName),
                                                                                      numIterations,
                                                                                      featureCutOff))
            sub.call(
                ["java", "-jar", "-Xmx1024m", "MaxEntCreatModel.jar", self.featureFileName(fileName), numIterations,
                 featureCutOff], stdout = sub.PIPE)

        print('Done training...\n')


    def getTaggedList(self, raw):
        """ Takes a list of raw texts and returns a list of tuples, where each tuple is created from
        the raw text"""

        # taggedList = list of tuples of (word, POS, NETag, wordNum, sentNum, relation or None)
        taggedList = []
        for line in raw:
            l = line.split()
            if len(l) == 5:
                l.append('None')
            if len(l) == 6:
                l.append('None')
            taggedList.append(tuple(l))
        pickleFile = open("data/taggedList.pickle", "w")
        pickle.dump(taggedList, pickleFile)
        pickleFile.close()
        return taggedList

    def getFeatures(self, firstItemIndex, secondItemIndex, spList):
        """A method to collect features between two tokens. Returns a dictionary of features extracted"""
        candPredInSameNP = candPredInSameVP = candPredInSamePP = False
        existSupportBetweenCandPred = existVerbBetweenCandPred = False

        # tokensBetweenCandPred
        tokensBetween = spList[0][firstItemIndex:secondItemIndex + 1]
        tokensBetweenCandPred = '_'.join(tokensBetween)

        # numberOfTokensBetween
        numberOfTokensBetween = len(tokensBetween)

        # possBetweenCandPred
        tokensBetween = spList[1][firstItemIndex:secondItemIndex + 1]
        possBetweenCandPred = '_'.join(tokensBetween)

        # existVerbBetweenCandPred
        for item in tokensBetween:
            if item.startswith('VB'):
                existVerbBetweenCandPred = True

        # BIOChunkChain
        tokensBetween = spList[2][firstItemIndex:secondItemIndex + 1]
        BIOChunkChain = '_'.join(tokensBetween)

        # ChunkChain
        ChunkChain = [re.sub(r'[A-Za-z]-', '', tokensBetween[0])]

        # candPredInSameNP
        if ChunkChain[0] == 'NP':
            candPredInSameNP = True
            for item in tokensBetween[1:]:
                if item.startswith('B') or item == 'O':
                    candPredInSameNP = False
                    break
        # candPredInSamePP
        elif ChunkChain[0] == 'PP':
            candPredInSamePP = True
            for item in tokensBetween[1:]:
                if item.startswith('B') or item == 'O':
                    candPredInSamePP = False
                    break
        # candPredInSameVP
        elif ChunkChain[0] == 'VP':
            candPredInSameVP = True
            for item in tokensBetween[1:]:
                if item.startswith('B') or item == 'O':
                    candPredInSameVP = False
                    break
        for i in xrange(1, len(tokensBetween) - 1):
            item = tokensBetween[i]
            if item.startswith('B'):
                ChunkChain.append(item[2:])
            elif item == 'O' and tokensBetween[i - 1] != 'O':
                ChunkChain.append('O')
        ChunkChain = '_'.join(ChunkChain)

        # existSupportBetweenCandPred
        tokensBetween = spList[5][firstItemIndex:secondItemIndex + 1]
        if tokensBetween.count('SUPPORT') > 0:
            existSupportBetweenCandPred = True

        return {
            'tokensBetweenCandPred': tokensBetweenCandPred,
            'numberOfTokensBetween': numberOfTokensBetween,
            'possBetweenCandPred': possBetweenCandPred,
            'existVerbBetweenCandPred': existVerbBetweenCandPred,
            'BIOChunkChain': BIOChunkChain,
            'ChunkChain': ChunkChain,
            'candPredInSameNP': candPredInSameNP,
            'candPredInSameVP': candPredInSameVP,
            'candPredInSamePP': candPredInSamePP,
            'existSupportBetweenCandPred': existSupportBetweenCandPred
        }


    def writeOneWordFeatures(self, i, outputFile, sent, listOutput = False, MEMMTagGuess = None):
        featuresDict = {
            'candToken': sent[i][0],
            'candTokenPOS': sent[i][1]
        }
        if listOutput:
            if sent[i][5] in ['ARG0', 'ARG1', 'ARG2', 'ARG3']:
                featuresDict['output'] = sent[i][5]
            else:
                featuresDict['output'] = 'None'
        else:
            featuresDict['output'] = '?'
        if i > 0:
            # can use token before candidate
            featuresDict['tokenBeforeCand'] = sent[i - 1][0]
            featuresDict['posBeforeCand'] = sent[i - 1][1]
            # added to convert MaxEnt model to MEMM
            if MEMMTagGuess is None:
                featuresDict['MEMMBeforeCand'] = sent[i - 1][5]
            else:
                featuresDict['MEMMBeforeCand'] = MEMMTagGuess
        if i < len(sent) - 1:
            # can use token after candidate
            featuresDict['tokenAfterCand'] = sent[i + 1][0]
            featuresDict['posAfterCand'] = sent[i + 1][1]
        spList = zip(*sent)
        if spList[5].count('PRED') > 0:
            predIndex = spList[5].index('PRED')
            if spList[6][predIndex] != 'None':
                #featuresDict['predToken'] = spList[0][predIndex]
                featuresDict['relationClass'] = spList[6][predIndex]
            if i < predIndex:
                featuresDict.update(self.getFeatures(i, predIndex, spList))
            else:
                featuresDict.update(self.getFeatures(predIndex, i, spList))
        outputFile.write('{0} {1}\n'.format(" ".join(
            ['%s=%s' % (key, value) for key, value in featuresDict.iteritems() if
             key != 'output' and value != '']), featuresDict['output']))

    def writeAllWordFeatures(self, sent, outputFile, listOutput = False, limitedSet = False, MEMMTagGuess = None):
        """Extracts features for each token in the sentence and writes those features to the output file
        Used in 2 ways:
        1. To train a model by appending the outcome at the end of the feature list
        2. To run the model on a list of features by appending ? at the end of the feature list
        """

        # Only consider negative samples if the POS is in negPOSSampleList

        negPOSSampleList = ['NN', 'NNS', 'NNP', 'VBD', 'PRP$', 'JJ', 'IN', 'VB', 'VBN', 'VBG', 'VBZ', 'CD', 'PRP',
                            'NNPS', 'VBP', 'DT', 'JJR', 'WP$', 'WP', 'RBR', 'RB', 'JJS', 'WDT', 'TO', '$', 'WRB', '``']
        for i in xrange(0, len(sent)):
            if not limitedSet or (sent[i][5] in ['ARG0', 'ARG1', 'ARG2', 'ARG3'] or sent[i][1] in negPOSSampleList):
                # kept limited set of negative samples... see commit
                self.writeOneWordFeatures(i, outputFile, sent, listOutput, MEMMTagGuess)


    def GetPredictions(self, test, model, predict):
        """Calls Ang's wrapper to get predictions"""
        sub.call(["java", "-jar", "-Xmx512m", "MaxEntPredict.jar", test, model,
                  predict], stdout = sub.PIPE)

    def MEMMTagFile(self):
        """Tags an entire file by calling TagSentence on each sentence"""
        raw = self.readFile(self.devFileName)
        outFile = open(self.outFileName, 'w')
        tokenList = []
        className = 'None'
        for line in raw:
            line = line.strip().split()
            if not line:
                print ('tagging sentence: {0}'.format(' '.join([tokenList[i][0] for i in xrange(0, len(tokenList))])))
                t = time.time()
                self.MEMMTagSentence(tokenList, className, outFile)
                print('time to tag in minutes: ', (time.time() - t) / 60.0)
                tokenList = []
                outFile.write('\n')
                className = 'None'
            else:
                # guarantee that each token in tokenList has 7 items exactly.
                if len(line) == 5:
                    line.append('None')
                if len(line) == 6:
                    line.append('None')
                if 7 > len(line) > 0:
                    raise Exception("Something went wrong... line: {0}".format(line))
                if line[5] == 'PRED':
                    className = line[6]
                tokenList.append(tuple(line))
        if len(tokenList) > 0:
            print ('tagging sentence: {0}'.format(' '.join([tokenList[i][0] for i in xrange(0, len(tokenList))])))
            # get the className
            className = [line[6] for line in tokenList if line[5] == 'PRED']
            if not className or className[0] == 'None':
                raise Exception("Something went wrong at the end of the file. TokenList = {0}".format(tokenList))
            className = className[0]
            self.MEMMTagSentence(tokenList, className, outFile)
        outFile.close()
        print('Done tagging... Out of the total, {0} sentences fell back to MaxEnt'.format(fallBackCount))

    def MEMMTagSentence(self, tokenList, className, outFile):
        li = [item[5] for item in tokenList]
        if not li.count('PRED'):
            for item in tokenList:
                (word, POS, BIO, wordNum, sentNum, keyTag) = item[:6]
                keyTag = keyTag.replace('None', '')
                outFile.write(
                    '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n'.format(word, POS, BIO, wordNum, sentNum, keyTag))
            return
        stateList = {0: '<s>', 1: 'ARG0', 2: 'ARG1', 3: 'ARG2', 4: 'ARG3', 5: 'None', 6: 'PRED', 7: 'SUPPORT',
                     8: '<qF>'}
        N = len(stateList)
        T = len(tokenList)
        predPos = li.index('PRED')
        if li.count('SUPPORT'):
            supportPos = [i for i, val in enumerate(li) if val == 'SUPPORT']
        else:
            supportPos = None
        viterbi = numpy.zeros((N, T + 2), dtype = numpy.object)
        path = {}
        prevMEMMTag = 'None'
        # first column, put a 1.0 in start symbol
        viterbi[0, 0] = 1.0

        testFile = open(self.testFileName, 'w')
        self.writeOneWordFeatures(0, testFile, tokenList, MEMMTagGuess = 'None')
        for i in xrange(1, len(tokenList)):
            for j in xrange(1, len(stateList) - 1):
                self.writeOneWordFeatures(i, testFile, tokenList, MEMMTagGuess = stateList[j])

        testFile.close()

        AllMaxEntValues = {0: {}}
        for i in xrange(1, len(tokenList)):
            AllMaxEntValues[i] = {}
        i = 1
        tokenIndex = 0
        otherState = stateList[i]
        for item in self.getMaxEntValues(className):
            if not tokenIndex:
                # only one row to get back because we are in the first token
                AllMaxEntValues[tokenIndex]['None'] = item
                tokenIndex += 1
            else:
                AllMaxEntValues[tokenIndex][otherState] = item
                i += 1
                if i % 8 == 0:
                    tokenIndex += 1
                    i += 1 # to skip the <s> tag
                otherState = stateList[i % 8]

        MaxEntValues = AllMaxEntValues[0]
        for s in xrange(1, N - 1):
            state = stateList[s]
            if MaxEntValues.has_key(state):
                viterbi[s, 1] = MaxEntValues[state]['None']
            else:
                viterbi[s, 1] = 0.0
            path[(s, 1)] = 0

        # find most likely tag
        prob, prevMEMMTag = None, 'None'
        for s in xrange(1, N - 1):
            if viterbi[s, 1] > prob:
                prob, prevMEMMTag = viterbi[s, 1], stateList[s]


        # 3rd column to 2nd to last column
        for ts in xrange(2, T + 1):
            # for each column, get the word features, then feed it to the MaxEnt wrapper, then get results
            # which will be used in the viterbi algorithm
            if ts - 1 == predPos:
                # we are in the predicate
                viterbi[6, ts] = 1.0
                for key, value in stateList.iteritems():
                    if value == prevMEMMTag:
                        path[(6, ts)] = key
                        prevMEMMTag = 'PRED'
                        break
                continue
            elif supportPos is not None and ts - 1 in supportPos:
                # we are in the support
                viterbi[7, ts] = 1.0
                for key, value in stateList.iteritems():
                    if value == prevMEMMTag:
                        path[(7, ts)] = key
                        prevMEMMTag = 'SUPPORT'
                        break
                continue
            MaxEntValues = AllMaxEntValues[ts - 1][prevMEMMTag]

            for s in xrange(1, N - 1):
                if MaxEntValues.has_key(stateList[s]):
                    viterbi[s, ts] = None
                    argmax = ()

                    for sp in xrange(1, N - 1):
                    # prob = V_{t-1}(sp) * P(s_j | s_sp, o_t) for 1<=j<=N, 1<t<=T
                    # we find the maximum value for prob for sp=1 to N-1
                        prob = viterbi[sp, ts - 1] * MaxEntValues[stateList[s]]
                        if viterbi[s, ts] < prob:
                            viterbi[s, ts] = prob
                            argmax = (sp, ts - 1)
                    path[(s, ts)] = argmax[0]

            # find the most likely state for the current observation
            prob = None
            for s in xrange(1, N - 1):
                if viterbi[s, ts] > prob:
                    prob, prevMEMMTag = viterbi[s, ts], stateList[s]

        # final column, just need to find the state from previous column
        viterbi[N - 1, T + 1] = None
        argmax = ()
        for s in xrange(1, N - 1):
            prob = viterbi[s, T]
            if viterbi[N - 1, T + 1] < prob:
                viterbi[N - 1, T + 1] = prob
                argmax = (s, T)
        path[(N - 1, T + 1)] = argmax[0]
        self.writeTaggedOutputToFile(path, outFile, tokenList, stateList, className)


    def getMaxEntValues(self, className):
        """Calls Ang's wrapper, opens the prediction file, and returns a dictionary
        of {tokenPosition: (NoneProb, ARG1Prob)}"""
        self.GetPredictions(self.testFileName, self.modelFileName(className),
                            self.predictFileName)
        prediction = open(self.predictFileName)
        values = prediction.read().splitlines()
        icoll = iter(values)
        for item in icoll:
            retVal = {}
            item = item.split()
            for i in item:
                var1 = i.split('[')
                var2 = float(var1[1].split(']')[0])
                retVal[var1[0]] = var2
            yield retVal

    def writeTaggedOutputToFile(self, path, outFile, tokenList, stateList, className):
        global fallBackCount
        states = path.keys()
        states.sort(key = lambda x: x[1])
        states.reverse()
        wordTagsList = []
        currentState = states[0]
        currentState = (path[currentState], currentState[1] - 1)
        while currentState != (0, 0):
            wordTagsList.append(stateList[currentState[0]])
            currentState = (path[currentState], currentState[1] - 1)
        wordTagsList.reverse()
        if not wordTagsList.count('ARG1'):
            # fall back to MaxEnt
            print('No ARG1 found using MEMM, falling back to MaxEnt model...')
            fallBackCount += 1
            self.MaxEntTagSentence(tokenList, className, outFile)
            return
        wordTagsList = zip(tokenList, wordTagsList)
        for ((word, POS, BIO, wordNum, sentNum, keyTag, keyClass), sysTag) in wordTagsList:
            keyTag = keyTag.replace('None', '')
            sysTag = sysTag.replace('None', '')
            keyClass = keyClass.replace('None', '')
            outFile.write(
                '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n'.format(word, POS, BIO, wordNum, sentNum, keyTag
                                                                  ,
                                                                  sysTag, keyClass))


    def MaxEntTagSentence(self, tokenList, className, outFile):
        """Finds the most probable ARG1 for a sentence and outputs the input with the system choice for ARG1"""
        testFile = open(self.testFileName, 'w')
        self.writeAllWordFeatures(tokenList, testFile)
        testFile.close()


        # Find the most probable ARG1
        # TODO: experiment if its better to use elif or regular ifs. with regular if statements the idea is that the same word can be guessed as two predicates. With elif the idea is that each token can only have at most one sysTag. Note: if choosing regular ifs we need to modify both if statemetns below (see TO DO2) AND scoring algorithm


        arg0Pos = arg1Pos = arg2Pos = arg3Pos = None
        # attempt to shimmy up initial probabilities so that only high scoring results will be registered
        arg1Prob = 0.01
        arg0Prob = 0.5
        arg2Prob = 0.5
        arg3Prob = 0.5
        pos = 0
        for value in self.getMaxEntValues(className):
            if tokenList[pos][5] in self.ignoredClasses:
                pos += 1
                continue
            if value.has_key('ARG0') and arg0Prob < value['ARG0'] > 0:
                arg0Prob = value['ARG0']
                arg0Pos = pos
            if value.has_key('ARG1') and arg1Prob < value['ARG1'] > 0:
                arg1Prob = value['ARG1']
                arg1Pos = pos
            if value.has_key('ARG2') and arg2Prob < value['ARG2'] > 0:
                arg2Prob = value['ARG2']
                arg2Pos = pos
            if value.has_key('ARG3') and arg3Prob < value['ARG3'] > 0:
                arg3Prob = value['ARG3']
                arg3Pos = pos
            pos += 1

        # TODO: figure out way to disambiguate between two competing tags
        for i in xrange(0, len(tokenList)):
            if 0 < len(tokenList[i]) < 7:
                raise Exception('Error: Invalid token. Token: {0}'.format(tokenList[i]))
            (word, POS, BIO, wordNum, sentNum, keyTag) = tokenList[i][:6]
            keyClass = tokenList[i][6].replace('None', '')
            keyTag = keyTag.replace('None', '')
            if keyTag in self.ignoredClasses:
                sysTag = keyTag
            elif i == arg0Pos:
                sysTag = 'ARG0'
            elif i == arg1Pos:
                sysTag = 'ARG1'
            elif i == arg2Pos:
                sysTag = 'ARG2'
            elif i == arg3Pos:
                sysTag = 'ARG3'
            else:
                sysTag = ''
            outFile.write(
                '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n'.format(word, POS, BIO, wordNum, sentNum, keyTag
                                                                  ,
                                                                  sysTag, keyClass))


def main():
    global options, args
    if len(args) < 2:
        print('Usage: python2.6 hw7.py [devFileName] [outputFileName]')
        exit(1)
    MaxEntTagger = MaxEntRelationTagger(args[0], args[1])
    MaxEntTagger.TrainModel(100, 2)
    MaxEntTagger.MEMMTagFile()

if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter = optparse.TitledHelpFormatter(), usage = globals()['__doc__'],
                                       version = '$')
        parser.add_option('-v', '--verbose', action = 'store_true', default = False, help = 'verbose output')
        (options, args) = parser.parse_args()
        if options.verbose: print (time.asctime())
        main()
        if options.verbose: print (time.asctime())
        if options.verbose: print ('TOTAL TIME IN MINUTES:',)
        if options.verbose: print ((time.time() - start_time) / 60.0)
        sys.exit(0)
    except KeyboardInterrupt as e: # Ctrl-C
        raise e
    except SystemExit as e: # sys.exit()
        raise e
    except Exception as e:
        print ('ERROR, UNEXPECTED EXCEPTION')
        print (str(e))
        traceback.print_exc()
        os._exit(1)



