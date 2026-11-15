"""Start PRESIDENT X.

    pip install -r requirements.txt
    python3 main.py

You are the President's secretary. Three clones are at the table.
One of them is wearing his stolen mind. You have five minutes.
"""

import os
import sys

# The dummy drivers must be chosen before Pygame is imported.
if "--selftest" in sys.argv:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"

from game import Game


def main(argv):
    """Open the game, or run the tests when the argument asks for them."""
    if "--selftest" in argv:
        import test_game
        try:
            test_game.run()
        except Exception:
            import traceback
            traceback.print_exc()
            import pygame
            pygame.quit()
            return 1
        return 0
    Game().loop()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
