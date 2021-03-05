from pattern.en import conjugate
import pandas as pd
import numpy as np

"""import json
with open('../data/synthetic1.jsonl', 'r') as syn:
    val_x = []
    val_y = []
    for line in syn.readlines():
        data = json.loads(line)
        val_x.append(data['question']['stem'])
        val_y.append(data['question']['output'])


pipeline = PolarizationPipeline(verbose=0)
i = 0
for i in range(len(val_x)):
    if i > 10:
        break
    annotation = pipeline.single_polarization(val_x[i])
    ann = list(annotation['annotated'].popkeys())
    ann = list(zip(*ann))
    polarity = ann[2]
    print(' '.join(ann[0]))
    print(' '.join(polarity))
    print(val_y[i].replace('u', '+').replace('e', '=').replace('d', '-'))
    tree1 = pipeline.postprocess(annotation["polarized_tree"], [])
    btree = Tree.fromstring(tree1.replace('[', '(').replace(']', ')'))
    jupyter_draw_nltk_tree(btree)"""

negate_mark = {
    "+": "-",
    "-": "+",
    "=": "="
}

det_mark = {
    "det:univ": "-",
    "det:exist": "+",
    "det:limit": "=",
    "det:negation": "-"
}

det_type_words = {
    "det:univ": ["all", "every", "each", "any", "all-of-the"],
    "det:exist": ["a", "an", "some", "double", "triple", "some-of-the", "al-least", "more-than"],
    "det:limit": ["such", "both", "the", "this", "that",
                  "those", "these", "my", "his", "her",
                  "its", "either", "both", "another"],
    "det:negation": ["no", "neither", "never", "none", "none-of-the", "less-than", "at-most"]
}

negtive_implicative = ["refuse", "reject", "oppose", "forget",
                       "hesitate", "without", "disapprove", "disagree",
                       "eradicate", "erase", "dicline", "eliminate",
                       "decline", "resist", "block", "stop", "hault",
                       "disable", "disinfect", "disapear", "disgard",
                       "disarm", "disarrange", "disallow", "discharge",
                       "disbelieve", "disclaim", "disclose", "disconnect",
                       "disconnect", "discourage", "discredit", "discorporate",
                       "disengage", "disentangle", "dismiss", "disobeye",
                       "distrust", "disrupt", "suspen", "suspend ",
                       "freeze",
                       ]

at_least_implicative = ["for", "buy", "drink", "take", "hold", "receive",
                        "get", "catch"]

exactly_implicative = ["like", "love", "admires", "marry"]


def build_implicative_dict():
    verbs = list(df['Verb'])
    signs = list(df['Signature'])
    implicatives = {}
    for i in range(len(verbs)):
        implicatives[verbs[i]] = signs[i]
    return implicatives


implicatives = {}  # build_implicative_dict()
imp_types = {
    '-': negtive_implicative,
    'at_least': at_least_implicative,
    '=': exactly_implicative
}


def is_implicative(word, imp_type):
    verb = conjugate(word, tense="present", person=1, number="singular")
    if imp_type in ['+', '-']:
        if verb in implicatives:
            return implicatives
    return verb in imp_types[imp_type]


def det_type(word):
    for det in det_type_words:
        if word.lower() in det_type_words[det]:
            return det


arrows = {
    "+": "\u2191",
    "-": "\u2193",
    "=": "=",
    "0": ""
}

arrow2int = {
    "\u2191": 1,
    "\u2193": -1,
    "=": 0
}


def btree2list(binaryDepdency, verbose=0):
    def to_list(tree):
        treelist = []
        if tree.is_tree:
            word = tree.val + arrows[tree.mark]
            if verbose == 2:
                word += str(tree.key)
            treelist.append(word)
        else:
            treelist.append(tree.pos)
            word = tree.val.replace('-', ' ') + arrows[tree.mark]
            if verbose == 2:
                word += str(tree.key)
            treelist.append(word)

        if tree.left is not None:
            treelist.append(to_list(tree.left))

        if tree.right is not None:
            treelist.append(to_list(tree.right))

        return treelist
    return to_list(binaryDepdency)


def annotation2string(annotation):
    annotated = list(annotation['annotated'].popkeys())

    def compose_token(word):
        if '-' in word[0]:
            orig = word[0].split('-')
            return ' '.join([x + arrows[word[2]] for x in orig])
        else:
            return word[0] + arrows[word[2]]
    annotated_sent = ' '.join([compose_token(x) for x in annotated])
    return annotated_sent


def arrow2int(word):
    if arrows['+'] in word:
        return 1
    elif arrows['-'] in word:
        return -1
    elif arrows['='] in word:
        return 0
