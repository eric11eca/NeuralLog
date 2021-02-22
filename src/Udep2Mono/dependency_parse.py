import stanza

#from nltk.parse import CoreNLPParser
#from nltk.parse.corenlp import CoreNLPDependencyParser

#parser = CoreNLPParser(url='http://localhost:9000')
#dep_parser = CoreNLPDependencyParser(url='http://localhost:9000')

pkg = "ewt"
pkg = "gum"

nlp = stanza.Pipeline(
    "en",
    processors={"tokenize": pkg, "pos": pkg,
                "lemma": pkg, "depparse": pkg},
    use_gpu=True,
    pos_batch_size=2000
)

# cd ./Desktop/Udep2Mono/NaturalLanguagePipeline/lib/stanford-corenlp-4.1.0
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000

replacement = {
    "out of": "out-of",
    "none of the": "no",
    "all of the": "all",
    "some of the": "some",
    "most of the": "most",
    "many of the": "many",
    "several of the": "several",
    "some but not all": "some",
    "at most": "at-most",
    "at least": "at-least",
    "more than": "more-than",
    "less than": "less-than",
}


def preprocess(sentence):
    replaced = {}
    processed = sentence.lower()
    for orig in replacement:
        if orig in processed:
            processed = processed.replace(orig, replacement[orig])
            replaced[replacement[orig]] = orig
    return processed, replaced


def dependency_parse(sentence, parser="stanford"):
    processed, replaced = preprocess(sentence)
    if parser == "stanford":
        return stanford_parse(processed), replaced
    elif parser == "stanza":
        return stanza_parse(processed), replaced


def stanza_parse(sentence):
    postags = {}
    words = {}
    parse_tree = []
    head_log = {}
    depdent_log = {}
    parsed = nlp(sentence)

    for sent in parsed.sentences:
        for word in sent.words:
            tree_node = post_process(sent, word, postags, words)

            if len(tree_node) == 0:
                continue

            if tree_node[2] in head_log:
                head_log[tree_node[2]].append(tree_node[0])
            else:
                head_log[tree_node[2]] = [tree_node[0]]

            if tree_node[1] in depdent_log:
                depdent_log[tree_node[1]].append(tree_node[0])
            else:
                depdent_log[tree_node[1]] = [tree_node[0]]

            parse_tree.append(tree_node)

        enhance_parse(parse_tree, head_log, depdent_log, words)
    return parse_tree, postags, words


def enhance_parse(tree, heads, deps, words):
    for node in tree:
        if node[0] == "conj":
            if "nsubj" in heads[node[1]] and "nsubj" in heads[node[2]]:
                node[0] = "conj-sent"
            elif words[node[1]][1] == "JJ" and words[node[2]][1] == "JJ":
                node[0] = "conj-adj"
            elif "NN" in words[node[1]][1] and "NN" in words[node[2]][1]:
                node[0] = "conj-n"
                vp_rel = set(["amod", "compound", "compound",  "compound:prt", "det",
                              "nummod", "appos", "advmod", "nmod", "nmod:poss"])
                vp_left = set(heads[node[1]]) & vp_rel
                vp_right = set(heads[node[2]]) & vp_rel
                if len(vp_left) and len(vp_right):
                    node[0] = "conj-np"
            elif "VB" in words[node[1]][1] and "VB" in words[node[2]][1]:
                node[0] = "conj-vb"
                vp_rel = set(["obj", "xcomp", "obl"])
                vp_left = set(heads[node[1]]) & vp_rel
                vp_right = set(heads[node[2]]) & vp_rel

                if len(vp_left):
                    if len(vp_right):
                        node[0] = "conj-vp"
                    # else:

        if node[0] == "advcl":
            if words[1][0] == "if":
                node[0] = "advcl-sent"
        if node[0] == "advmod":
            if words[node[1]][0] == "not" and node[1] == 1:
                node[0] = "advmod-sent"
        if node[0] == "case" and node[1] - node[2] > 0:
            node[0] = "case-after"
        if words[node[1]][0] in ["at-most", "at-least", "more-than", "less-than"]:
            node[0] = "det"


def post_process(sent, word, postag, words):
    word_id = int(word.id)
    if word_id not in words:
        postag[word.text] = (word_id, word.xpos)
        words[word_id] = (word.text, word.xpos)
    if word.deprel != "punct":
        tree_node = [word.deprel, word_id,
                     word.head if word.head > 0 else "root"]
        return tree_node
    return []


def printTree(tree, tag, word):
    if tree[0] != "root":
        print(
            f"word: {word[tree[1]][0]}\thead: {word[tree[2]][0]}\tdeprel: {tree[0]}", sep="\n")


def stanford_parse(sentence):
    postag = {}
    wordids = {}
    head_log = {}
    depdent_log = {}
    parse_tree = []

    tokenized = list(parser.tokenize(sentence))

    parsed = list(dep_parser.raw_parse(sentence))[0]
    dep_rels = parsed.to_conll(4).split('\n')
    for dep_rel in dep_rels:
        rel = dep_rel.split('\t')
        if len(rel) == 4:
            dependent = tokenized.index(rel[0]) + 1
            govenor = int(rel[2])
            relation = rel[3].lower()
            postag[rel[0]] = (dependent, rel[1])
            wordids[dependent] = (rel[0], rel[1])

            if relation != "punct":
                node = [relation, dependent, govenor]

                if node[2] in head_log:
                    head_log[node[2]].append(node[0])
                else:
                    head_log[node[2]] = [node[0]]

                if node[1] in depdent_log:
                    depdent_log[node[1]].append(node[0])
                else:
                    depdent_log[node[1]] = [node[0]]

                parse_tree.append(node)

    enhance_parse(parse_tree, head_log, depdent_log, wordids)
    return parse_tree, postag, wordids


if __name__ == '__main__':
    # test spanish model
    '''nlp = stanza.Pipeline(
        'es',
        use_gpu=True,
        pos_batch_size=2000
    )

    parsed, replace = dependency_parse("buen tiempo", parser="stanza")
    tree, postags, words = parsed
    print(tree)
    print(postags)
    parsed, replace = dependency_parse("tiempo de bueno", parser="stanza")
    tree, postags, words = parsed
    print(tree)
    print(postags)'''

    tree, postags, words = stanza_parse("A girl makes and eats an apple")
    print(tree)
    print(words)
