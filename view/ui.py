import pygame
from view import utils, theme

from collections import OrderedDict
from pygame.rect import Rect
from pygame.font import Font

from model.grid import Grid, Position
from common.events import GameReadyEvent, GridUpdateEvent, ScoreUpdateEvent, GameOverEvent
from common.mediator import Listener


class UserInterface(Listener):

    def __init__(self, width: int, height: int):
        pygame.font.init()

        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((self.width, self.height))

        self._grid_rect = None
        self._grid_rows = None
        self._grid_cols = None
        self._tile_side = None
        self._tiles_cache = None

        self._grid_spacing = 15
        self._padding = 40

        # The main padded area inside the window
        self._container = Rect(self._padding, self._padding,
                               self.width - self._padding * 2,
                               self.height - self._padding * 2)

        self._title = "2048"
        self._score = "SCORE"
        self._best = "BEST"
        self._caption = "Join the numbers and get to the 2048 tile!"
        self._how_to = OrderedDict(move=['arrows', 'W, A, S, D'], restart=['R'], quit=['Q', 'ESC'])

        self.window.fill(theme.BACKGROUND)

        self._header = self._setup_header()
        self._footer = self._setup_footer()

        self._drawable = True
        pygame.display.set_caption("2048 Game by Oleg Pavlovich")
        pygame.display.update()

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

        self._tile_side = (self._grid_rect.width - self._grid_spacing * (self._grid_cols + 1)) / self._grid_cols
        return self._grid_rect

    def _setup_header(self) -> Rect:
        # Draw title
        title = Rect((self._container.left, self._container.top), theme.H1_FONT.size(self._title))
        utils.draw_text(self.window, self._title, theme.COLOR_DARK, title, theme.H1_FONT, True)

        # Draw caption
        margin = 15
        caption = Rect((self._container.left, title.bottom + margin), theme.BASE_FONT.size(self._caption))
        utils.draw_text(self.window, self._caption, theme.COLOR_DARK, caption, theme.BASE_FONT, True)

        self._header = Rect(self._container.topleft, (self._container.width, caption.height + title.height + margin))
        pygame.display.update()
        return self._header

    def _setup_footer(self) -> Rect:
        # Draw tips from bottom to top
        margin_top = 5
        margin_right = 6
        tips = reversed(self._how_to.keys())

        tip_h = theme.BOLD_FONT.size("Tg")[1]
        tip_x = self._container.left
        tip_y = self._container.bottom - tip_h

        for tip in tips:
            label = f"{tip.title()}"
            label_font = theme.BOLD_FONT
            label_size = label_font.size(label)
            label_rect = Rect((tip_x, tip_y), label_size)

            options = "with " + " or ".join(self._how_to[tip])
            options_font = theme.BASE_FONT
            options_size = options_font.size(options)
            options_rect = Rect((label_rect.right + margin_right, label_rect.y), options_size)

            utils.draw_text(self.window, label, theme.COLOR_DARK, label_rect, label_font, True)
            utils.draw_text(self.window, options, theme.COLOR_DARK, options_rect, options_font, True)

            height = label_rect.height + margin_top
            tip_y = label_rect.top - height

        pygame.display.update()
        total_height = tip_h * len(self._how_to.keys())
        self._footer = Rect(self._container.left, self._container.bottom - total_height,
                            self._container.width, total_height)

        return self._footer

    def _draw_scores(self, score: int = 0, best: int = 0):
        score_margin = 10

        score_side = (self._container.width // 2 - score_margin * 2) / 2
        scale_factor = (self._header.height // 2) / score_side
        score_side *= scale_factor

        score_y = (self._header.centery - score_side / 2) - 15  # purely visual offset
        score_x = self._container.right - score_margin - 2 * score_side

        for label, value in zip((self._score, self._best), (score, best)):
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

    def _draw_tiles(self, grid: Grid):
        if not self._grid_rect:
            self._setup_grid(grid)

        utils.draw_rounded_rect(self.window, theme.GRID_COLOR, self._grid_rect, border_radius=8)

        x, y = self._grid_rect.topleft
        for i in range(self._grid_rows):
            rect = None
            x = self._grid_rect.left

            for j in range(self._grid_cols):
                color = theme.CELL_COLOR
                tile = grid.get_cell(Position(j, i))
                text = None
                rect = Rect(x + self._grid_spacing, y + self._grid_spacing, self._tile_side, self._tile_side)

                if tile:
                    color = theme.TILE_COLOR_BASE
                    text = theme.H2_FONT.render(str(tile.value), True, theme.COLOR_DARK)

                utils.draw_rounded_rect(self.window, color, rect, 4)

                if text:
                    text_x = rect.left + (rect.width - text.get_width()) // 2
                    text_y = rect.top + (rect.height - text.get_height()) // 2
                    self.window.blit(text, (text_x, text_y))

                x = rect.right

            y = rect.bottom

        pygame.display.update()

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
        pygame.display.update()

    def notify(self, event):
        if isinstance(event, GameReadyEvent):

            # Game was restarted with this flag
            if not self._drawable:
                self._reset_background()
                self._drawable = True

            self._setup_grid(event.grid)
            self._draw_tiles(event.grid)
            self._draw_scores(score=event.score, best=event.best)

        # If the game has ended this flag is raised
        if not self._drawable:
            return

        if isinstance(event, GridUpdateEvent):
            self._draw_tiles(event.grid)

        if isinstance(event, ScoreUpdateEvent):
            self._draw_scores(score=event.score, best=event.best)

        if isinstance(event, GameOverEvent):
            self._draw_scores(score=event.score, best=event.best)
            self._draw_message(f"Game over! Score {event.score}.\nPress r to restart or q to quit :)")
            self._drawable = False

