import math
import random

import pygame
from settings import *
from casino_ui import *

pygame.init()

SYMBOLS = {
    "1": (1, (70, 130, 255)),
    "2": (2, (60, 170, 90)),
    "5": (5, (240, 140, 40)),
    "10": (10, (130, 70, 200)),
    "20": (20, (210, 50, 50)),
    "JOKER": (40, GOLD),
}


SEGMENTS = [
    "1", "2", "1", "5", "1", "2", "1", "10",
    "1", "2", "5", "1", "20", "1", "2", "5",
    "1", "10", "2", "1", "5", "2", "1", "JOKER",
]

SEGMENT_ANGLE = 360 / len(SEGMENTS)


def get_symbol_rects():
    rects = []
    names = list(SYMBOLS)
    for i in range(len(names)):
        rect = pygame.Rect(0, 0, 88, 42)
        rect.center = (55 + i * 98, 485)
        rects.append(rect)
    return rects


SYMBOL_RECTS = get_symbol_rects()

SPIN_BUTTON_RECT = pygame.Rect(0, 0, 160, 50)
SPIN_BUTTON_RECT.center = (300, 553)

segment_font = pygame.font.SysFont("segoeui", 16, bold=True)


# ---------------------------------------------------------------- kreslení

def draw_rim(now, spinning):
    # Dřevěný okraj se světly. Při točení blikají střídavě, v klidu svítí všechna.
    pygame.draw.circle(screen, (90, 60, 30), WHEEL_CENTER, WHEEL_RADIUS + RIM_WIDTH)
    pygame.draw.circle(screen, GOLD, WHEEL_CENTER, WHEEL_RADIUS + RIM_WIDTH, width=3)

    phase = (now // LIGHT_BLINK_MS) % 2
    cx, cy = WHEEL_CENTER
    r = WHEEL_RADIUS + RIM_WIDTH // 2
    for i in range(LIGHT_COUNT):
        a = math.radians(i * 360 / LIGHT_COUNT)
        pos = (cx + math.cos(a) * r, cy + math.sin(a) * r)
        on = not spinning or i % 2 == phase
        color = (255, 240, 150) if on else (110, 90, 40)
        pygame.draw.circle(screen, color, pos, 5)


def point_on_circle(angle, radius):
    a = math.radians(angle)
    return (WHEEL_CENTER[0] + math.cos(a) * radius, WHEEL_CENTER[1] + math.sin(a) * radius)


def draw_wheel(angle):
    for i, name in enumerate(SEGMENTS):
        start = angle + i * SEGMENT_ANGLE
        color = SYMBOLS[name][1]

        # Výseč = střed + pár bodů po oblouku, ať je kulatá
        points = [WHEEL_CENTER]
        for step in range(5):
            points.append(point_on_circle(start + step * SEGMENT_ANGLE / 4, WHEEL_RADIUS))
        pygame.draw.polygon(screen, color, points)

        # Název symbolu otočený podél poloměru
        middle = start + SEGMENT_ANGLE / 2
        text_color = BLACK if color == GOLD else WHITE
        label = segment_font.render(name, True, text_color)
        # Na levé půlce kola otočit o 180°, jinak by byl text vzhůru nohama
        flip = 180 if 90 < middle % 360 < 270 else 0
        label = pygame.transform.rotate(label, -middle + flip)
        screen.blit(label, label.get_rect(center=point_on_circle(middle, WHEEL_RADIUS * 0.66)))

    # Kolíky na hranicích políček – o ty "ťuká" ukazatel
    for i in range(len(SEGMENTS)):
        peg = point_on_circle(angle + i * SEGMENT_ANGLE, WHEEL_RADIUS - 7)
        pygame.draw.circle(screen, WHITE, peg, 4)

    pygame.draw.circle(screen, WHITE, WHEEL_CENTER, WHEEL_RADIUS, width=3)

    # Střed kola
    pygame.draw.circle(screen, GOLD, WHEEL_CENTER, 28)
    pygame.draw.circle(screen, (90, 60, 30), WHEEL_CENTER, 28, width=4)


def draw_pointer(kick):
    # Ukazatel nahoře. kick = o kolik stupňů je vychýlený (když ho trkne kolík)
    x, y = WHEEL_CENTER[0], WHEEL_CENTER[1] - WHEEL_RADIUS - RIM_WIDTH
    a = math.radians(kick)
    points = [(-14, -22), (14, -22), (0, 22)]
    rotated = [(x + px * math.cos(a) - py * math.sin(a),
                y + px * math.sin(a) + py * math.cos(a)) for px, py in points]
    pygame.draw.polygon(screen, RED, rotated)
    pygame.draw.polygon(screen, WHITE, rotated, width=2)
    pygame.draw.circle(screen, GOLD, (x, y - 14), 6)


def draw_symbol_buttons(selected, mouse_pos, enabled):
    for rect, name in zip(SYMBOL_RECTS, SYMBOLS):
        payout, color = SYMBOLS[name]
        shadow_offset = 2 if rect.collidepoint(mouse_pos) and enabled else 4
        pygame.draw.rect(screen, SHADOW, rect.move(0, shadow_offset), border_radius=10)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=10)

        text_color = BLACK if color == GOLD else WHITE
        draw_text(name, (rect.centerx, rect.centery - 7), text_color, segment_font)
        draw_text(f"{payout}:1", (rect.centerx, rect.centery + 10), text_color, segment_font)

        if name == selected:
            pygame.draw.rect(screen, WHITE, rect.inflate(10, 10), width=3, border_radius=14)


