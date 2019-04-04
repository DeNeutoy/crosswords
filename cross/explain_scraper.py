
import requests
from requests_html import HTMLSession
import json
import os
import argparse
import datetime

MONTHS = {
    1: "jan",
    2: "feb",
    3: "mar",
    4: "apr",
    5: "may",
    6: "jun",
    7: "jul",
    8: "aug",
    9: "sep",
    10: "oct",
    11: "nov",
    12: "dec"
}
def parse_timestamp(timestamp:int):
    date = datetime.datetime.fromtimestamp(timestamp/1000)
    day = str(date.day) 
    if len(day) == 1:
        day = f"0{day}"
    return str(date.year), MONTHS[date.month], day

def parse_solutions(solutions):

    context = []
    clues = []
    seen_clues = False
    for line in solutions:
        if not line[0].isnumeric() and not seen_clues:
            # There is some introduction to the crossword
            context.append(line)

        elif not line[0].isnumeric():
            # solution wrapped a line, because it was long.
            clues[-1] = clues[-1] + " " + line
        else:
            seen_clues = True
            clues.append(line)

    return {"solutions": clues, "context": context}

"""
Hard example to parse.
https://www.theguardian.com/crosswords/2010/dec/06/annotated-solutions-genius-89-crossword

"""

def main(dir: str):

    files = [x for x in os.listdir(dir) if x.lower()[-4:] == "json"]
    session = HTMLSession()
    os.makedirs(f"{dir}_solutions", exist_ok=True)
    for crossword_file in files:

        crossword = json.load(open(os.path.join(dir, crossword_file)))

        timestamp = crossword["dateSolutionAvailable"]
        year, month, day = parse_timestamp(timestamp)
        number = crossword["number"]
        crossword_type = crossword["crosswordType"]

        url = f"https://www.theguardian.com/crosswords/{year}/{month}/{day}/annotated-solutions-for-{crossword_type}-{number}"
        print(crossword["solutionAvailable"], url)
        result = session.get(url)
        if result.status_code >= 300:
            continue
        html = result.html
        relevant_divs = html.find("div.content__main-column.content__main-column--article.js-content-main-column")
        if len(relevant_divs) != 1:
            print(relevant_divs)

        solutions = [x.text for x in relevant_divs[0].find("p") if x.text]

        parsed = parse_solutions(solutions)
        save_name = os.path.join("crosswords/prize_solutions", f"{number}_solution.json")

        with open(save_name, "w+") as file:
            json.dump(parsed, file, indent=4)




if __name__ == "__main__":


    parser = argparse.ArgumentParser(description="Scrape crosswords from The Guardian.")
    parser.add_argument('--dir', type=str, help='The path to the crossword data directory.')

    args = parser.parse_args()
    main(args.dir)