"""The dark edge of the screen.

The same picture can be built with a Python loop or with one NumPy
expression over every pixel. Pygame still shows the surface.
"""

import math

import pygame

USED_ARRAY = False


def vignette_loop(width, height):
    """Return the vignette by visiting each pixel in a loop."""
    small = pygame.Surface((320, 180), pygame.SRCALPHA)
    for y in range(180):
        for x in range(320):
            dx = (x - 160) / 160
            dy = (y - 90) / 102
            dist = math.sqrt(dx * dx + dy * dy)
            alpha = int(max(0, min(150, (dist - 0.42) * 210)))
            if alpha:
                small.set_at((x, y), (0, 0, 0, alpha))
    return pygame.transform.smoothscale(small, (width, height))


def vignette_array(width, height):
    """Return the vignette from one array of distances.

    Precondition: NumPy is installed. Raises ImportError if it is not.
    Arithmetic applies to every pixel at once. No Python loop is written.
    """
    import numpy as np

    global USED_ARRAY
    xs = (np.arange(320) - 160) / 160
    ys = (np.arange(180) - 90) / 102
    dist = np.sqrt(xs[None, :] ** 2 + ys[:, None] ** 2)
    alpha = np.clip((dist - 0.42) * 210, 0, 150).astype(np.uint8)
    small = pygame.Surface((320, 180), pygame.SRCALPHA)
    pixels = pygame.surfarray.pixels_alpha(small)
    pixels[:, :] = np.ascontiguousarray(alpha.T)
    del pixels
    USED_ARRAY = True
    return pygame.transform.smoothscale(small, (width, height))


def make_vignette(width, height):
    """Return the vignette, using the array when NumPy is available.

    If the array path cannot run, the loop still produces the picture.
    """
    try:
        return vignette_array(width, height)
    except (ImportError, pygame.error, AttributeError, ValueError):
        return vignette_loop(width, height)
