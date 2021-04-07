import json
import urllib.request
from nltk.corpus import wordnet


def find_relation(word1, word2, pos, verbose=0):
    hyper, hypo, syn, ant = get_word_sets(word2, pos)

    if verbose == 1:
        print("hypernyms:", hyper)
        print("hyponyms:", hypo)
        print("synonyms:", syn)
        print("antonyms:", ant)

    if word1 in hyper:
        return 'hypernym'  # word1 > word2
    elif word1 in hypo:
        return 'hyponym'  # word1 < word2
    elif word1 in syn:
        return 'synonym'
    elif word1 in ant:
        return 'antonym'
    return None


class ConceptNet:
    def __init__(self):
        self.url = "http://api.conceptnet.io/"

    def lookup(self, lang, term, verbose):
        url_to_search = self.url + "c/" + lang + "/" + term
        data = urllib.request.urlopen(url_to_search)
        json_data = json.load(data)
        if verbose:
            # print(url_to_search)
            for edge in json_data["edges"]:
                print("--------------")
                print(edge['end']['label'])
                print(edge['rel']['label'])

    def get_sense_label(self, concept):
        url_to_search = self.url + "query?end=/c/en/" + concept
        data = urllib.request.urlopen(url_to_search)
        json_data = json.load(data)
        for edge in json_data["edges"]:
            if "sense_label" in edge["end"]:
                return edge["end"]["sense_label"]

    def relation(self, concept, rel='IsA'):
        synonyms = {}
        url_to_search = self.url + "query?end=/c/en/" + \
            concept + "&rel=/r/" + "RelatedTo" + "&limit=50"
        # print(url_to_search)
        data = urllib.request.urlopen(url_to_search)
        json_data = json.load(data)
        for edge in json_data["edges"]:
            surface_text = edge['surfaceText']
            if edge['start']["language"] == 'en':
                # if 'a type of' in surface_text or 'a kind of' in surface_text:
                synonyms[edge['start']['label']] = 1

        hypernyms = {}
        url_to_search = self.url + "query?start=/c/en/" + \
            concept + "&rel=/r/" + "IsA" + "&limit=50"
        # print(url_to_search)
        data = urllib.request.urlopen(url_to_search)
        json_data = json.load(data)
        for edge in json_data["edges"]:
            surface_text = edge['surfaceText']
            if edge["weight"] >= 1.0:
                # if 'a type of' in surface_text or 'a kind of' in surface_text:
                hypernyms[edge['end']['label']] = 1

        hyponyms = {}
        url_to_search = self.url + "query?end=/c/en/" + \
            concept + "&rel=/r/" + "IsA" + "&limit=50"
        # print(url_to_search)
        data = urllib.request.urlopen(url_to_search)
        json_data = json.load(data)
        for edge in json_data["edges"]:
            if edge["weight"] >= 1.0:
                hyponyms[edge['start']['label']] = 1

        antonyms = {}
        url_to_search = self.url + "query?end=/c/en/" + \
            concept + "&rel=/r/" + "Antonym" + "&limit=20"
        # print(url_to_search)
        data = urllib.request.urlopen(url_to_search)
        json_data = json.load(data)
        for edge in json_data["edges"]:
            if edge['start']["language"] == 'en' and edge["weight"] >= 0.1:
                antonyms[edge['start']['label']] = 1

        return hypernyms, hyponyms, synonyms, antonyms


def get_word_sets(word):
    synonyms = {}
    antonyms = {}
    hypernyms = {}
    hyponyms = {}

    for syn in wordnet.synsets(word):
        for x in syn.hypernyms():
            for l in x.lemmas():
                hypernyms[l.name().replace('_', ' ')] = 1
        for x in syn.hyponyms():
            for l in x.lemmas():
                hyponyms[l.name().replace('_', ' ')] = 1
        for l in syn.lemmas():
            synonyms[l.name().replace('_', ' ')] = 1
            if l.antonyms():
                antonyms[l.antonyms()[0].name().replace('_', ' ')] = 1

    conceptNet = ConceptNet()
    hyper, hypo, syn, ant = conceptNet.relation(word)
    hypernyms_full = {**hypernyms, **hyper}
    hyponyms_full = {**hyponyms, **hypo}
    synonyms_full = {**synonyms, **syn}
    antonyms_full = {**antonyms, **ant}

    sense_label = conceptNet.get_sense_label(word)

    return hypernyms_full, hyponyms_full, synonyms_full, antonyms_full, sense_label


def test():
    relation = find_relation('animal', 'dog', 'nn', verbose=1)
    print(relation)


if __name__ == '__main__':
    hypernyms, hyponyms, synonyms, antonyms, sense_label = get_word_sets(
        "cyclist")
    print(list(hypernyms))
    # print(list(hyponyms))
    print(list(synonyms))
    print(list(antonyms))
    print(sense_label)
