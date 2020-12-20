from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.UdepLog
quantifier = db.quantifier
implicative = db.implicative


universals = [{"word": "all",
               ">": [],
               "<": ["most", "many", "several", "some", "a", "an", "one"],
               "=": ["each", "every", "all-of-the", "each-of-the"],
               "!": []},
              {"word": "every",
               ">": [],
               "<": ["most", "many", "several", "some", "a", "an", "one"],
               "=": ["each", "all", "all-of-the", "each-of-the"],
               "!": []},
              {"word": "each",
               ">": [],
               "<": ["most", "many", "several", "some", "a", "an", "one"],
               "=": ["all", "every", "all-of-the", "each-of-the"],
               "!": []},
              {"word": "all-of-the",
               ">": [],
               "<": ["most", "many", "several", "some", "a", "an", "one"],
               "=": ["each", "every", "all", "each-of-the"],
               "!": []},
              {"word": "each-of-the",
               ">": [],
               "<": ["most", "many", "several", "some", "a", "an", "one"],
               "=": ["each", "every", "all", "all-of-the"],
               "!": []}]

#result = quantifier.insert_many(universals)
existial = [
    {"word": "some",
     ">": ["every", "all", "each", "most", "many", "several", "the", "at-least", "num"],
     "<": [],
     "=": ["a", "an", "one", "at-least-1"],
     "!": []},
    {"word": "a",
     ">": ["every", "all", "each", "most", "many", "several", "the", "at-least", "num"],
     "<": [],
     "=": ["some", "an", "one"],
     "!": []},
    {"word": "an",
        ">": ["every", "all", "each", "most", "many", "several", "the", "at-least", "num"],
        "<": [],
        "=": ["a", "some", "one"],
        "!": []},
    {"word": "several",
        ">": ["every", "all", "each", "most", "many", "num"],
        "<": ["some", "a", "an", "one",  "at-least-several"],
        "=": ["a few", "several-of-the"],
        "!": []},
    {"word": "a-few",
        ">": ["every", "all", "each", "most", "many", "num"],
        "<": ["some", "a", "an", "one",  "at-least-several"],
        "=": ["several", "several-of-the"],
        "!": []},
    {"word": "several-of-the",
     ">": ["every", "all", "each", "most", "many", "num"],
     "<": ["some", "a", "an", "one",  "at-least-several"],
     "=": ["several", "a-few"],
     "!": []},
    {"word": "the",
     ">": [],
     "<": [""],
     "=": ["a", "an", "one"],
     "!": []},
]

#result = quantifier.insert_many(existial)
negation = [
    {"word": "no",
     ">": [],
     "<": ["at-most"],
     "=": ["none-of-the"],
     "!": []},
]

#result = quantifier.insert_many(negation)
alls = ["all", "each", "every", "all-of-the", "each-of-the"]
comparison = [
    {"word": "most",
     ">": alls,
     "<": ["many", "several", "some", "a", "an"],
     "=": [],
     "!": []},
    {"word": "many",
     ">": alls + ["most"],
     "<": ["several", "some", "a", "an"],
     "=": [],
     "!": []}]
#result = quantifier.insert_many(comparison)
