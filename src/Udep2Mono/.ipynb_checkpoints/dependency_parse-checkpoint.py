import os
import copy
import string
import stanza

from nltk.parse import CoreNLPParser
from nltk.parse.corenlp import CoreNLPDependencyParser

parser = CoreNLPParser(url='http://localhost:9000')
dep_parser = CoreNLPDependencyParser(url='http://localhost:9000')

nlp = stanza.Pipeline(
    "en",
    processors={"tokenize": "gum", "pos": "gum",
                "lemma": "gum", "depparse": "gum"},
    use_gpu=True,
    pos_batch_size=2000
)

# cd ./Desktop/Udep2Mono/NaturalLanguagePipeline/lib/stanford-corenlp-4.1.0
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000

replacement = {
    "out of": "out-of",
    "none of the": "none-of-the",
    "all of the": "all-of-the",
    "some of the": "some-of-the",
    "most of the": "most-of-the",
    "many of the": "many-of-the",
    "several of the": "several-of-the",
    "some but not all": "some-but-not-all"
}


def preprocess(sentence):
    replaced = {}
    processed = sentence.lower()
    for orig in replacement:
        if orig in processed:
            processed = processed.replace(orig, replacement[orig])
            replaced[replacement[orig]] = orig
    return processed, replaced


def dependencyParse(sentence, parser="stanford"):
    processed, replaced = preprocess(sentence)
    if parser == "stanford":
        return stanfordParse(processed), replaced
    elif parser == "stanza":
        return stanzaParse(processed), replaced


def stanzaParse(sentence):
    postag = {}
    words = {}
    parsed = nlp(sentence)
    parse_tree = []
    for sent in parsed.sentences:
        for word in sent.words:
            tree_node = postProcess(sent, word, postag, words)
            if len(tree_node) > 0:
                parse_tree.append(tree_node)

    # for tree_node in parse_tree:
    #    printTree(tree_node, postag, words)
    return parse_tree, postag, words


def postProcess(sent, word, postag, words):
    wordID = int(word.id)
    if wordID not in words:
        postag[word.text] = (wordID, word.xpos)
        words[wordID] = (word.text, word.xpos)
    if word.deprel != "punct":
        tree_node = [word.deprel, wordID,
                     word.head if word.head > 0 else "root"]
        return tree_node
    return []


def printTree(tree, tag, word):
    if tree[0] != "root":
        print(
            f"word: {word[tree[1]][0]}\thead: {word[tree[2]][0]}\tdeprel: {tree[0]}",
            sep="\n",
        )


def stanfordParse(sentence):
    postag = {}
    wordids = {}
    tokens = {}
    parse_tree = []

    tokenized = list(parser.tokenize(sentence))
    for i in range(len(tokenized)):
        tokens[tokenized[i]] = i+1

    parsed = list(dep_parser.raw_parse(sentence))[0]
    dep_rels = parsed.to_conll(4).split('\n')
    for dep_rel in dep_rels:
        rel = dep_rel.split('\t')
        if len(rel) == 4:
            dependent = tokens[rel[0]]
            govenor = int(rel[2])
            relation = rel[3].lower()
            postag[rel[0]] = (dependent, rel[1])
            wordids[dependent] = (rel[0], rel[1])
            if relation != "punct":
                parse_tree.append([relation, dependent, govenor])
    return parse_tree, postag, wordids


if __name__ == '__main__':
    nlp = stanza.Pipeline(
        'es',
        use_gpu=True,
        pos_batch_size=2000
    )

    parsed, replace = dependencyParse("buen tiempo", parser="stanza")
    tree, postags, words = parsed
    print(tree)
    print(postags)
    parsed, replace = dependencyParse("tiempo de bueno", parser="stanza")
    tree, postags, words = parsed
    print(tree)
    print(postags)
