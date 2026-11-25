import random

import pygame
from settings import *
from casino_ui import *

pygame.init()

# Kolíky (pegs) – trojúhelník, každá řada má o jeden víc
PEG_ROWS = 10
PEG_GAP = 40
PEG_RADIUS = 5
PEG_START_Y = 110

# Přihrádky dole a jejich násobitele (krajní = vzácné = víc)



def get_pegs():
    pegs = []
    for row in range(PEG_ROWS):
        count = row + 3
        total_width = (count - 1) * PEG_GAP
        start_x = 300 - total_width // 2
        for i in range(count):
            pegs.append((start_x + i * PEG_GAP, PEG_START_Y + row * PEG_GAP))
    return pegs


def get_slot_rects():
    width = 600 // len(SLOT_MULTIPLIERS)
    return [pygame.Rect(i * width, SLOT_Y, width, SLOT_HEIGHT) for i in range(len(SLOT_MULTIPLIERS))]


PEGS = get_pegs()
SLOT_RECTS = get_slot_rects()


def drop_ball(bet):
    # Nový míček nahoře uprostřed, malý náhodný posun ať nepadá pokaždé stejně
    return {
        "x": 300 + random.uniform(-4, 4),
        "y": PEG_START_Y - 30,
        "vx": 0,
        "vy": 0,
        "bet": bet,
    }


def update_ball(ball):
    ball["vy"] += GRAVITY
    ball["vx"] *= 0.99
    ball["x"] += ball["vx"]
    ball["y"] += ball["vy"]

    hit_distance = PEG_RADIUS + BALL_RADIUS
    for peg_x, peg_y in PEGS:
        dx = ball["x"] - peg_x
        dy = ball["y"] - peg_y
        distance = (dx * dx + dy * dy) ** 0.5
        if distance < hit_distance:
            if distance == 0:
                dx, dy, distance = 0, -1, 1
            # Vytlač míček z kolíku, ať se v něm nezasekne
            ball["x"] = peg_x + dx / distance * hit_distance
            ball["y"] = peg_y + dy / distance * hit_distance
            # Odraz náhodně doleva nebo doprava, trochu nahoru
            ball["vx"] = random.choice((-1, 1)) * random.uniform(1.2, 2.2)
            ball["vy"] = -abs(ball["vy"]) * 0.3
            break

    # Nepouštěj míček ven z okna
    if ball["x"] < BALL_RADIUS:
        ball["x"] = BALL_RADIUS
        ball["vx"] = abs(ball["vx"])
    if ball["x"] > 600 - BALL_RADIUS:
        ball["x"] = 600 - BALL_RADIUS
        ball["vx"] = -abs(ball["vx"])


def check_slot(ball):
    # Když je míček dole, vrať výhru = bet * násobitel přihrádky, jinak None
    if ball["y"] < SLOT_Y:
        return None
    width = 600 // len(SLOT_MULTIPLIERS)
    index = min(int(ball["x"] // width), len(SLOT_MULTIPLIERS) - 1)
    return round(ball["bet"] * SLOT_MULTIPLIERS[index])


def draw_board():
    for peg in PEGS:
        pygame.draw.circle(screen, WHITE, peg, PEG_RADIUS)

    for rect, mult in zip(SLOT_RECTS, SLOT_MULTIPLIERS):
        color = GOLD if mult >= 3 else (RED if mult < 1 else theme["button"])
        pygame.draw.rect(screen, color, rect.inflate(-4, 0), border_radius=6)
        draw_text(f"x{mult}", rect.center, BLACK if color == GOLD else WHITE)


def draw_ball(ball):
    pos = (int(ball["x"]), int(ball["y"]))
    pygame.draw.circle(screen, RED, pos, BALL_RADIUS)
    pygame.draw.circle(screen, WHITE, pos, BALL_RADIUS, width=2)


def run_plinko(score):
    clock = pygame.time.Clock()
    bet = 10
    balls = []

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BG)

        draw_board()
        draw_balance(score, bet)
        draw_bet_buttons(mouse_pos)
        draw_button(DROP_BUTTON_RECT, "DROP", mouse_pos, enabled=score >= bet)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", score

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back", score

            if event.type == pygame.MOUSEBUTTONDOWN:
                if BET_MINUS_RECT.collidepoint(event.pos):
                    bet = max(BET_STEP, bet - BET_STEP)
                if BET_PLUS_RECT.collidepoint(event.pos):
                    bet = bet + BET_STEP
                if DROP_BUTTON_RECT.collidepoint(event.pos) and score >= bet:
                    score -= bet
                    balls.append(drop_ball(bet))

        # Kopie seznamu ([:]), protože z něj během cyklu odebíráme
        for ball in balls[:]:
            update_ball(ball)
            win = check_slot(ball)
            if win is not None:
                score += win
                balls.remove(ball)

        for ball in balls:
            draw_ball(ball)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_plinko(100)
    pygame.quit()
