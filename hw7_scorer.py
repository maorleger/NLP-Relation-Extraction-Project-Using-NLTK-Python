"""
SYNOPSIS

    'python2.6 hw7_scorer' [-h,--help] [-v,--verbose] [--version] OutputFile

DESCRIPTION

    A simple scorer for hw7. Takes as input a file produced by hw7.py.
    Computes Precision, Recall, and F-Measure.
    Note: Since there is exactly 1 system ARG1 and exactly 1 key ARG1 Precision = Recall = F-Measure

EXIT STATUS

    0: program exited normally
    1: program exited with an error

AUTHOR

    Maor Leger

LICENSE

    hw7_scorer.py 
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


def score(outputFile):
    correct = 0
    lst = outputFile.readlines()
    for line in lst:
        lineTup = line.split()
        if lineTup:
            sentNum = lineTup[4]
            if len(lineTup) == 7:
                if lineTup[5] == lineTup[6] == 'ARG1':
                    correct += 1
    system = float(sentNum) + 1
    precision = correct / system
    recall = correct / system
    if recall > 0 < precision:
        fscore = 2/((1/recall) + (1/precision))
    elif recall > 0:
        fscore = 2/((1/recall))
    else:
        fscore = 0.0
    print('Number of sentences = {0}\t Number of tokens = {1}\n'.format(system, len([item for item in lst if item])))
    print('Precision = {0}\tRecall = {1}\tF-Score = {2}\n'.format(precision, recall, fscore))





def main():
    global options, args
    if len(args) < 1:
        print('Usage: python2.6 hw7_scorer.py [SystemOutputFileName]')
        exit(1)
    outputFile = open(args[0])
    score(outputFile)


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
    
        