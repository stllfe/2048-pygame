import pygame.font
from pygame.font import Font
from pygame import Color


pygame.font.init()

FONT_SIZE = 24
FONT_STYLE_REGULAR = "./assets/font/ClearSans-Regular.ttf"
FONT_STYLE_BOLD = "./assets/font/ClearSans-Bold.ttf"
FONT_STYLE_MEDIUM = "./assets/font/ClearSans-Medium.ttf"


def _rem_to_px(rem: float):
    return round(rem * FONT_SIZE)


H1_FONT = Font(FONT_STYLE_BOLD, _rem_to_px(3.6))
H2_FONT = Font(FONT_STYLE_BOLD, _rem_to_px(2.4))
H3_FONT = Font(FONT_STYLE_BOLD, _rem_to_px(1.6))

BASE_FONT = Font(FONT_STYLE_REGULAR, _rem_to_px(1))
BOLD_FONT = Font(FONT_STYLE_BOLD, _rem_to_px(1))
MEDIUM_FONT = Font(FONT_STYLE_MEDIUM, _rem_to_px(1))

LABEL_FONT = Font(FONT_STYLE_BOLD, _rem_to_px(0.74))
VALUE_FONT = Font(FONT_STYLE_BOLD, _rem_to_px(1.2))

BACKGROUND = Color("#faf8ef")
CELL_COLOR = Color("#cdc1b4")
GRID_COLOR = Color("#bbada0")

TILE_COLOR_BASE = Color("#eee4da")
TILE_COLOR_GOLD = Color("#edc22e")
TILE_COLOR_GLOW = Color("#edc22e")  # not really

TILE_COLOR_04 = Color("#f78e48")
TILE_COLOR_08 = Color("#f2b179")
TILE_COLOR_16 = Color("#fc5e2e")
TILE_COLOR_32 = Color("#ff3333")
TILE_COLOR_64 = Color("#ff0000")

COLOR_DARK = Color("#776e65")
COLOR_LIGHT = Color("#eee4da")
COLOR_WHITE = Color("white")

BUTTON_COLOR = Color("#8f7a66")
