import binarytree as bt
from wordnet import find_relation, get_word_sets
from PIL import Image, ImageDraw
from nltk.tree import Tree
from nltk.draw import TreeWidget
from nltk.draw.util import CanvasFrame
from IPython.display import Image, display
import gensim.downloader as api
from Udep2Mono.dependency_parse import quantifier_replacement
w2v_model = api.load("glove-wiki-gigaword-50")
from gensim.models.keyedvectors import KeyedVectors
#word_vecs = KeyedVectors.load_word2vec_format('../model/numberbatch-en.txt', binary=False)
#word_vecs.save('numberbatch-en.gensim')
model = KeyedVectors.load('numberbatch-en.gensim', mmap='r')
from nltk.stem.snowball import SnowballStemmer 
stemmer = SnowballStemmer(language = 'english')
import spacy
nlp = spacy.load('en_core_web_sm')
doc = nlp("Apples and oranges are similar. Boots and hippos aren't.")
contradict_verbs = {
        'perform':set(['fail']),
        'fail': set(['perform'])
}
negation_words = ["no", "not", "n't"]
det_type_words = {
    "det:univ": ["all", "every", "each", "any", "all-of-the"],
    "det:exist": ["a", "an", "some", "double", "triple", "some-of-the", "al-least", "more-than"],
    "det:limit": ["such", "both", "the", "this", "that",
                  "those", "these", "my", "his", "her",
                  "its", "either", "both", "another"],
    "det:negation": ["no", "neither", "never", "none", "none-of-the", "less-than", "at-most", "few"]
}



nounModifiers = {"det", "nummod", "amod","obl:tmod", "acl:relcl", "nmod", "case","nmod:pass",  "acl", "Prime","cc"}
verbModifiers = {"advmod","xcomp","advcl","mark","aux"}
nounCategories = {"compound"}
verbs = {"VBZ", "VBP", "VBD", "VBG"}
modified = {"NN", "PRP", "JJ", "VB","RB"}.union(verbs)
modifiers = nounModifiers.union(verbModifiers)
offFocus = {"expl"}
contents = {"nsubj","obj","cop","compound","conj","nsubj:pass","obl"}
cont_npos = {"nsubj":'nn', "obj": 'nn', "cop": 'vbz', "verb": 'vbz'}
mark_toProp = {"+": {"hyponym","synonym"}, "-": {"hypernym","synonym"}, "=": {"synonym"}}
clause_prop = {"which", "that", "who"}
be_verbs = {"is", "am", "are", "be","was","were"}
directions = {0: "lexical", 1: "phrasal", 2: "syntatic_variation", 3: "implicative"}
arrows = {
    "+": "\u2191",
    "-": "\u2193",
    "=": "=",
    "0": ""
}


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


