
import json
import os
import regex


def insert_single_clue_separators(clue):

    if len(clue["separatorLocations"]) != 0:

        ans = clue["solution"].lower()
        full_locations = []

        for x in clue["separatorLocations"].items():
            full_locations += [(x[0],y) for y in x[1]]

        for i, (str, loc) in enumerate(full_locations):
            ans = ans[0:loc + i] + str + ans[loc + i:]

    else:
        ans = clue["solution"].lower()

    clue["solution"] = ans
    return clue

def insert_separators(crossword):
    """The scraper format returns solution fields with no separators.
       To allow non-seq2seq approaches, we insert these in place."""
    new_entries = []
    for clue in crossword["entries"]:
        # Split the answer up into it's parts and insert separators.
        clue = insert_single_clue_separators(clue)
        new_entries.append(clue)

    crossword["entries"] = new_entries
    return crossword

def remove_clue_duplicates(crossword):
    """Sometimes clues are split over multiple grid entries. In this case,
       one of the clues will simply refer to the other clue, e.g 'See 15 Down'.
       This removes clues which are not the first entry in a group of clues,
       which are always just references to the first clue in the group. """
    deduped_entries = []
    for clue in crossword["entries"]:

        if len(clue["group"]) == 1:
            deduped_entries.append(clue)

        else:
            multi_ref = clue["group"][0].split("-")
            if multi_ref[0] == clue["number"] and multi_ref[1] == clue["direction"]:
                # Retrieve all the parts of the solution as
                # they are stored across all parts of the clue.
                complete_solution = "".join([x["solution"] for x in
                                             crossword["entries"] if x["group"] == clue["group"]])

                clue["solution"] = complete_solution
                deduped_entries.append(clue)
            else:
                pass

    crossword["entries"] = deduped_entries

    return crossword


def get_references(clue):
    """Return all references to other solutions in the grid from
       a given clue. """
    try:
        last_bracket = clue["clue"].rindex("(")
    except:
        last_bracket = len(clue["clue"])
    clue_minus_length_descriptor = clue["clue"][:last_bracket].strip()

    # Agressively finds and removes clues containing "10", "12 Across" etc.
    regex_matches = regex.findall("([0-9]{1,2})(( [Aa]cross| [Dd]own){0,1})(?=(\W|$))", clue_minus_length_descriptor)

    return regex_matches



def remove_referential_clues(crossword):
    """Some clues reference other solutions in the grid by number.
       To simplify the clue and remove extraneous context, we
       replace these references with the solution if they occur."""
    new_entries = []
    for clue in crossword["entries"]:
        clue_references = get_references(clue)
        if len(clue_references) == 0:
            new_entries.append(clue)

    crossword["entries"] = new_entries
    return crossword

def extract_and_save_clues(file_path, save_file):

    for crossword in os.listdir(file_path):

        with open(os.path.join(file_path,crossword), "rb") as file:
            crossword = json.load(file)

        # Note that the order here is important. Inserting separators must happen before
        # we remove duplicates, as the seperator indicies are based on only the part of
        # the clue which is entered in that grid slot, not the whole solution.

        crossword = remove_clue_duplicates(crossword)
        crossword = remove_referential_clues(crossword)
        crossword = insert_separators(crossword)

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
