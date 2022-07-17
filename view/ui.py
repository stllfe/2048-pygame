import abc
import math
from re import X
import time
from typing import List

import pygame
from copy import copy
from view import utils, theme

from collections import OrderedDict
from pygame.rect import Rect

from model.grid import Grid, Position, Tile
from common.events import CPUTickEvent, GameReadyEvent, GridUpdateEvent, ScoreUpdateEvent, GameOverEvent
from common.mediator import Listener


class UITile:

    def __init__(
        self,
        value: int,
        size: int, 
        origin: Position,
        target: Position = None,
    ):   
        self.value = value 
        self.rect = Rect(origin.x, origin.y, size, size)
        self.target = target
        self.position = copy(origin)

        if self.target:
            angle = math.atan2(self.target.y - self.position.y, self.target.x - self.position.x)
            self.dx = math.cos(angle)
            self.dy = math.sin(angle)

    def move(self, delta: float, speed: float):
        if not self.target:
            return

        # todo: add stop check

        self.position.x += self.dx * speed * delta
        self.position.y += self.dy * speed * delta

        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)

    def render(self, surface: pygame.Surface):
        pygame.draw.rect(surface, theme.TILE_COLOR_BASE, self.rect, border_radius=4)
        text = theme.H2_FONT.render(str(self.value), True, theme.COLOR_DARK)
        text_x = self.rect.left + (self.rect.width - text.get_width()) // 2
        text_y = self.rect.top + (self.rect.height - text.get_height()) // 2
        surface.blit(text, (text_x, text_y))