def draw_flash(flash_color, flash_start, now):
    # Průhledný záblesk přes celou obrazovku, postupně mizí
    if flash_color is None:
        return
    progress = (now - flash_start) / FLASH_DURATION
    if progress >= 1:
        return
    overlay = pygame.Surface((600, 600), pygame.SRCALPHA)
    overlay.fill((*flash_color, int(140 * (1 - progress))))
    screen.blit(overlay, (0, 0))


# ---------------------------------------------------------------- logika

def segment_index_at_pointer(angle):
    # Ukazatel je nahoře = 270° (osa y míří dolů)
    return int((270 - angle) % 360 // SEGMENT_ANGLE)


def get_segment_at_pointer(angle):
    return SEGMENTS[segment_index_at_pointer(angle)]


def passed_peg(old_angle, new_angle):
    # Kolík prošel ukazatelem = změnilo se políčko pod ukazatelem
    return segment_index_at_pointer(old_angle) != segment_index_at_pointer(new_angle)


def payout_for(selected, landed, bet):
    if landed != selected:
        return 0
    return bet + bet * SYMBOLS[selected][0]


# ---------------------------------------------------------------- hlavní smyčka

def run_wheel(score):
    clock = pygame.time.Clock()
    bet = 10
    selected = None        # název symbolu, na který hráč vsadil
    angle = 0
    speed = 0
    spinning = False
    pointer_kick = 0       # vychýlení ukazatele ve stupních
    result_text = ""
    flash_color = None
    flash_start = 0

    while True:
        now = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BG)

        draw_balance(score, bet)
        draw_rim(now, spinning)
        draw_wheel(angle)
        draw_pointer(pointer_kick)
        draw_symbol_buttons(selected, mouse_pos, enabled=not spinning)

        if not spinning:
            draw_bet_buttons(mouse_pos)
            draw_button(SPIN_BUTTON_RECT, "SPIN", mouse_pos,
                        enabled=selected is not None and score >= bet)
            draw_text(result_text if result_text else "Pick a symbol, then SPIN",
                      (300, 452), GOLD)

        draw_flash(flash_color, flash_start, now)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", score

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not spinning:
                return "back", score

            if event.type == pygame.MOUSEBUTTONDOWN and not spinning:
                if BET_MINUS_RECT.collidepoint(event.pos):
                    bet = max(BET_STEP, bet - BET_STEP)
                if BET_PLUS_RECT.collidepoint(event.pos):
                    bet = bet + BET_STEP
                for rect, name in zip(SYMBOL_RECTS, SYMBOLS):
                    if rect.collidepoint(event.pos):
                        selected = name
                if SPIN_BUTTON_RECT.collidepoint(event.pos) and selected is not None and score >= bet:
                    score -= bet
                    speed = random.uniform(8, 14)
                    spinning = True
                    result_text = ""

        if spinning:
            old_angle = angle
            angle = (angle + speed) % 360
            speed *= FRICTION

            if passed_peg(old_angle, angle):
                pointer_kick = -20

            if speed < STOP_SPEED:
                spinning = False
                landed = get_segment_at_pointer(angle)
                win = payout_for(selected, landed, bet)
                score += win
                if win > 0:
                    result_text = f"{landed} – YOU WIN {win}"
                    flash_color = (60, 170, 90)
                else:
                    result_text = f"{landed} – no luck"
                    flash_color = RED
                flash_start = now

        # Ukazatel se po cvaknutí pomalu vrací zpět
        pointer_kick *= 0.8

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_wheel(100)
    pygame.quit()
