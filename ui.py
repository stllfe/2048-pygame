import pygame
import theme
import utils

from pygame.rect import Rect
from pygame.font import Font

from grid import Grid, Position
from events import GridReadyEvent, GridUpdateEvent
from mediator import Listener


class UserInterface(Listener):

    def __init__(self, width: int, height: int):
        pygame.font.init()

        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((self.width, self.height))

        self.grid_rect = None
        self.grid_rows = None
        self.grid_cols = None

        self.grid_spacing = 15
        self.inner_padding = 40
        self.font_size = 16

        self.title_font = Font('./assets/font/ClearSans-Bold.ttf', self._rem_to_px(5))
        self.tile_font = Font('./assets/font/ClearSans-Medium.ttf', self._rem_to_px(3))
        self.title = self.title_font.render("2048", True, theme.FONT_COLOR_DARK)

        pygame.display.set_caption("2048 game by Oleg Pavlovich")
        pygame.display.update()

    def _clear_window(self):
        self.window.fill(theme.BACKGROUND)
        self.window.blit(self.title, (40, 20))
        pygame.display.flip()

    def _rem_to_px(self, rem: float):
        return rem * self.font_size

    def _set_grid_info(self, grid: Grid):
        min_window_side = min(self.width - self.inner_padding * 2, self.height - self.inner_padding * 2)
        scale_factor = min_window_side / max(grid.width, grid.height)

        grid_height = grid.height * scale_factor
        grid_width = grid.width * scale_factor

        grid_x = (self.width - grid_width) // 2
        grid_y = (self.height - grid_height) // 2

        self.grid_rect = Rect(grid_x, grid_y, grid_width, grid_height)
        self.grid_rows = grid.height
        self.grid_cols = grid.width

    def _draw_grid(self, grid: Grid):
        tile_side = (self.grid_rect.width - self.grid_spacing * (self.grid_cols + 1)) / self.grid_cols

        utils.draw_rounded_rect(self.window, theme.GRID_COLOR, self.grid_rect, border_radius=8)

        x, y = self.grid_rect.topleft
        for i in range(self.grid_rows):

            cell = None
            x = self.grid_rect.left

            for j in range(self.grid_cols):
                color = theme.CELL_COLOR
                text = None
                tile = grid.get_cell(Position(j, i))
                cell = Rect(x + self.grid_spacing, y + self.grid_spacing, tile_side, tile_side)

                if tile:
                    color = theme.TILE_COLOR_BASE
                    text = self.tile_font.render(str(tile.value), True, theme.FONT_COLOR_DARK)

                utils.draw_rounded_rect(self.window, color, cell, 4)

                if text:
                    text_x = cell.left + (cell.width - text.get_width()) // 2
                    text_y = cell.top + (cell.height - text.get_height()) // 2
                    self.window.blit(text, (text_x, text_y))

                x = cell.right

            y = cell.bottom

        pygame.display.update()

    def notify(self, event):
        if isinstance(event, GridReadyEvent):
            self._clear_window()
            self._set_grid_info(event.grid)
            self._draw_grid(event.grid)
        if isinstance(event, GridUpdateEvent):
            self._draw_grid(event.grid)
