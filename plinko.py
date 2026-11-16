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


def drop_ball():
    # TODO: vytvoř nový míček nahoře uprostřed (třeba dict s x, y, vx, vy, bet)
    #       malý náhodný posun x, ať nepadá pokaždé stejně
    pass


def update_ball(ball):
    # TODO: přičti gravitaci k vy, posuň míček o vx, vy
    # TODO: když se míček dotkne kolíku (vzdálenost < PEG_RADIUS + BALL_RADIUS),
    #       odraz ho náhodně doleva nebo doprava
    # TODO: nepouštěj míček ven z okna (0 až 600)
    pass


def check_slot(ball):
    # TODO: když je míček dole (y >= SLOT_Y), zjisti do které přihrádky spadl
    #       a vrať výhru = bet * násobitel. Jinak vrať None.
    return None


def draw_board():
    for peg in PEGS:
        pygame.draw.circle(screen, WHITE, peg, PEG_RADIUS)

    for rect, mult in zip(SLOT_RECTS, SLOT_MULTIPLIERS):
        color = GOLD if mult >= 3 else (RED if mult < 1 else theme["button"])
        pygame.draw.rect(screen, color, rect.inflate(-4, 0), border_radius=6)
        draw_text(f"x{mult}", rect.center, BLACK if color == GOLD else WHITE)


def draw_ball(ball):
    # TODO: nakresli míček (pygame.draw.circle)
    pass


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
                    # TODO: odečti sázku ze score a přidej míček do balls
                    pass

        # TODO: pro každý míček zavolej update_ball a check_slot,
        #       výhru přičti ke score a dopadlý míček odeber ze seznamu
        for ball in balls:
            draw_ball(ball)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_plinko(100)
    pygame.quit()
