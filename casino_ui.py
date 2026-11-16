import pygame
from settings import *

pygame.init()

# Společné kreslení pro všechny casino hry

button_font = pygame.font.SysFont("segoeui", 24, bold=True)
info_font = pygame.font.SysFont("segoeui", 22, bold=True)
big_font = pygame.font.SysFont("segoeui", 40, bold=True)

TABLE_GREEN = (20, 90, 50)
GOLD = (230, 190, 60)
RED = (200, 40, 40)


def draw_button(rect, text, mouse_pos, enabled=True):
    hovered = rect.collidepoint(mouse_pos) and enabled
    shadow_offset = 2 if hovered else 4
    color = theme["button"] if enabled else (90, 90, 100)

    pygame.draw.rect(screen, SHADOW, rect.move(0, shadow_offset), border_radius=12)
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=12)

    label = button_font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))


def draw_text(text, center, color=WHITE, font=info_font):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))


def draw_balance(score, bet):
    draw_text(f"Chips: {score}", (90, 25), GOLD)
    draw_text(f"Bet: {bet}", (510, 25), WHITE)


# Tlačítka pro změnu sázky (stejná ve všech hrách)
BET_MINUS_RECT = pygame.Rect(0, 0, 40, 40)
BET_MINUS_RECT.center = (420, 25)
BET_PLUS_RECT = pygame.Rect(0, 0, 40, 40)
BET_PLUS_RECT.center = (580, 25)
BET_STEP = 5


def draw_bet_buttons(mouse_pos, enabled=True):
    draw_button(BET_MINUS_RECT, "-", mouse_pos, enabled)
    draw_button(BET_PLUS_RECT, "+", mouse_pos, enabled)