class Unode:
    def __init__(self, prop, word, npos, mark):
        self.nexts = dict()
        self.prop = prop
        self.isRoot = False
        self.nexts["all"] = set()
        self.word = word
        self.npos = npos
        self.mark = mark
        self.phrases = set()
        self.pair = -1
        self.pairParts = dict()
        self.start = -1
        self.end = -1
        self.nodes = set()
        self.cc = None
        self.aligned = []
        self.alignedBy = []
        self.parent = None
        self.explMain = False
    def add_Unode(self, node):
        # print(node.prop)
        if(self.isRoot):
            if(node.prop == "obl"):
                node.prop = "obj"
            self.nexts[node.prop].add(node)
        else:
            self.nexts["all"].add(node)

    def addNode(self, node):
        self.nodes.add(node)

    def getText(self):
        if(self.isRoot):
            output = ""
            for cont in ["nsubj", "verb", "obj"]:
                for ele in self.nexts[cont]:
                    output += ele.getText()
                    output += " "
            return output.strip()
        else:
            if(self.nexts["all"] == set()):
                return self.word
            output = self.word
            for element in self.nexts["all"]:
                if(element.prop == "amod"):
                    output = " " + output
                    output = element.getText() + output
                else:
                    output += " "
                    output += element.getText()

            return output

    def get_inText(self, index):
        connected_info = ""
        if(self.isRoot):
            for key in self.nexts.keys():
                if(key != "all"):
                    print(key)
                    for keyItem in self.nexts[key]:
                        connected_info += (key + ": " +
                                           keyItem.get_inText(index + 1) + " ")
            return "{ " + connected_info + "}"
        else:
            for node in self.nexts["all"]:
                if(node != None):
                    # print("111")
                    connected_info += node.get_inText(index + 1)
            return "{ The " + str(index) + " layer" + ": " + self.word + connected_info + "}"

    def get_magicText(self):
        connected_info = ""
        if(self.isRoot):
            for key in self.nexts.keys():
                component = ""
                if(key != "all"):
                    print(key)
                    for keyItem in self.nexts[key]:
                        component += " (" + keyItem.get_magicText() + ")"
                    component = "(" + key + " " + component + ")"
                connected_info += component
            return "(" + connected_info + ")"
        else:
            for node in self.nexts["all"]:
                if(node != None):
                    # print("111")
                    connected_info += "(" + node.get_magicText() + ")"
            if(self.nexts["all"] == set()):
                if(self.pair != -1):
                    return self.word + str(self.pair)
                return self.word
            if(self.pair != -1):
                return self.word + str(self.pair) + connected_info
            return self.word + connected_info

    def addNum(self, num):
        self.pair = num

    def addPart(self, newNode, type1):
        if(type1 not in self.pairParts):
            self.pairParts[type1] = set()
        self.pairParts[type1].add(newNode)

    def getParts(self):
        # return verb-obj subParts now
        return self.pairParts["obj"]
    def addCC(self,node):
        self.cc = node

class PairCounter:
    def __init__(self, initial=0):
        self.nsubj = initial
        self.obj = initial

    def incrementN(self):
        self.nsubj += 1

    def incrementO(self):
        self.obj += 1


