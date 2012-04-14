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
__author__ = 'Maor Leger'

import sys, os, traceback, optparse
import time
import re
import subprocess as sub
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






class MaxEntRelationTagger():
    """The MaxEntRelationTagger class - contains everything needed to run a MaxEntRelationTagger tagger"""

    def __init__(self, devFileName, outFileName):
        """constructor for MaxEntRelationTagger"""
        self.featuresFileName = 'features.dat'
        self.trainingFileName = 'training'
        self.devFileName, self.outFileName = devFileName, outFileName
        self.modelFileName, self.predictFileName, self.testFileName = 'featuresModel.txt', 'features.predictions', 'features.test'

    def readFile(self, fileName):
        """Reads a file and returns a list containing all the lines in the file"""
        inputFile = open(fileName, 'r')
        if not inputFile:
            print('error, input file cant be opened!')
            exit(1)
        return inputFile.readlines()


    def TrainModel(self, numIterations, featureCutOff):
        """Trains the MaxEnt Model using Ang's MaxEnt wrapper"""
        print('Training model...\n')
        numIterations = str(numIterations)
        featureCutOff = str(featureCutOff)
        raw = self.readFile(self.trainingFileName)
        self.taggedList = self.getTaggedList(raw)
        oneSent = []
        dataFile = open(self.featuresFileName, 'w')
        totalSents = 10263
        i = 0
        for item in self.taggedList:
            if item:
                oneSent.append(item)
            else:
                i += 1
                print('i={0} %completed={1}'.format(i, float(i) / totalSents))
                self.writeAllWordFeatures(oneSent, dataFile, True, True)
                oneSent = []
        dataFile.close()
        print(
        'Running java -jar -Xmx1024m MaxEntCreatModel.jar {0} {1} {2}'.format(self.featuresFileName, numIterations,
                                                                              featureCutOff))
        sub.call(
            ["java", "-jar", "-Xmx1024m", "MaxEntCreatModel.jar", self.featuresFileName, numIterations, featureCutOff])
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
        return taggedList

    def getFeatures(self, firstItemIndex, secondItemIndex, spList):
        """A method to collect features between two tokens. Returns a dictionary of features extracted"""
        candPredInSameNP = candPredInSameVP = candPredInSamePP = False
        existSupportBetweenCandPred = existVerbBetweenCandPred = False

        # tokensBetweenCandPred
        tokensBetween = spList[0][firstItemIndex + 1:secondItemIndex]
        tokensBetweenCandPred = '_'.join(tokensBetween)

        # numberOfTokensBetween
        numberOfTokensBetween = len(tokensBetween)

        # possBetweenCandPred
        tokensBetween = spList[1][firstItemIndex + 1:secondItemIndex]
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
        tokensBetween = spList[5][firstItemIndex + 1:secondItemIndex]
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


    def writeAllWordFeatures(self, sent, outputFile, listOutput = False, limitedSet = False):
        """Extracts features for each token in the sentence and writes those features to the output file
        Used in 2 ways:
        1. To train a model by appending the outcome at the end of the feature list
        2. To run the model on a list of features by appending ? at the end of the feature list
        """

        # Only consider negative samples if the POS is in negPOSSampleList
        negPOSSampleList = ['NN', 'NNS', 'NNP', 'JJ', 'PRP', 'CD', 'DT', 'NNPS', 'VBG', 'FW', 'IN', 'RB', 'VBZ', 'WDT',
                            'WP']
        for i in xrange(0, len(sent)):
            if not limitedSet or (sent[i][5] in ['ARG1'] or sent[i][1] in negPOSSampleList):
                featuresDict = {
                    'candToken': sent[i][0],
                    'candTokenPOS': sent[i][1]
                }
                if listOutput:
                    if sent[i][5] == 'ARG1':
                        featuresDict['output'] = 'ARG1'
                    else:
                        featuresDict['output'] = 'None'
                else:
                    featuresDict['output'] = '?'
                if i > 0:
                    # can use token before candidate
                    featuresDict['tokenBeforeCand'] = sent[i - 1][0]
                    featuresDict['posBeforeCand'] = sent[i - 1][1]
                if i < len(sent) - 1:
                    # can use token after candidate
                    featuresDict['tokenAfterCand'] = sent[i + 1][0]
                    featuresDict['posAfterCand'] = sent[i + 1][1]
                spList = zip(*sent)
                if spList[5].count('PRED') > 0:
                    predIndex = spList[5].index('PRED')
                    if i < predIndex:
                        featuresDict.update(self.getFeatures(i, predIndex, spList))
                    else:
                        featuresDict.update(self.getFeatures(predIndex, i, spList))
                    outputFile.write('{0} {1}\n'.format(" ".join(
                        ['%s=%s' % (key, value) for key, value in featuresDict.iteritems() if
                         key != 'output' and value != '']), featuresDict['output']))


    def GetPredictions(self):
        """Calls Ang's wrapper to get predictions"""
        sub.call(["java", "-jar", "-Xmx512m", "MaxEntPredict.jar", self.testFileName, self.modelFileName,
                  self.predictFileName], stdout = sub.PIPE)

    def MaxEntTagFile(self):
        """Tags an entire file by calling TagSentence on each sentence"""
        raw = self.readFile(self.devFileName)
        outFile = open(self.outFileName, 'w')
        tokenList = []
        lines = []
        for line in raw:
            line = line.strip().split()
            if len(line) == 5:
                line.append('None')
            if 5 > len(line) > 0:
                raise Exception
            lines.append(tuple(line))
        for line in lines:
            if not line:
                print ('tagging sentence: {0}'.format(' '.join([tokenList[i][0] for i in xrange(0, len(tokenList))])))
                self.MaxEntTagSentence(tokenList, outFile)
                tokenList = []
                outFile.write('\n')
            else:
                tokenList.append(line)
        if len(tokenList) > 0:
            print ('tagging sentence: {0}'.format(' '.join([tokenList[i][0] for i in xrange(0, len(tokenList))])))
            self.MaxEntTagSentence(tokenList, outFile)
        outFile.close()


    def MaxEntTagSentence(self, tokenList, outFile):
        """Finds the most probable ARG1 for a sentence and outputs the input with the system choice for ARG1"""
        testFile = open(self.testFileName, 'w')
        self.writeAllWordFeatures(tokenList, testFile)
        testFile.close()
        MaxEntValues = self.getMaxEntValues()

        # Find the most probable ARG1
        arg1Pos = None
        prob = None
        for key, value in MaxEntValues.iteritems():
            # value = (NoneProb, ARG1Prob)
            if value[1] > prob:
                prob = value[1]
                arg1Pos = key
        for i in xrange(0, len(tokenList)):
            if len(tokenList[i]) == 6:
                (word, POS, BIO, wordNum, sentNum, keyTag) = tokenList[i]
            else:
                (word, POS, BIO, wordNum, sentNum, keyTag, keyClass) = tokenList[i]
            keyTag = keyTag.replace('None', '')
            if i == arg1Pos:
                sysTag = 'ARG1'
            else:
                sysTag = ''
            outFile.write('{0} {1} {2} {3} {4} {5} {6}\n'.format(word, POS, BIO, wordNum, sentNum, keyTag, sysTag))


    def getMaxEntValues(self):
        """Calls Ang's wrapper, opens the prediction file, and returns a dictionary
        of {tokenPosition: (NoneProb, ARG1Prob)}"""
        self.GetPredictions()
        prediction = open(self.predictFileName)
        values = prediction.read().split()
        ret = {}
        for i in xrange(0, len(values), 2):
            var1 = values[i].split('[')
            var2 = values[i + 1].split('[')
            ret[i / 2] = (float(var1[1].split(']')[0]), float(var2[1].split(']')[0]))
        return ret


def main():
    global options, args
    if len(args) < 2:
        print('Usage: python2.6 hw7.py [devFileName] [outputFileName]')
        exit(1)
    MaxEntTagger = MaxEntRelationTagger(args[0], args[1])
    #MaxEntTagger.TrainModel(100, 2)
    MaxEntTagger.MaxEntTagFile()

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



