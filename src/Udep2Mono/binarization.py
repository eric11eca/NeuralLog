from pqdict import pqdict
from Udep2Mono.util import negate_mark


class BinaryDependencyTree:
    def __init__(self, val, left, right, key, counter, id=None, pos=None):
        self.val = val
        self.parent = None
        self.left = left
        self.right = right
        self.mark = "0"
        self.id = id
        self.pos = pos
        self.key = key
        self.is_root = False
        self.is_tree = True
        self.length = 0
        self.leaves = pqdict({})
        self.counter = counter
        self.replaced = {}

    def sorted_leaves(self):
        self.traverse(self)
        return self.leaves

    def traverse(self, tree, multi_word=False):
        if not tree.is_tree:
            replacement = False
            if str((tree.val, tree.id)) in self.replaced:
                tree.val = self.replaced[str((tree.val, tree.id))]
                replacement = True
            if "-" in tree.val and replacement and multi_word:
                words = tree.val.split('-')
                words.reverse()
                for i in range(len(words)):
                    word_id = tree.id - i * 0.1
                    key = (words[i], tree.pos, tree.mark, word_id)
                    if words[i].lower() == "not" and len(words) == 2:
                        key = (words[i], tree.pos,
                               negate_mark[tree.mark], word_id)
                    self.leaves[key] = (word_id)
            else:
                item = (tree.id)
                key = (tree.val, tree.pos, tree.mark, tree.id)
                self.leaves[key] = item
        else:
            self.traverse(tree.left)
            self.traverse(tree.right)

    def copy(self):
        left = None
        if self.left is not None:
            left = self.left.copy()
        right = None
        if self.right is not None:
            right = self.right.copy()
        new_tree = BinaryDependencyTree(
            self.val, left, right, self.key, self.counter, self.id, self.pos)
        new_tree.mark = self.mark
        new_tree.parent = self.parent
        new_tree.is_tree = self.is_tree
        new_tree.is_root = self.is_root
        new_tree.leaves = pqdict({})
        return new_tree

    def set_length(self, lth):
        self.length = lth

    def set_root(self):
        self.is_root = True

    def set_not_tree(self):
        self.is_tree = False


hierarchy = {
    "conj-sent": 0,
    "advcl-sent": 1,
    "advmod-sent": 2,
    "case": 10,
    "case-after": 75,
    "mark": 10,
    "expl": 10,
    "discourse": 10,
    "nsubj": 20,
    "csubj": 20,
    "nsubj:pass": 20,
    "conj-vp": 25,
    "ccomp": 30,
    "advcl": 30,
    "advmod": 30,
    "nmod": 30,
    "nmod:tmod": 30,
    "nmod:npmod": 30,
    "nmod:poss": 30,
    "xcomp": 40,
    "aux": 40,
    "aux:pass": 40,
    "obj": 60,
    "iobj": 60,
    "obl": 50,
    "obl:tmod": 50,
    "obl:npmod": 50,
    "cop": 50,
    "acl": 60,
    "acl:relcl": 60,
    "appos": 60,
    "conj": 60,
    "conj-np": 60,
    "conj-adj": 60,
    "det": 55,
    "det:predet": 55,
    "cc": 70,
    "cc:preconj": 70,
    "nummod": 75,
    "fixed": 80,
    "compound": 80,
    "compound:prt": 80,
    "fixed": 80,
    "amod": 75,
    "conj-n": 90,
    "conj-vb": 90,
    "dep": 100,
    "flat": 100,
    "goeswith": 100,
    "parataxis": 100
}


class UnifiedCounter:
    def __init__(self, initial_val=0):
        self.addi_negates = initial_val
        self.unifies = initial_val
        self.nsubjLeft = False
        self.expl = False
        self.willing_verb = False

    def add_negates(self):
        self.addi_negates += 1

    def add_unifies(self):
        self.unifies += 1

    def is_unified_clause_subj(self):
        return self.unifies % 2 == 1 and self.nsubjLeft


class Binarizer:
    def __init__(self, parse_table=None, postag=None, words=None):
        self.postag = postag
        self.parse_table = parse_table
        self.words = words
        self.id = 0
        self.counter = UnifiedCounter(0)
        self.replaced = {}

    def process_not(self, children):
        if len(children) > 1:
            if children[0][0] == "advmod":
                if self.words[children[1][1]][0] == "not":
                    return [children[1]]
        return children

    def compose(self, head):
        children = list(filter(lambda x: x[2] == head, self.parse_table))
        children.sort(key=(lambda x: hierarchy[x[0]]))
        children = self.process_not(children)

        if len(children) == 0:
            word = self.words[head][0]
            tag = self.words[head][1]
            binary_tree = BinaryDependencyTree(
                word, None, None, self.id, self.counter, head, tag)
            binary_tree.replaced = self.replaced
            self.id += 1
            binary_tree.set_not_tree()
            return binary_tree, [binary_tree.key]
        else:
            top_dep = children[0]
        self.parse_table.remove(top_dep)

        left, left_rel = self.compose(top_dep[1])
        right, right_rel = self.compose(top_dep[2])
        if "conj" in top_dep[0]:
            dep_rel = "conj"
        elif "case" in top_dep[0]:
            dep_rel = "case"
        elif "advcl" in top_dep[0]:
            dep_rel = "advcl"
        elif "advmod" in top_dep[0]:
            dep_rel = "advmod"
        else:
            dep_rel = top_dep[0]

        binary_tree = BinaryDependencyTree(
            dep_rel, left, right, self.id, self.counter)
        binary_tree.left.parent = binary_tree
        binary_tree.right.parent = binary_tree
        binary_tree.replaced = self.replaced

        left_rel.append(binary_tree.key)
        self.id += 1
        return binary_tree, left_rel + right_rel

    def binarization(self):
        self.id = 0
        self.relation = []
        root = list(filter(lambda x: x[0] == "root", self.parse_table))[0][1]
        self.counter = UnifiedCounter(0)
        binary_tree, relation = self.compose(root)
        binary_tree.set_root()
        binary_tree.length = len(self.words)
        return binary_tree, relation
