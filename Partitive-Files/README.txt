I. General Description 

   These files are annotated with the relations between predicates and
   their arguments for a set of approximately 500 different words. All
   these words are in the same or similar classes as % (the percent
   sign) that was the predicate used for HW7. These words fall into
   several classes of nouns have different (but similar) sets of
   arguments. All such nouns take an ARG1 which is, in some sense,
   quantified by the head noun, i.e., the noun phrase represents a
   multiple or a fraction of the ARG1. In the training set, there are
   over 10 thousand instances of predicates. There are over 300
   instances in the dev corpus. We will withhold the test set, as
   before, unless you have modified the task sufficiently that a blind
   test is not practical.

II. Specifications

1. As with the HW tasks, the data is presented in a one-word-per-line
   format with blank lines between sentences. The format is an
   extension of the homework 7 format. However, these files were
   generated with different considerations in mind. In addition to the
   differences noted below, there may also be minor differences in
   part of speech or other tags.

2. The first six columns are essentially the same as HW 7, but there
   is an additional seventh column. The columns are as follows:

   Column     Function
   1	      Word
   2	      POS
   3	      Begin/Inside/Other (BIO) Chunk tag
   4	      Token Number
   5	      Sentence Number
   6	      Role Label (Pred, Support, ARG0, ARG1, ARG2, ARG3)

   7 	      Class of Predicate (PARTITIVE-QUANT, PARTITIVE-PART, 
   	      MERONYM, GROUP, SHARE or a combination separated by "/")

