class BinaryDependencyTree:
    def __init__(self, val, left, right, key, wid=None, npos=None):
        self.val = val
        self.parent = ""
        self.left = left
        self.right = right
        self.mark = "0"
        self.id = wid
        self.npos = npos
        self.key = key
        self.is_root = False

    def setRoot(self):
        self.is_root = True

    def isTree(self):
        return not (type(self.left) is str and type(self.right) is str)

    def getVal(self):
        return self.val

    def getLeft(self):
        return self.left

    def getRight(self):
        return self.right


priority = ["conj-sent", "case", "cc", "mark", "nsubj", "conj-vp",
            "ccomp", "advcl", "advmod", "nmod",
            "nmod:tmod", "nmod:npmod", "nmod:poss",
            "xcomp", "aux", "aux:pass", "obj", "obl",
            "cop", "acl", "acl:relcl", "appos",
            "conj-np", "conj-adj", "det", "compound",
            "amod", "conj-vb", "flat"]
queue = {}
for i in range(len(priority)):
    queue[priority[i]] = i


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
        children.sort(key=(lambda x: queue[x[0]]))
        # key=(lambda x: (x[2]-x[1])*20 if x[2] > x[1] else abs(x[2]-x[1])), reverse=True)
        children = self.process_not(children)
        if len(children) == 0:
            word = self.words[head][0]
            tag = self.words[head][1]
            binary_tree = BinaryDependencyTree(
                word, "N", "N", self.id, head, tag)
            self.id += 1
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
        binary_tree.setRoot()
        return binary_tree, relation
