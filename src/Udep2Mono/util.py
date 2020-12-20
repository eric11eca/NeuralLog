import heapq
from pattern.en import conjugate

relations = [
    "acl",
    "acl:relcl",
    "advcl",
    "advmod",
    "advmod:count",
    "amod",
    "appos",
    "aux",
    "aux:pass",
    "case",
    "cc",
    "cc:preconj",
    "ccomp",
    "clf",
    "compound",
    "compound:prt",
    "conj",
    "cop",
    "csubj",
    "csubj:pass",
    "dep",
    "det",
    "det:predet",
    "discourse",
    "dislocated",
    "expl",
    "fixed",
    "flat",
    "goeswith",
    "iobj",
    "list",
    "mark",
    "nmod",
    "nmod:poss",
    "nmod:npmod",
    "nmod:tmod",
    "nmod:count",
    "nsubj",
    "nsubj:pass",
    "nummod",
    "obj",
    "obl",
    "obl:npmod",
    "obl:tmod",
    "orphan",
    "parataxis",
    "punct",
    "reparandum",
    "root",
    "vocative",
    "xcomp"
]

negate_mark = {
    "+": "-",
    "-": "+",
    "=": "="
}

det_mark = {
    "det:univ": ("+", "-"),
    "det:exist": ("+", "+"),
    "det:limit": ("+", "="),
    "det:negation": ("+", "-")
}

det_type_words = {
    "det:univ": ["all", "every", "each", "any"],
    "det:exist": ["a", "an", "some", "double", "triple"],
    "det:limit": ["such", "both", "the", "this", "that",
                  "those", "these", "my", "his", "her",
                  "its", "either", "both", "another"],
    "det:negation": ["no", "neither", "never", "few"]
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
                       "freeze", "remove", "regret", "object", "impossible",
                       "hate"
                       ]

at_least_implicative = ["smoke", "for", "buy", "drink", "take", "hold", "receive",
                        "get", "catch"]

exactly_implicative = ["like", "love", "admires", "marry"]


def is_implicative(verb, imp_type):
    return conjugate(verb, tense="present", person=1, number="singular") in imp_type


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


def btreeToList(binaryDepdency, length, replaced, verbose=2):
    annotated = []
    postags = []
    reverse = {}

    def toList(tree):
        treelist = []
        if tree.getVal() not in relations:
            treelist.append(tree.npos)
            if tree.getVal() == "n't":
                tree.val = "not"
            if tree.val in replaced.keys():
                original = replaced[tree.val].split()
                new = []
                for word in original:
                    new.append(word + arrows[tree.mark])
                reverse[tree.val + arrows[tree.mark]
                        ] = '%s' % ', '.join(map(str, new)).replace(",", " ")
            word = tree.getVal() + arrows[tree.mark]
            if verbose == 2:
                word += str(tree.key)
            index = tree.id
            heapq.heappush(annotated, (int(index), word))
            heapq.heappush(postags, (int(index), tree.npos))
            treelist.append(word)
        else:
            word = tree.getVal() + arrows[tree.mark]
            if verbose == 2:
                word += str(tree.key)
            treelist.append(word)

        left = tree.getLeft()
        right = tree.getRight()

        if left is not 'N':
            treelist.append(toList(left))

        if right is not 'N':
            treelist.append(toList(right))

        return treelist
    return toList(binaryDepdency), annotated, postags, reverse


def convert2vector(result):
    result_vec = []
    if type(result) is "str":
        result_ls = result.split()
    else:
        result_ls = result
    for word in result_ls:
        if arrows['+'] in word:
            result_vec.append(1)
        elif arrows['-'] in word:
            result_vec.append(-1)
        elif arrows['='] in word:
            result_vec.append(0)
    return result_vec
