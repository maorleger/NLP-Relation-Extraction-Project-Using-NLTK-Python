from nltk.corpus import wordnet as wn

sent = [('But', 'CC', 'O', '0', '0', 'None', 'None'), ('about', 'IN', 'B-NP', '1', '0', 'None', 'None'),
    ('25', 'CD', 'I-NP', '2', '0', 'None', 'None'), ('%', 'NN', 'I-NP', '3', '0', 'PRED', 'PARTITIVE-QUANT'),
    ('of', 'IN', 'B-PP', '4', '0', 'None', 'None'), ('the', 'DT', 'B-NP', '5', '0', 'None', 'None'),
    ('insiders', 'NNS', 'I-NP', '6', '0', 'ARG1', 'None'), ('COMMA', 'COMMA', 'O', '7', '0', 'None', 'None'),
    ('according', 'VBG', 'B-PP', '8', '0', 'None', 'None'), ('to', 'IN', 'B-PP', '9', '0', 'None', 'None'),
    ('SEC', 'NNP', 'B-NP', '10', '0', 'None', 'None'), ('figures', 'NNS', 'I-NP', '11', '0', 'None', 'None'),
    ('COMMA', 'COMMA', 'O', '12', '0', 'None', 'None'), ('file', 'VBP', 'O', '13', '0', 'None', 'None'),
    ('their', 'PRP$', 'B-NP', '14', '0', 'None', 'None'), ('reports', 'NNS', 'I-NP', '15', '0', 'None', 'None'),
    ('late', 'RB', 'B-ADVP', '16', '0', 'None', 'None'), ('.', '.', 'O', '17', '0', 'None', 'None')]
tokensBetween = ('of', 'the', 'insiders', 'COMMA')
synsets = wn.synsets('cake')
print('_'.join(set([synset.lexname for synset in synsets])))
# Print the information
for synset in synsets:
    print "-" * 10
    print "Name:", synset.name
    print "Lexical Type:", synset.lexname
    print "Lemmas:", synset.lemma_names
    print "Definition:", synset.definition
    for example in synset.examples:
        print "Example:", example