class Ugraph:
    def __init__(self, rootNode):
        self.root = rootNode
        self.root.isRoot = True
        self.root.nexts.pop("all", None)
        for main in {"nsubj", "obj", "verb"}:
            self.root.nexts[main] = set()
        self.nodes = set()
        self.contentSet = set()
        self.chunks = set()
        self.Pairs = dict()
        self.Pairs["nsubj"] = dict()
        self.Pairs["obj"] = dict()
        self.align_log = []
        self.expl = False
        
    def add_node(self, node):
        self.nodes.add(node)
        self.root.addNode(node)

    def add_edge(self, node1, node2):
        if(node1.isRoot):
            self.contentSet.add(node2.word)
        node1.add_Unode(node2)
        node2.parent = node1
    def contains(self, word_assigned):
        return word_assigned in self.contentSet

    def get_magicText(self):
        return self.root.get_magicText()

    def addPair(self, newNode, num, type1):
        newNode.addNum(num)
        if(num not in self.Pairs[type1]):
            self.Pairs[type1][num] = [None]
        if(newNode.prop == "verb"):
            self.Pairs[type1][num][0] = newNode
        else:
            self.Pairs[type1][num].append(newNode)
        if(len(self.Pairs[type1][num]) > 1 and self.Pairs[type1][num][0] is not None):
            if(newNode.prop == "verb"):
                self.Pairs[type1][num][0].addPart(
                    self.Pairs[type1][num][-1], "obj")
            else:
                self.Pairs[type1][num][0].addPart(newNode, "obj")

    def jupyter_draw_nltk_tree(self, tree):
        cf = CanvasFrame()
        tc = TreeWidget(cf.canvas(), tree)
        tc['node_font'] = 'arial 14 bold'
        tc['leaf_font'] = 'arial 14'
        tc['node_color'] = '#005990'
        tc['leaf_color'] = '#3F8F57'
        tc['line_color'] = '#175252'
        cf.add_widget(tc, 20, 20)
        cf.print_to_file('../data/tree_img/tree.ps')
        cf.destroy()
        os.system(
            'magick convert ../data/tree_img/tree.ps ../data/tree_img/tree.png')
        display(Image(filename='../data/tree_img/tree.png'))
    
    def visualize_tree(self, tree):
        btree = Tree.fromstring(tree.replace('[', '(').replace(']', ')'))
        self.jupyter_draw_nltk_tree(btree)

    def printUgraph_inText(self, Ugraph):
        print(Ugraph.root.get_inText(1))
        
    def combine_comp(self, tree, node):
        if(tree.right == None):
            node.word = node.word + " " + tree.val
            node.end = tree.id
            return
        else:
            node.word = node.word + " " + tree.left.val
            return self.combine_comp(tree.right, node)
    
    def mono2Graph_recur(self, sent_tree, G, mods, pos = None, counter = -1):
        needleft = True
        needright = True
        if(sent_tree is None):

            return
        else:
            if(any(list(map(lambda x: sent_tree.val is not None and x in sent_tree.val, list(modifiers))))):
                if("acl" in sent_tree.val):
                    gp = GraphPipeline()
                    G_prime = gp.mono2Graph(sent_tree.left)
                    mods.add(G_prime.root)
                else:
                    left_result = self.mono2Graph_recur(sent_tree.left, G, set(), sent_tree.val,counter)
                    if(left_result is not None):
                        if(type(left_result) is set):
                            for item_result in left_result:
                                if(item_result is not None):
                                    mods.add(item_result)
                        else:
                            mods.add(left_result)
                return self.mono2Graph_recur(sent_tree.right, G, mods, pos,counter)            
            else:
                if ((sent_tree.left is None and sent_tree.right is None) or sent_tree.val == "compound" ):
                        if("compound" in sent_tree.val):
                            right = sent_tree.right
                            comPos = right.pos
                            while(right != None):
                                comPos = right.pos
                                right = right.right
                            newNode = Unode(pos, quantifier_replacement.get(sent_tree.left.val, sent_tree.left.val),
                                            comPos, sent_tree.mark)
                            newNode.start = sent_tree.left.id
                            self.combine_comp(sent_tree.right, newNode)
                            if(pos in contents or pos == "verb"):
                                    G.add_edge(G.root,newNode)
                                    if(pos != "nsubj"):
                                        G.addPair(newNode, counter.obj,"obj")
                            for node in mods:
                                    if(node.npos == "CC"):
                                        newNode.addCC(node)
                                    else:
                                        G.add_edge(newNode, node)
                            return newNode
                        newNode = Unode(pos, quantifier_replacement.get(sent_tree.val, sent_tree.val), sent_tree.pos, sent_tree.mark)
                        newNode.start = sent_tree.id
                        newNode.end = sent_tree.id
                        G.add_node(newNode)
                        if (any(list(map(lambda x : sent_tree.pos is not None and x in sent_tree.pos, list(modified)))) 
                                                            or any(list(map(lambda x: pos is not None and x in pos, list(contents))))
                                                                or pos == "verb"):
                            if(pos in contents or pos == "verb"):

                                    G.add_edge(G.root,newNode)
                                    if(pos != "nsubj"):
                                        G.addPair(newNode, counter.obj,"obj")
                                        if(pos == "verb" and sent_tree.parent.val != "cop"):
                                            counter.incrementO()
                            for node in mods:

                                    if(node.npos == "CC"):
                                        newNode.addCC(node)
                                    else:
                                        G.add_edge(newNode, node)
                            return newNode
                        else:
                            mods.add(newNode)
                            return newNode
                else: 
                    if(any(list(map(lambda x: sent_tree.val is not None and x in sent_tree.val, list(contents))))):
                        pos_left = sent_tree.val
                        pos_right = pos
                        if("nsubj" in sent_tree.val):
                            pos_right = "verb"
                            pos_left = sent_tree.val[0:5]
                        if("cop" in sent_tree.val):
                            target = sent_tree.right
                            ifObj = False
                            while(target != None):
                                if(target.val == "nsubj"):
                                    break
                                if(target.val in ["obj", "obl"]):
                                    ifObj = True
                                    break
                                target = target.right
                            if(ifObj):
                                sent_tree.val = "aux"
                                return self.mono2Graph_recur(sent_tree, G, mods, pos,counter )
                            else:
                                pos_left = "verb"
                                pos_right = "obj" 
                                self.mono2Graph_recur(sent_tree.left, G,set(),pos_left,counter)
                                output = self.mono2Graph_recur(sent_tree.right, G, mods, pos_right,counter)
                                counter.incrementO()
                                return output
                        if('conj' in sent_tree.val):
                            if (any(list(map(lambda x: pos is not None and x in pos, list(modifiers))))):
                                results = set()
                          
                                results.add(self.mono2Graph_recur(sent_tree.left, G, set(), pos,counter))
                                results.add(self.mono2Graph_recur(sent_tree.right, G, set(), pos,counter))
                                return results
                            else:
                                self.mono2Graph_recur(sent_tree.left, G, set(), pos,counter)

                                self.mono2Graph_recur(sent_tree.right, G, mods, pos,counter)

                        elif("aux" in sent_tree.val):
                            self.mono2Graph_recur(sent_tree.right, G, mods, "verb",counter)
                        elif("ob" in sent_tree.val):
                            if(not pos in ["verb", "obj"]):
                                right_result = self.mono2Graph_recur(sent_tree.right, G, set(), "Prime",counter)
                                if(right_result is not None):
                                    mods.add(right_result)
                                self.mono2Graph_recur(sent_tree.left, G, mods, pos_left, counter)
                            else:
                                self.mono2Graph_recur(sent_tree.left, G, set(),"obj",counter)
                                self.mono2Graph_recur(sent_tree.right, G, mods, "verb", counter)
                        else:
                            self.mono2Graph_recur(sent_tree.left, G,set(),pos_left,counter)
                            return self.mono2Graph_recur(sent_tree.right, G, mods, pos_right,counter)
                    elif(any(list(map(lambda x: sent_tree.val is not None and x in sent_tree.val, list(offFocus))))):
                        if(sent_tree.val == "expl"):
                            G.expl = True
                        self.mono2Graph_recur(sent_tree.right, G, mods, pos,counter)


