import json


def post_process(word, deprel, word_id, words):
    if word_id not in words:
        words[word_id] = word
    if deprel[1] != "punct":
        tree_node = [deprel[1], word_id,
                     deprel[0] if deprel[0] > 0 else "root"]
        return tree_node
    return []


def udify_parse():
    parsed = []
    with open('output.txt', 'r') as depparse:
        for p in depparse:
            parsed.append(json.loads(p))

    parse_trees = []
    for sent in parsed:
        words = {}
        deptree = []
        head_log = {}
        depdent_log = {}

        word = zip(sent['words'], sent['upos'])
        deprel = zip(sent['predicted_heads'], sent['predicted_dependencies'])
        tree = list(zip(word, deprel))

        for i in range(len(tree)):
            tree_node = post_process(tree[i][0], tree[i][1], i+1, words)
            if len(tree_node) == 0:
                continue

            if tree_node[2] in head_log:
                head_log[tree_node[2]].append(tree_node[0])
            else:
                head_log[tree_node[2]] = [tree_node[0]]

            if not tree_node[1] in head_log:
                head_log[tree_node[1]] = []

            if tree_node[1] in depdent_log:
                depdent_log[tree_node[1]].append(tree_node[0])
            else:
                depdent_log[tree_node[1]] = [tree_node[0]]

            deptree.append(tree_node)

        enhance_parse(deptree, head_log, depdent_log, words)
        parse_trees.append((deptree, words))
    return parse_trees


def enhance_parse(tree, heads, deps, words):
    for node in tree:
        if node[0] == "conj":
            if "nsubj" in heads[node[1]] and "nsubj" in heads[node[2]]:
                node[0] = "conj-sent"
            elif words[node[1]][1] == "JJ" and words[node[2]][1] == "JJ":
                node[0] = "conj-adj"
            elif "NOUN" in words[node[1]][1] and "NOUN" in words[node[2]][1]:
                node[0] = "conj-n"
                vp_rel = set(["amod", "compound", "compound",  "compound:prt", "det",
                              "nummod", "appos", "advmod", "nmod", "nmod:poss"])
                vp_left = set(heads[node[1]]) & vp_rel
                vp_right = set(heads[node[2]]) & vp_rel
                if len(vp_left) and len(vp_right):
                    node[0] = "conj-np"
            elif "VERB" in words[node[1]][1] and "VERB" in words[node[2]][1]:
                node[0] = "conj-vb"
                vp_rel = set(["obj", "xcomp", "obl"])
                vp_left = set(heads[node[1]]) & vp_rel
                vp_right = set(heads[node[2]]) & vp_rel

                if len(vp_left):
                    if len(vp_right):
                        node[0] = "conj-vp"
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
