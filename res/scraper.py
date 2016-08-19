
from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import json

"""
Web scraper to generate JSON files of the Guardian quick, speedy and cryptic crosswords.

    Returns JSON with the following fields:

    name: "Quick crossword No 14,343"
    dateSolutionAvailable: not used
    number: crossword number
    crosswordType: eg cryptic, quick etc
    entries: list of dictionaries describing the clues in the format:
            direction: across or down
            group: [id] used for clues split across multiple entries.
            number: clue number
            clue: string of clue, including length descriptor
            separatorLocations: {separating string: letterwise location}
            length: total clue length, not including separators
            humanNumber: clue number
            position: {x:val, y:val} grid coordinates
            solution: UPPERCASE solution, no spaces or separators
            id: eg 8-across
    date:
    pdf: url to pdf of grid
    solutionAvailable: Bool
    id: type/number
    dimensions: {rows:val, columns: val}

    """

# Guardian website only has data from circa 2000, these are
# the crossword numbers
QUICK = (9093,14363,"quick")
SPEEDY = (410,1078, "speedy")
CRYPTIC = (21620,26889, "cryptic")

CROSSWORD_TYPE = [CRYPTIC]

for crossword in CROSSWORD_TYPE:
    crossword_type = crossword[2]
    for crossword_no in xrange(*crossword[:2]):

        try:
            url = "https://www.theguardian.com/crosswords/" + crossword_type + "/" + str(crossword_no)
            result = requests.get(url)

            c = result.content
            # strip out JSON crossword data from the page
            soup = BeautifulSoup(c)
            try:
                clues = soup.find("div", {"class":"js-crossword "})["data-crossword-data"]
            except:
                clues = soup.find("div", {"class":"js-crossword has-grouped-clues"})["data-crossword-data"]

            clues_json = json.loads(clues)

            save_name = clues_json["id"] + ".JSON"

            with open(save_name, "wb") as file:
                json.dump(clues_json, file, indent=4)

        except:
            print("couldn't find crossword no:{}".format(crossword_no))
            with open(crossword_type+"/missing_ids.txt", "w+") as file:
                file.write(str(crossword_no) + "\n")
            continue




