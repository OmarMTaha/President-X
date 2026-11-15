"""The interview room: the table, the questions and the overlays.

Lecture 12: the selected unit, the used questions and the notes are a
dictionary, a dictionary and a list. The seen observations are a set.
"""

import math
import pygame
import logic
import portrait
import widgets
from casebook import *
from settings import *
from textutil import clock_str, wrap

def render_stage(game, screen):
    old = screen.get_clip()
    screen.set_clip(pygame.Rect(0, TOP, W, DOCK - TOP))
    screen.fill((22, 26, 32), (0, TOP, W, DOCK - TOP))
    for i in range(8):
        x = 16 + i * 158
        pygame.draw.rect(screen, (34, 40, 50), (x, 78, 146, 220))
        pygame.draw.rect(screen, (14, 18, 24), (x + 10, 92, 126, 140))
        pygame.draw.line(screen, (58, 68, 80), (x, 78), (x + 146, 78), 2)
    for wx in (392, 848):
        pygame.draw.rect(screen, (16, 52, 64), (wx, 108, 76, 128))
        for bar in range(3):
            pygame.draw.line(screen, (8, 22, 28), (wx + 16 + bar * 22, 112), (wx + 16 + bar * 22, 232), 3)
        pygame.draw.rect(screen, (120, 180, 190), (wx + 8, 116, 18, 6))
    pygame.draw.rect(screen, (6, 6, 8), (0, TOP, W, 22))
    pygame.draw.line(screen, (42, 44, 48), (70, 66), (1210, 66), 4)
    lx = game.light_x()
    pygame.draw.rect(screen, (58, 60, 64), (lx - 34, 52, 68, 16))
    bulb = int(180 + 75 * game.flick())
    pygame.draw.rect(screen, (bulb, bulb - 8, bulb - 30), (lx - 10, 66, 20, 6))
    game.fx.fill((0, 0, 0, 0))
    alpha = int(150 * game.flick())
    pygame.draw.polygon(game.fx, (255, 214, 160, int(alpha * 0.55)), [(lx, 72), (lx - 380, DOCK), (lx + 380, DOCK)])
    pygame.draw.polygon(game.fx, (255, 244, 220, alpha), [(lx, 72), (lx - 120, DOCK), (lx + 120, DOCK)])
    screen.blit(game.fx, (0, 0))
    for i in range(7):
        mx = lx + math.sin(game.anim_t * 0.7 + i) * 80
        my = 90 + ((game.anim_t * 28 + i * 46) % 250)
        pygame.draw.circle(screen, (255, 236, 210), (int(mx), int(my)), 1)
    rec_on = math.sin(game.anim_t * 3) > 0
    pygame.draw.circle(screen, (210, 40, 40) if rec_on else (70, 20, 20), (28, 78), 5)
    screen.blit(game.f_tiny.render("REC", True, (180, 70, 70)), (40, 70))
    for div_x in (425, 855):
        pane = pygame.Surface((10, 250), pygame.SRCALPHA)
        pane.fill((170, 210, 214, 40))
        screen.blit(pane, (div_x, 80))
    screen.blit(game.vignette, (0, 0))
    interactive = game.overlay is None and game.dialogue is None and game.state == "room"
    for clone in game.clones:
        x = SEATS[clone.seat]
        pygame.draw.rect(screen, (28, 32, 38), (x - 62, 132, 124, 190), border_radius=10)
        pygame.draw.rect(screen, (14, 16, 20), (x - 46, 148, 92, 78), border_radius=8)
        pygame.draw.rect(screen, (24, 26, 30), (x - 86, 236, 24, 78), border_radius=4)
        pygame.draw.rect(screen, (24, 26, 30), (x + 62, 236, 24, 78), border_radius=4)
        cuff = (80, 210, 200) if clone.shocked else ((190, 64, 58) if clone.hostile else (86, 92, 98))
        pygame.draw.rect(screen, cuff, (x - 84, 258, 20, 12), border_radius=2)
        pygame.draw.rect(screen, cuff, (x + 64, 258, 20, 12), border_radius=2)
        if clone.shocked:
            pygame.draw.line(screen, (80, 190, 200), (x - 68, 300), (x - 40, 270), 2)
            pygame.draw.line(screen, (80, 190, 200), (x + 68, 300), (x + 40, 270), 2)
        if clone.shock_anim > 0:
            for n in range(5):
                x2 = x + int(math.sin(game.anim_t * 40 + n) * 46)
                y2 = 150 + n * 22
                pygame.draw.line(screen, (170, 220, 255), (x - 20 + n * 10, 230), (x2, y2), 1)
        lit = abs(lx - x) < 195 or game.selected == clone.id
        talking = bool(game.dialogue) and game.overlay is None and game.dialogue.get("cid") == clone.id
        portrait.paint(game, screen, x, 198, clone, 0.84, lit, talking)
        rect = pygame.Rect(x - 78, 92, 156, 300)
        if interactive:
            widgets.hit(game, rect, ("select", clone.id), zone="stage")
        hovered = interactive and rect.collidepoint(pygame.mouse.get_pos())
        focused = bool(game.nav) and game.focus == len(game.nav) - 1 and game.nav[-1][1] == ("select", clone.id)
        if game.selected == clone.id or hovered or focused:
            pulse = 2 + int((math.sin(game.anim_t * 5) + 1) * 2)
            bracket = CRIMSON if clone.hostile else (AMBER if focused else CYAN)
            widgets.corners(game, screen, rect.inflate(pulse, pulse), bracket)
    pygame.draw.rect(screen, (20, 22, 26), (0, 336, W, DOCK - 336))
    pygame.draw.line(screen, (92, 104, 112), (0, 336), (W, 336), 2)
    for gx in (425, 855):
        stencil = game.f_tiny.render("DO NOT CONFER", True, (70, 78, 84))
        screen.blit(stencil, stencil.get_rect(center=(gx, 390)))
    screen.set_clip(old)
    for clone in game.clones:
        x = SEATS[clone.seat]
        if clone.hostile:
            color = CRIMSON
            plate = str(clone) + "  LOCKED"
        elif game.selected == clone.id:
            color = CYAN
            plate = str(clone)
        else:
            color = (196, 192, 184)
            plate = str(clone)
        label = game.f_ui_s.render(plate, True, color)
        screen.blit(label, label.get_rect(center=(x, 368)))


