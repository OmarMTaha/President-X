"""Pixel-art portraits. Each unit is drawn small, then scaled up.

Pygame blits the picture. The blink, the jaw and the mouth are plain functions.
"""

import math
import pygame

def paint(game, screen, cx, cy, clone, scale, lit, talking=False, preview=False):
    raw = pygame.Surface((120, 160), pygame.SRCALPHA)
    paint_raw(game, raw, clone, lit, talking, preview)
    if clone.glitch > 0.02:
        raw = apply_glitch(game, raw, clone.glitch)
    sw, sh = max(2, int(240 * scale)), max(2, int(320 * scale))
    image = pygame.transform.scale(raw, (sw, sh))
    breath = int(round(math.sin(game.anim_t * 1.7 + clone.seat * 1.2) * 2.4 * scale))
    jitter = int(round(math.sin(game.anim_t * 90) * 4 * scale)) if clone.shock_anim > 0 else 0
    lean = int(round(5 * scale)) if clone.hostile else 0
    rect = image.get_rect(center=(int(cx + lean + jitter), int(cy + 30 * scale + breath)))
    screen.blit(image, rect)


def apply_glitch(game, surf, amount):
    w, h = surf.get_size()
    out = surf.copy()
    slices = 8
    for i in range(slices):
        y = int(h * i / slices)
        sh = int(h / slices)
        dx = int(math.sin(game.anim_t * 18 + i * 1.7) * max(2, w // 18) * amount)
        strip = surf.subsurface((0, y, w, sh)).copy()
        out.fill((0, 0, 0, 0), (0, y, w, sh))
        out.blit(strip, (dx, y))
    return out


def blink_amount(game, clone):
    if clone.eyes == "black":
        return 0.0
    period = {"ash": 4.8, "bone": 3.3, "cinder": 1.2}[clone.id]
    local = game.anim_t % period
    if local < 0.16:
        return math.sin((local / 0.16) * math.pi)
    return 0.0


def jaw_amount(game, clone):
    if clone.id != "bone" or clone.eyes == "black":
        return 0.0
    local = (game.anim_t % 3.6) - 3.15
    if local < 0:
        return 0.0
    if local < 0.1:
        return local / 0.1
    if local < 0.24:
        return 1.0
    if local < 0.4:
        return 1 - (local - 0.24) / 0.16
    return 0.0


def paint_raw(game, surf, clone, lit, talking, preview=False):
    t = game.anim_t
    s = 0.5
    who = "ash" if preview else clone.id

    def p(v):
        return int(v * s + 0.5)

    skin = (224, 196, 174) if preview or clone.id != "cinder" else (214, 176, 156)
    skin_shadow = (176, 140, 118) if preview or clone.id != "cinder" else (168, 124, 108)
    jacket = (18, 24, 36)
    jacket_hi = (42, 52, 68)
    hair = (28, 26, 30)
    # shoulders and jacket
    pygame.draw.polygon(surf, jacket, [(p(18), p(320)), (p(8), p(214)), (p(58), p(176)), (p(120), p(198)), (p(182), p(176)), (p(232), p(214)), (p(222), p(320))])
    pygame.draw.polygon(surf, jacket_hi, [(p(78), p(188)), (p(120), p(206)), (p(162), p(188)), (p(150), p(250)), (p(90), p(250))])
    pygame.draw.polygon(surf, (232, 228, 220), [(p(104), p(198)), (p(120), p(248)), (p(136), p(198))])
    pygame.draw.polygon(surf, (146, 28, 40), [(p(112), p(206)), (p(128), p(206)), (p(132), p(268)), (p(120), p(278)), (p(108), p(268))])
    pygame.draw.polygon(surf, (186, 48, 58), [(p(114), p(206)), (p(126), p(206)), (p(120), p(220))])
    pygame.draw.line(surf, (8, 10, 16), (p(74), p(204)), (p(112), p(252)), p(3))
    pygame.draw.line(surf, (8, 10, 16), (p(166), p(204)), (p(128), p(252)), p(3))
    pygame.draw.circle(surf, (70, 76, 86), (p(120), p(236)), p(3))
    # neck and collar
    pygame.draw.rect(surf, skin_shadow, (p(104), p(176), p(32), p(36)))
    pygame.draw.rect(surf, skin, (p(110), p(176), p(16), p(30)))
    # head, lit from the upper left
    pygame.draw.ellipse(surf, skin_shadow, (p(54), p(46), p(132), p(162)))
    pygame.draw.ellipse(surf, skin, (p(62), p(52), p(112), p(140)))
    pygame.draw.ellipse(surf, skin_shadow, (p(78), p(150), p(84), p(36)))
    # ears
    pygame.draw.ellipse(surf, skin_shadow, (p(40), p(104), p(26), p(40)))
    pygame.draw.ellipse(surf, skin, (p(46), p(112), p(14), p(24)))
    pygame.draw.ellipse(surf, skin_shadow, (p(174), p(104), p(26), p(40)))
    pygame.draw.ellipse(surf, skin, (p(180), p(112), p(14), p(24)))
    # hair
    pygame.draw.polygon(surf, hair, [
        (p(58), p(112)), (p(48), p(78)), (p(64), p(40)), (p(108), p(28)),
        (p(168), p(40)), (p(196), p(78)), (p(186), p(118)), (p(168), p(96)),
        (p(150), p(86)), (p(92), p(88)), (p(70), p(104)),
    ])
    pygame.draw.polygon(surf, (48, 46, 52), [(p(150), p(36)), (p(186), p(70)), (p(168), p(48))])
    # forehead port
    if who == "bone" and clone.eyes != "black":
        pulse = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 6))
        seam = (int(90 + 140 * pulse), 48, 56)
    else:
        seam = (46, 150, 146)
    pygame.draw.rect(surf, (24, 28, 32), (p(86), p(100), p(68), p(10)), border_radius=p(2))
    pygame.draw.line(surf, seam, (p(90), p(105)), (p(150), p(105)), p(2))
    draw_brows(game, surf, clone, p, who)
    draw_eyes(game, surf, clone, lit, skin, p, who)
    # nose
    pygame.draw.polygon(surf, skin_shadow, [(p(118), p(132)), (p(112), p(158)), (p(132), p(158)), (p(126), p(132))])
    pygame.draw.circle(surf, skin_shadow, (p(114), p(158)), p(3))
    pygame.draw.circle(surf, skin_shadow, (p(128), p(158)), p(3))
    draw_mouth(game, surf, clone, talking, p, who)
    # sweat and flush
    if who == "bone" and clone.eyes != "black":
        drip = (t * 22) % 28
        pygame.draw.circle(surf, (198, 220, 226), (p(154), p(150) + int(drip)), p(3))
    if who == "cinder":
        drip = (t * 30) % 34
        pygame.draw.circle(surf, (198, 214, 220), (p(158), p(108) + int(drip)), p(3))
        pygame.draw.circle(surf, (198, 214, 220), (p(78), p(120) + int((t * 16) % 20)), p(2))
    wash = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    if lit:
        pygame.draw.ellipse(wash, (255, 214, 160, 46), (p(48), p(36), p(150), p(170)))
    else:
        wash.fill((4, 8, 16, 36))
    surf.blit(wash, (0, 0))
    if clone.shock_anim > 0.05:
        flash = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        flash.fill((180, 230, 255, int(150 * min(1, clone.shock_anim))))
        surf.blit(flash, (0, 0))
        for n in range(4):
            y = p(80 + n * 40) + int(math.sin(t * 40 + n) * 6)
            pygame.draw.line(surf, (220, 245, 255), (p(40), y), (p(200), y + p(8)), p(1))
    if clone.glitch > 0.35:
        y = p(118) + int(math.sin(t * 25) * p(4))
        pygame.draw.line(surf, (255, 36, 48), (p(30), y), (p(210), y), p(2))


