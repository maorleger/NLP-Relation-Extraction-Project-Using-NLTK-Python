"""
SYNOPSIS

    'project_scorer.py' [-h,--help] [-v,--verbose] [--version]

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

    project_scorer.py.py 
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


# TODO: Fix this issue. Seems like the following work:
# Key
# correct
# some system args arent being taken into account
#noinspection PyUnboundLocalVariable
def score(sysOutFile, keyOutFile):
    correct = 0
    key = 0
    system = 0
    sysOut = sysOutFile.readlines()
    keyOut = keyOutFile.readlines()
    if len(sysOut) <> len(keyOut):
        raise Exception("dev and output file are not of same length")
    for sysLine, keyLine in zip(sysOut, keyOut):
        sysTup = sysLine.split()
        keyTup = keyLine.split()
        if sysTup and keyTup:
            sentNum = sysTup[4]
        if len(keyTup) > 5 and keyTup[5] in ['ARG0', 'ARG1', 'ARG2', 'ARG3']:
            key += 1
        if len(sysTup) > 6 and sysTup[6] in ['ARG0', 'ARG1', 'ARG2', 'ARG3']:
            system += 1
            if sysTup[6] == sysTup[5]:
                correct += 1
        elif len(sysTup) == 6 and sysTup[5] in ['ARG0', 'ARG1', 'ARG2', 'ARG3']:
            if len(keyTup) < 6 or keyTup[5] not in ['ARG0', 'ARG1', 'ARG2', 'ARG3']:
                system += 1
    correct = float(correct)
    system = float(system)
    key = float(key)
    precision = correct / system
    recall = correct / key
    try:
        fscore = 2 / ((1 / recall) + (1 / precision))
    except ZeroDivisionError:
        if recall > 0.0:
            fscore = 2 / ((1 / recall))
        else:
            if precision > 0.0:
                raise Exception("Something went wrong...")
            fscore = 0.0
    print('Number of sentences = {0}\t Number of tokens = {1}\n'.format(int(sentNum) + 1,
                                                                        len([item for item in sysOut if item])))
    print('correct = {0}\tsystem = {1}\tkey = {2}\n'.format(correct, system, key))
    print('Precision = {0}\tRecall = {1}\tF-Score = {2}\n'.format(precision, recall, fscore))


def main():
    global options, args
    if len(args) < 2:
        print('Usage: python2.6 project_scorer.py SystemOutputFileName KeyFile')
        exit(1)
    sysOutFile = open(args[0])
    keyOutFile = open(args[1])

    score(sysOutFile, keyOutFile)

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

        