def draw_banner(game, screen):
    if game.banner <= 0 or game.state != "room":
        return
    alpha = 255 if game.banner > 0.35 else int(255 * (game.banner / 0.35))
    title = game.f_ui_b.render("SESSION OPEN", True, CYAN)
    sub_text = "Five minutes. Each question can be asked of only one unit."
    if not game.picked:
        sub_text = "No categories locked. You can still observe, then accuse."
    sub = game.f_ui.render(sub_text, True, INK)
    title.set_alpha(alpha)
    sub.set_alpha(alpha)
    screen.blit(title, title.get_rect(center=(W // 2, 150)))
    screen.blit(sub, sub.get_rect(center=(W // 2, 184)))


def draw_topbar(game, screen):
    pygame.draw.rect(screen, (5, 6, 8), (0, 0, W, TOP))
    pygame.draw.line(screen, (36, 58, 58), (0, TOP - 1), (W, TOP - 1), 1)
    screen.blit(game.f_ui_s.render("SUBLEVEL C", True, DIM), (16, 16))
    shown = clock_str(game.time_left)
    total = int(math.ceil(max(0, game.time_left) - 1e-6))
    if game.banner > 0:
        color = CYAN
    elif total <= 15 and int(game.anim_t * 2) % 2 == 0:
        color = WHITE
    elif total <= 60:
        color = CRIMSON
    else:
        color = AMBER
    timer = game.f_timer.render(shown, True, color)
    screen.blit(timer, timer.get_rect(center=(560, TOP // 2)))
    frac = max(0, min(1, game.time_left / ROOM_SECONDS))
    pygame.draw.rect(screen, (28, 30, 34), (470, 38, 180, 4))
    pygame.draw.rect(screen, color, (470, 38, int(180 * frac), 4))
    live = game.overlay is None and game.dialogue is None
    widgets.button(game, screen, (860, 8, 110, 32), "FILES", ("open", "files") if live else None, "ghost" if live else "dim", zone="bar")
    notes = f"NOTES {len(game.notes)}"
    widgets.button(game, screen, (978, 8, 120, 32), notes, ("open", "notes") if live else None, "ghost" if live else "dim", zone="bar")
    accuse_on = live and game.banner <= 0
    widgets.button(game, screen, (1106, 8, 156, 32), "ACCUSE", ("accuse_open",) if accuse_on else None, "danger" if accuse_on else "dim", zone="bar")


def draw_dock(game, screen):
    pygame.draw.rect(screen, (12, 14, 18), (0, DOCK, W, H - DOCK))
    pygame.draw.line(screen, (70, 96, 102), (0, DOCK), (W, DOCK), 2)
    if game.dialogue and game.overlay is None:
        draw_dialogue(game, screen)
        return
    clone = game.current()
    frame = pygame.Rect(16, DOCK + 14, 214, H - DOCK - 28)
    pygame.draw.rect(screen, (8, 9, 12), frame)
    pygame.draw.rect(screen, (48, 64, 70), frame, 1)
    if clone:
        glow = pygame.Surface((190, 210), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (48, 110, 112, 80), glow.get_rect())
        screen.blit(glow, glow.get_rect(center=(frame.centerx, frame.y + 120)))
        portrait.paint(game, screen, frame.centerx, frame.y + 128, clone, 0.62, True, False)
        name = game.f_ui_s.render(str(clone), True, CRIMSON if clone.hostile else CYAN)
        screen.blit(name, name.get_rect(center=(frame.centerx, frame.bottom - 16)))
    else:
        hint = wrap(game.f_ui_s, "Select a unit at the table.", 180)
        yy = frame.y + 90
        for line in hint:
            img = game.f_ui_s.render(line, True, DIM)
            screen.blit(img, img.get_rect(center=(frame.centerx, yy)))
            yy += 18
    rule = "ARROWS move     ENTER choose     O observe     A accuse"
    screen.blit(game.f_tiny.render(rule, True, DIM), (250, DOCK + 12))
    y = DOCK + 36
    if not clone:
        idle = wrap(game.f_dlg, "They are seated apart so they cannot compare stories. Left and right move between them. Enter opens the one in focus.", 980)
        yy = y + 30
        for line in idle:
            screen.blit(game.f_dlg.render(line, True, INK), (250, yy))
            yy += 32
        return
    status = "SAFETY LOCK" if clone.hostile else ("RESTRAINED" if clone.shocked else "LISTENING")
    status_color = CRIMSON if clone.hostile else DIM
    screen.blit(game.f_tiny.render(status, True, status_color), (980, DOCK + 12))
    widgets.button(game, screen, (250, y, 1000, 30), "OBSERVE  /  read the body, spends no question", ("observe",), "ghost", zone="dock")
    y += 34
    if clone.hostile:
        widgets.button(game, screen, (250, y, 1000, 36), "OVERRIDE SAFETY LOCK", ("puzzle",), "danger", zone="dock")
        y += 44
        screen.blit(game.f_ui.render("Questions are sealed until the restraint fires.", True, CRIMSON), (250, y))
        return
    active = logic.questions_for(QUESTIONS, game.picked)
    if not active:
        screen.blit(game.f_ui.render("No question categories were locked. Observation is all you have.", True, AMBER), (250, y + 8))
        return
    for question in active:
        if question["id"] in game.used:
            who = game.cmap[game.used[question["id"]]].code
            label = f"ASKED OF {who}   {question['label']}"
            widgets.button(game, screen, (250, y, 1000, 30), label, None, "dim", zone="dock")
        else:
            widgets.button(game, screen, (250, y, 1000, 30), question["label"], ("ask", question["id"]), "ghost", zone="dock")
        y += 33


def draw_dialogue(game, screen):
    frame = pygame.Rect(16, DOCK + 14, 214, H - DOCK - 28)
    pygame.draw.rect(screen, (8, 9, 12), frame)
    pygame.draw.rect(screen, (48, 64, 70), frame, 1)
    clone = game.cmap.get(game.dialogue.get("cid"))
    if clone:
        glow = pygame.Surface((190, 210), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (48, 110, 112, 80), glow.get_rect())
        screen.blit(glow, glow.get_rect(center=(frame.centerx, frame.y + 120)))
        portrait.paint(game, screen, frame.centerx, frame.y + 128, clone, 0.62, True, True)
    who = game.f_ui_s.render(game.dialogue["who"], True, CYAN)
    screen.blit(who, (250, DOCK + 16))
    y = DOCK + 46
    old = screen.get_clip()
    screen.set_clip(pygame.Rect(250, y, 1000, 230))
    for line in wrap(game.f_dlg, game.dialogue["text"], 980):
        screen.blit(game.f_dlg.render(line, True, INK), (250, y))
        y += 30
    screen.set_clip(old)
    widgets.button(game, screen, (960, DOCK + 12, 280, 32), "CONTINUE", ("advance",), "solid", zone="dock")
    widgets.hit(game, (0, DOCK, W, H - DOCK), ("advance",), nav=False)


def draw_room(game, screen):
    render_stage(game, screen)
    draw_dock(game, screen)
    draw_banner(game, screen)
    draw_topbar(game, screen)
    if game.overlay == "pause":
        draw_pause(game, screen)
    elif game.overlay == "files":
        draw_files(game, screen)
    elif game.overlay == "notes":
        draw_notes(game, screen)
    elif game.overlay == "puzzle":
        draw_puzzle(game, screen)
    elif game.overlay == "accuse":
        draw_accuse(game, screen)


def draw_files(game, screen):
    widgets.begin_modal(game, screen, 180)
    panel = pygame.Rect(70, 36, 1140, 650)
    draw_tabs(game, screen, (70, 36))
    widgets.draw_document(game, screen, (70, 84, 1140, 560), FILES[game.file_tab][1])
    if game.state == "room" and game.banner <= 0:
        chip = f"CLOCK RUNNING   {clock_str(game.time_left)}"
        chip_img = game.f_tiny.render(chip, True, CRIMSON)
        screen.blit(chip_img, (90, 646))
    widgets.button(game, screen, (1000, 632, 180, 36), "CLOSE", ("close",), "ghost")
    del panel


def draw_tabs(game, screen, origin):
    x, y = origin
    for index, (title, _blocks) in enumerate(FILES):
        rect = pygame.Rect(x + index * 420, y, 400, 42)
        on = index == game.file_tab
        pygame.draw.rect(screen, PAPER if on else (48, 42, 34), rect)
        pygame.draw.rect(screen, (120, 96, 64), rect, 1)
        color = PAPER_INK if on else PAPER
        img = game.f_ui.render(title, True, color)
        screen.blit(img, img.get_rect(center=rect.center))
        widgets.hit(game, rect, ("tab", index))
        if game.nav and game.focus == len(game.nav) - 1:
            pygame.draw.rect(screen, AMBER, rect, 2)


def draw_notes(game, screen):
    widgets.begin_modal(game, screen, 180)
    panel = pygame.Rect(120, 50, 1040, 620)
    pygame.draw.rect(screen, (14, 16, 20), panel)
    pygame.draw.rect(screen, CYAN, panel, 1)
    screen.blit(game.f_ui_b.render("CASE NOTES", True, CYAN), (148, 68))
    widgets.button(game, screen, (960, 60, 160, 34), "CLOSE", ("close",), "ghost")
    if not game.notes:
        screen.blit(game.f_dlg.render("Nothing recorded yet.", True, DIM), (148, 140))
        return
    width = 960
    height = 24
    for _code, prompt, answer in game.notes:
        height += 22 + len(wrap(game.f_ui_s, prompt, width)) * 16
        height += len(wrap(game.f_body, answer, width)) * 24 + 18
    max_scroll = max(0, height - 500)
    game.scroll = max(0, min(game.scroll, max_scroll))
    old = screen.get_clip()
    screen.set_clip(pygame.Rect(148, 120, 980, 500))
    y = 124 - game.scroll
    for code, prompt, answer in game.notes:
        screen.blit(game.f_tiny.render(code, True, AMBER), (148, y))
        y += 18
        for line in wrap(game.f_ui_s, prompt, width):
            screen.blit(game.f_ui_s.render(line, True, CYAN), (148, y))
            y += 16
        for line in wrap(game.f_body, answer, width):
            screen.blit(game.f_body.render(line, True, INK), (148, y))
            y += 24
        y += 16
    screen.set_clip(old)
    if max_scroll > 0:
        screen.blit(game.f_tiny.render("SCROLL", True, DIM), (148, 640))


def draw_puzzle(game, screen):
    widgets.begin_modal(game, screen, 190)
    card = pygame.Rect(250, 70, 780, 580)
    pygame.draw.rect(screen, (8, 14, 16), card)
    pygame.draw.rect(screen, CYAN, card, 1)
    screen.blit(game.f_tiny.render("CHAIR TERMINAL  /  SAFETY LATCH", True, CYAN), (278, 92))
    screen.blit(game.f_ui_b.render("RESTRAINT OVERRIDE", True, INK), (278, 114))
    screen.blit(game.f_ui_s.render("It subdues. It does not identify the thief.", True, DIM), (278, 148))
    names = ("CYAN", "RED", "WHITE")
    for i, name in enumerate(names):
        rect = pygame.Rect(300 + i * 230, 200, 200, 92)
        shut = game.gates[i] == 1
        fill = (16, 64, 68) if name == "CYAN" and shut else (64, 16, 20) if name == "RED" and shut else (48, 48, 44) if shut else (16, 18, 20)
        pygame.draw.rect(screen, fill, rect)
        pygame.draw.rect(screen, INK, rect, 1)
        state = "SHUT  1" if shut else "OPEN  0"
        screen.blit(game.f_ui_b.render(name, True, INK), (rect.x + 18, rect.y + 16))
        screen.blit(game.f_ui.render(state, True, AMBER if shut else DIM), (rect.x + 18, rect.y + 50))
        widgets.hit(game, rect, ("gate", i))
        if game.nav and game.focus == len(game.nav) - 1:
            pygame.draw.rect(screen, AMBER, rect, 2)
    y = 330
    for label, ok in game.gate_status():
        color = (110, 200, 140) if ok else CRIMSON
        mark = "OK" if ok else "NO"
        screen.blit(game.f_ui.render(f"{label}    {mark}", True, color), (300, y))
        y += 32
    engage = ("engage",) if game.rules_ok() else None
    style = "solid" if game.rules_ok() else "dim"
    widgets.button(game, screen, (300, 460, 300, 48), "ENGAGE SHOCKER", engage, style)
    widgets.button(game, screen, (620, 460, 340, 48), "OPEN FAILSAFE FILE", ("open", "files"), "ghost")
    screen.blit(game.f_tiny.render("The latch positions are written in your Personal Failsafe File.", True, DIM), (300, 530))
    if game.banner <= 0:
        screen.blit(game.f_tiny.render(f"CLOCK RUNNING   {clock_str(game.time_left)}", True, CRIMSON), (300, 560))
    widgets.button(game, screen, (300, 590, 160, 36), "BACK", ("close",), "ghost")


def draw_accuse(game, screen):
    widgets.begin_modal(game, screen, 190)
    card = pygame.Rect(240, 120, 800, 480)
    pygame.draw.rect(screen, (10, 12, 16), card)
    pygame.draw.rect(screen, CRIMSON, card, 1)
    screen.blit(game.f_ui_b.render("LOCK ACCUSATION", True, CRIMSON), (280, 148))
    screen.blit(game.f_ui.render("This ends the investigation.", True, DIM), (280, 184))
    if not game.pending:
        screen.blit(game.f_ui_s.render("Name the unit who is wearing the stolen mind.", True, INK), (280, 230))
        for clone in game.clones:
            rect = pygame.Rect(280, 280 + clone.seat * 70, 720, 56)
            widgets.button(game, screen, rect, f"UNIT 0{clone.seat + 1}   /   {clone.code}", ("arm", clone.id), "danger")
        widgets.button(game, screen, (280, 530, 160, 40), "BACK", ("close",), "ghost")
        return
    clone = game.cmap[game.pending]
    lines = wrap(game.f_card, f"Lock the accusation against UNIT 0{clone.seat + 1}, {clone.code}?", 700)
    y = 280
    for line in lines:
        screen.blit(game.f_card.render(line, True, INK), (280, y))
        y += 36
    widgets.button(game, screen, (280, 460, 280, 52), "CONFIRM", ("confirm",), "danger")
    widgets.button(game, screen, (580, 460, 200, 52), "BACK", ("arm_clear",), "ghost")


def draw_pause(game, screen):
    widgets.begin_modal(game, screen, 200)
    card = pygame.Rect(390, 160, 500, 400)
    pygame.draw.rect(screen, (8, 10, 12), card)
    pygame.draw.rect(screen, CYAN, card, 1)
    widgets.center(game, screen, game.f_ui_b, "PAUSED", CYAN, W // 2, 190)
    widgets.center(game, screen, game.f_ui, "The clock is stopped.", INK, W // 2, 230)
    help_lines = (
        "LEFT RIGHT    change unit",
        "UP DOWN       move the highlight",
        "ENTER         choose it",
        "ESC           close, then pause",
        "O  F  N  A    observe, files, notes, accuse",
    )
    y = 280
    for line in help_lines:
        img = game.f_ui_s.render(line, True, DIM)
        screen.blit(img, img.get_rect(center=(W // 2, y)))
        y += 24
    widgets.button(game, screen, (460, 430, 360, 46), "RESUME", ("resume",), "solid")
    widgets.button(game, screen, (460, 490, 360, 46), "[ QUIT ]", ("quit",), "danger")

