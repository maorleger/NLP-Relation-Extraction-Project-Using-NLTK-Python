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

'''
Some specs:
first six columns are same as hw7.
There is additional 7th column:
Word    POS     BIO     TokenNumber     SentNumber      RoleLabel       ClassOfPredicate
Role Label = {PRED, SUPPORT, ARG0, ARG1, ARG2, ARG3}
ClassOfPredicate = {PARTITIVE-QUANT, PARTITIVE-PART, MERONYM, GROUP, SHARE, combination of these separated by /}

Inventory of possible role labels (column 6) are dependent on the predicate class (column 7) - so column 7
    is VERY important feature for predicting the possibilty of particular tags.

There can be more than one of the same argument label for a given predicate.
    - most common case: conjunction
        - assumed that a conjoined phrase has 2 heads:
        - ex: Time Warner/ARG0 's 50 %/ARG2 interest in Working Women/ARG1 and Working Mother/ARG1

ARG3 is special - should also be treated as a dupe of ARG1:
    - ex: Tiny next/ARG1 arteries of rats/ARG3
    - for scoring - ARG1 and ARG3 should not be differentiated
    - actually: ARG3 should not occur without an ARG1 => predicting an ARG1 is a necessary condition
        for the occurence of ARG3


Description of predicate classes:
Partitive-Quant - same class as %
    - Words represent multiple instances of an item, or a specific enumeration
    - Includes over 200 distinct words: %, percent, 1/10, acre, array, jumble, quart, wave, watt, yen...
    - Ex: newsstands are packed with a colorful array/PRED of magazines/ARG1
Partitive-Part -
    - ARG1 is a whole such that the whole phrase is a part of that whole
    - Includes over 200 words: another, back, borough, component, ...
    - Ex: Of the 11 components/PRED to the index/ARG1, only three others rose in September
    - Includes meornyms:
        - class = MERONYM/PARTITIVE-PART
        - stronger roofs/PRED for light trucks/ARG1 and minivans/ARG1
Group -
    - PARTITIVE-QUANT except they have an ARG2 (approx: a leader of group)
    - Over 60 words: army, association, bank, clan, troop,...
    Ex: Robin/ARG2 's band/PRED of merry men/ARG1
Share
    - PARTITIVE-PART except they can have an ARG0 (owner) and an ARG2 (value)
    - 13 words including: allotment, chunk, interest, niche, portion,...
    - Ex: Time Warner/ARG0 's 50 %/ARG2 interest in Working Women/ARG1 and Working Mother/ARG1

Argument definitions:
ARG1 (or ARG3) possibilities:
    - List of (i) set members or (ii) whole object that PRED is part of
        - Ex:
            - The 11 components/PRED to the index/ARG1
            - The price/ARG1 rose/SUPPORT 5 %/PRED
            - team of managers/ARG1
            - team of editors/ARG1
    - Description of a property of that set
        - Ex:
            - Management/ARG1 team
            - editing/ARG1 team
    - Possible to have both (a) and (b) simultaneously,
        - In that case, mark one an ARG1 and the other an ARG3
        - 5-editor/ARG1 management/ARG3 team

ARG0 - Owner
    - for SHARE nouns only
    - ex: Mary/ARG0 's portion/PRED of the pizza/ARG1

ARG2
    - For SHARE nouns: Value (fraction, money, amount, etc) of share
        - Ex: the largest/ARG2 chunk/PRED of Western Union/ARG1
    - For GROUP nouns: Employer, leader or other pivotal entity
        - Ex: California/ARG2 's assembly/PRED
This list is NOT exhaustive!
Sometimes idiosyncratic properties of particular words cause there to be additional argument types.

Special labels: PRED and SUPPORT
    - PRED marks the predicate of the relations. One example is generated for each predicate.
    - SUPPORT marks words that connect the predicate with one or more of its arguments when they do not occur close by

Choosing head of a phrase:
    - For simple, common noun phrases and PPs with common NP objects:
        - they choose the head noun
        - ex: Dozens/PRED of travel books/ARG1
    - For conjunctions, they mark each conjunct
        - Ex: Dozens/PRED of tour books/ARG1 and travel magazines/ARG1
    - For proper noun phrases and some similar cases
        - they select the last "name" element of the phrase
        - ex: The head/PRED of Anne Boleyn/ARG1
    - There are rare cases when they choose head some other way. Limited effect on result.
        - Ex: in a range expression, we use the word "to" as the head -
            - Five percent/PRED of $374 to/ARG1 $375

System guidelines:
    - Many possible tasks
    - May decide to simplify task in some way - make sure simplification is encoded in the scorer somehow
        - Ex subtasks:
            - Only predict ARG1s
            - Limit to a particular subclass
            - Use support tags in test for system output
            - Predict your own support tags and don't use support tags in test etc
    - Can write manual rule system, ML system, combination,etc
    - provide clear description of whatever you do


'''


def main():
    global options, args
    # TODO: Do something more interesting here...
    print ('Hello world!')

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
        