
from aux import Clue

import json
class Crossword(object):

    def __init__(self, crossword_path):

        with open(crossword_path, "rb") as file:
            json_crossword = json.load(file)

        self.dimensions = json_crossword["dimensions"]
        self.name = json_crossword["name"]
        self.type = json_crossword["crosswordType"]
        self.number = json_crossword["number"]
        self.date = json_crossword["date"]

        all_clues = []
        for entry in json_crossword["entries"]:
            all_clues.append(Clue(entry, self.name))

        self.clues = all_clues

    def get_clues(self):

        clue_strings = []
        solutions = []
        for clue in self.clues:

            # split the answer up into it's parts and insert separators
            if not len(clue.separator) == 0:
                for str, loc in clue.separator.items():
                    offset_index = zip([0]+loc, loc+[None])
                    parts = [clue.solution[i:j] for i,j in offset_index]
                    ans = str.join(parts).lower()
            else:
                ans = clue.solution.lower()

            clue_strings.append(clue.value)
            solutions.append(ans)
        return clue_strings, solutions


class CrypticCrossword(Crossword):

    def init(self, json_crossword):
        super(CrypticCrossword,self).__init__(json_crossword)

        self.setter = json_crossword["author"]["name"]


