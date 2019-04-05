import json
import os
from collections import Counter
import argparse
import gensim
import gensim.downloader as gensim_models
from spacy.lang.en import STOP_WORDS
from spacy.lang.char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, LIST_CURRENCY


def clues_iterator(clues_path: str):

    for line in open(clues_path):

        yield json.loads(line)


STOP_SYMBOLS = set().union(LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, LIST_CURRENCY)

def process_clue(clue: str, length: int, answer: str, model):
    words = clue.lower().split(" ")
    bag = []
    for word in words:
        if word in STOP_SYMBOLS:
            continue
        try:
            bag.append(model[word])
        except KeyError:
            continue

    if not bag:
        similar = []
        oov = True
    else:
        avg = sum(bag) / len(bag)
        similar = model.similar_by_vector(avg, topn=1000)
        oov = False
    
    filtered_by_length = [x[0] for x in similar if len(x[0]) == length]
    similar_words = [x[0] for x in similar]

    top1 = answer in similar_words[:1]
    top10 = answer in similar_words[:10]
    top100 = answer in similar_words[:100]
    top1000 = answer in similar_words
    filter1 = answer in filtered_by_length[:1]
    filter10 = answer in filtered_by_length[:10]
    filter100 = answer in filtered_by_length[:100]
    filter1000 = answer in filtered_by_length

    if top1000 and not filter1000:
        print(clue, answer, length)

    return {"top1": top1, "top10": top10, "top100": top100, "top1000": top1000,
            "filter1": filter1, "filter10": filter10, "filter100": filter100,  "filter1000": filter1000, "clue_oov": oov}

def main(clues_path:str):

    count = Counter()
    total = 0
    multi_word = 0
    #model = gensim_models.load("glove-wiki-gigaword-100")
    model = gensim_models.load("word2vec-google-news-300")
    for clue_json in clues_iterator(clues_path):
        
        if clue_json["separatorLocations"]:
            multi_word += 1
            continue
        clue = clue_json["clue"]
        length = int(clue_json["length"])
        solution = clue_json["solution"]

        results = process_clue(clue, length, solution, model)

        count.update(results)
        total +=1
        print(total)


    for k, v in count.items():

        print(k, ":\t", v/total)


    print("multi word: ", multi_word/ (multi_word + total))
    


if __name__=="__main__":


    parser = argparse.ArgumentParser(description="Process raw clues into annotated formats.")
    parser.add_argument('--path', type=str, help="Path to the directory containing raw files.")

    args = parser.parse_args()
    main(args.path)
