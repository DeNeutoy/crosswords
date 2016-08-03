

class Clue(object):

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