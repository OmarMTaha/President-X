"""Short tones, packed as samples for Pygame's mixer.

Pygame plays the buffer. This function only builds the numbers.
"""

import math
import struct

import pygame


def tone(freq, ms, volume=0.18, kind="sine"):
    """Return a Pygame sound of freq hertz lasting ms milliseconds.

    Precondition: freq and ms are positive. kind is sine, square, noise or chord.
    The mixer must already be open, or Sound raises pygame.error.
    """
    rate = 22050
    count = max(1, int(rate * ms / 1000))
    data = bytearray()
    for i in range(count):
        t = i / rate
        if kind == "square":
            wave = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif kind == "noise":
            wave = math.sin(i * 12.9898) * 2 - 1
            wave = (wave * 13.13) % 2 - 1
        else:
            wave = math.sin(2 * math.pi * freq * t)
            if kind == "chord":
                wave = 0.6 * wave + 0.4 * math.sin(2 * math.pi * freq * 1.5 * t)
        attack = min(1.0, i / 180)
        release = min(1.0, (count - i) / 500)
        sample = int(max(-32767, min(32767, wave * volume * attack * release * 32767)))
        data += struct.pack("<h", sample)
    return pygame.mixer.Sound(buffer=bytes(data))
