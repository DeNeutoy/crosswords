
from typing import List
import requests
from requests_html import HTMLSession
import json
import os
import argparse
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
CROSSWORDS = {
    "quick": (9093,15240),
    "speedy": (410,1223),
    "cryptic": (21620,27767),
    "weekend": (321, 427),
    "quiptic": (1, 1008),
    "everyman": (2965, 3777),
    "prize": (12579, 27758),
}

def main(crossword_types: List[str]):

    session = HTMLSession()
    for crossword_type in crossword_types:

        if crossword_type not in CROSSWORDS.keys():
            raise ValueError(f"crosword type must be in one of {CROSSWORDS.keys()}")
        start, end = CROSSWORDS[crossword_type]

        os.makedirs(f"crosswords/{crossword_type}", exist_ok=True)
        for crossword_no in reversed(range(start, end)):

            try:
                url = "https://www.theguardian.com/crosswords/" + crossword_type + "/" + str(crossword_no)
                result = session.get(url)
                if result.status_code >= 300:
                    continue
                html = result.html
                try:
                    relevant_divs = html.find("div.js-crossword")
                    if len(relevant_divs) != 1:
                        print(relevant_divs)
                    clues = relevant_divs[0].attrs["data-crossword-data"]
                except:
                    relevant_divs = html.find("div.js-crossword has-grouped-clues")
                    if len(relevant_divs) != 1:
                        print(relevant_divs)
                    clues = relevant_divs[0].attrs["data-crossword-data"]

                clues_json = json.loads(clues)
                save_name = clues_json["id"] + ".json"

                with open(save_name, "w+") as file:
                    json.dump(clues_json, file, indent=4)
            except IndexError:
                print("couldn't find crossword no:{}".format(crossword_no))
                with open("crosswords/" + crossword_type + "/missing_ids.txt", "a+") as file:
                    file.write(str(crossword_no) + "\n")



if __name__ == "__main__":


    parser = argparse.ArgumentParser(description="Scrape crosswords from The Guardian.")
    parser.add_argument('--type', nargs='+', help='<Required> Set flag', required=True)

    args = parser.parse_args()
    main(args.type)
