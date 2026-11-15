"""Lines of text, and the clock as a string.

wrap_words calls itself on the words that did not fit. The empty list
is the base case: there is nothing left to place, so it returns.
"""

import math


def wrap_words(font, words, width):
    """Return lines made from words, each no wider than width.

    Precondition: font has a size method, and words is a list of strings.
    Base case: words is empty, and the answer is written down as [].
    Recursive case: fill one line, then call again on the words that remain.
    """
    if words == []:
        return []
    line = words[0]
    index = 1
    while index < len(words) and font.size(line + " " + words[index])[0] <= width:
        line = line + " " + words[index]
        index = index + 1
    return [line] + wrap_words(font, words[index:], width)


def wrap(font, text, width):
    """Return text broken into lines that fit width.

    Precondition: width is wide enough for a single word the font can draw.
    A newline starts a new paragraph. A blank paragraph stays a blank line.
    """
    lines = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
        else:
            lines.extend(wrap_words(font, para.split(), width))
    if lines == []:
        return [""]
    return lines


def fit(font, text, width):
    """Return text cut down until it fits width, with ... on the end.

    Precondition: font has a size method. Strings are not edited in place:
    each cut is a new, shorter string.
    """
    if font.size(text)[0] <= width:
        return text
    ellipsis = "..."
    while text and font.size(text + ellipsis)[0] > width:
        text = text[:-1]
    if text:
        return text + ellipsis
    return ellipsis


def clock_str(seconds):
    """Return seconds as MM:SS, rounded up to the next second.

    Precondition: seconds is a number. A negative value is shown as 00:00.
    """
    total = max(0, int(math.ceil(seconds - 1e-6)))
    return f"{total // 60:02d}:{total % 60:02d}"
