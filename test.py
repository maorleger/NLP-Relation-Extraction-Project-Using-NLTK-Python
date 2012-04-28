"""
SYNOPSIS

    'test' [-h,--help] [-v,--verbose] [--version]

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

    test.py 
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

__author__ = 'mleger'

import sys, os, traceback, optparse
import time
import cPickle as pickle

argList = ['ARG0', 'ARG1', 'ARG2', 'ARG3']
classCounts = {}

def analyze(sentence, outFile):
    args = zip(*sentence)
    if not args[5].count('PRED'):
        return
    className = args[6][args[5].index('PRED')]
    arg0Count = args[5].count('ARG0')
    arg1Count = args[5].count('ARG1')
    arg2Count = args[5].count('ARG2')
    arg3Count = args[5].count('ARG3')
    sentNum = int(args[4][0])
    if classCounts.has_key(className):
        classCount = classCounts[className]
        if classCount.has_key('ARG0'):
            classCount['ARG0'] += arg0Count
        elif arg0Count:
            classCount['ARG0'] = arg0Count
        if classCount.has_key('ARG2'):
            classCount['ARG2'] += arg2Count
        elif arg2Count:
            classCount['ARG2'] = arg2Count


def main():
    global options, args
    trainingFile = open('data/training')
    outFile = open('data/training-filled', 'w')
    taggedList = pickle.load(open("data/taggedList.pickle"))
    sentence = []
    for tup in taggedList:
        if tup:
            sentence.append(tup)
        else:
            analyze(sentence, outFile)


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

        