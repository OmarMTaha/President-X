"""Buttons, files on screen, and the highlight.

These functions take the game as their first argument, the same way a
method takes self. Pygame still does the drawing.
"""

import pygame
from casebook import *
from settings import *
from textutil import fit, wrap

def center(game, surf, font, text, color, cx, y):
    img = font.render(text, True, color)
    surf.blit(img, (cx - img.get_width() // 2, y))
    return img.get_height()


def hit(game, rect, action, zone="ui", nav=True):
    rect = pygame.Rect(rect)
    if action is not None:
        game.hotspots.append((rect, action))
        if nav and action[0] != "noop":
            game.nav.append((rect, action, zone))
    return rect


def button(game, screen, rect, label, action, style="ghost", zone="ui"):
    before = len(game.nav)
    rect = hit(game, rect, action, zone=zone)
    focused = action is not None and len(game.nav) > before and game.focus == len(game.nav) - 1
    mouse = pygame.mouse.get_pos()
    hover = action is not None and rect.collidepoint(mouse)
    if style == "solid":
        fill = (168, 236, 224) if hover else CYAN
        border = CYAN
        color = (12, 18, 18)
    elif style == "danger":
        fill = (64, 16, 22) if hover else (36, 12, 16)
        border = CRIMSON
        color = (255, 214, 214)
    elif style == "gold":
        fill = (48, 38, 18) if hover else (24, 20, 12)
        border = GOLD
        color = GOLD
    elif style == "dim":
        fill = (16, 16, 18)
        border = (50, 54, 58)
        color = (90, 94, 98)
    else:
        fill = (20, 46, 46) if hover else (12, 18, 20)
        border = CYAN if action is not None else (50, 60, 62)
        color = INK if action is not None else DIM
    pygame.draw.rect(screen, fill, rect)
    pygame.draw.rect(screen, AMBER if focused else border, rect, 3 if focused else 1)
    if focused:
        pygame.draw.rect(screen, AMBER, (rect.x, rect.y, 5, rect.h))
    shown = fit(game.f_ui, label, rect.w - 22)
    img = game.f_ui.render(shown, True, color)
    screen.blit(img, img.get_rect(center=rect.center))
    return rect


def begin_modal(game, screen, alpha=170):
    game.nav = []
    game.fx.fill((0, 0, 0, alpha))
    screen.blit(game.fx, (0, 0))
    hit(game, (0, 0, W, H), ("noop",), nav=False)


def block_font(game, style):
    if style == "kicker":
        return game.f_ui_b, 30, 10, (140, 28, 32)
    if style == "sub":
        return game.f_tiny, 16, 16, (110, 72, 48)
    if style == "dim":
        return game.f_ui_s, 18, 12, (96, 78, 58)
    return game.f_body, 26, 14, PAPER_INK


def doc_height(game, blocks, width):
    height = 8
    for style, text in blocks:
        font, line_h, pad, _color = block_font(game, style)
        height += len(wrap(font, text, width)) * line_h + pad
    return height


def draw_document(game, screen, rect, blocks):
    rect = pygame.Rect(rect)
    pygame.draw.rect(screen, PAPER, rect)
    pygame.draw.rect(screen, (120, 96, 64), rect, 2)
    inner_w = rect.w - 56
    content_h = doc_height(game, blocks, inner_w)
    max_scroll = max(0, content_h - rect.h + 24)
    game.scroll = max(0, min(game.scroll, max_scroll))
    old = screen.get_clip()
    screen.set_clip(rect.inflate(-8, -8))
    y = rect.y + 18 - game.scroll
    for style, text in blocks:
        font, line_h, pad, color = block_font(game, style)
        lines = wrap(font, text, inner_w)
        block_h = len(lines) * line_h
        if style == "mark":
            pygame.draw.rect(screen, (236, 196, 96), (rect.x + 16, y - 3, rect.w - 32, block_h + 4))
        for line in lines:
            if rect.bottom + 20 >= y >= rect.y - 30:
                screen.blit(font.render(line, True, color), (rect.x + 28, y))
            y += line_h
        y += pad
    screen.set_clip(old)
    if max_scroll > 0:
        hint = game.f_tiny.render("SCROLL", True, (120, 96, 70))
        screen.blit(hint, (rect.right - hint.get_width() - 14, rect.bottom - 22))
    return max_scroll


def corners(game, screen, rect, color):
    length = 14
    x, y, w, h = rect
    for px, py, sx, sy in (
        (x, y, 1, 1),
        (x + w, y, -1, 1),
        (x, y + h, 1, -1),
        (x + w, y + h, -1, -1),
    ):
        pygame.draw.line(screen, color, (px, py), (px + sx * length, py), 2)
        pygame.draw.line(screen, color, (px, py), (px, py + sy * length), 2)


def crumb(game, screen, y):
    steps = [("tutor", "HOW TO"), ("paper", "OPENING"), ("brief", "BRIEF"), ("drop", "FILES"), ("prep", "PREP"), ("room", "INTERVIEW")]
    current = {"title": "tutor", "zoom": "paper", "end": "room"}.get(game.state, game.state)
    if current not in {sid for sid, _label in steps}:
        current = "title"
    here = [sid for sid, _label in steps].index(current)
    x = 28
    for index, (_sid, label) in enumerate(steps):
        color = CYAN if index == here else (70, 78, 82)
        img = game.f_tiny.render(label, True, color)
        screen.blit(img, (x, y))
        x += img.get_width() + 8
        if index < len(steps) - 1:
            arrow = game.f_tiny.render(">", True, (50, 56, 60))
            screen.blit(arrow, (x, y))
            x += arrow.get_width() + 8

