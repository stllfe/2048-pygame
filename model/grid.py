import random

from enum import Enum
from typing import List, Optional, Iterable


class Position:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y

        return False


class Direction(Enum):

    LEFT = Position(-1, 0)
    RIGHT = Position(1, 0)
    UP = Position(0, -1)
    DOWN = Position(0, 1)


class Tile:

    def __init__(self, position: Position, value: int):
        self._position = position
        self._value = value

        # Handy attributes for UI entities and debugging
        self._previous_position = None
        self._merged_from = tuple()

    @property
    def value(self):
        return self._value

    @property
    def x(self):
        return self._position.x

    @property
    def y(self):
        return self._position.y

    @property
    def merged_from(self):
        return self._merged_from

    @property
    def previous_position(self):
        return self._previous_position

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, other: Position):
        self._set_position(other)

    @merged_from.setter
    def merged_from(self, tiles: Iterable):
        self._set_merged_from(tiles)

    def save_position(self):
        # Backup position
        self._previous_position = self._position

    def _set_position(self, other: Position):
        self._position = other

    def _set_merged_from(self, tiles: Iterable):

        if not tiles:
            tiles = tuple()

        for tile in tiles:
            if not isinstance(tile, Tile):
                raise TypeError("Tile can only be merged from other tiles. "
                                f"Got `{type(tile)}` instead.")

        self._merged_from = tuple(tiles)


class Grid:

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._cells = None

        self.empty()

    def __str__(self):
        s = ''
        for row in self._cells:
            for tile in row:
                s += '[{}]'.format(tile.value if tile else ' ')
            s += '\n'
        return s

    @property
    def cells(self) -> List[List]:
        return self._cells

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def empty(self) -> None:
        """
        Builds the grid and fills it with empty cells.

        :return: None
        """

        self._cells = [[None for _ in range(self._width)]
                       for _ in range(self._height)]

    def insert_tile(self, tile: Tile) -> bool:
        """
        Inserts new ``Tile`` in the grid according to its ``position`` attribute.

        :return: bool True if inserted, False otherwise
        """

        if not self.is_within(tile.position) or not tile:
            return False

        self._cells[tile.y][tile.x] = tile
        return True

    def remove_tile(self, tile: Tile) -> bool:
        """
        Removes ``Tile`` from the grid according to its ``position`` attribute.
        If no ``Tile`` found at this position returns ``False``.

        :return: bool True if removed, False otherwise
        """

        if not self.is_within(tile.position) or self.is_cell_empty(tile.position):
            return False

        self._cells[tile.y][tile.x] = None
        return True

    @property
    def tiles(self) -> List[Tile]:
        """
        Returns list of ``Tile`` objects found in the grid.

        :return: list of tiles
        """

        tiles = list()

        for y, row in enumerate(self._cells):
            for x, tile in enumerate(row):
                if tile:
                    tiles.append(tile)

        return tiles

    def get_cell(self, position: Position) -> Optional[Tile]:
        if self.is_within(position):
            return self._cells[position.y][position.x]

    def is_cell_filled(self, position: Position) -> bool:
        return not self.is_cell_empty(position)

    def is_cell_empty(self, position: Position) -> bool:
        return not self._cells[position.y][position.x]

    def is_within(self, position: Position) -> bool:
        return (0 <= position.y < self._height and
                0 <= position.x < self._width)

    def has_available_cells(self) -> bool:
        return self.get_empty_cell() is not None

    def get_empty_cell(self) -> Optional[Position]:
        """
        Get next empty cell in the grid.

        :return: tuple (x, y) of a randomly chosen empty cell
                 None if there are no empty cells
        """

        empty_tiles = list()

        for y, row in enumerate(self._cells):
            for x, tile in enumerate(row):
                if not tile:
                    empty_tiles.append(Position(x, y))

        if empty_tiles:
            return random.choice(empty_tiles)