def draw_brows(game, surf, clone, p, who):
    color = (42, 30, 28)
    if clone.hostile:
        pygame.draw.line(surf, color, (p(74), p(112)), (p(112), p(124)), p(3))
        pygame.draw.line(surf, color, (p(166), p(112)), (p(128), p(124)), p(3))
    elif who == "cinder":
        pygame.draw.line(surf, color, (p(74), p(122)), (p(112), p(112)), p(3))
        pygame.draw.line(surf, color, (p(166), p(122)), (p(128), p(112)), p(3))
    else:
        pygame.draw.line(surf, color, (p(74), p(116)), (p(112), p(116)), p(3))
        pygame.draw.line(surf, color, (p(128), p(116)), (p(166), p(116)), p(3))


def draw_eyes(game, surf, clone, lit, skin, p, who):
    blink = blink_amount(game, clone)
    for ex, left in ((72, True), (130, False)):
        if clone.eyes == "black":
            sclera = (16, 12, 14)
        elif who == "cinder":
            sclera = (214, 112, 118)
        elif who == "bone":
            sclera = (236, 214, 208)
        else:
            sclera = (244, 238, 230)
        pygame.draw.ellipse(surf, sclera, (p(ex), p(124), p(40), p(24)))
        pygame.draw.ellipse(surf, (255, 252, 248), (p(ex + 4), p(126), p(18), p(8)))
        if clone.eyes == "black":
            iris = (0, 0, 0)
            radius = p(8)
        elif who == "bone" and left and lit and math.sin(game.anim_t * 14) > -0.15:
            iris = (210, 255, 248)
            radius = p(9)
        elif who == "bone" and not left:
            iris = (28, 48, 52)
            radius = p(8)
        else:
            iris = (36, 132, 134)
            radius = p(8)
        look = int(math.sin(game.anim_t * 0.9) * p(3))
        center = (p(ex + 20) + look, p(136))
        pygame.draw.circle(surf, iris, center, radius)
        pygame.draw.circle(surf, (8, 12, 16), center, p(4))
        if clone.eyes != "black":
            pygame.draw.circle(surf, (70, 210, 200), center, radius + p(2), p(1))
            pygame.draw.circle(surf, (255, 255, 255), (center[0] - p(3), center[1] - p(3)), p(2))
        if who == "bone" and clone.eyes != "black":
            ix = p(ex + 32) if left else p(ex + 8)
            pygame.draw.circle(surf, (176, 16, 28), (ix, p(140)), p(8) if left else p(5))
        if blink > 0.04:
            lid_h = int(p(24) * blink)
            pygame.draw.rect(surf, skin, (p(ex) - 1, p(122), p(42), lid_h))
            pygame.draw.line(surf, (70, 48, 42), (p(ex), p(122) + lid_h), (p(ex + 40), p(122) + lid_h), p(2))


def draw_mouth(game, surf, clone, talking, p, who):
    jaw = 0.0 if who != "bone" else jaw_amount(game, clone)
    mouth_y = 172 + jaw * 8
    if clone.hostile:
        open_h = 16
    elif talking:
        open_h = 6 + int((math.sin(game.anim_t * 14) + 1) * 6)
    else:
        open_h = 4
    pygame.draw.ellipse(surf, (120, 64, 68), (p(100), p(mouth_y), p(40), p(open_h + 4)))
    inner = (70, 24, 30) if not talking else (92, 32, 36)
    pygame.draw.ellipse(surf, inner, (p(106), p(mouth_y + 2), p(28), p(max(3, open_h))))
    if open_h > 8:
        pygame.draw.rect(surf, (236, 230, 222), (p(112), p(mouth_y + 2), p(16), p(3)))
    if jaw > 0.4:
        pygame.draw.line(surf, (150, 70, 74), (p(78), p(156)), (p(104), p(mouth_y + 2)), p(3))

