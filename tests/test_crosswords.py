
import unittest

from cross.crossword import Crossword, Clue


class TestCrosswords(unittest.TestCase):

    def test_crossword_can_load_from_json(self):

        path = "tests/fixtures/example.json"

        crossword = Crossword(path)
        clues = crossword.get_clues()

        for clue in clues:
            print(clue)