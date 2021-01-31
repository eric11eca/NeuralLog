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
            "aux": self.polarize_inherite,
            "aux:pass": self.polarize_inherite,
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
            "discourse": self.polarize_inherite,
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
        self.DETNEGATE = "det:negation"

    def polarize_deptree(self):
        self.polarize(self.dependtree)

    def polarize(self, tree):
        if tree.is_tree:
            self.polarize_function[tree.val](tree)

    def polarize_acl_relcl(self, tree):
        self.sentence_head.append(tree)
        self.right_inheritance(tree)
        right = tree.right
        left = tree.left

        if left.is_tree:
            self.polarize(left)
        if right.is_tree:
            self.polarize(right)

        if right.id == 1:
            right.mark = "-"

        tree.mark = right.mark

        if right.mark == "-" and left.pos != "VBD":
            self.negate(left, -1)
        elif right.mark == "=" and left.pos != "VBD":
            self.equalize(left)
        elif right.val == "impossible":
            self.negate(left, -1)

        self.sentence_head.pop()

    def polarize_advmod(self, tree):
        left = tree.left
        right = tree.right
        self.polarize_inherite(tree)
        root_mark = tree.mark

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

        if left.val.lower() == "when":
            self.equalize(self.dependtree)

    def polarize_amod(self, tree):
        left = tree.left
        right = tree.right
        self.polarize_inherite(tree)

        if left.val.lower() in ["many", "most"]:
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

    def polarize_case(self, tree):
        self.polarize_inherite(tree)
        right = tree.right
        left = tree.left

        if left.val == "without":
            if right.is_tree:
                self.polarize(right)
            self.negate(tree, self.relation.index(left.key))
        elif right.pos == "CD":
            right.mark = "="
            if left.is_tree:
                self.polarize(left)
        elif right.val == "nmod:poss":
            left.mark = "="
            if right.is_tree:
                self.polarize(right)
        elif left.val == "except":
            right.mark = "="
            self.polarize(right)

    def polarize_cc(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.val != "expl" and right.val != "det":
            right.mark = tree.mark

        if right.is_tree:
            self.polarize(right)

        if left.id == 1:
            self.equalize(right)

    def polarize_ccomp(self, tree):
        right = tree.right
        left = tree.left

        if tree.mark != "0":
            right.mark = tree.mark

        if right.is_tree:
            self.polarize(right)

        left.mark = right.mark
        if left.is_tree:
            self.polarize(left)

    def polarize_dep(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.is_tree:
            self.polarize(right)

        if left.is_tree:
            self.polarize(left)

    def polarize_det(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

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
        right.mark = detmark
        tree.mark = detmark

        if right.is_tree:
            self.polarize(right)

        if dettype == self.DETNEGATE:
            self.top_down_negate(tree, "det", self.relation.index(tree.key))

        if right.val == "nummod":
            if dettype == self.DETEXIST:
                right.left.mark = "-"
            elif dettype == self.DETNEGATE:
                right.left.mark = "+"
        if right.pos == 'CD':
            if left.val == "more-than" or left.val == "at-least":
                right.mark = "-"
            if left.val == "less-than" or left.val == "at-most":
                right.mark = "+"

    def polarize_expl(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if self.dependtree.left.mark == "-":
            right.mark = "-"

        if left.is_tree:
            self.polarize(left)

        if right.is_tree:
            self.polarize(right)

    def polarize_nmod(self, tree):
        self.right_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.pos == "DT" or right.pos == "CC":
            detType = det_type(right.val)
            if detType == None:
                detType = self.DETEXIST
            left.mark = det_mark[detType][1]
            if detType == "det:negation":
                self.top_down_negate(
                    tree, "nmod", self.relation.index(tree.key))
        elif right.val.lower() in ["many", "most"]:
            left.mark = "="

        if left.is_tree:
            self.polarize(left)

        if right.is_tree:
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
        right = tree.right
        left = tree.left

        left.mark = tree.mark
        if left.is_tree:
            self.polarize(left)
        else:
            left.mark = "+"

        right.mark = tree.mark
        if self.search_dependency("det", tree.left):
            right.mark = left.mark
        if right.is_tree:
            self.polarize(right)
        else:
            right.mark = "+"

    def polarize_nsubj(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if self.search_dependency("expl", right):
            self.polarize(left)
            self.polarize(right)
            return

        self.polarize(right)

        if left.val.lower() == "that":
            self.equalize(right)
        if not tree.is_root:
            if tree.parent.left.val.lower() == "that":
                self.equalize(left)

        if left.is_tree:
            self.polarize(left)
        else:
            if left.val.lower() in ["nobody"]:
                self.negate(tree, self.relation.index(tree.key))

        if tree.mark == "0":
            tree.mark = right.mark

        if left.pos == "NN":
            left.mark = tree.mark

        if is_implicative(right.val.lower(), "-"):
            tree.mark = "-"

    def polarize_nummod(self, tree):
        right = tree.right
        left = tree.left

        left.mark = "="
        if tree.mark != "0":
            right.mark = tree.mark
        else:
            right.mark = "+"

        if left.val == "det":
            left.mark = "+"

        if tree.parent == "compound":
            right.mark = left.mark

        if left.is_tree:
            if left.val == "advmod":
                left.mark = "+"
            self.polarize(left)
            if left.mark == "=":
                right.mark = left.mark
                tree.mark = left.mark
        elif left.id == 1:
            left.mark = "="

        if not tree.is_tree:
            if is_implicative(tree.parent.right.val, "-"):
                left.mark = "-"
            elif is_implicative(tree.parent.right.val, "="):
                left.mark = "="

        if right.is_tree:
            self.polarize(right)

    def polarize_obj(self, tree):
        self.right_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.is_tree:
            self.polarize(right)

        if left.is_tree:
            self.polarize(left)

        if is_implicative(right.val.lower(), "-"):
            tree.mark = "-"
            self.negate(left, -1)

        if left.val == "mark" and left.left.val == "to":
            left.left.mark = right.mark

    def polarize_obl(self, tree):
        self.right_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.is_tree:
            self.polarize(right)

        if left.is_tree:
            self.polarize(left)

        if right.mark == "-":
            self.negate(left, -1)

    def polarize_oblnpmod(self, tree):
        right = tree.right
        left = tree.left

        if left.is_tree:
            self.polarize(left)
        right.mark = left.mark
        if right.is_tree:
            self.polarize(right)

    def polarize_inherite(self, tree):
        self.full_inheritance(tree)
        right = tree.right
        left = tree.left

        if right.is_tree:
            self.polarize(right)

        if left.val.lower() == "there":
            left.mark = "+"

        if left.is_tree:
            self.polarize(left)
        elif left.val.lower() == "if":
            self.negate(right, -1)

    def search_dependency(self, deprel, tree):
        if tree.val == deprel:
            return True
        else:
            right = tree.right
            left = tree.left

            left_found = False
            right_found = False

            if right is not None and right.is_tree:
                right_found = self.search_dependency(deprel, right)

            if left is not None and left.is_tree:
                left_found = self.search_dependency(deprel, left)

            return left_found or right_found

    def noun_mark_replace(self, tree, mark):
        if isinstance(tree, str):
            return False
        if tree.pos is not None and "NN" in tree.pos:
            tree.mark = mark
            return True
        right = self.noun_mark_replace(tree.right, mark)
        if not right:
            self.noun_mark_replace(tree.left, mark)

    def right_inheritance(self, tree):
        if tree.mark != "0":
            tree.right.mark = tree.mark
        else:
            tree.right.mark = "+"
            tree.mark = "+"
        tree.left.mark = "+"

    def full_inheritance(self, tree):
        if tree.mark != "0":
            tree.right.mark = tree.mark
            tree.left.mark = tree.mark
        else:
            tree.right.mark = "+"
            tree.left.mark = "+"
            tree.mark = "+"

    def equalize(self, tree):
        if tree.is_tree:
            self.equalize(tree.right)
            self.equalize(tree.left)
            if tree.mark != "0":
                tree.mark = "="
        else:
            if tree.pos != "CC" and tree.val.lower() != "when":
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
        if tree.is_tree:
            # print(tree.val)
            if self.relation.index(tree.key) > anchor or "nsubj" in tree.val:
                # print(tree.val)
                self.negate(tree.right, anchor)
                self.negate(tree.left, anchor)
                if self.negate_condition(tree, anchor):
                    tree.mark = negate_mark[tree.mark]
        else:
            if self.relation.index(tree.key) > anchor and self.negate_condition(tree, anchor):
                if tree.pos != "EX":
                    # print(tree.val)
                    tree.mark = negate_mark[tree.mark]


class PolarizationPipeline:
    def __init__(self, sentences=None, verbose=0, parser="stanza"):
        self.binarizer = Binarizer()
        self.polarizer = Polarizer()
        self.annotations = []
        self.annotated_sentences = []
        self.exceptioned = []
        self.incorrect = []
        self.verbose = verbose
        self.parser = parser
        self.sentences = sentences
        self.num_sent = 0 if sentences is None else len(sentences)

    def run_binarization(self, parsed, replaced, sentence):
        self.binarizer.parse_table = parsed[0]
        self.binarizer.postag = parsed[1]
        self.binarizer.words = parsed[2]

        if self.verbose == 2:
            print()
            print(parsed[0])
            print()
            print(parsed[1])

        binary_dep, relation = self.binarizer.binarization()
        if self.verbose == 2:
            self.postprocess(binary_dep, replaced)
        return binary_dep, relation

    def postprocess(self, tree, replaced):
        sexpression = btree2list(tree, replaced, 0)
        sexpression = '[%s]' % ', '.join(
            map(str, sexpression)).replace(",", " ").replace("'", "")
        if self.verbose == 2:
            print(sexpression)
        return sexpression

    def run_polarization(self, binary_dep, relation, replaced, sentence):
        self.polarizer.dependtree = binary_dep
        self.polarizer.relation = relation

        self.polarizer.polarize_deptree()
        if self.verbose == 2:
            self.postprocess(binary_dep, replaced)

    def get_annotation_info(self, annotation):
        ann = list(annotation.popkeys())
        return list(zip(*ann))

    def single_polarization(self, sentence):
        parsed, replaced = dependency_parse(sentence, self.parser)

        binary_dep, relation = self.run_binarization(
            parsed, replaced, sentence)
        self.run_polarization(binary_dep, relation, replaced, sentence)
        annotated = self.polarizer.dependtree.sorted_leaves()

        if self.verbose == 2:
            annotated_sent = ' '.join([word[0] for word in annotated.keys()])
            self.annotated_sentences.append(annotated_sent)

        return {
            'original': sentence,
            'annotated': annotated,
            'polarized_tree': self.polarizer.dependtree,
        }

    def batch_polarization(self, sentences):
        for i in tqdm(range(self.num_sent)):
            sent = sentences[i]
            try:
                annotation = self.single_polarization(sent)
                self.annotations.append(annotation)
            except Exception as e:
                if self.verbose == 2:
                    print(str(e))
                self.exceptioned.append(sent)

    def polarize_eval(self, sentences, labels):
        incorrect = []
        need_process = []
        num_correct = 0

        for i in tqdm(range(len(sentences))):
            annotation = pipeline.single_polarization(sentences[i])
            annotated_sent = annotation2string(annotation)
            vec = [arrow2int(x) for x in annotated_sent.split(' ')]
            label = [arrow2int(x) for x in labels[i].split(' ')]

            if len(vec) == len(label):
                x = np.array(vec)
                y = np.array(label)
                if np.array_equal(x, y):
                    num_correct += 1
                else:
                    incorrect.append(annotation['original'])
            else:
                need_process.append(annotation['original'])

        print("Correct annotation: ", num_correct)
        print(incorrect)
        print(need_process)
