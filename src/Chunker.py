import binarytree as bt
from wordnet import find_relation, get_word_sets
from PIL import Image, ImageDraw
from nltk.tree import Tree
from nltk.draw import TreeWidget
from nltk.draw.util import CanvasFrame
from IPython.display import Image, display

nounModifiers = {"det", "nummod", "amod", "obl:tmod",
                 "acl:relcl", "nmod", "case", "nmod:pass",  "acl", "Prime","cc"}
verbModifiers = {"advmod", "obl","xcomp","advcl","mark","aux"}
nounCategories = {"compound"}
verbs = {"VBZ", "VBP", "VBD", "VBG"}
modified = {"NN", "PRP", "JJ", "VB"}.union(verbs)
modifiers = nounModifiers.union(verbModifiers)
offFocus = {"expl"}
contents = {"nsubj", "obj", "cop", "compound",
            "conj", "nsubj:pass"}
cont_npos = {"nsubj": 'nn', "obj": 'nn', "cop": 'vbz', "verb": 'vbz'}
mark_toProp = {"+": {"hyponym", "synonym"},
               "-": {"hypernym", "synonym"}, "=": {"synonym"}}
clause_prop = {"which", "that", "who"}
be_verbs = {"is", "am", "are", "be"}
directions = {0: "lexical", 1: "phrasal",
              2: "syntatic_variation", 3: "implicative"}
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
    def add_Unode(self, node):
        # print(node.prop)
        if(self.isRoot):
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

    def add_node(self, node):
        self.nodes.add(node)
        self.root.addNode(node)

    def add_edge(self, node1, node2):
        if(node1.isRoot):
            self.contentSet.add(node2.word)
        node1.add_Unode(node2)

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
    
    def mono2Graph_recur(self, sent_tree, G, mods, pos=None, counter=-1):
        if(sent_tree is None):
            return
        else:
            if(any(list(map(lambda x: sent_tree.val is not None and x in sent_tree.val, list(modifiers))))):
                if("acl" in sent_tree.val):
                    pipeTemp = GraphPipeline()
                    G_prime = pipeTemp.mono2Graph(sent_tree.left)
                    mods.add(G_prime.root)
                else:
                    left_result = self.mono2Graph_recur(
                        sent_tree.left, G, set(), sent_tree.val, counter)
                    if(left_result is not None):
                        if(type(left_result) is set):
                            for item_result in left_result:
                                if(item_result is not None):
                                    mods.add(item_result)
                        else:
                            mods.add(left_result)

                return self.mono2Graph_recur(sent_tree.right, G, mods, pos, counter)
            else:
                if ((sent_tree.left is None and sent_tree.right is None) or sent_tree.val == "compound"):
                    if(sent_tree.val == 'and'):
                        return
                    if(sent_tree.val == "compound"):
                        newNode = Unode(pos, sent_tree.left.val,
                                        sent_tree.pos, sent_tree.mark)
                        newNode.start = sent_tree.left.id
                        self.combine_comp(sent_tree.right, newNode)
                        if(pos in contents or pos == "verb"):
                            G.add_edge(G.root, newNode)
                            if(pos != "nsubj"):
                                G.addPair(newNode, counter.obj, "obj")
                                if(pos == "verb"  and sent_tree.parent.val != "cop"):
                                    counter.incrementO()
                        for node in mods:
                            if(node.npos == "CC"):
                                newNode.addCC(node)
                            else:
                                G.add_edge(newNode, node)
                        return newNode
                    newNode = Unode(pos, sent_tree.val,
                                    sent_tree.pos, sent_tree.mark)
                    newNode.start = sent_tree.id
                    newNode.end = sent_tree.id
                    G.add_node(newNode)
                    if (any(list(map(lambda x: sent_tree.pos is not None and x in sent_tree.pos, list(modified))))
                        or any(list(map(lambda x: pos is not None and x in pos, list(contents))))
                            or pos == "verb"):
                        if(pos in contents or pos == "verb"):

                            G.add_edge(G.root, newNode)
                            if(pos != "nsubj"):
                                G.addPair(newNode, counter.obj, "obj")
                                if(pos == "verb"  and sent_tree.parent.val != "cop"):
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
                            self.mono2Graph_recur(
                                sent_tree.right, G, mods, "verb", counter)
                        elif("obj" in sent_tree.val and pos != "verb"):
                            right_result = self.mono2Graph_recur(
                                sent_tree.right, G, set(), "Prime", counter)
                            if(right_result is not None):
                                mods.add(right_result)
                            self.mono2Graph_recur(
                                sent_tree.left, G, mods, pos_left, counter)
                        else:
                            self.mono2Graph_recur(
                                sent_tree.left, G, set(), pos_left, counter)
                            self.mono2Graph_recur(
                                sent_tree.right, G, mods, pos_right, counter)
                    elif(any(list(map(lambda x: sent_tree.val is not None and x in sent_tree.val, list(offFocus))))):
                        self.mono2Graph_recur(
                            sent_tree.right, G, mods, pos, counter)


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
            if(nodeChunk.ifVP):
                tempStr = "Somebody " + tempStr
            outList.add(tempStr.rstrip())

        return list(outList)

    def get_chunks_byDepTree(self, tree):
        pipe1 = GraphPipeline()
        g1 = pipe1.mono2Graph(tree)
        return self.make_chunks(g1, [])
