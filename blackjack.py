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
    # Všech 52 karet jako (rank, suit), zamíchané
    deck = [(rank, suit) for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck


def hand_value(hand):
    # J/Q/K = 10, eso = 11, a dokud je součet > 21, eso se počítá jako 1
    total = 0
    aces = 0
    for rank, _ in hand:
        if rank in ("J", "Q", "K"):
            total += 10
        elif rank == "A":
            total += 11
            aces += 1
        else:
            total += int(rank)

    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21


def dealer_play(deck, dealer_hand):
    # Dealer bere karty, dokud má méně než 17
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.pop())


def decide_winner(player_hand, dealer_hand):
    player = hand_value(player_hand)
    dealer = hand_value(dealer_hand)

    if player > 21:
        return "dealer"
    if dealer > 21:
        return "player"
    if is_blackjack(player_hand) and not is_blackjack(dealer_hand):
        return "player"
    if is_blackjack(dealer_hand) and not is_blackjack(player_hand):
        return "dealer"
    if player > dealer:
        return "player"
    if dealer > player:
        return "dealer"
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
        # Dealerův součet ukaž až po odkrytí druhé karty
        dealer_label = "DEALER" if state == "player_turn" or not dealer_hand else f"DEALER ({hand_value(dealer_hand)})"
        player_label = f"YOU ({hand_value(player_hand)})" if player_hand else "YOU"
        draw_text(dealer_label, (300, DEALER_Y - 25))
        draw_text(player_label, (300, PLAYER_Y - 25))

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
                        score -= bet
                        deck = create_deck()
                        player_hand = [deck.pop(), deck.pop()]
                        dealer_hand = [deck.pop(), deck.pop()]
                        result_text = ""
                        # Blackjack hned z rozdání = není co hrát, rovnou vyhodnotit
                        state = "dealer_turn" if is_blackjack(player_hand) else "player_turn"

                elif state == "player_turn":
                    if HIT_BUTTON_RECT.collidepoint(event.pos):
                        player_hand.append(deck.pop())
                        if hand_value(player_hand) >= 21:
                            state = "dealer_turn"
                    if STAND_BUTTON_RECT.collidepoint(event.pos):
                        state = "dealer_turn"

        if state == "dealer_turn":
            # Když hráč přetáhl, dealer už nebere
            if hand_value(player_hand) <= 21:
                dealer_play(deck, dealer_hand)

            winner = decide_winner(player_hand, dealer_hand)
            if winner == "player":
                score += bet * 2
                result_text = f"YOU WIN {bet * 2}"
            elif winner == "push":
                score += bet
                result_text = "PUSH"
            elif hand_value(player_hand) > 21:
                result_text = "BUST"
            else:
                result_text = "DEALER WINS"
            state = "result"

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_blackjack(100)
    pygame.quit()