3. Chunk tags (slightly different than HW7
     * Beginining of Chunk Tags: B-ADJP B-ADVP B-CONJP B-INTJ B-LST
       		  B-NP B-PP B-PRT B-SBAR B-VP
     * Inside Chunk Tags: I-ADJP I-ADVP I-CONJP I-NP I-PP I-SBAR I-VP
     * Other Constituents: O
   As before, these represent beginning of groups, not full consituents. 
   Examples:
       * Because/B-PP of/I-PP the/B-NP flood/I-NP
       		    -- "because of" is a preposition group, not a PP
       * to/B-VP have/I-VP eaten/I-VP a/B-NP sandwich/I-NP
       	       	    -- "to have eaten" is a Verb Group, not a VP

4. The inventory of possible role labels (column 6) are dependent on
   the predicate class (column 7). This makes column 7 a very
   important feature for predicting the probability of particular tags.

   -- Labels for Column 7
      * PRED = Marks instances of the predicate
      * ARG0, ARG1, ARG2, ARG3 = Marks the "head" of an argument
      * SUPPORT = Marks a verb or noun that links the predicate to its argument

5. There can be more than one of the same argument label for a given
   predicate, e.g., a single instance of % or other predicate can have
   multiple ARG1s. The most common case is for conjunction, where (for
   this task), it is assume that a conjoined phrase has two heads, e.g.,

   -- Time Warner/ARG0 's 50 %/ARG2 interest in Working Women/ARG1 and Working Mother/ARG1

6. ARG3 is special in that it should also be treated as a duplicate of
   ARG1. In Nombank, it is called a secondary-theme, e.g., 

   -- Tiny neck/ARG1 arteries of rats/ARG3

   The arteries are both part of the neck and part of the rats. For
   purposes of scoring ARG1 and ARG3 should not be differentiated for
   these classes. 

   In fact, an ARG3 should not occur without an ARG1 (thus predicting
   an ARG1 is a necessary condition for the occurance of ARG3).

7. Description of Predicate Classes

   Partitive-Quant (the same class as %). Words represent multiples of
   instances of an item, or a specific enumeration, even if partial
   (like %). 

   -- Includes over 200 distinct words: %, percent, 1/10, acre, array,
      jumble, quart, wave, watt, yen, … 

   -- Example: Newsstands are packed with a colorful array/PRED of magazines/ARG1 .

   Partitive-Part – ARG1 is a whole such that the whole phrase is a
   part of that whole.

   -- Includes over 200 words including: anther, back,  borough, component, …

   -- Example: Of the 11 components/PRED to the index/ARG1 , only three others rose in September 

   -- This class includes meronyms (the class MERONYM/PARTITIVE-PART), which
      are idiosyncratic part-of cases
         * Example: stronger roofs/PRED for light trucks/ARG1 and minivans/ARG1

   Group – These are like Partitive-Quant, except they can have an ARG2 (approx: a leader of group)

   -- Over 60 words including: army, association, band, clan, troop, …
   -- Example:Robin/ARG2's band/PRED of merry men/ARG1

   Share – These are like Partitive-Part, except they can have an ARG0 (owner) and an ARG2 (value)

    -- 13 words including: allotment, chunk, interest, niche, portion, … 
    -- Example: Time Warner/ARG0 's 50 %/ARG2 interest in Working Women/ARG1 and Working Mother/ARG1

8. Some argument definitions

   ARG1 (or ARG3): Possibilities:
   	(a) List of (i) set members or (ii) whole object that PRED is part of
	    -- Examples: 
	       * the 11 components/PRED to the index/ARG1
	       * The price/ARG1 rose/SUPPORT 5 %/PRED
               * team of managers/ARG1
	       * team of editors/ARG1
	(b) Description of a property of that set
	    -- Examples:
	       * management/ARG1 team
	       * editing/ARG1 team
        (c) It is possible to have both (a) and (b) simultaneusly,
            marking one an ARG1 and the other an ARG3
	       * 5-editor/ARG1 management/ARG3 team 

   ARG0 -- Owner (SHARE nouns only)
   	-- Example: Mary/ARG0 's portion/PRED of the pizza/ARG1

   ARG2 for SHARE nouns: Value (fraction, money amount, etc.) of share
   	-- Example: the largest/ARG2 chunk/PRED of Western Union/ARG1

   ARG2 for Group nouns: Employer, leader or other pivotal entity
   	-- Example: California/ARG2 's assembly/PRED

   Note that this list is not exhaustive as the idiosyncratic
   properties of particular words sometimes cause there to be
   additional argument types, e.g., there are some ARG2s for words in
   the PARTICLE-PART and PARTICLE-QUANT classes with meanings
   idiosyncratic to those nouns.

9. Special labels PRED and SUPPORT

   PRED marks the predicate of the relation. One example is generated for each predicate.

   SUPPORT marks words that connect the predicate with one or more of
   	   its arguments when they do not occur close by (see Examples above).

10. Choosing the head of a phrase: Since we are only marking the heads
   of arguments, you should understand our choice of head. This is
   somewhat simplified because the vast majority of cases are NPs or
   PPs (in which case we mark the object of the preposition). 

   (a) For simple, common noun phrases and PPs with common noun phrase
       objects, we simply choose the head noun.
 
       Example: "Dozens/PRED of travel books/ARG1"

   (b) For conjunctions, we mark each conjunct.

       Example: Dozens/PRED of tour books/ARG1 and travel magazines/ARG1

   (c) For proper noun phrases and some similar cases (number phrases,
       dates), we select the last "name" element of the phrase.

       Example: The head/PRED of Anne Boleyn/ARG1

   (d) There are some very rare cases where we select the head in some
       other way. We suspect that they will have a limited effect on
       the result. Here is one such example: In a range expressions,
       we use the word "to" as the head.

       Example: Five percent/PRED of $374 to/ARG1 $375 

III. Some System Guidelines

1. There may be some errors in this data (it is based on manual
   annotation). Part of your job is to make your system work as well
   as possible given the data.

2. There are many possible tasks that you can do with these data. You
   may decide to simplify the task in some way. Your simplification or
   subtask should be encoded into the scorer that you use, so that way
   it is possible for us to run on the test data. As mentioned above,
   if a blind test is not practical, we can give you the test data (to
   modify or run yourself). However, running a blind test has its
   advantages as well.

   Example Subtasks: Only predict ARG1s; Limit to a particular
   subclass; Use Support tags in test for system output; Predict your
   own support tags and don't use support tags in test for system
   output; etc.

3. System Output can be in the same format as input. However, if it is
   in some other format, you must provide clear specifications, so we
   know what you are doing.

4. Please feel free to write a manual-rule-based system, a ML-based
   system, a combination, etc. However, please provide a clear
   description of whatever you do; and please provide clear
   instructions for running your system and your scoring program.
