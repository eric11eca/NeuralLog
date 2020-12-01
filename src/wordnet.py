import urllib.request
import requests
import json
import spacy
import itertools

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
            print(url_to_search)
            for edge in json_data["edges"]:
                print("--------------")
                print(edge['end']['label'])
                print(edge['rel']['label'])

    def relation(self, concept, rel='IsA'):
        hypernyms = set([])
        url_to_search = self.url + "query?start=/c/en/" + \
            concept + "&rel=/r/" + rel + "&limit=1000"
        data = urllib.request.urlopen(url_to_search)
        json_data = json.load(data)
        for edge in json_data["edges"]:
            hypernyms.add(edge['end']['label'])

        url_to_search = self.url + "query?end=/c/en/" + \
            concept + "&rel=/r/" + rel + "&limit=1000"
        data = urllib.request.urlopen(url_to_search)
        json_data = json.load(data)
        hyponyms = set([])
        for edge in json_data["edges"]:
            hyponyms.add(edge['start']['label'])

        return hypernyms, hyponyms


def get_word_sets(word, pos):
    synonyms = set([])
    antonyms = set([])
    hypernyms = set([])
    hyponyms = set([])

    for syn in wordnet.synsets(word):
        for x in syn.hypernyms():
            for l in x.lemmas():
                hypernyms.add(l.name().replace('_', ' '))
        for x in syn.hyponyms():
            for l in x.lemmas():
                hyponyms.add(l.name().replace('_', ' '))
        for l in syn.lemmas():
            synonyms.add(l.name().replace('_', ' '))
            if l.antonyms():
                antonyms.add(l.antonyms()[0].name().replace('_', ' '))

    conceptNet = ConceptNet()
    hyper, hypo = conceptNet.relation(word)
    hypernyms = hypernyms.union(hyper)
    hyponyms = hyponyms.union(hypo)

    return hypernyms, hyponyms, synonyms, antonyms


def test():
    relation = find_relation('animal', 'bird', 'nn')
    print(relation)


if __name__ == '__main__':
    test()
