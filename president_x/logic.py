"""Small algorithms the interview uses.

find_question walks the list from the front. On n questions the worst
case is n comparisons. gate_status is one recipe for every latch position:
the same steps, whatever the three bits are, and then it stops.
"""


def find_question(questions, qid):
    """Return the question whose id is qid, or None if it is not there.

    Precondition: questions is a list of dictionaries, each with an "id".
    """
    for question in questions:
        if question["id"] == qid:
            return question
    return None


def questions_for(questions, picked):
    """Return the questions whose category is one of the locked ones.

    Precondition: picked is a list of category ids.
    The result is a new list. questions itself is not edited.
    """
    return [question for question in questions if question["cat"] in picked]


def gate_status(gates):
    """Return each latch rule and whether that rule holds.

    Precondition: gates is three integers, CYAN then RED then WHITE.
    1 means shut. 0 means open.
    """
    cyan, red, white = gates
    return (
        ("CYAN XOR RED = 1", (cyan ^ red) == 1),
        ("RED OR WHITE = 0", (red | white) == 0),
        ("WHITE = 0", white == 0),
    )


def rules_ok(gates):
    """Return True when every latch rule holds.

    Precondition: gates is a sequence gate_status accepts.
    """
    for _label, passed in gate_status(gates):
        if not passed:
            return False
    return True
