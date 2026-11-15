"""Tests for the case. One input, one expected result.

Run them with:

    python3 main.py --selftest
    python3 test_game.py

Running is not the same as working, so the script asks the questions
the player is not there to ask.
"""

import json
import os
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from casebook import (
    ANSWERS,
    BRIEF,
    FAIL_TEXT,
    FRAGMENTS,
    QUESTIONS,
    WARN_TEXT,
    load_case,
)
from game import Game
from logic import find_question, questions_for, rules_ok
from textutil import clock_str, wrap
from units import Clone, Unit


def test_case_text():
    """The lines the player must read are the lines that were written."""
    assert FRAGMENTS[0] == "Killed by one of his clones"
    assert FRAGMENTS[1] == "President's top-secret consciousness stolen"
    assert FRAGMENTS[2] == "Is the country at risk?"
    assert BRIEF[0].startswith("You are the President's trusted secretary")
    assert BRIEF[1].startswith("The CIA have also given you a file")
    assert WARN_TEXT.startswith("TIME EXPIRED.")
    assert FAIL_TEXT.startswith("INVESTIGATION FAILED.")


def test_search_and_latches():
    """Linear search finds a question. The latch recipe accepts one setting."""
    found = find_question(QUESTIONS, "ashtray")
    assert found["cat"] == "failsafe"
    assert find_question(QUESTIONS, "missing") is None
    picked = questions_for(QUESTIONS, ["ocular"])
    assert picked[0]["id"] == "light"
    assert rules_ok([1, 0, 0])
    assert not rules_ok([0, 0, 0])
    assert not rules_ok([1, 0, 1])


def test_units():
    """A clone is a unit, and each clone keeps its own lock."""
    first = Clone("ash", "ASH", 0)
    second = Clone("bone", "BONE", 1)
    assert isinstance(first, Unit)
    assert isinstance(first, Clone)
    assert str(first) == "UNIT 01  /  ASH"
    first.hostile = True
    assert second.hostile is False


def test_clock():
    """214 seconds is three minutes and thirty-four, rounded up."""
    assert clock_str(214) == "03:34"
    assert clock_str(0) == "00:00"


def test_case_file():
    """A missing file and a broken file are reported, not ignored."""
    try:
        load_case("/no/such/president_x_case.json")
        raise AssertionError("a missing file should raise")
    except FileNotFoundError:
        pass
    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump({"FRAGMENTS": []}, handle)
    handle.close()
    try:
        load_case(handle.name)
        raise AssertionError("a short file should raise")
    except ValueError:
        pass
    finally:
        os.remove(handle.name)


def test_wrap(game):
    """The recursive wrapper keeps a narrow line from overflowing."""
    wide = wrap(game.f_body, "one two three", 4000)
    assert wide == ["one two three"]
    word = game.f_body.size("hello")[0]
    narrow = wrap(game.f_body, "hello world", word + 2)
    assert narrow == ["hello", "world"]
    blank = wrap(game.f_body, "alpha\n\nbeta", 4000)
    assert blank == ["alpha", "", "beta"]


def test_play(game):
    """Play the interrogation without the mouse and check each ending."""
    game.toggle_cat("failsafe")
    game.toggle_cat("ocular")
    game.toggle_cat("motor")
    game.toggle_cat("alibi")
    assert game.picked == ["failsafe", "ocular", "motor"]
    game.begin_room()
    game.banner = 0
    game.select("ash")
    game.activate(("ask", "ashtray"))
    assert game.used["ashtray"] == "ash"
    assert game.dialogue
    game.advance()
    game.select("bone")
    game.activate(("ask", "ashtray"))
    assert game.dialogue is None
    game.activate(("ask", "nickname"))
    assert game.cmap["bone"].hostile
    assert "Marrow" in ANSWERS["nickname"]["bone"]
    game.advance()
    game.activate(("ask", "phrase"))
    assert "phrase" not in game.used
    game.activate(("puzzle",))
    assert game.overlay == "puzzle"
    assert not game.rules_ok()
    game.gates = [1, 0, 0]
    assert game.rules_ok()
    game.activate(("engage",))
    assert game.cmap["bone"].shocked and not game.cmap["bone"].hostile
    game.advance()
    game.activate(("ask", "phrase"))
    assert "third lamp" in game.dialogue["text"]
    game.advance()
    game.activate(("accuse_open",))
    game.activate(("arm", "ash"))
    game.activate(("confirm",))
    assert game.ending == "bad"
    game.restart()
    assert game.state == "prep"
    game.picked = ["ocular"]
    game.begin_room()
    game.banner = 0
    game.select("cinder")
    game.activate(("ask", "light"))
    assert game.cmap["cinder"].hostile
    game.advance()
    game.activate(("puzzle",))
    game.gates = [1, 0, 0]
    game.activate(("engage",))
    assert game.cmap["cinder"].shocked
    game.restart()
    game.picked = ["alibi"]
    game.begin_room()
    game.banner = 0
    game.select("ash")
    game.activate(("ask", "ashtray"))
    assert "ashtray" not in game.used
    game.activate(("ask", "alibi"))
    assert game.used["alibi"] == "ash"
    game.advance()
    game.activate(("ask", "access"))
    assert game.cmap["ash"].hostile
    game.restart()
    game.begin_room()
    game.banner = 0
    game.activate(("accuse_open",))
    game.activate(("arm", "bone"))
    game.activate(("confirm",))
    assert game.ending == "good" and game.accused == "bone"
    game.restart()
    game.begin_room()
    game.banner = 0
    game.time_left = 0.01
    game.update(0.05)
    assert game.state == "end" and game.ending == "timeout"


def test_every_screen(game):
    """Draw each screen once, so a broken page fails here."""
    game.restart()
    game.anim_t = 1.2
    for state in ("title", "tutor", "paper", "zoom", "brief", "drop", "prep", "room", "end"):
        game.state = state
        if state == "end":
            game.ending = "timeout"
            game.cine_phase = 0
        game.update(0.016)
        game.draw()


def run():
    """Run every test, then close Pygame."""
    test_case_text()
    test_search_and_latches()
    test_units()
    test_clock()
    test_case_file()
    game = Game()
    test_wrap(game)
    test_play(game)
    test_every_screen(game)
    pygame.quit()
    print("SELFTEST OK")


if __name__ == "__main__":
    run()
