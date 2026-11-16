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


def is_winning_bet(bet_name, number):
    # TODO: vrať True, pokud sázka bet_name vyhrává na čísle number
    #       (pozor: na 0 prohrávají všechny tyhle sázky)
    return False


def draw_wheel(angle):
    # TODO: nakresli kolo – pro každé číslo z WHEEL_ORDER výseč
    #       v barvě number_color(číslo), otočené o angle
    pygame.draw.circle(screen, (90, 60, 30), WHEEL_CENTER, WHEEL_RADIUS + 12)
    pygame.draw.circle(screen, WHITE, WHEEL_CENTER, WHEEL_RADIUS, width=3)


def draw_ball(ball_angle):
    # TODO: nakresli míček na okraji kola podle ball_angle (cos/sin)
    pass


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
                    # TODO: odečti sázku, vyber náhodné result_number,
                    #       spinning = True, spin_start = pygame.time.get_ticks()
                    pass

        if spinning:
            # TODO: dokud neuplyne SPIN_DURATION, otáčej kolo a míček (míček opačně)
            #       a postupně je zpomaluj
            # TODO: po skončení: is_winning_bet -> výhra = bet + bet * výplata,
            #       nastav result_text (např. "17 RED – YOU WIN 20")
            pass

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_roulette(100)
    pygame.quit()
