import math
import random

import pygame
from settings import *
from casino_ui import *

pygame.init()

# Evropská ruleta: 0–36, pořadí čísel na kole
WHEEL_ORDER = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10,
               5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

WHEEL_CENTER = (300, 210)
WHEEL_RADIUS = 150

SPIN_DURATION = 4000  # ms

# Typy sázek: (název, výplata) – výplata 1 znamená 1:1
BET_TYPES = [
    ("RED", 1),
    ("BLACK", 1),
    ("ODD", 1),
    ("EVEN", 1),
    ("1-18", 1),
    ("19-36", 1),
]


def get_bet_rects():
    rects = []
    for i in range(len(BET_TYPES)):
        rect = pygame.Rect(0, 0, 170, 45)
        rect.center = (110 + (i % 3) * 190, 420 + (i // 3) * 60)
        rects.append(rect)
    return rects


BET_RECTS = get_bet_rects()

SPIN_BUTTON_RECT = pygame.Rect(0, 0, 160, 50)
SPIN_BUTTON_RECT.center = (300, 560)


def number_color(number):
    if number == 0:
        return (60, 170, 90)
    return RED if number in RED_NUMBERS else BLACK


POCKET_ANGLE = 360 / len(WHEEL_ORDER)
BALL_TRACK_RADIUS = WHEEL_RADIUS * 0.68

number_font = pygame.font.SysFont("segoeui", 13, bold=True)


def is_winning_bet(bet_name, number):
    # Na 0 prohrávají všechny tyhle sázky
    if number == 0:
        return False
    if bet_name == "RED":
        return number in RED_NUMBERS
    if bet_name == "BLACK":
        return number not in RED_NUMBERS
    if bet_name == "ODD":
        return number % 2 == 1
    if bet_name == "EVEN":
        return number % 2 == 0
    if bet_name == "1-18":
        return number <= 18
    if bet_name == "19-36":
        return number >= 19
    return False


def color_name(number):
    if number == 0:
        return "GREEN"
    return "RED" if number in RED_NUMBERS else "BLACK"


def point_on_circle(angle, radius):
    a = math.radians(angle)
    return (WHEEL_CENTER[0] + math.cos(a) * radius, WHEEL_CENTER[1] + math.sin(a) * radius)


def draw_wheel(angle):
    pygame.draw.circle(screen, (90, 60, 30), WHEEL_CENTER, WHEEL_RADIUS + 12)

    for i, number in enumerate(WHEEL_ORDER):
        start = angle + i * POCKET_ANGLE
        # Výseč = střed + pár bodů po oblouku, ať je kulatá
        points = [WHEEL_CENTER]
        for step in range(4):
            points.append(point_on_circle(start + step * POCKET_ANGLE / 3, WHEEL_RADIUS))
        pygame.draw.polygon(screen, number_color(number), points)

        label = number_font.render(str(number), True, WHITE)
        label = pygame.transform.rotate(label, -(start + POCKET_ANGLE / 2) - 90)
        screen.blit(label, label.get_rect(center=point_on_circle(start + POCKET_ANGLE / 2, WHEEL_RADIUS * 0.87)))

    # Vnitřní část kola, po jejímž okraji jezdí míček
    pygame.draw.circle(screen, (90, 60, 30), WHEEL_CENTER, int(WHEEL_RADIUS * 0.55))
    pygame.draw.circle(screen, GOLD, WHEEL_CENTER, int(WHEEL_RADIUS * 0.55), width=3)
    pygame.draw.circle(screen, WHITE, WHEEL_CENTER, WHEEL_RADIUS, width=3)


def draw_ball(ball_angle):
    pos = point_on_circle(ball_angle, BALL_TRACK_RADIUS)
    pygame.draw.circle(screen, WHITE, pos, 8)
    pygame.draw.circle(screen, (150, 150, 150), pos, 8, width=1)


def run_roulette(score):
    clock = pygame.time.Clock()
    bet = 10
    selected_bet = None   # index do BET_TYPES
    spinning = False
    spin_start = 0
    wheel_angle = 0
    ball_angle = 0
    result_number = None
    result_text = ""
    wheel_start = wheel_travel = 0
    ball_start = ball_travel = 0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(TABLE_GREEN)

        draw_balance(score, bet)
        draw_wheel(wheel_angle)
        draw_ball(ball_angle)

        for i, (rect, (name, _)) in enumerate(zip(BET_RECTS, BET_TYPES)):
            draw_button(rect, name, mouse_pos, enabled=not spinning)
            if i == selected_bet:
                pygame.draw.rect(screen, GOLD, rect.inflate(8, 8), width=3, border_radius=14)

        if not spinning:
            draw_bet_buttons(mouse_pos)
            draw_button(SPIN_BUTTON_RECT, "SPIN", mouse_pos,
                        enabled=selected_bet is not None and score >= bet)
            draw_text(result_text, (300, 385), GOLD)

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
                for i, rect in enumerate(BET_RECTS):
                    if rect.collidepoint(event.pos):
                        selected_bet = i
                if SPIN_BUTTON_RECT.collidepoint(event.pos) and selected_bet is not None and score >= bet:
                    score -= bet
                    result_number = random.choice(WHEEL_ORDER)
                    spinning = True
                    spin_start = pygame.time.get_ticks()

                    # Výsledek je vybraný předem, takže spočítáme, o kolik se má
                    # kolo a míček otočit, aby míček skončil přesně na jeho políčku
                    wheel_start = wheel_angle
                    wheel_travel = 360 * 2 + random.uniform(0, 360)
                    pocket = WHEEL_ORDER.index(result_number)
                    target = wheel_start + wheel_travel + (pocket + 0.5) * POCKET_ANGLE
                    ball_start = ball_angle
                    ball_travel = 360 * 4 + (ball_start - target) % 360

        if spinning:
            progress = min(1, (pygame.time.get_ticks() - spin_start) / SPIN_DURATION)
            # Plynulé zpomalování (rychle na začátku, pomalu na konci)
            ease = 1 - (1 - progress) ** 3
            wheel_angle = (wheel_start + wheel_travel * ease) % 360
            ball_angle = (ball_start - ball_travel * ease) % 360

            if progress >= 1:
                spinning = False
                name, payout = BET_TYPES[selected_bet]
                label = f"{result_number} {color_name(result_number)}"
                if is_winning_bet(name, result_number):
                    win = bet + bet * payout
                    score += win
                    result_text = f"{label} – YOU WIN {win}"
                else:
                    result_text = f"{label} – YOU LOSE"

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_roulette(100)
    pygame.quit()
