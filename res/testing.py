

from src.aux import Clue
from src.Crossword import Crossword


testCrossword = Crossword("/Users/markneumann/Documents/Machine_Learning/crosswords/res/cryptic/22343.JSON")

clues = testCrossword.get_clues()
x = 2