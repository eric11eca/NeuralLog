import numpy as np
from tqdm import tqdm
from copy import deepcopy
from Udep2Mono.binarization import Binarizer, BinaryDependencyTree
from Udep2Mono.dependency_parse import dependency_parse
from Udep2Mono.util import *


class Polarizer:
    def __init__(self, dependtree=None, relation=None):
        self.dependtree = dependtree
        self.sentence_head = []
        self.relation = relation
        self.polarize_function = {
            "acl": self.polarize_acl_relcl,
            "acl:relcl": self.polarize_acl_relcl,
            "advcl": self.polarize_acl_relcl,
            "advmod": self.polarize_advmod,
            "advmod:count": self.polarize_advmod,
            "amod": self.polarize_amod,
            "appos": self.polarize_inherite,
            "aux": self.polarize_aux,
            "aux:pass": self.polarize_aux,
            "case": self.polarize_case,
            "cc": self.polarize_cc,
            "cc:preconj": self.polarize_det,
            "ccomp": self.polarize_ccomp,
            "compound": self.polarize_inherite,
            "compound:prt": self.polarize_inherite,
            "conj": self.polarize_inherite,
            "cop": self.polarize_inherite,
            "csubj": self.polarize_nsubj,
            "csubj:pass": self.polarize_nsubj,
            "dep": self.polarize_dep,
            "det": self.polarize_det,
            "det:predet": self.polarize_det,
            "discourse": self.polarize_discourse,
            "expl": self.polarize_expl,
            "fixed": self.polarize_inherite,
            "flat": self.polarize_inherite,
            "goeswith": self.polarize_inherite,
            "iobj": self.polarize_inherite,
            "mark": self.polarize_inherite,
            "nmod": self.polarize_nmod,
            "nmod:npmod": self.polarize_nmod,
            "nmod:tmod": self.polarize_nmod,
            "nmod:poss": self.polarize_nmod_poss,
            "nsubj": self.polarize_nsubj,
            "nsubj:pass": self.polarize_nsubj,
            "nummod": self.polarize_nummod,
            "obj": self.polarize_obj,
            "obl": self.polarize_obj,
            "obl:npmod": self.polarize_oblnpmod,
            "obl:tmod": self.polarize_inherite,
            "parataxis": self.polarize_inherite,
            "xcomp": self.polarize_obj,
        }
        self.tree_log = []
        self.polar_log = []
        self.DETEXIST = "det:exist"

    def polarize_deptree(self):
        self.polarize(self.dependtree)

    def polarize(self, tree):
        if tree.isTree():
            self.polarize_function[tree.val](tree)

    def polarize_acl_relcl(self, tree):
        self.polar_log.append("polarize_acl:relcl")
        self.sentence_head.append(tree)
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
        else:
            tree.mark = "+"
            right.mark = "+"

        left.mark = "+"
        if left.isTree():
            self.polarize(left)
        if right.isTree():
            self.polarize(right)

        tree.mark = right.mark

        if right.mark == "-" and left.npos != "VBD":
            self.negate(left, -1)
        elif right.mark == "=" and left.npos != "VBD":
            self.equalize(left)
        elif right.val == "impossible":
            self.negate(left, -1)

        self.sentence_head.pop()

    def polarize_advmod(self, tree):
        self.polar_log.append("advmod")

        left = tree.getLeft()
        right = tree.getRight()
        self.polarize_inherite(tree)
        root_mark = tree.mark

        more_than = False
        less_than = False
        at_most = False
        at_least = False

        if tree.left.val == "fixed":
            more_than = tree.left.right.val.lower(
            ) == "more" and tree.left.left.val.lower() == "than"
            less_than = tree.left.right.val.lower(
            ) == "less" and tree.left.left.val.lower() == "than"
            at_most = tree.left.left.val.lower() == "most" and tree.left.right.val.lower() == "at"
            at_least = tree.left.left.val.lower() == "least" and tree.left.right.val.lower() == "at"

        if tree.left.val == "case":
            at_most = tree.left.left.val.lower() == "at" and tree.left.right.val.lower() == "most"
            at_least = tree.left.left.val.lower() == "at" and tree.left.right.val.lower() == "least"

        if left.val.lower() in ["many", "most"]:
            right.mark = "="
            if isinstance(tree.parent, BinaryDependencyTree) and tree.parent.val == "amod":
                self.equalize(tree.parent.right)
        elif left.val.lower() in ["not", "no", "n't", "never"]:
            self.negate(right, -1)
        elif left.val.lower() in ["exactly"]:
            self.equalize(tree.parent.parent)
            left.mark = root_mark
            tree.mark = right.mark
        elif more_than:
            if right.val == "nummod":
                right.left.mark = "-"
            elif right.npos == "CD":
                right.mark = "-"
            elif right.isTree() and right.left.val == "nummod":
                right.left.left.mark = "-"
                right.left.right.mark = "+"
        elif less_than:
            self.negate(right, self.relation.index(tree.key))
            if right.val == "nummod":
                right.left.mark = "+"
            elif right.npos == "CD":
                right.mark = "+"
            elif right.isTree() and right.left.val == "nummod":
                right.left.left.mark = "+"
                right.left.right.mark = "-"
        elif at_most:
            self.negate(right, self.relation.index(tree.key))
            if right.val == "nmod":
                right.right.mark = "+"
            elif right.val == "nummod":
                right.left.mark = "+"
            elif right.npos == "CD":
                right.mark = "+"
            elif right.isTree() and right.left.val == "nummod":
                right.left.left.mark = "+"
                right.left.right.mark = "-"
        elif at_least:
            if right.val == "nmod":
                right.right.mark = "-"
            elif right.val == "nummod":
                right.left.mark = "-"
            elif right.npos == "CD":
                right.mark = "-"
            elif right.isTree() and right.left.val == "nummod":
                right.left.left.mark = "-"
                right.left.right.mark = "+"

        if left.val.lower() == "when":
            self.equalize(self.dependtree)

    def polarize_amod(self, tree):
        self.polar_log.append("amod")

        left = tree.getLeft()
        right = tree.getRight()
        self.polarize_inherite(tree)

        at_most = False
        at_least = False

        if isinstance(tree.parent, BinaryDependencyTree):
            at_most = tree.parent.left.val.lower() == "at" and left.val.lower() == "most"
            at_least = tree.parent.left.val.lower() == "at" and left.val.lower() == "least"

        if at_most:
            self.negate(right, self.relation.index(tree.key))
            if right.val == "nummod":
                right.left.mark = "+"
            elif right.npos == "CD":
                right.mark = "+"
            elif right.isTree() and right.left.val == "nummod":
                right.left.left.mark = "+"
                right.left.right.mark = "-"
        elif at_least:
            if right.val == "nummod":
                right.left.mark = "-"
            elif right.npos == "CD":
                right.mark = "-"
            elif right.isTree() and right.left.val == "nummod":
                right.left.left.mark = "-"
                right.left.right.mark = "+"
        elif left.val.lower() in ["many", "most"] and not at_most:
            self.equalize(right)
            tree.mark = right.mark
        elif left.val.lower() == "fewer":
            self.noun_mark_replace(right, "-")
        elif left.val == "advmod":
            if left.right.val == "many":
                self.equalize(right)
                tree.mark = right.mark
            if left.left.val.lower() == "not":
                self.top_down_negate(
                    tree, "amod", self.relation.index(tree.key))

    def polarize_aux(self, tree):
        self.polarize_inherite(tree)

    def polarize_case(self, tree):
        self.polar_log.append("polarize_case")

        right = tree.getRight()
        left = tree.getLeft()
        self.polarize_inherite(tree)

        if tree.mark != "0":
            left.mark = tree.mark
            right.mark = tree.mark
        else:
            tree.mark = "+"
            left.mark = "+"
            right.mark = "+"

        if left.val == "without":
            if right.isTree():
                self.polarize(right)
            self.negate(tree, self.relation.index(left.key))
        elif right.npos == "CD":
            right.mark = "="
            if left.isTree():
                self.polarize(left)
        # elif left.val.lower() == "for":
        #    if right.isTree():
        #        self.polarize(right)
        #    self.equalize(right)
        elif right.val == "nmod:poss":
            left.mark = "="
            if right.isTree():
                self.polarize(right)
        elif left.val == "except":
            right.mark = "="
            self.polarize(right)

    def polarize_cc(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = "+"
        right.mark = "+"

        if right.val != "expl" and right.val != "det":
            right.mark = tree.mark

        if right.isTree():
            self.polarize(right)

        if left.id == 1:
            self.equalize(right)

    def polarize_ccomp(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark

        if right.isTree():
            self.polarize(right)

        left.mark = right.mark
        if left.isTree():
            self.polarize(left)

    def polarize_dep(self, tree):
        self.polar_log.append("polarize_dep")

        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
            left.mark = tree.mark
        else:
            tree.mark = "+"
            right.mark = "+"
            left.mark = "+"

        if right.isTree():
            self.polarize(right)

        if left.isTree():
            self.polarize(left)

    def polarize_det(self, tree):
        self.polar_log.append("polarize_det")
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            left.mark = tree.mark
            right.mark = tree.mark
        else:
            left.mark = "+"
            right.mark = "+"

        dettype = det_type(left.val)
        if dettype is None:
            dettype = self.DETEXIST

        if left.val.lower() == "any":
            if isinstance(tree.parent, BinaryDependencyTree) and isinstance(tree.parent.parent, BinaryDependencyTree):
                negate_signal = tree.parent.parent.left
                if negate_signal.val == "not":
                    dettype = self.DETEXIST
                if negate_signal.val == "det" and negate_signal.left.val.lower() == "no":
                    dettype = self.DETEXIST
        detmark = det_mark[dettype]

        right.mark = detmark[1]
        tree.mark = detmark[1]

        if right.isTree():
            self.polarize(right)

        if dettype == "det:negation":
            self.top_down_negate(tree, "det", self.relation.index(tree.key))

    def polarize_discourse(self, tree):
        self.polarize_inherite(tree)
        right = tree.getRight()
        left = tree.getLeft()

        more_than = False
        less_than = False

        if tree.left.val == "fixed":
            more_than = left.right.val.lower() == "more" and left.left.val.lower() == "than"
            less_than = left.right.val.lower() == "less" and left.left.val.lower() == "than"

        if more_than:
            if right.val == "nummod":
                right.left.mark = "-"
            elif right.npos == "CD":
                right.mark = "-"
            elif right.isTree() and right.left.val == "nummod":
                right.left.left.mark = "-"
                right.left.right.mark = "+"
        elif less_than:
            self.negate(right, self.relation.index(tree.key))
            if right.val == "nummod":
                right.left.mark = "+"
            elif right.npos == "CD":
                right.mark = "+"
            elif right.isTree() and right.left.val == "nummod":
                right.left.left.mark = "+"
                right.left.right.mark = "-"

    def polarize_expl(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = "+"
        right.mark = "+"

        if self.dependtree.left.mark == "-":
            right.mark = "-"

        if left.isTree():
            self.polarize(left)

        if right.isTree():
            self.polarize(right)

    def polarize_nmod(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
        else:
            right.mark = "+"
        left.mark = "+"

        if right.npos == "DT" or right.npos == "CC":
            detType = det_type(right.val)
            if detType == None:
                detType = "det:exist"
            left.mark = det_mark[detType][1]
            if detType == "det:negation":
                self.top_down_negate(
                    tree, "nmod", self.relation.index(tree.key))
        elif right.val.lower() in ["many", "most"]:
            left.mark = "="

        if left.isTree():
            self.polarize(left)

        if right.isTree():
            self.polarize(right)

        if left.val == "case":
            if isinstance(tree.parent, BinaryDependencyTree):
                if tree.parent.left.val.lower() == "more":
                    left.right.mark = "-"

        tree.mark = right.mark
        if right.mark == "-":
            self.negate(left, -1)
        elif right.mark == "=":
            self.equalize(left)

    def polarize_nmod_poss(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = tree.mark
        if left.isTree():
            self.polarize(left)
        else:
            left.mark = "+"

        right.mark = tree.mark
        if self.search_dependency("det", tree.left):
            right.mark = left.mark
        if right.isTree():
            self.polarize(right)
        else:
            right.mark = "+"

    def polarize_nsubj(self, tree):
        self.polar_log.append("polarize_nsubj")
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
            left.mark = tree.mark
        else:
            tree.mark = "+"
            right.mark = "+"
            left.mark = "+"

        if self.search_dependency("expl", right):
            self.polarize(left)
            self.polarize(right)
            return

        self.polarize(right)

        if left.val.lower() == "that":
            self.equalize(right)
        if not isinstance(tree.parent, str):
            if tree.parent.left.val.lower() == "that":
                self.equalize(left)

        if left.isTree():
            self.polarize(left)
        else:
            if left.val.lower() in ["nobody"]:
                self.negate(tree, self.relation.index(tree.key))

        if tree.mark == "0":
            tree.mark = right.mark

        if left.npos == "NN":
            left.mark = tree.mark

        if is_implicative(right.val.lower(), negtive_implicative):
            tree.mark = "-"

    def polarize_nummod(self, tree):
        self.polar_log.append("polarize_nummod")
        right = tree.getRight()
        left = tree.getLeft()

        left.mark = "="
        if tree.mark != "0":
            right.mark = tree.mark
        else:
            right.mark = "+"

        if tree.parent == "compound":
            right.mark = left.mark

        if left.isTree():
            if left.val == "advmod":
                left.mark = "+"
            self.polarize(left)
            if left.mark == "=":
                right.mark = left.mark
                tree.mark = left.mark
        elif left.id == 1:
            left.mark = "="

        if not isinstance(tree.parent, str):
            if is_implicative(tree.parent.right.val, at_least_implicative):
                left.mark = "-"
            elif is_implicative(tree.parent.right.val, exactly_implicative):
                left.mark = "="

        if right.isTree():
            self.polarize(right)

    def polarize_obj(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
        else:
            right.mark = "+"
            tree.mark = "+"
        left.mark = "+"

        if right.isTree():
            self.polarize(right)

        if left.isTree():
            self.polarize(left)

        if is_implicative(right.val.lower(), negtive_implicative):
            tree.mark = "-"
            self.negate(left, -1)

        if left.val == "mark" and left.left.val == "to":
            left.left.mark = right.mark

    def polarize_obl(self, tree):
        self.polar_log.append("polarize_obl")

        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
        else:
            right.mark = "+"
        left.mark = "+"

        if right.isTree():
            self.polarize(right)

        if left.isTree():
            self.polarize(left)

        if right.mark == "-":
            self.negate(left, -1)

    def polarize_oblnpmod(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if left.isTree():
            self.polarize(left)
        right.mark = left.mark
        if right.isTree():
            self.polarize(right)

    def polarize_inherite(self, tree):
        right = tree.getRight()
        left = tree.getLeft()

        if tree.mark != "0":
            right.mark = tree.mark
            left.mark = tree.mark
        else:
            right.mark = "+"
            left.mark = "+"

        if right.isTree():
            self.polarize(right)

        if left.val.lower() == "there":
            left.mark = "+"

        if left.isTree():
            self.polarize(left)
        elif left.val.lower() == "if":
            self.negate(right, -1)

    def search_dependency(self, deprel, tree):
        if tree.val == deprel:
            return True
        else:
            right = tree.getRight()
            left = tree.getLeft()

            left_found = False
            right_found = False

            if not isinstance(right, str) and right.isTree():
                right_found = self.search_dependency(deprel, right)

            if not isinstance(left, str) and left.isTree():
                left_found = self.search_dependency(deprel, left)

            return left_found or right_found

    def verb_mark_replace(self, tree, mark):
        if isinstance(tree, str):
            return
        if tree.npos is not None and "VB" in tree.npos:
            tree.mark = mark
        self.verb_mark_replace(tree.left, mark)
        self.verb_mark_replace(tree.right, mark)

    def noun_mark_replace(self, tree, mark):
        if isinstance(tree, str):
            return False
        if tree.npos is not None and "NN" in tree.npos:
            tree.mark = mark
            return True
        right = self.noun_mark_replace(tree.right, mark)
        if not right:
            self.noun_mark_replace(tree.left, mark)

    def equalize(self, tree):
        if tree.isTree():
            self.equalize(tree.getRight())
            self.equalize(tree.getLeft())
            if tree.mark != "0":
                tree.mark = "="
        else:
            if tree.npos != "CC" and tree.val.lower() != "when":
                tree.mark = "="

    def negate_condition(self, tree, anchor):
        not_truth_connection = not tree.val in ["and", "or"]
        not_empty_mark = tree.mark != "0"
        return not_empty_mark and not_truth_connection

    def top_down_negate(self, tree, deprel, anchor):
        if not isinstance(tree.parent, BinaryDependencyTree):
            return
        if tree.parent.left.val == deprel:
            self.negate(tree.parent.left, anchor)
            self.negate(tree.parent.right, -1)
        elif tree.parent.right.val == deprel:
            self.negate(tree.parent.right, anchor)
            self.negate(tree.parent.left, -1)

    def negate(self, tree, anchor):
        if isinstance(tree, str):
            return
        if tree.val == "cc" and tree.right.val in ["expl", "nsubj", "det"]:
            return
        if tree.isTree():
            # print(tree.val)
            if self.relation.index(tree.key) > anchor or "nsubj" in tree.val:
                # print(tree.val)
                self.negate(tree.getRight(), anchor)
                self.negate(tree.getLeft(), anchor)
                if self.negate_condition(tree, anchor):
                    tree.mark = negate_mark[tree.mark]
        else:
            if self.relation.index(tree.key) > anchor and self.negate_condition(tree, anchor):
                if tree.npos != "EX":
                    # print(tree.val)
                    tree.mark = negate_mark[tree.mark]


class PolarizationPipeline:
    def __init__(self, sentences, verbose=0, parser="stanza"):
        self.binarizer = Binarizer()
        self.polarizer = Polarizer()
        self.annotations = []
        self.exceptioned = []
        self.incorrect = []
        self.verbose = verbose
        self.parser = parser
        self.sentences = sentences
        self.num_sent = len(self.sentences)

    def run_binarization(self, parsed, replaced, sentence):
        self.binarizer.parse_table = parsed[0]
        self.binarizer.postag = parsed[1]
        self.binarizer.words = parsed[2]

        if self.verbose == 2:
            print()
            print(parsed[0])
            print()
            print(parsed[1])

        try:
            binary_dep, relation = self.binarizer.binarization()
            if self.verbose == 2:
                self.postprocess(binary_dep, len(parsed[2]), replaced)
            return binary_dep, relation

        except Exception as e:
            print(str(e))
            self.exceptioned.append(sentence)
            return None

    def postprocess(self, tree, length, replaced):
        sexpression, annotated, postags, reverse = btreeToList(
            tree, length, replaced, 0)
        sexpression = '[%s]' % ', '.join(
            map(str, sexpression)).replace(",", " ")
        return sexpression, annotated, postags, reverse

    def run_polarization(self, binary_dep, relation, length, replaced, sentence):
        self.polarizer.dependtree = binary_dep
        self.polarizer.relation = relation

        try:
            self.polarizer.polarize_deptree()
            polarized, annotated, postags, reverse = self.postprocess(
                binary_dep, length, replaced)
            return polarized, annotated, postags, reverse
        except Exception as e:
            if self.verbose == 2:
                print(str(e))
            self.exceptioned.append(sentence)
            return None

    def run_polarize_pipeline(self):
        for i in tqdm(range(self.num_sent)):
            sent = self.sentences[i] if len(self.sentences[i]) > 0 else "skip"
            parsed, replaced = dependency_parse(sent, self.parser)

            binary_dep, relation = self.run_binarization(
                parsed, replaced, sent)
            polarized, annotated, postags, reverse = self.run_polarization(
                binary_dep, relation, len(parsed[2]), replaced, sent)

            annotated = ' '.join(list(annotated.popkeys()))
            for word in reverse:
                annotated = annotated.replace(word, reverse[word])

            self.annotations.append(
                {
                    'annotated': annotated,
                    'original': sent,
                    'word_dict': pqdict(parsed[1]),
                    'polarized': polarized,
                    'postags': postags,
                    'polarized_tree': self.polarizer.dependtree,
                })

    def polarize_eval(self, annotations_val=[]):
        num_unmatched = 0
        self.incorrect = []
        self.annotations = []
        self.verbose = 1

        outputs, _ = self.run_polarize_pipeline()

        for i in tqdm(range(len(outputs))):
            output = outputs[i]
            postags = ' '.join(list(output[3].popkeys()))
            vec = convert2vector(output[0])

            if len(annotations_val) > 0:
                annotation_val = annotations_val[i]
                vec_val = convert2vector(annotation_val)
                if len(vec) == len(vec_val):
                    if not np.array_equal(vec, vec_val):
                        num_unmatched += 1
                        self.incorrect.append(
                            (output[1], output[0], annotation_val, postags))
                    if self.parser == "stanford":
                        continue

            validate = ""
            if len(annotations_val) > 0:
                validate = annotations_val[i]

            self.annotations.append(
                {
                    "annotated": output[0],
                    "polarized": output[2],
                    "validation": validate,
                    "orig": output[1],
                    "postag": postags
                }
            )

        print()
        print("Number of unmatched sentences: ", num_unmatched)


if __name__ == '__main__':
    sentences = ["At most 6 dogs are hungry"]
    pipeline = PolarizationPipeline(sentences, verbose=0, parser="stanza")
    print(pipeline.annotations[0][0])
    print(pipeline.annotations[0][2])
    print(pipeline.annotations[0][3])