class GraphPipeline:
    def __init__(self):
        self.graph_logs = []

    def mono2Graph(self, sent_info):
        G = Ugraph(Unode("root", "Root", "r00t", "="))
        self.graph_logs.append(G)
        counter = PairCounter()
        G.mono2Graph_recur(sent_info, G, set(), "verb", counter)
        return G


class Chunk:
    def __init__(self, node, nodeList):
        self.node = node
        self.nodeList = nodeList
        self.ifVP = False


class Chunker:
    def __init__(self):
        self.ifGraph = False

    def insert_byOrder(self, nodeList, totalList):
        index = 0
        for i in range(len(totalList)):
            if(nodeList[-1].end < totalList[i][0].start):
                break
            index += 1
        totalList.insert(index, nodeList)
        return index

    def check_nodesForChunk(self, nodeList, center, total):
        size = len(nodeList)
        splitpos = [0, size]
        for j in range(size - 1):
            if(nodeList[j][-1].end + 1 != nodeList[j+1][0].start):
                if(j < center):
                    if(j >= splitpos[0]):
                        splitpos[0] = j
                else:
                    if((j+1) < splitpos[1]):
                        splitpos[1] = j+1
        outList = nodeList[splitpos[0]:splitpos[1]]
        newList = []
        for k in range(len(outList)):
            for node in outList[k]:
                newList.append(node)
        newChunk = Chunk(nodeList[center][0], newList)
        total.append(newChunk)
        return newChunk

    def construct_sentence(self, root):
        listNodes = list(root.nodes)
        output = []
        for k in range(len(root.nodes)):
            index = 0
            for i in range(len(output)):
                if(listNodes[k].end < output[i].start):
                    break
                index += 1
            output.insert(index, listNodes[k])
        newChunk = Chunk(None, output)
        return newChunk

    def chunk_from_nodes(self, node, results):
        if(node.isRoot):
            self.make_chunks(node, results)
            # considering chunks from clause unrelated to main clause now
            output = self.construct_sentence(node)
            results.append(output)
            return output
        if(node.nexts["all"] == set()):
            return Chunk(node, [node])
        # sorting goes:
        tempList = []
        for nodeItem in node.nexts["all"]:
            result = self.chunk_from_nodes(nodeItem, results)
            if(result is not None):
                if(nodeItem.cc != None):
                    self.insert_byOrder([nodeItem.cc],tempList)
                self.insert_byOrder(result.nodeList, tempList)
        center = self.insert_byOrder([node], tempList)
        output = self.check_nodesForChunk(tempList, center, results)

        return output
    def combine_conj_chunk(self, chunkList):
        out_results = []
        chunkList.sort(key=(lambda x: x.node.start))
        size = len(chunkList)
        splitIndex = 0
        if(chunkList != []):
            temp = Chunk(chunkList[0].node, chunkList[0].nodeList.copy())
        else:
            return []

        for j in range(size -1):
            if(chunkList[j+1].node.cc != None and chunkList[j].nodeList[-1].end + 1 == chunkList[j+1].node.cc.start):
                temp.nodeList += [chunkList[j+1].node.cc]
                temp.nodeList += chunkList[j+1].nodeList
            else:
                if(temp != []):
                    out_results.append(temp)
                temp = Chunk(chunkList[j+1].node, chunkList[j+1].nodeList.copy())
        out_results.append(temp)

        return out_results
    def make_chunks(self, graph_or_root, results):
        if(type(graph_or_root) is Ugraph):
            root = graph_or_root.root
        else:
            root = graph_or_root
        cont_out = dict()
        for cont in root.nexts.keys():
            for contNode in root.nexts[cont]:
                comp = self.chunk_from_nodes(contNode, results)
                if(cont in cont_out):
                    cont_out[cont].append(comp)
                else:
                    cont_out[cont] = []
                    cont_out[cont].append(comp)
            if(cont in cont_out):
                cont_out[cont] = self.combine_conj_chunk(cont_out[cont])
                results += cont_out[cont]           
        if("verb" in cont_out and "obj" in cont_out):
            for vbChunk in cont_out["verb"]:
                for objChunk in cont_out["obj"]:
                    if(vbChunk.node.pair == objChunk.node.pair):
                        vb = vbChunk.nodeList
                        obj = objChunk.nodeList
                        if(vb[-1].end +1 == obj[0].start):
                                vpChunk = Chunk(vbChunk.node, vb+obj)
                                vpChunk.ifVP = True
                                results.append(vpChunk)
        elif("verb" in cont_out and not "obj" in cont_out):
            for vbChunk in cont_out["verb"]:
                    vbChunk.ifVP = True
            
        outList = set()
        for nodeChunk in results:
            tempStr = ""
            for node in nodeChunk.nodeList:
                tempStr += node.word
                tempStr += " "
            #if(nodeChunk.ifVP):
            #    tempStr = "Somebody " + tempStr
            outList.add(tempStr.rstrip())

        return list(outList)

    def get_chunks_byDepTree(self, tree):
        pipe1 = GraphPipeline()
        g1 = pipe1.mono2Graph(tree)
        return self.make_chunks(g1, [])
