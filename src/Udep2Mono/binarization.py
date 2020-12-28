from pqdict import pqdict


class BinaryDependencyTree:
    def __init__(self, val, left, right, key, id=None, pos=None):
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

    def sorted_leaves(self):
        self.traverse(self)
        return self.leaves

    def traverse(self, tree):
        if not tree.is_tree:
            item = (tree.id)
            key = (tree.val, tree.pos, tree.mark)
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
            self.val, left, right, self.key, self.id, self.pos)
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


priority = ["conj-sent", "case", "cc", "mark", "nsubj", "conj-vp",
            "ccomp", "advcl", "advmod", "nummod", "nmod",
            "nmod:tmod", "nmod:npmod", "nmod:poss",
            "xcomp", "aux", "aux:pass", "obj", "obl",
            "cop", "acl", "acl:relcl", "appos",
            "conj-np", "conj-adj", "det", "compound",
            "amod", "conj-vb", "flat"]
hierarchy = {}
for i in range(len(priority)):
    hierarchy[priority[i]] = i


class Binarizer:
    def __init__(self, parse_table=None, postag=None, words=None):
        self.postag = postag
        self.parse_table = parse_table
        self.words = words
        self.id = 0

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
                word, None, None, self.id, head, tag)
            self.id += 1
            binary_tree.set_not_tree()
            return binary_tree, [binary_tree.key]
        else:
            top_dep = children[0]
        self.parse_table.remove(top_dep)

        left, left_rel = self.compose(top_dep[1])
        right, right_rel = self.compose(top_dep[2])
        dep_rel = "conj" if "conj" in top_dep[0] else top_dep[0]

        binary_tree = BinaryDependencyTree(dep_rel, left, right, self.id)
        binary_tree.left.parent = binary_tree
        binary_tree.right.parent = binary_tree

        left_rel.append(binary_tree.key)
        self.id += 1
        return binary_tree, left_rel + right_rel

    def binarization(self):
        self.id = 0
        self.relation = []
        root = list(filter(lambda x: x[0] == "root", self.parse_table))[0][1]
        binary_tree, relation = self.compose(root)
        binary_tree.set_root()
        binary_tree.length = len(self.words)
        return binary_tree, relation
