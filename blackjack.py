import random

import pygame
from settings import *
from casino_ui import *

pygame.init()

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

CARD_WIDTH = 70
CARD_HEIGHT = 100
CARD_GAP = 15

DEALER_Y = 160
PLAYER_Y = 360

DEAL_BUTTON_RECT = pygame.Rect(0, 0, 140, 50)
DEAL_BUTTON_RECT.center = (300, 540)
HIT_BUTTON_RECT = pygame.Rect(0, 0, 140, 50)
HIT_BUTTON_RECT.center = (220, 540)
STAND_BUTTON_RECT = pygame.Rect(0, 0, 140, 50)
STAND_BUTTON_RECT.center = (380, 540)

card_font = pygame.font.SysFont("dejavusans", 26, bold=True)

# Stavy hry: "betting" -> "player_turn" -> "dealer_turn" -> "result"


def create_deck():
    # TODO: vytvoř seznam všech 52 karet (např. tuple (rank, suit)) a zamíchej ho
    return []


def hand_value(hand):
    # TODO: sečti hodnotu ruky. J/Q/K = 10, A = 11 nebo 1
    #       (eso počítej jako 11, a dokud je součet > 21, změň eso na 1)
    return 0


def dealer_play(deck, dealer_hand):
    # TODO: dealer bere karty, dokud má méně než 17
    pass


def decide_winner(player_hand, dealer_hand):
    # TODO: vrať "player", "dealer" nebo "push" (remíza)
    #       nezapomeň na přetažení (> 21) a blackjack
    return "push"


def draw_card(card, topleft, hidden=False):
    rect = pygame.Rect(topleft, (CARD_WIDTH, CARD_HEIGHT))
    pygame.draw.rect(screen, SHADOW, rect.move(0, 4), border_radius=8)

    if hidden:
        pygame.draw.rect(screen, theme["button"], rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=8)
        return

    rank, suit = card
    color = RED if suit in ("♥", "♦") else BLACK
    pygame.draw.rect(screen, WHITE, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, width=2, border_radius=8)
    label = card_font.render(f"{rank}{suit}", True, color)
    screen.blit(label, label.get_rect(center=rect.center))


def draw_hand(hand, y, hide_second=False):
    total_width = len(hand) * CARD_WIDTH + (len(hand) - 1) * CARD_GAP
    start_x = 300 - total_width // 2
    for i, card in enumerate(hand):
        hidden = hide_second and i == 1
        draw_card(card, (start_x + i * (CARD_WIDTH + CARD_GAP), y), hidden)


def run_blackjack(score):
    clock = pygame.time.Clock()
    bet = 10
    state = "betting"
    deck = []
    player_hand = []
    dealer_hand = []
    result_text = ""

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(TABLE_GREEN)

        draw_balance(score, bet)
        draw_text("DEALER", (300, DEALER_Y - 25))
        draw_text("YOU", (300, PLAYER_Y - 25))

        draw_hand(dealer_hand, DEALER_Y, hide_second=state == "player_turn")
        draw_hand(player_hand, PLAYER_Y)

        if state in ("betting", "result"):
            draw_bet_buttons(mouse_pos)
            draw_button(DEAL_BUTTON_RECT, "DEAL", mouse_pos, enabled=score >= bet)
        elif state == "player_turn":
            draw_button(HIT_BUTTON_RECT, "HIT", mouse_pos)
            draw_button(STAND_BUTTON_RECT, "STAND", mouse_pos)

        if state == "result":
            draw_text(result_text, (300, 290), GOLD, big_font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", score

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back", score

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state in ("betting", "result"):
                    if BET_MINUS_RECT.collidepoint(event.pos):
                        bet = max(BET_STEP, bet - BET_STEP)
                    if BET_PLUS_RECT.collidepoint(event.pos):
                        bet = bet + BET_STEP
                    if DEAL_BUTTON_RECT.collidepoint(event.pos) and score >= bet:
                        # TODO: odečti sázku, vytvoř balíček, rozdej 2 karty hráči
                        #       a 2 dealerovi, přepni state na "player_turn"
                        pass

                elif state == "player_turn":
                    if HIT_BUTTON_RECT.collidepoint(event.pos):
                        # TODO: přidej hráči kartu; když má > 21, konec kola
                        pass
                    if STAND_BUTTON_RECT.collidepoint(event.pos):
                        state = "dealer_turn"

        if state == "dealer_turn":
            # TODO: dealer_play, decide_winner, vyplať výhru (bet * 2 při výhře,
            #       bet zpět při remíze), nastav result_text a state = "result"
            pass

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_blackjack(100)
    pygame.quit()
