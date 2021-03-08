import stanza

#from nltk.parse import CoreNLPParser
#from nltk.parse.corenlp import CoreNLPDependencyParser

#parser = CoreNLPParser(url='http://localhost:9000')
#dep_parser = CoreNLPDependencyParser(url='http://localhost:9000')

depparse_gum_config = {
    'lang': "en",
    'processors': "tokenize,pos,lemma,depparse",
    'tokenize_model_path': '../model/en/tokenize/gum.pt',
    'pos_model_path': '../model/en/pos/ewt.pt',
    'depparse_model_path': '../model/en/depparse/gum.pt',
    'lemma_model_path': '../model/en/lemma/gum.pt',
    'use_gpu': True,
    'pos_batch_size': 3000
}

"""depparse_ewt_config = {
    'lang': "en",
    'processors': "tokenize,pos,lemma,depparse",
    'tokenize_model_path': '../model/en/tokenize/gum.pt',
    'pos_model_path': '../model/en/pos/ewt.pt',
    'depparse_model_path': '../model/en/depparse/ewt.pt',
    'lemma_model_path': '../model/en/lemma/ewt.pt',
    'use_gpu': True,
    'pos_batch_size': 3000
}"""

token_config = {
    'lang': "en",
    'processors': "tokenize",
    'tokenize_model_path': '../model/en/tokenize/gum.pt',
    'use_gpu': True,
    'pos_batch_size': 3000
}

gum_depparse = stanza.Pipeline(**depparse_gum_config)
#ewt_depparse = stanza.Pipeline(**depparse_ewt_config)
tokenizer = stanza.Pipeline(**token_config)

# cd ./Desktop/Udep2Mono/NaturalLanguagePipeline/lib/stanford-corenlp-4.1.0
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000

replacement = {

    "a few": "a-few",
    "a lot of": "a-lot-of",
    "lots of": "lots-of",

    "a few of the": "a-few-of-the",
    "none of the": "none-of-the",
    "all of the": "all-of-the",
    "each of the": "each-of-the",
    "some of the": "some-of-the",
    "most of the": "most-of-the",
    "many of the": "many-of-the",
    "several of the": "several-of-the",
    "some but not all": "some-but-not-all",
    "at most": "at-most",
    "at least": "at-least",
    "more than": "more-than",
    "less than": "less-than",

    "after all": "after-all",
    "out of": "out-of",
    "hardly ever": "hardly-ever",
    "even if": "even-if",
    "no longer": "no-longer",

    "A few": "A-few",
    "A few of the": "A-few-of-the",
    "None of the": "None-of-the",
    "All of the": "All-of-the",
    "Some of the": "Some-of-the",
    "Most of the": "Most-of-the",
    "Many of the": "Many-of-the",
    "Several of the": "Several-of-the",
    "Some but not all": "Some-but-not-all",
    "At most": "At-most",
    "At least": "At-least",
    "More than": "More-than",
    "Less than": "Less-than",
    "No longer": "No-longer",
    "A lot of": "A-lot-of",
    "Lots of": "Lots-of",
    "Each of the": "Each-of-the",
    "Even if": "Even-if",

    "not every": "not-every",
    "not some": "not-some",
    "not all": "not-all",
    "not each": "not-each",
    "Not every": "Not-every",
    "Not some": "Not-some",
    "Not all": "Not-all",
    "Not each": "Not-each",
}

quantifier_replacement = {
    "a-few": "some",
    "a-few of the": "some",
    "none-of-the": "no",
    "all-of-the": "all",
    "some-of-the": "some",
    "most-of-the": "most",
    "many-of-the": "many",
    "several-of-the": "several",
    "some-but-not-all": "some",
    "at-most": "no",
    "at-least": "some",
    "more-than": "some",
    "less-than": "no",
    "no-longer": "not",
    "a-lot-of": "some",
    "lots-of": "some",
    "each of the": "each",
    "A-few": "Some",
    "A-few of the": "Some",
    "None-of-the": "No",
    "All-of-the": "All",
    "Some-of-the": "Some",
    "Most-of-the": "Most",
    "Many-of-the": "Many",
    "Several-of-the": "Several",
    "Some-but-not-all": "Some",
    "At-most": "No",
    "At-least": "Some",
    "More-than": "Some",
    "Less-than": "No",
    "No-longer": "Not",
    "A-lot-of": "Some",
    "Lots-of": "Some",
    "Each of the": "Each",
    "hardly-ever": "never",
    "Even-if": "If",
    "even-if": "if",
    "not-every": "every",
    "not-some": "some",
    "not-all": "all",
    "not-each": "each",
    "Not-every": "every",
    "Not-some": "some",
    "Not-all": "all",
    "Not-each": "each",

    "after-all": "after-all",
    "out-of": "out-of",
    "hardly-ever": "never",
    "no-longer": "no-longer",
}


def preprocess(sentence):
    replaced = {}
    processed = sentence
    for orig in replacement:
        if orig in processed:
            processed = processed.replace(orig, replacement[orig])

    tokens = tokenizer(processed).sentences[0].words
    for tok in tokens:
        if tok.text in quantifier_replacement:
            processed = processed.replace(
                tok.text, quantifier_replacement[tok.text])
            replaced[str((quantifier_replacement[tok.text], tok.id))] = tok.text

    return processed, replaced


def dependency_parse(sentence, parser="gum"):
    processed, replaced = preprocess(sentence)
    return stanza_parse(processed, parser=parser), replaced


def stanza_parse(sentence, parser="gum"):
    postags = {}
    words = {}
    parse_tree = []
    head_log = {}
    depdent_log = {}

    parsed = gum_depparse(sentence)
    """if parser == "ewt":
        parsed = ewt_depparse(sentence)"""

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


"""def stanford_parse(sentence):
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
"""

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