class Controller:
    
    def check_type(self, node1, node2):
        npos1 = node1.npos
        npos2 = node2.npos
        if(npos1 is None):
            print('The word with none npos ', node1.word)
        if(npos2 is None):
            print('The word with none npos ', node2.word)
        if(npos1 in npos2 or npos2 in npos1):
            return 1
        if("VB" in npos1 and "VB" in npos2):
            return 1
        return 0
    def check_sim(self, word1, word2):
        fill = 0.4
        if(word1 == word2):
            return 1.0
        try:
            output1 = w2v_model.similarity(word1, word2)
        except:
            output1 = -1
        if(output1 < 0.9):
            try:
                list1 = word1.split(' ')
                list2 = word2.split(' ')
                output2 = model.similarity('_'.join(list1), '_'.join(list2))
            except:
                output2 = -1
        else:
            output2 = -1
        if(output1 == -1 and output2 == -1):
            return fill
        return max(output1, output2)
    def cal_sim_nodes(self, node1, node2, prop = 1.0):
        if(type(node1) is not set and type(node2) is not set and (node1.isRoot or node2.isRoot)):
            return 0
        if(type(node1) is set):
            set1 = node1
        else:
            set1 = node1.nexts["all"]
        if(type(node2) is set):
            set2 = node2
        else:
            set2 = node2.nexts["all"]
        if(set1 == set() or set2 == set()):
            if(type(node1) is not set):
                return prop * self.check_sim(node1.word.lower(), node2.word.lower())
            return 0
        nextSizes = min(len(set1), len(set2))
        tracked = set()
        outputRank = 0
        for nodeNext1 in set1:
            tempMax = [None, 0]
            for nodeNext2 in set2:
                if nodeNext2 not in tracked:
                    rank = self.cal_sim_nodes(nodeNext1, nodeNext2, prop*0.4/nextSizes)
                    if(rank >= tempMax[1]):
                        tempMax[0] = nodeNext2
                        tempMax[1] = rank
            if(tempMax[0] is None):
                break
            tracked.add(tempMax[0])
            outputRank += tempMax[1]
        if(type(node1) is set):
            return outputRank
        return 0.6*prop*self.check_sim(node1.word.lower(), node2.word.lower()) + outputRank
    def getRootNodes(self, node):
        output = set()
        for root in node.nexts["all"]:
            if(root.isRoot):
                output.add(root)
        return output
    def align_nodes(self, node1, node2, G, label1 = "all", label2 = "all", fit=False):
        aligneded = set()
        for nextNode1 in node1.nexts[label1]:
            tempMax = [None, -1]
            for nextNode2 in node2.nexts[label2]:
                if(nextNode1.isRoot and nextNode2.isRoot):
                    nextNode1.aligned.append(nextNode2)
                    nextNode2.alignedBy.append(nextNode1)
                    continue
                if(nextNode1.isRoot != nextNode2.isRoot):

                    if(nextNode1.isRoot and not nextNode1.explMain):
                        self.align_nodes(nextNode1, node2, G, "obj", label2)
                    elif(nextNode2.isRoot and not nextNode2.explMain):
                        self.align_nodes(node1, nextNode2, G, label1, "obj")

                    continue
                else:
                    score = self.cal_sim_nodes(nextNode1, nextNode2) + 0.5*self.check_type(nextNode1, nextNode2)
                #print(nextNode1.word, '  ', nextNode2.word, score)
                if(score > tempMax[1]):
                    tempMax[0] = nextNode2
                    tempMax[1] = score
                #if(score > 0.8):
                #   tempMax.append(nextNode2)
            if(tempMax[1] > 0.7):
                nextNode1.aligned.append(tempMax[0])
                tempMax[0].alignedBy.append(nextNode1)
            for alignedOne in nextNode1.aligned:
                if(nextNode1.isRoot and alignedOne.isRoot):
                    self.align_nodes(nextNode1, alignedOne, G, "nsubj","nsubj")
                    self.align_nodes(nextNode1, alignedOne, G, "verb", "verb")
                    self.align_nodes(nextNode1, alignedOne, G, "obj", "obj")
                elif(not nextNode1.isRoot and not alignedOne.isRoot ):
                    self.align_nodes(nextNode1, alignedOne, G)
            #nextNode1.aligned += tempMax
            G.align_log.append("{} => {}".format(nextNode1.word, [node.word for node in nextNode1.aligned]))
        if(fit):
            for nextNode1 in node1.nexts[label1]:
                if(nextNode1.aligned == []):
                    for nextNode2 in node2.nexts[label2]:
                        if(nextNode2.alignedBy == [] and nextNode1.isRoot == nextNode2.isRoot):
                            nextNode1.aligned.append(nextNode2)
                            nextNode2.alignedBy.append(nextNode1)
                            G.align_log.append("{} => {} by default".format(nextNode1.word, [node.word for node in nextNode1.aligned]))
    def find_Root(self, G):
        newRoot = G.root
        if(G.expl):
            for nodeSubj1 in G.root.nexts["nsubj"]:
                for nodeNext1 in nodeSubj1.nexts["all"]:
                    if (nodeNext1.isRoot):
                        newRoot = nodeNext1
                        break
            newRoot.explMain = True
        return newRoot
    def align_G(self, G1, G2):
        G1.align_log = []
        for nodeR in G2.nodes:
            nodeR.alignedBy = []
        newRoot1 = self.find_Root(G1)
        newRoot2 = self.find_Root(G2)
        #print(newRoot2.nexts["nsubj"])
        self.align_nodes(G1.root, G2.root, G1, "nsubj", "nsubj")
        self.align_nodes(newRoot1, newRoot2, G1, "verb", "verb")
        self.align_nodes(newRoot1, newRoot2, G1, "obj", "obj")
        #print(G1.align_log)
    def process_branch(self, node1, node2, label = "all"):
        toRemove = set()
        for nextNode1 in node1.nexts[label]:
            if(nextNode1.aligned != []):
                for alignedOne in nextNode1.aligned:
                    #####
                    if(alignedOne.isRoot and nextNode1.isRoot):
                        nsubjRe = self.process_branch(nextNode1, alignedOne, "nsubj")
                        verbRe = self.process_branch(nextNode1, alignedOne, "verb") 
                        objRe = self.process_branch(nextNode1, alignedOne, "obj")
                        ifRemove = nsubjRe and verbRe and objRe
                    else:
                        ifRemove = self.process_branch(nextNode1, alignedOne)
                    if(ifRemove):
                        toRemove.add(nextNode1)
                        if(alignedOne.parent == None):
                            node2.nexts[label].discard(alignedOne)
                        else:
                            alignedOne.parent.nexts[label].discard(alignedOne)
        for item in toRemove:
            node1.nexts[label].discard(item)


        if(node1.nexts[label] == set() and node2.nexts[label] ==set() and node1.word == node2.word):
            return True
        return False
    def process_graph(self, G1, G2):
        self.process_branch(G1.root, G2.root, "nsubj")
        newRoot1 = self.find_Root(G1)
        newRoot2 = self.find_Root(G2)
        self.process_branch(newRoot1, newRoot2, "verb")
        self.process_branch(newRoot1, newRoot2, "obj")
        #jupyter_draw_nltk_tree(Tree.fromstring(G1.get_magicText()))
        #jupyter_draw_nltk_tree(Tree.fromstring(G2.get_magicText()))

    def find_not(self, node1, node2, label = "all"):
        nots = 0
        nots2 = 0
        for nextItem in node1.nexts[label]:
            if(nextItem.isRoot):
                for aligned in nextItem.aligned:
                    nots += self.check_con(nextItem, aligned)
                continue
            if(nextItem.word in negation_words and not(nextItem.npos == "DT" and nextItem.aligned != [])):
                nots += 1
            #elif(nextItem.npos == "DT" and nextItem.aligned != []):
            #    for alignedNext in nextItem.aligned:
                    #det_con(nextItem, alignedNext)
        for nextItem2 in node2.nexts[label]:
            if(nextItem2.word in negation_words and not(nextItem2.npos == "DT" and nextItem2.alignedBy != [])):
                nots2 += 1

        return nots, nots2
    def check_con(self, root1, root2):
        notUps = 0
        notDowns = 0
        for node1 in root1.nexts["nsubj"]:
            if(node1.word.lower() in ["nobody","nothing"]):
                notUps += 1
            for aligned in node1.aligned:
                if(aligned.word.lower() in ["nobody", "nothing"]):
                    notDowns += 1

            if(notUps ==0 and notDowns ==0):
                for nodeNext1 in node1.nexts["all"]:
                    if(nodeNext1.word in negation_words):
                        notUps += 1
                for aligned in node1.aligned:
                    for nodeNext2 in aligned.nexts["all"]:
                        if(nodeNext2.word in negation_words):
                            notDowns += 1

        nsubjNot = abs(notUps-notDowns)%2
        notUps = 0
        notDowns = 0

        for nodev in root1.nexts["verb"]:
            if(notUps ==0 and notDowns ==0):
                for alignedv in nodev.aligned:
                    #if(alignedv.word != nodev.word):
                    #    return 3
                    wordv = stemmer.stem(nodev.word.lower())
                    alignwordv = stemmer.stem(alignedv.word.lower())
                    #print(wordv)
                    #print(alignwordv)
                    try:
                        notUps += wordv in get_word_sets(alignwordv)[3] or alignwordv in get_word_sets(wordv)[3] \
                                                or wordv in contradict_verbs.get(alignwordv, set())     
                    except:
                        notUps += 0
                    nots = self.find_not(nodev, alignedv)
                    notUps += nots[0]
                    notDowns += nots[1]

        verbNot = abs(notUps-notDowns)%2
        #print(verbNot)

        notUps = 0
        notDowns = 0
        for nodeo in root1.nexts["obj"]:
            if(notUps ==0 and notDowns ==0):
                for alignedo in nodeo.aligned:
                    try:
                        notUps += nodeo.word.lower() in get_word_sets(alignedo.word.lower())[3]
                    except:
                        notUps += 0
              
                    nots = self.find_not(nodeo, alignedo)
                    notUps += nots[0]
                    notDowns += nots[1]

        objNot = abs(notUps-notDowns)%2

        if((verbNot+nsubjNot+objNot)%2 == 1 ):
            return 1

        return 0
    def control_direct(self, node1, node2, ranks, logs, label="all"):
        if(not node1.isRoot and not node2.isRoot and node1.nexts[label] == set() and node2.nexts[label] == set() 
                   and node1.word.lower() != node2.word.lower()):
            ranks[0] += 1
            logs.append([0, node1.start, node2.start, node1.word, node2.word])
            return
        ##
        for node11 in node1.nexts[label]:
            if(node11.aligned == [] and not node11.explMain):
                ranks[1] += 1
                logs.append([1, node11.start, -1,node11.word,None])
        for node22 in node2.nexts[label]:
            if(node22.alignedBy == [] and not node22.explMain):
                ranks[1] += 1
                logs.append([1, -1, node22.start, None, node22.word])

        if(self.check_sim(node1.word.lower(), node2.word.lower()) > 0.9):#node1.word.lower() == node2.word.lower() or 
            if(node1.word.lower() != node2.word.lower()):
                ranks[0] += 1
                logs.append([0, node1.start, node2.start, node1.word, node2.word])
            for new1 in node1.nexts[label]:
                for new2 in new1.aligned:
                    if(new1.isRoot and new2.isRoot):
                        self.control_direct(new1, new2, ranks, logs,"nsubj")
                        self.control_direct(new1, new2, ranks, logs, "verb")
                        self.control_direct(new1, new2, ranks, logs, "obj")
                    else:
                        self.control_direct(new1, new2, ranks, logs)
        else:
            ranks[2] += 1
            logs.append([2, node1.start, node2.start, node1.word, node2.word])
    def control_graph(self, G1, G2):
        ranks = [0] * 3
        logs = []
        newRoot1 = self.find_Root(G1)
        newRoot2 = self.find_Root(G2)
        self.control_direct(G1.root, G2.root, ranks, logs, "nsubj")
        self.control_direct(newRoot1, newRoot2, ranks, logs, "verb")
        self.control_direct(newRoot1, newRoot2, ranks, logs, "obj")
        return logs
        #print(logs)
    def controlPipeline(self, tree1, tree2):
        gp = GraphPipeline()
        gh1 = gp.mono2Graph(tree1)
        gh2 = gp.mono2Graph(tree2)
        self.align_G(gh1, gh2)
        self.process_graph(gh1,gh2)
        return self.control_graph(gh1, gh2)
