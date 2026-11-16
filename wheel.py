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


def draw_wheel(angle):
    # TODO: pro každé políčko i ze SEGMENTS nakresli výseč (pygame.draw.polygon)
    #       v barvě SYMBOLS[SEGMENTS[i]][1]
    #       políčko začíná na úhlu angle + i * SEGMENT_ANGLE
    #       bod na kraji = (cx + cos(úhel) * r, cy + sin(úhel) * r)  (math.radians!)
    #       tip: výseč = střed + několik bodů po oblouku, ať je kulatá
    # TODO: do prostředku každé výseče napiš název symbolu (segment_font)
    # TODO: na hranici mezi políčky nakresli malý kolík (pygame.draw.circle
    #       kousek od okraje) – o ty pak "ťuká" ukazatel
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

def get_segment_at_pointer(angle):
    # TODO: podle úhlu kola zjisti, které políčko je pod ukazatelem (nahoře = 270°)
    #       a vrať jeho název ze SEGMENTS
    #       tip: (270 - angle) % 360 // SEGMENT_ANGLE
    return SEGMENTS[0]


def passed_peg(old_angle, new_angle):
    # TODO: vrať True, pokud mezi old_angle a new_angle prošel ukazatelem kolík
    #       (tj. změnilo se číslo políčka pod ukazatelem)
    return False


def payout_for(selected, landed, bet):
    # TODO: když landed == selected, vrať bet + bet * výplata, jinak 0
    return 0


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
                    # TODO: odečti sázku, nastav náhodnou počáteční rychlost
                    #       (random.uniform), spinning = True, smaž result_text
                    pass

        if spinning:
            # TODO: ulož starý úhel, otoč kolo (angle += speed), zpomal (speed *= FRICTION)
            # TODO: když passed_peg(...): pointer_kick = -20 (ukazatel cvakne)
            # TODO: když speed < STOP_SPEED: spinning = False, zjisti políčko,
            #       přičti payout_for(...) ke score, nastav result_text
            #       a záblesk: flash_color = zelená/červená, flash_start = now
            pass

        # Ukazatel se po cvaknutí pomalu vrací zpět
        pointer_kick *= 0.8

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_wheel(100)
    pygame.quit()
