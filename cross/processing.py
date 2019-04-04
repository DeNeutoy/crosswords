
import json
import os
import regex

from cross.crossword import Clue, Crossword

def insert_answer_seperators(clue):

    new_clue = clue.copy()
    if len(clue["separatorLocations"]) != 0:
        answer = clue["solution"].lower()
        full_locations = []
        for x in clue["separatorLocations"].items():
            full_locations.append((x[0], y) for y in x[1])

        for i, (insert_string, loc) in enumerate(full_locations):
            answer = answer[0:loc + i] + insert_string + answer[loc + i:]
    else:
        answer = clue["solution"].lower()

    new_clue["solution"] = answer
    return new_clue

def insert_separators(clue_list):
    """
    The scraper format returns solution fields with
    no separators, so we insert these in place.
    """
    new_entries = []
    for clue in clue_list:
        # Split the answer up into it's parts and insert separators.
        clue_with_ans_seperators = insert_answer_seperators(clue)
        new_entries.append(clue_with_ans_seperators)

    return new_entries

def remove_clue_duplicates(clue_list):
    """Sometimes clues are split over multiple grid entries. In this case,
       one of the clues will simply refer to the other clue, e.g 'See 15 Down'.
       This removes clues which are not the first entry in a group of clues,
       which are always just references to the first clue in the group. """
    deduped_entries = []
    for clue in clue_list:

        if len(clue["group"]) == 1:
            deduped_entries.append(clue)

        else:
            multi_ref = clue["group"][0].split("-")
            if multi_ref[0] == clue["number"] and multi_ref[1] == clue["direction"]:
                # Retrieve all the parts of the solution as
                # they are stored across all parts of the clue.
                complete_solution = "".join([x["solution"] for x in
                                             clue_list if x["group"] == clue["group"]])

                clue["solution"] = complete_solution
                deduped_entries.append(clue)
            else:
                pass

    return deduped_entries


def get_references(clue):
    """Return all references to other solutions in the grid from
       a given clue. """
    try:
        last_bracket = clue["clue"].rindex("(")
    except:
        last_bracket = len(clue["clue"])
    clue_minus_length_descriptor = clue["clue"][:last_bracket].strip()

    # Agressively finds and removes clues containing "10", "12 Across" etc.
    regex_matches = regex.findall("([0-9]{1,2})(( [Aa]cross| [Dd]own){0,1})(?=(\W|$))",
                                  clue_minus_length_descriptor)
    return regex_matches

def remove_referential_clues(clue_list):
    """Some clues reference other solutions in the grid by number.
       To simplify the clue and remove extraneous context, we
       replace these references with the solution if they occur."""
    new_entries = []
    for clue in clue_list:
        clue_references = get_references(clue)
        if len(clue_references) == 0:
            new_entries.append(clue)

    return clue_list

def extract_and_save_clues(file_path: str, save_file: str):

    for crossword in os.listdir(file_path):
        with open(os.path.join(file_path,crossword), "rb") as file:
            crossword = json.load(file)
        # Note that the order here is important. Inserting separators must happen before
        # we remove duplicates, as the seperator indicies are based on only the part of
        # the clue which is entered in that grid slot, not the whole solution.

        clue_list = crossword["entries"]
        clue_list = remove_clue_duplicates(clue_list)
        clue_list = remove_referential_clues(clue_list)
        clue_list = insert_separators(clue_list)

        # Extract id and type to put into every clue.
        id = crossword["number"]
        crossword_type = crossword["crosswordType"]

        with open(save_file, "a+") as file:

            for entry in crossword["entries"]:
                entry.pop("humanNumber")
                entry.pop("position")
                entry.pop("group")
                entry["id"] = id
                entry["type"] = crossword_type
                json.dump(entry, file)
                file.write("\n")

if __name__=="__main__":


    clue_path = "/Users/markneumann/Documents/Machine_Learning/crosswords/res/clues_refs.txt"

    extract_and_save_clues("/Users/markneumann/Documents/Machine_Learning/crosswords/res/cryptic/", clue_path)