class UI(Listener):

    def __init__(self, width: int, height: int):
        pygame.font.init()

        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((self.width, self.height))

        self._curr_grid = None
        self._curr_score = 0
        self._curr_best = 0

        self._last_frame_time = time.time()
        self._frame_delta = 0

        self._tiles_velocity = 2000
        self._tiles = list()

        self._grid_rect = None
        self._grid_rows = None
        self._grid_cols = None
        self._tile_size = None
        self._tiles_cache = None

        self._grid_spacing = 15
        self._padding = 40

        # The main padded area inside the window
        self._container = Rect(self._padding, self._padding, self.width - self._padding * 2, self.height - self._padding * 2)

        self._title_text = "2048"
        self._score_text = "SCORE"
        self._best_text = "BEST"
        self._caption_text = "Join the numbers and get to the 2048 tile!"
        self._how_to_texts = OrderedDict(move=['arrows', 'W, A, S, D'], restart=['R'], quit=['Q', 'ESC'])

        self._draw_background()
        self._drawable = True
        pygame.display.set_caption("2048 Game by Oleg Pavlovich")

    def _draw_background(self):
        self.window.fill(theme.BACKGROUND)
        self._header = self._setup_header()
        self._footer = self._setup_footer()
        # pygame.display.update()

    def _update_frame_delta(self) -> float:
        now = time.time()
        self._frame_delta = now - self._last_frame_time
        self._last_frame_time = now

    def _reset_background(self):
        self.window.fill(theme.BACKGROUND)
        self._setup_header()
        self._setup_footer()

    def _setup_grid(self, grid: Grid) -> Rect:
        assert self._header
        assert self._footer

        # Calculate grid size and draw it
        margin = 40
        reserved = self._header.height + self._footer.height + 2 * margin

        min_side = min(self._container.width, self._container.height - reserved)
        scale_factor = min_side / max(grid.width, grid.height)
        grid_height = grid.height * scale_factor
        grid_width = grid.width * scale_factor
        grid_size = (grid_width, grid_height)

        # Save computed values and instances
        self._grid_rows = grid.height
        self._grid_cols = grid.width
        self._grid_rect = Rect((self._container.centerx - grid_width / 2, self._header.bottom + margin), grid_size)

        self._tile_size = (self._grid_rect.width - self._grid_spacing * (self._grid_cols + 1)) / self._grid_cols
        return self._grid_rect

    def _setup_header(self) -> Rect:
        # Draw title
        title = Rect((self._container.left, self._container.top), theme.H1_FONT.size(self._title_text))
        utils.draw_text(self.window, self._title_text, theme.COLOR_DARK, title, theme.H1_FONT, True)

        # Draw caption
        margin = 15
        caption = Rect((self._container.left, title.bottom + margin), theme.BASE_FONT.size(self._caption_text))
        utils.draw_text(self.window, self._caption_text, theme.COLOR_DARK, caption, theme.BASE_FONT, True)

        self._header = Rect(self._container.topleft, (self._container.width, caption.height + title.height + margin))
        # pygame.display.update()
        return self._header

    def _setup_footer(self) -> Rect:
        # Draw tips from bottom to top
        margin_top = 5
        margin_right = 6
        tips = reversed(self._how_to_texts.keys())

        tip_h = theme.BOLD_FONT.size("Tg")[1]
        tip_x = self._container.left
        tip_y = self._container.bottom - tip_h

        for tip in tips:
            label = f"{tip.title()}"
            label_font = theme.BOLD_FONT
            label_size = label_font.size(label)
            label_rect = Rect((tip_x, tip_y), label_size)

            options = "with " + " or ".join(self._how_to_texts[tip])
            options_font = theme.BASE_FONT
            options_size = options_font.size(options)
            options_rect = Rect((label_rect.right + margin_right, label_rect.y), options_size)

            utils.draw_text(self.window, label, theme.COLOR_DARK, label_rect, label_font, True)
            utils.draw_text(self.window, options, theme.COLOR_DARK, options_rect, options_font, True)

            height = label_rect.height + margin_top
            tip_y = label_rect.top - height

        # pygame.display.update()
        total_height = tip_h * len(self._how_to_texts.keys())
        self._footer = Rect(self._container.left, self._container.bottom - total_height,
                            self._container.width, total_height)

        return self._footer

    def _draw_scores(self):
        score_margin = 10
        score_side = (self._container.width // 2 - score_margin * 2) / 2
        scale_factor = (self._header.height // 2) / score_side
        score_side *= scale_factor

        score_y = (self._header.centery - score_side / 2) - 15  # purely visual offset
        score_x = self._container.right - score_margin - 2 * score_side

        for label, value in zip((self._score_text, self._best_text), (self._curr_score, self._curr_best)):
            value = str(value)

            label_size = theme.LABEL_FONT.size(label)
            value_size = theme.VALUE_FONT.size(value)

            bg_rect = Rect(score_x, score_y, score_side, score_side)
            label_rect = Rect((bg_rect.centerx - label_size[0] / 2, bg_rect.top + 6), label_size)
            value_rect = Rect((bg_rect.centerx - value_size[0] / 2, label_rect.bottom), value_size)

            utils.draw_rounded_rect(self.window, theme.GRID_COLOR, bg_rect, border_radius=4)
            utils.draw_text(self.window, label, theme.COLOR_LIGHT, label_rect, theme.LABEL_FONT, True)
            utils.draw_text(self.window, value, theme.COLOR_WHITE, value_rect, theme.VALUE_FONT, True)

            # Set next block's x-coordinate
            score_x = bg_rect.right + score_margin

        pygame.display.update()

    def _draw_grid(self):
        utils.draw_rounded_rect(self.window, theme.GRID_COLOR, self._grid_rect, border_radius=8)

        cell_x, cell_y = self._grid_rect.topleft
        for _ in range(self._grid_rows):
            cell_x = self._grid_rect.left
            
            for _ in range(self._grid_cols):
                rect = Rect(cell_x + self._grid_spacing, cell_y + self._grid_spacing, self._tile_size, self._tile_size)
                utils.draw_rounded_rect(self.window, theme.CELL_COLOR, rect, 4)
                cell_x = rect.right

            cell_y = rect.bottom

    def _update_grid(self, grid: Grid):
        self._curr_grid = grid

    def _update_scores(self, score: int, best: int):
        self._curr_score = score
        self._curr_best = best

    def render(self):
        self._draw_background()
        self._draw_grid()
        self._draw_tiles()
        self._draw_scores()


    def _update_tiles(self, tiles: List[Tile]):

        def to_ui(tile: Tile):
            if tile.previous_position:
                origin = self._get_pixel_tile_position(tile.previous_position)
                target = self._get_pixel_tile_position(tile.position)
            else:
                origin = self._get_pixel_tile_position(tile.position)
                target = None
            
            return UITile(tile.value, self._tile_size, origin, target)

        # def rm_ui_for(tile: Tile):
        #     del self._tiles[tile]

        self._tiles = list(map(to_ui, tiles))
        # for tile in tiles:
        #     if tile not in self._tiles:
        #         add_ui_for(tile)
        #         for parent in tile.merged_from:
        #             if parent in self._tiles:
        #                 rm_ui_for(parent)
  
    def _get_pixel_tile_position(self, pos: Position) -> Position:
        origin_x, origin_y = self._grid_rect.topleft
        abs_x = self._grid_spacing + origin_x + (self._tile_size + self._grid_spacing) * pos.x
        abs_y = self._grid_spacing + origin_y + (self._tile_size + self._grid_spacing) * pos.y
        return Position(abs_x, abs_y)

    def _draw_tiles(self):
        for elem in self._tiles:
            elem.move(self._frame_delta, self._tiles_velocity)
            elem.render(self.window)
        
        # pygame.display.update()

    def _draw_message(self, text: str, overlay: bool = True):
        message_rect = self._header.copy()
        message_rect.y = message_rect.height * 2

        if overlay:
            alpha = 235
            color = theme.BACKGROUND
            color = color.r, color.g, color.b, alpha
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            surf.fill(color)
            self.window.blit(surf, (0, 0))
        else:
            self.window.fill(theme.BACKGROUND)

        utils.draw_text(self.window, text, theme.COLOR_DARK, message_rect, theme.H3_FONT, True)
        # pygame.display.update()

    def notify(self, event):
        if isinstance(event, GameReadyEvent):

            # Game was restarted with this flag
            if not self._drawable:
                self._reset_background()
                self._drawable = True

            self._setup_grid(event.grid)
            self._update_grid(event.grid)
            self._update_tiles(event.grid.tiles)
            self._update_scores(event.score, event.best)

        # If the game has ended this flag is raised
        if not self._drawable:
            return

        if isinstance(event, CPUTickEvent):
            self._update_frame_delta()
            self.render()

        if isinstance(event, GridUpdateEvent):
            self._update_grid(event.grid)
            self._update_tiles(event.grid.tiles)

        if isinstance(event, ScoreUpdateEvent):
            self._update_scores(score=event.score, best=event.best)

        # better add a state pattern to simplify this flag logic
        if isinstance(event, GameOverEvent):
            self._update_scores(score=event.score, best=event.best)
            self.render()
            self._draw_message(f"Game over! Score {event.score}.\nPress r to restart or q to quit :)")
            self._drawable = False

        pygame.display.update()