"""The case, read back from a file.

The questions, the two dossiers and the endings live in data/case.json.
open() hands back a file object. json.load turns the characters into
lists and dictionaries. The file is still there after the program ends.
"""

import json
import os


def load_case(path):
    """Return the case stored at path.

    Precondition: path names a JSON object with the keys this game expects.
    Raises FileNotFoundError if the file is missing.
    Raises ValueError if a required key is absent.
    """
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    required = (
        "FRAGMENTS", "BRIEF", "TUTOR", "WARN_TEXT", "FAIL_TEXT",
        "LOCK_FIRST", "LOCK_AGAIN", "CATEGORIES", "QUESTIONS", "ANSWERS",
        "OBSERVE", "SHOCK_LINE", "FILES", "GOOD_CARDS", "BAD_CARDS",
        "COL_LEFT", "COL_RIGHT",
    )
    for key in required:
        if key not in data:
            raise ValueError("case file is missing " + key)
    return data


_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "case.json")
try:
    _DATA = load_case(_PATH)
except FileNotFoundError as err:
    raise FileNotFoundError("The case file is not next to the game: " + _PATH) from err

FRAGMENTS = _DATA["FRAGMENTS"]
BRIEF = _DATA["BRIEF"]
TUTOR = _DATA["TUTOR"]
WARN_TEXT = _DATA["WARN_TEXT"]
FAIL_TEXT = _DATA["FAIL_TEXT"]
LOCK_FIRST = _DATA["LOCK_FIRST"]
LOCK_AGAIN = _DATA["LOCK_AGAIN"]
ALIBI = _DATA["ALIBI"]
ACCESS = _DATA["ACCESS"]
OATH = _DATA["OATH"]
CATEGORIES = _DATA["CATEGORIES"]
QUESTIONS = _DATA["QUESTIONS"]
ANSWERS = _DATA["ANSWERS"]
OBSERVE = _DATA["OBSERVE"]
SHOCK_LINE = _DATA["SHOCK_LINE"]
FAILSAFE_FILE = _DATA["FAILSAFE_FILE"]
CIA_FILE = _DATA["CIA_FILE"]
FILES = _DATA["FILES"]
GOOD_CARDS = _DATA["GOOD_CARDS"]
BAD_CARDS = _DATA["BAD_CARDS"]
COL_LEFT = _DATA["COL_LEFT"]
COL_RIGHT = _DATA["COL_RIGHT"]

# A dictionary finds a question by its id. Building it is one pass over the list.
QBY = {question["id"]: question for question in QUESTIONS}
