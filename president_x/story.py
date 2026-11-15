"""Everything before the table, and everything after the accusation.

The pages are a list. The function for the current page is chosen by name.
"""

import math
import pygame
import portrait
import stage
import widgets
from casebook import *
from settings import *
from textutil import clock_str, wrap

def draw_title(game, screen):
    screen.blit(game.vignette, (0, 0))
    glitch = math.sin(game.anim_t * 3) > 0.82
    title = "PRESIDENT X"
    if glitch:
        ghost = game.f_title.render(title, True, CRIMSON)
        screen.blit(ghost, ghost.get_rect(center=(W // 2 + 4, 230)))
    img = game.f_title.render(title, True, INK)
    screen.blit(img, img.get_rect(center=(W // 2, 226)))
    widgets.center(game, screen, game.f_ui, "A CAPITAL INTERROGATION", CYAN, W // 2, 300)
    pygame.draw.line(screen, (40, 70, 70), (460, 340), (820, 340), 1)
    lines = (
        "One of them is wearing his mind.",
        "You have the only file that can tell.",
        "Once the door shuts, you have five minutes.",
    )
    y = 380
    for line in lines:
        widgets.center(game, screen, game.f_body, line, DIM, W // 2, y)
        y += 34
    widgets.crumb(game, screen, 28)
    widgets.button(game, screen, (490, 520, 300, 46), "HOW TO PLAY", ("goto", "tutor"), "solid")
    widgets.center(game, screen, game.f_tiny, "Instructions first    the lamp flickers", (90, 70, 70), W // 2, 660)
    widgets.hit(game, (0, 0, W, H), ("goto", "tutor"), nav=False)


def draw_paper(game, screen):
    screen.fill((18, 16, 14))
    shadow = pygame.Surface((820, 680), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 90))
    screen.blit(shadow, (250, 36))
    screen.blit(game.paper, (230, 16))
    widgets.button(game, screen, (490, 660, 300, 40), "LOOK CLOSER", ("goto", "zoom"), "solid")
    widgets.hit(game, (0, 0, W, H), ("goto", "zoom"), nav=False)


def draw_tutor(game, screen):
    screen.fill((0, 0, 0))
    widgets.crumb(game, screen, 28)
    title, body = TUTOR[game.tutor_i]
    screen.blit(game.f_tiny.render(f"BEFORE THE MISSION    {game.tutor_i + 1}  /  {len(TUTOR)}", True, CYAN), (100, 78))
    screen.blit(game.f_ui_b.render(title, True, AMBER), (100, 108))
    y = 164
    for line in wrap(game.f_dlg, body, 1040):
        if line:
            screen.blit(game.f_dlg.render(line, True, INK), (100, y))
        y += 32
    if game.tutor_i == 0:
        for clone in game.clones:
            portrait.paint(game, screen, SEATS[clone.seat], 470, clone, 0.7, True, False, preview=True)
            tag = game.f_tiny.render(f"0{clone.seat + 1}  {clone.code}", True, CYAN)
            screen.blit(tag, tag.get_rect(center=(SEATS[clone.seat], 600)))
    widgets.hit(game, (0, 0, W, H), ("advance",), nav=False)
    label = "OPEN THE FILE" if game.tutor_i == len(TUTOR) - 1 else "NEXT"
    widgets.button(game, screen, (860, 640, 300, 48), label, ("advance",), "solid")
    if game.tutor_i > 0:
        widgets.button(game, screen, (100, 640, 200, 48), "BACK", ("tutor_back",), "ghost")


def draw_zoom(game, screen):
    screen.fill((0, 0, 0))
    index = min(game.zoom_i, 2)
    phrase = game.phrases[index]
    view = game.paper.copy()
    pygame.draw.rect(view, (240, 196, 70), phrase["rect"])
    pygame.draw.rect(view, (160, 36, 36), (52, phrase["pos"][1] + 8, 8, 8))
    img = game.f_quote.render(phrase["text"], True, PAPER_INK)
    view.blit(img, phrase["pos"])
    target = phrase["text_rect"]
    fit = min((W - 160) / max(1, target.w), (H - 260) / max(1, target.h))
    fit = max(1.08, min(fit, 2.3))
    scale = 1.08 + (fit - 1.08) * min(1.0, game.zoom_t / 0.55)
    big = pygame.transform.smoothscale(view, (int(view.get_width() * scale), int(view.get_height() * scale)))
    screen.blit(big, (W / 2 - target.centerx * scale, (H - 110) / 2 - target.centery * scale))
    if 0.48 < game.zoom_t < 0.72:
        strength = 1 - abs(game.zoom_t - 0.6) / 0.12
        game.fx.fill((255, 255, 255, int(170 * max(0, strength))))
        screen.blit(game.fx, (0, 0))
    count = game.f_tiny.render(f"{index + 1}  /  3", True, AMBER)
    chip = pygame.Surface((count.get_width() + 20, 26), pygame.SRCALPHA)
    chip.fill((0, 0, 0, 170))
    screen.blit(chip, (18, 16))
    screen.blit(count, (28, 20))
    widgets.button(game, screen, (540, 672, 200, 36), "NEXT", ("advance",), "solid")
    widgets.hit(game, (0, 0, W, H), ("advance",), nav=False)


def draw_brief(game, screen):
    screen.fill((0, 0, 0))
    box = pygame.Rect(120, 140, 1040, 420)
    pygame.draw.rect(screen, (8, 10, 12), box)
    pygame.draw.rect(screen, CYAN, box, 1)
    screen.blit(game.f_tiny.render(f"ASSIGNMENT    {game.brief_i + 1} / 2", True, CYAN), (156, 164))
    shown = BRIEF[game.brief_i][: int(game.chars)]
    y = 220
    for line in wrap(game.f_dlg, shown, 960):
        screen.blit(game.f_dlg.render(line, True, INK), (156, y))
        y += 36
    widgets.crumb(game, screen, 28)
    label = "CONTINUE" if game.chars >= len(BRIEF[game.brief_i]) else "SKIP LINE"
    widgets.button(game, screen, (470, 590, 340, 44), label, ("advance",), "solid")
    widgets.hit(game, (0, 0, W, H), ("advance",), nav=False)


def draw_folder(game, screen, x, y, title, sub):
    pygame.draw.rect(screen, (196, 164, 104), (x, y + 22, 340, 210))
    pygame.draw.rect(screen, (168, 132, 74), (x, y, 180, 28))
    pygame.draw.rect(screen, (92, 64, 32), (x, y + 22, 340, 210), 2)
    screen.blit(game.f_ui.render(title, True, PAPER_INK), (x + 18, y + 48))
    for i, line in enumerate(wrap(game.f_tiny, sub, 300)):
        screen.blit(game.f_tiny.render(line, True, (80, 52, 28)), (x + 18, y + 84 + i * 16))


def draw_drop(game, screen):
    screen.fill((14, 12, 11))
    pygame.draw.rect(screen, (42, 34, 28), (140, 520, 1000, 200))
    pygame.draw.rect(screen, (72, 56, 36), (170, 536, 940, 22))
    widgets.center(game, screen, game.f_tiny, "INVENTORY DRAWER", DIM, W // 2, 250)
    t = min(1.0, game.drop_t / 0.85)
    ease = 1 - (1 - t) ** 3
    settle = math.sin(max(0.0, game.drop_t - 0.82) * 14) * 12 * max(0.0, 1 - (game.drop_t - 0.82))
    draw_folder(game, screen, 220, -220 + ease * 620 + settle, "Personal Failsafe File", "Only you and the President know what is inside.")
    draw_folder(game, screen, 700, -280 + ease * 680 + settle * 0.7, "CIA Physical Symptoms File", "What a thief's body does when it wears his mind.")
    widgets.center(game, screen, game.f_ui_b, "TWO FILES LOADED", INK, W // 2, 80)
    widgets.crumb(game, screen, 28)
    if game.drop_t >= 0.7:
        widgets.button(game, screen, (470, 150, 340, 44), "TAKE THE DESK", ("advance",), "solid")
    widgets.hit(game, (0, 0, W, H), ("advance",), nav=False)


def draw_prep(game, screen):
    screen.fill(BG)
    pygame.draw.rect(screen, (5, 6, 8), (0, 0, W, 72))
    screen.blit(game.f_ui_s.render("PREP WINDOW", True, CYAN), (24, 14))
    screen.blit(game.f_tiny.render("Left and Right switch files.   Up and Down move.   Enter picks a category, or starts.", True, DIM), (24, 40))
    left = clock_str(game.prep_left)
    total = int(math.ceil(max(0, game.prep_left) - 1e-6))
    color = CRIMSON if total <= 10 else AMBER
    timer = game.f_timer.render(left, True, color)
    screen.blit(timer, timer.get_rect(midright=(820, 30)))
    count = game.f_ui.render(f"{len(game.picked)} / 3", True, INK)
    screen.blit(count, (860, 22))
    stage.draw_tabs(game, screen, (24, 84))
    widgets.draw_document(game, screen, (24, 132, 760, 520), FILES[game.file_tab][1])
    y = 84
    for cid, title, blurb in CATEGORIES:
        rect = pygame.Rect(810, y, 446, 78)
        on = cid in game.picked
        pygame.draw.rect(screen, (18, 42, 42) if on else (14, 16, 20), rect)
        pygame.draw.rect(screen, CYAN if on else (50, 58, 62), rect, 1)
        if on:
            num = game.f_tiny.render(str(game.picked.index(cid) + 1), True, CYAN)
            screen.blit(num, (rect.x + 12, rect.y + 10))
        screen.blit(game.f_ui.render(title, True, INK if on else (210, 210, 204)), (rect.x + 36, rect.y + 12))
        screen.blit(game.f_tiny.render(blurb, True, DIM), (rect.x + 36, rect.y + 40))
        widgets.hit(game, rect, ("toggle", cid))
        if game.nav and game.focus == len(game.nav) - 1:
            pygame.draw.rect(screen, AMBER, rect.inflate(2, 2), 2)
        y += 86
    unlocked = sum(1 for q in QUESTIONS if q["cat"] in game.picked)
    screen.blit(game.f_tiny.render(f"{unlocked} QUESTIONS UNLOCK", True, DIM), (810, 610))
    widgets.button(game, screen, (1030, 636, 226, 48), "BEGIN", ("begin",), "solid")
    if game.overlay == "pause":
        stage.draw_pause(game, screen)


def draw_cards(game, screen, cards, gold=False):
    screen.fill((0, 0, 0))
    if not gold:
        density = (0.15, 0.55, 0.9)[min(game.card, 2)]
        game.fx.fill((70, 96, 62, int(40 + 80 * density)))
        for i in range(10):
            x = (i * 173 + game.anim_t * 24) % (W + 80) - 40
            y = H - ((game.anim_t * 18 + i * 80) % (H + 80))
            pygame.draw.circle(game.fx, (186, 206, 150, 22), (int(x), int(y)), 54 + (i % 4) * 18)
        screen.blit(game.fx, (0, 0))
        veil = pygame.Surface((980, 300), pygame.SRCALPHA)
        veil.fill((0, 0, 0, int(80 + 70 * density)))
        screen.blit(veil, (150, 140))
    kicker, body = cards[game.card]
    color = GOLD if gold else (190, 210, 170)
    widgets.center(game, screen, game.f_tiny, kicker, color, W // 2, 120)
    if gold and game.card == game.last_card():
        draw_seal(game, screen, W // 2, 210, 46)
        text_y = 280
    else:
        text_y = 180
    for line in wrap(game.f_card, body, 860):
        widgets.center(game, screen, game.f_card, line, INK, W // 2, text_y)
        text_y += 36
    if game.card < game.last_card():
        widgets.button(game, screen, (470, 620, 340, 44), "CONTINUE", ("advance",), "solid")
        widgets.hit(game, (0, 0, W, H), ("advance",), nav=False)
        return
    end_buttons(game, screen)


def draw_seal(game, screen, cx, cy, radius):
    pygame.draw.circle(screen, GOLD, (cx, cy), radius, 2)
    pygame.draw.circle(screen, GOLD, (cx, cy), radius - 8, 1)
    points = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        dist = (radius - 16) if i % 2 == 0 else (radius - 16) * 0.45
        points.append((cx + dist * math.cos(ang), cy + dist * math.sin(ang)))
    pygame.draw.polygon(screen, GOLD, points)


def end_buttons(game, screen):
    widgets.button(game, screen, (280, 600, 440, 52), "[ RESTART INVESTIGATION ]", ("restart",), "danger")
    widgets.button(game, screen, (760, 600, 220, 52), "[ QUIT ]", ("quit",), "ghost")


def draw_timeout(game, screen):
    phase = game.cine_phase
    if phase <= 0:
        stage.render_stage(game, screen)
        game.fx.fill((50, 0, 0, 80))
        screen.blit(game.fx, (0, 0))
        box = pygame.Rect(90, 430, 1100, 70)
        pygame.draw.rect(screen, (20, 0, 0), box)
        pygame.draw.rect(screen, CRIMSON, box, 2)
        widgets.center(game, screen, game.f_ui_b, WARN_TEXT, CRIMSON, W // 2, 452)
        widgets.button(game, screen, (1040, 448, 140, 36), "NEXT", ("advance",), "ghost")
        widgets.hit(game, (0, 0, W, H), ("advance",), nav=False)
        return
    if phase == 1:
        screen.fill((0, 0, 0))
        bone = game.cmap["bone"]
        drop = 0 if game.cine_t < 2.35 else int((game.cine_t - 2.35) * 520)
        portrait.paint(game, screen, W // 2, 340 + drop, bone, 2.05, True, False)
        widgets.center(game, screen, game.f_ui, "UNIT 02  /  BONE", CRIMSON, W // 2, 48)
        if bone.eyes == "black":
            widgets.center(game, screen, game.f_tiny, "IRIS SIGNAL LOST", CRIMSON, W // 2, 80)
        widgets.button(game, screen, (540, 640, 200, 36), "NEXT", ("advance",), "ghost")
        widgets.hit(game, (0, 0, W, H), ("advance",), nav=False)
        return
    if phase == 2:
        draw_collapse(game, screen)
        widgets.button(game, screen, (540, 640, 200, 36), "NEXT", ("advance",), "ghost")
        widgets.hit(game, (0, 0, W, H), ("advance",), nav=False)
        return
    screen.fill((0, 0, 0))
    y = 250
    for line in wrap(game.f_card, FAIL_TEXT, 900):
        widgets.center(game, screen, game.f_card, line, INK, W // 2, y)
        y += 40
    end_buttons(game, screen)


def draw_collapse(game, screen):
    screen.fill((6, 6, 8))
    pygame.draw.rect(screen, (16, 14, 14), (0, 500, W, 220))
    pygame.draw.line(screen, (48, 40, 40), (0, 500), (W, 500), 2)
    k = min(1.0, game.cine_t / 1.5)
    k = k * k * (3 - 2 * k)
    standing = {
        "head": (640, 150), "neck": (640, 210), "hip": (640, 330),
        "knee_a": (590, 430), "foot_a": (560, 530), "knee_b": (700, 430), "foot_b": (740, 530),
        "shoulder": (540, 230), "hand_a": (470, 330), "elbow_b": (750, 230), "hand_b": (820, 320),
    }
    fallen = {
        "head": (560, 310), "neck": (610, 360), "hip": (700, 450),
        "knee_a": (610, 530), "foot_a": (520, 590), "knee_b": (820, 430), "foot_b": (910, 360),
        "shoulder": (600, 390), "hand_a": (470, 450), "elbow_b": (720, 340), "hand_b": (800, 270),
    }

    def mix(name):
        a, b = standing[name], fallen[name]
        return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)

    head, neck, hip = mix("head"), mix("neck"), mix("hip")
    knee_a, foot_a, knee_b, foot_b = mix("knee_a"), mix("foot_a"), mix("knee_b"), mix("foot_b")
    shoulder, hand_a, elbow_b, hand_b = mix("shoulder"), mix("hand_a"), mix("elbow_b"), mix("hand_b")
    body = [
        (head, neck), (neck, hip), (hip, knee_a), (knee_a, foot_a),
        (hip, knee_b), (knee_b, foot_b), (neck, shoulder), (shoulder, hand_a),
        (neck, elbow_b), (elbow_b, hand_b),
    ]
    pygame.draw.circle(screen, (214, 190, 168), (int(head[0]), int(head[1])), 26)
    pygame.draw.circle(screen, (0, 0, 0), (int(head[0] - 8), int(head[1] - 2)), 4)
    pygame.draw.circle(screen, (0, 0, 0), (int(head[0] + 9), int(head[1] - 1)), 4)
    for p0, q0 in body[1:]:
        pygame.draw.line(screen, (18, 20, 28), p0, q0, 14)
    shown = int(len(body) * min(1, max(0, game.cine_t - 0.35) / 2.2))
    for p0, q0 in body[:shown]:
        pygame.draw.line(screen, (230, 226, 214), (p0[0] + 10, p0[1] + 8), (q0[0] + 10, q0[1] + 8), 2)
    widgets.center(game, screen, game.f_ui, "THE HOST DROPS. THE LIMBS SETTLE WRONG.", CRIMSON, W // 2, 80)


def draw_end(game, screen):
    if game.ending == "timeout":
        draw_timeout(game, screen)
    elif game.ending == "good":
        draw_cards(game, screen, GOOD_CARDS, gold=True)
    else:
        draw_cards(game, screen, BAD_CARDS, gold=False)

