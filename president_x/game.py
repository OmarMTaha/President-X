"""The running case: the clock, the choices, and the screen.

Pygame owns the window and the keyboard. This class decides what they mean.
A call such as story.draw_title(self, screen) is an ordinary function call.
"""

import math
import pygame
import fx
import logic
import stage
import story
import widgets
from casebook import *
from settings import *
from sound import tone
from textutil import clock_str, wrap
from units import Clone


class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(22050, -16, 1, 512)
            self.audio = True
        except pygame.error:
            self.audio = False
        flags = 0
        try:
            self.screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)
        except pygame.error:
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("PRESIDENT X")
        self.clock = pygame.time.Clock()
        self.running = True
        self.muted = False
        self.anim_t = 0.0
        self._load_fonts()
        self._build_fx()
        self._build_paper()
        self._build_audio()
        self.clones = [Clone("ash", "ASH", 0), Clone("bone", "BONE", 1), Clone("cinder", "CINDER", 2)]
        self.cmap = {c.id: c for c in self.clones}
        self.hotspots = []
        self.nav = []
        self.focus = 0
        self.fade = 0.0
        self.prev_state = "title"
        self.reset_case()
        self.state = "title"

    def _load_fonts(self):
        def font(name, size, bold=False, italic=False):
            return pygame.font.SysFont(name, size, bold=bold, italic=italic)

        self.f_title = font("timesnewroman", 92, bold=True)
        self.f_head = font("timesnewroman", 58, bold=True)
        self.f_quote = font("timesnewroman", 28, bold=True, italic=True)
        self.f_big = font("timesnewroman", 40, bold=True)
        self.f_mast = font("timesnewroman", 22)
        self.f_body = font("georgia", 20)
        self.f_dlg = font("georgia", 22)
        self.f_card = font("georgia", 26)
        self.f_ui = font("menlo", 16)
        self.f_ui_s = font("menlo", 13)
        self.f_ui_b = font("menlo", 20, bold=True)
        self.f_timer = font("menlo", 28, bold=True)
        self.f_tiny = font("menlo", 12)

    def _build_fx(self):
        self.fx = pygame.Surface((W, H), pygame.SRCALPHA)
        self.scan = pygame.Surface((W, H), pygame.SRCALPHA)
        for y in range(0, H, 3):
            pygame.draw.line(self.scan, (0, 0, 0, 18), (0, y), (W, y))
        self.vignette = fx.make_vignette(W, H)

    def _build_audio(self):
        self.sfx = {}
        if not self.audio:
            return
        try:
            self.sfx["blip"] = tone(880, 40, 0.12)
            self.sfx["bad"] = tone(98, 140, 0.16, "square")
            self.sfx["shock"] = tone(70, 220, 0.2, "noise")
            self.sfx["good"] = tone(523, 220, 0.14, "chord")
        except (pygame.error, ValueError):
            self.audio = False
            self.sfx = {}

    def _build_paper(self):
        width, height = 820, 680
        surf = pygame.Surface((width, height))
        surf.fill(PAPER)
        pygame.draw.rect(surf, PAPER_INK, (0, 0, width, height), 3)
        pygame.draw.rect(surf, (186, 48, 48), (14, 14, width - 28, height - 28), 1)
        widgets.center(self, surf, self.f_mast, "THE CAPITAL MERIDIAN", PAPER_INK, width // 2, 36)
        pygame.draw.line(surf, PAPER_INK, (48, 68), (width - 48, 68), 2)
        pygame.draw.line(surf, PAPER_INK, (48, 74), (width - 48, 74), 1)
        widgets.center(self, surf, self.f_tiny, "NIGHT EXTRA    /    CAPITAL SPIRE    /    FINAL EDITION", (128, 36, 36), width // 2, 84)
        pygame.draw.circle(surf, (160, 36, 36), (752, 46), 24, 3)
        stamp = self.f_tiny.render("EXTRA", True, (160, 36, 36))
        surf.blit(stamp, stamp.get_rect(center=(752, 46)))
        headline = self.f_head.render("PRESIDENT FOUND DEAD", True, PAPER_INK)
        surf.blit(headline, ((width - headline.get_width()) // 2, 128))
        deck = "The residence is sealed. Three copies are in custody. One question is loose in the building."
        y = 206
        for line in wrap(self.f_body, deck, width - 140):
            img = self.f_body.render(line, True, (48, 42, 38))
            surf.blit(img, ((width - img.get_width()) // 2, y))
            y += 26
        y += 16
        self.phrases = []
        for frag in FRAGMENTS:
            img = self.f_quote.render(frag, True, PAPER_INK)
            pygame.draw.rect(surf, (160, 36, 36), (52, y + 8, 8, 8))
            surf.blit(img, (72, y))
            rect = pygame.Rect(60, y - 6, img.get_width() + 24, img.get_height() + 12)
            self.phrases.append({"rect": rect, "text": frag, "pos": (72, y), "text_rect": img.get_rect(topleft=(72, y))})
            y += img.get_height() + 20
        y += 8
        pygame.draw.line(surf, PAPER_INK, (48, y), (width - 48, y), 1)
        y += 16
        for index, column in enumerate((COL_LEFT, COL_RIGHT)):
            x = 48 + index * 380
            yy = y
            for line in wrap(self.f_tiny, column, 350):
                surf.blit(self.f_tiny.render(line, True, (48, 42, 38)), (x, yy))
                yy += 16
        self.paper = surf

    def play(self, name):
        if not self.audio or self.muted:
            return
        sound = self.sfx.get(name)
        if not sound:
            return
        try:
            sound.play()
        except pygame.error:
            self.audio = False

    def reset_case(self):
        self.picked = []
        self.brief_i = 0
        self.tutor_i = 0
        self.chars = 0.0
        self.zoom_i = 0
        self.zoom_t = 0.0
        self.drop_t = 0.0
        self.prep_left = float(PREP_SECONDS)
        self.time_left = float(ROOM_SECONDS)
        self.banner = 0.0
        self.overlay = None
        self.stack = None
        self.pause_return = None
        self.dialogue = None
        self.selected = None
        self.used = {}
        self.notes = []
        self.seen_obs = set()
        self.lock_explained = False
        self.pending = None
        self.gates = [0, 0, 0]
        self.scroll = 0
        self.file_tab = 0
        self.ending = None
        self.card = 0
        self.cine_phase = 0
        self.cine_t = 0.0
        self.accused = None
        for clone in getattr(self, "clones", []):
            clone.reset()

    def restart(self):
        self.reset_case()
        self.state = "prep"
        self.prep_left = float(PREP_SECONDS)

    def current(self):
        if not self.selected:
            return None
        return self.cmap.get(self.selected)

    def light_x(self):
        return 640 + math.sin(self.anim_t * 0.42) * 430

    def flick(self):
        value = 0.84 + 0.16 * math.sin(self.anim_t * 6.5)
        if math.sin(self.anim_t * 2.15) > 0.965:
            value *= 0.5
        return value

    def gate_status(self):
        """Return the latch rules for the gates on the chair terminal."""
        return logic.gate_status(self.gates)

    def rules_ok(self):
        """Return True when the three latch rules all hold."""
        return logic.rules_ok(self.gates)

    def toggle_pause(self):
        if self.overlay == "pause":
            self.overlay = self.pause_return
            self.pause_return = None
        else:
            self.pause_return = self.overlay
            self.overlay = "pause"
            self.focus = 0

    def close_overlay(self):
        self.overlay = self.stack
        self.stack = None
        self.pending = None
        self.scroll = 0

    def toggle_cat(self, cid):
        if cid in self.picked:
            self.picked.remove(cid)
            self.play("blip")
        elif len(self.picked) < 3:
            self.picked.append(cid)
            self.play("blip")
        else:
            self.play("bad")

    def begin_room(self):
        picked = list(self.picked)
        self.state = "room"
        self.time_left = float(ROOM_SECONDS)
        self.banner = 2.2
        self.overlay = None
        self.stack = None
        self.pause_return = None
        self.dialogue = None
        self.selected = None
        self.used = {}
        self.notes = []
        self.seen_obs = set()
        self.lock_explained = False
        self.pending = None
        self.gates = [0, 0, 0]
        self.scroll = 0
        self.picked = picked
        for clone in self.clones:
            clone.reset()

    def begin_ending(self, kind):
        self.state = "end"
        self.ending = kind
        self.card = 0
        self.cine_phase = 0
        self.cine_t = 0.0
        self.overlay = None
        self.stack = None
        self.pause_return = None
        self.dialogue = None
        self.play("good" if kind == "good" else "bad")

    def pushes_back(self, clone, question):
        if clone.shocked:
            return False
        if clone.id == "bone":
            return True
        if clone.id == "cinder" and (question["cat"] == "ocular" or clone.asked_count >= 2):
            return True
        if clone.id == "ash" and (question["cat"] == "motive" or clone.asked_count >= 2):
            return True
        return False

    def ask(self, qid):
        if self.overlay or self.dialogue:
            return
        question = logic.find_question(QUESTIONS, qid)
        if not question or question["cat"] not in self.picked or qid in self.used:
            return
        clone = self.current()
        if not clone or clone.hostile:
            return
        self.used[qid] = clone.id
        clone.asked_count += 1
        text = ANSWERS[qid][clone.id]
        self.notes.append((clone.code, question["label"], text))
        if self.pushes_back(clone, question):
            clone.hostile = True
            text += "\n\n" + (LOCK_FIRST if not self.lock_explained else LOCK_AGAIN)
            self.lock_explained = True
        self.dialogue = {
            "who": str(clone),
            "cid": clone.id,
            "text": text,
        }
        self.play("blip")

    def observe(self):
        if self.overlay or self.dialogue:
            return
        clone = self.current()
        if not clone:
            return
        if clone.id not in self.seen_obs:
            self.seen_obs.add(clone.id)
            self.notes.append((clone.code, "Observation", OBSERVE[clone.id]))
        self.dialogue = {
            "who": str(clone),
            "cid": clone.id,
            "text": OBSERVE[clone.id],
        }
        self.play("blip")

    def open_puzzle(self):
        clone = self.current()
        if not clone or not clone.hostile or self.dialogue:
            return
        self.gates = [0, 0, 0]
        self.stack = None
        self.overlay = "puzzle"
        self.focus = 0

    def engage(self):
        clone = self.current()
        if not clone or not clone.hostile or not self.rules_ok():
            self.play("bad")
            return
        clone.hostile = False
        clone.shocked = True
        clone.shock_anim = 0.75
        self.overlay = None
        self.stack = None
        self.play("shock")
        self.dialogue = {
            "who": str(clone),
            "cid": clone.id,
            "text": SHOCK_LINE[clone.id],
        }

    def confirm_accuse(self):
        if self.pending not in self.cmap:
            return
        self.accused = self.pending
        self.begin_ending("good" if self.pending == KILLER else "bad")

    def select(self, cid):
        if self.overlay or self.dialogue or cid not in self.cmap:
            return
        self.selected = cid
        self.focus = self.cmap[cid].seat
        self.play("blip")

    def advance(self):
        if self.overlay:
            return
        if self.state == "tutor":
            self.tutor_i += 1
            if self.tutor_i >= len(TUTOR):
                self.state = "paper"
            return
        if self.state == "zoom":
            self.zoom_i += 1
            self.zoom_t = 0
            if self.zoom_i >= 3:
                self.state = "drop"
                self.drop_t = 0
        elif self.state == "brief":
            full = BRIEF[self.brief_i]
            if self.chars < len(full):
                self.chars = float(len(full))
                return
            self.brief_i += 1
            self.chars = 0
            if self.brief_i >= len(BRIEF):
                self.state = "drop"
                self.drop_t = 0
        elif self.state == "drop":
            if self.drop_t >= 0.7:
                self.state = "prep"
                self.prep_left = float(PREP_SECONDS)
                self.picked = []
                self.scroll = 0
                self.file_tab = 0
        elif self.state == "room" and self.dialogue:
            self.dialogue = None
        elif self.state == "end":
            self.advance_end()

    def advance_end(self):
        if self.ending == "timeout":
            if self.cine_phase < 3:
                self.cine_phase += 1
                self.cine_t = 0
            return
        if self.card < self.last_card():
            self.card += 1

    def last_card(self):
        return 3 if self.ending == "good" else 2

    def activate(self, action):
        kind = action[0]
        if kind == "noop":
            return
        if kind == "goto":
            self.state = action[1]
            if self.state == "zoom":
                self.zoom_i = 0
                self.zoom_t = 0.0
            if self.state == "tutor":
                self.tutor_i = 0
            return
        if kind == "tutor_back":
            self.tutor_i = max(0, self.tutor_i - 1)
            return
        if kind == "advance":
            self.advance()
            return
        if kind == "toggle":
            self.toggle_cat(action[1])
            return
        if kind == "begin":
            self.begin_room()
            return
        if kind == "select":
            self.select(action[1])
            return
        if kind == "ask":
            self.ask(action[1])
            return
        if kind == "observe":
            self.observe()
            return
        if kind == "puzzle":
            self.open_puzzle()
            return
        if kind == "gate":
            self.gates[action[1]] ^= 1
            self.play("blip")
            return
        if kind == "engage":
            self.engage()
            return
        if kind == "open":
            self.stack = self.overlay
            self.overlay = action[1]
            self.scroll = 0
            self.focus = 0
            return
        if kind == "close":
            self.close_overlay()
            return
        if kind == "tab":
            self.file_tab = action[1]
            self.scroll = 0
            return
        if kind == "accuse_open":
            if self.banner > 0:
                return
            self.pending = None
            self.stack = self.overlay
            self.overlay = "accuse"
            self.focus = 0
            return
        if kind == "arm":
            self.pending = action[1]
            self.focus = 0
            return
        if kind == "arm_clear":
            self.pending = None
            return
        if kind == "confirm":
            self.confirm_accuse()
            return
        if kind == "restart":
            self.restart()
            return
        if kind == "quit":
            self.running = False
            return
        if kind == "resume":
            self.toggle_pause()
            return

    def nudge(self, delta, zone=None):
        if not self.nav:
            return
        pool = [i for i, item in enumerate(self.nav) if zone is None or item[2] == zone]
        if not pool:
            return
        if self.focus in pool:
            pos = pool.index(self.focus)
            self.focus = pool[(pos + delta) % len(pool)]
        elif delta > 0:
            self.focus = pool[0]
        else:
            self.focus = pool[-1]

    def activate_focus(self):
        if self.nav and 0 <= self.focus < len(self.nav):
            self.activate(self.nav[self.focus][1])
        else:
            self.advance()

    def on_escape(self):
        if self.state not in ("prep", "room"):
            return
        if self.overlay == "pause":
            self.toggle_pause()
        elif self.overlay:
            self.close_overlay()
            self.focus = 0
        else:
            self.toggle_pause()

    def on_key(self, key):
        if key == pygame.K_m:
            self.muted = not self.muted
            return
        if key == pygame.K_ESCAPE:
            self.on_escape()
            return
        if self.dialogue and not self.overlay and key in (pygame.K_RETURN, pygame.K_SPACE):
            self.advance()
            return
        ids = ["ash", "bone", "cinder"]
        if self.state == "room" and not self.overlay and not self.dialogue:
            if key in (pygame.K_1, pygame.K_KP1):
                self.select("ash")
                return
            if key in (pygame.K_2, pygame.K_KP2):
                self.select("bone")
                return
            if key in (pygame.K_3, pygame.K_KP3):
                self.select("cinder")
                return
            if key == pygame.K_LEFT:
                cur = ids.index(self.selected) if self.selected in ids else 0
                self.select(ids[(cur - 1) % 3])
                return
            if key == pygame.K_RIGHT:
                cur = ids.index(self.selected) if self.selected in ids else -1
                self.select(ids[(cur + 1) % 3])
                return
            if key == pygame.K_o:
                self.observe()
                return
            if key == pygame.K_f:
                self.activate(("open", "files"))
                return
            if key == pygame.K_n:
                self.activate(("open", "notes"))
                return
            if key == pygame.K_a and self.banner <= 0:
                self.activate(("accuse_open",))
                return
            if key == pygame.K_UP:
                self.nudge(-1, "dock")
                return
            if key == pygame.K_DOWN:
                self.nudge(1, "dock")
                return
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.activate_focus()
                return
        if self.state == "prep" and self.overlay != "pause":
            if key == pygame.K_LEFT:
                self.file_tab = 0
                self.scroll = 0
                return
            if key == pygame.K_RIGHT:
                self.file_tab = 1
                self.scroll = 0
                return
            if key in (pygame.K_UP, pygame.K_DOWN):
                self.nudge(-1 if key == pygame.K_UP else 1)
                return
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.activate_focus()
                return
        if key in (pygame.K_UP, pygame.K_LEFT):
            self.nudge(-1)
            return
        if key in (pygame.K_DOWN, pygame.K_RIGHT, pygame.K_TAB):
            self.nudge(1)
            return
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.nav:
                self.activate_focus()
            else:
                self.advance()

    def on_click(self, pos):
        for i in range(len(self.hotspots) - 1, -1, -1):
            rect, action = self.hotspots[i]
            if rect.collidepoint(pos):
                for n, item in enumerate(self.nav):
                    if item[0] == rect and item[1] == action:
                        self.focus = n
                        break
                self.activate(action)
                return

    def on_wheel(self, delta):
        if self.state == "prep" or self.overlay in ("files", "notes"):
            self.scroll = max(0, self.scroll - delta * 36)

    def update(self, dt):
        if self.state != self.prev_state:
            self.fade = 1.0
            self.prev_state = self.state
            self.focus = 0
        self.fade = max(0.0, self.fade - dt * 2.1)
        if self.overlay == "pause":
            return
        self.anim_t += dt
        if self.state == "zoom":
            self.zoom_t += dt
            if self.zoom_t > 3.05:
                self.zoom_i += 1
                self.zoom_t = 0
                if self.zoom_i >= 3:
                    self.state = "drop"
                    self.drop_t = 0
        elif self.state == "brief":
            self.chars = min(len(BRIEF[self.brief_i]), self.chars + 75 * dt)
        elif self.state == "drop":
            self.drop_t += dt
        elif self.state == "prep":
            self.prep_left -= dt
            if self.prep_left <= 0:
                self.begin_room()
        elif self.state == "room":
            for clone in self.clones:
                if clone.shock_anim > 0:
                    clone.shock_anim = max(0.0, clone.shock_anim - dt)
            if self.banner > 0:
                self.banner -= dt
            else:
                self.time_left -= dt
                if self.time_left <= 0:
                    self.begin_ending("timeout")
        elif self.state == "end":
            self.update_end(dt)
        if self.state != self.prev_state:
            self.fade = 1.0
            self.prev_state = self.state
            self.focus = 0

    def update_end(self, dt):
        if self.ending != "timeout" or self.cine_phase >= 3:
            return
        self.cine_t += dt
        limits = (2.8, 3.5, 4.4)
        if self.cine_t >= limits[self.cine_phase]:
            self.cine_phase += 1
            self.cine_t = 0.0

    def sync_visuals(self):
        for clone in self.clones:
            clone.glitch = 0.0
            clone.eyes = "auto"
        if self.state == "end" and self.ending == "timeout":
            bone = self.cmap["bone"]
            if self.cine_phase == 1:
                bone.glitch = min(1.0, self.cine_t / 1.05)
                if self.cine_t > 1.45:
                    bone.eyes = "black"
            elif self.cine_phase >= 2:
                bone.eyes = "black"
                bone.glitch = 0.2

    def draw(self):
        self.hotspots = []
        self.nav = []
        self.sync_visuals()
        screen = self.screen
        screen.fill(BG)
        drawer = {
            "title": story.draw_title,
            "tutor": story.draw_tutor,
            "paper": story.draw_paper,
            "zoom": story.draw_zoom,
            "brief": story.draw_brief,
            "drop": story.draw_drop,
            "prep": story.draw_prep,
            "room": stage.draw_room,
            "end": story.draw_end,
        }[self.state]
        drawer(self, screen)
        if self.nav:
            self.focus = max(0, min(self.focus, len(self.nav) - 1))
        else:
            self.focus = 0
        if self.state != "paper":
            screen.blit(self.scan, (0, 0))
        if self.fade > 0.02:
            self.fx.fill((0, 0, 0, int(220 * self.fade)))
            screen.blit(self.fx, (0, 0))

    def loop(self):
        while self.running:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.on_key(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    for i, item in enumerate(self.nav):
                        if item[0].collidepoint(event.pos):
                            self.focus = i
                            break
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.on_click(event.pos)
                elif event.type == pygame.MOUSEWHEEL:
                    self.on_wheel(event.y)
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()


