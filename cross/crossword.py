

import json

class Clue:

    def __init__(self, jsonclue, id):

        self.value = jsonclue["clue"]
        self.direction = jsonclue["direction"]
        self.total_length = jsonclue["length"]

        self.separator = jsonclue["separatorLocations"]
        self.grid_position = (jsonclue["position"]["x"],jsonclue["position"]["y"])
        self.crossword_id = id
        self.solution = jsonclue["solution"]

    def __len__(self):
        return self.total_length



class Crossword:

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

