import random

from itertools import product
from argparse import Namespace
from typing import Optional, Iterator

from model.grid import (
    Direction,
    Position,
    Grid,
    Tile,
)


def _next_position(position: Position, direction: Direction) -> Position:
    x = position.x + direction.value.x
    y = position.y + direction.value.y
    return Position(x, y)


class LogicState:

    def __init__(self, grid: Grid, params: Namespace, merged_total: int):
        self.grid = grid
        self.merged_total = merged_total
        self.params = params


class Logic:

    def __init__(self, params: Namespace):
        self._grid = Grid(width=params.width, height=params.height)
        self._start_tiles = params.start_tiles
        self._merged_total = 0
        self._params = params

    @property
    def grid(self) -> Grid:
        return self._grid

    @property
    def start_tiles(self) -> int:
        return self._start_tiles

    @property
    def merged_total(self) -> int:
        return self._merged_total

    def random_tile(self) -> Optional[Tile]:
        """Produce a new ``Tile`` with random value and position.

        If there are no empty cells in the grid returns ``None``.

        :return: Tile object or None if no available cells found.
        """

        if self._grid.has_available_cells():
            value = 4 if random.random() < 0.1 else 2
            return Tile(self._grid.get_empty_cell(), value)

    def save_state(self) -> LogicState:
        return LogicState(grid=self._grid, params=self._params, merged_total=self.merged_total)

    def load_state(self, state: LogicState):
        class InvalidStateException(Exception):
            pass
        try:
            self._start_tiles = state.params.start_tiles
            self._merged_total = state.merged_total
            self._params = state.params
            self._grid = state.grid
        except AttributeError as e:
            raise InvalidStateException(f"Logic state is corrupted! {e}")

    def setup(self) -> bool:
        """Clears the grid and inserts ``start_tiles`` number of tiles.

        :return: bool False if couldn't insert the number of tiles given,
                 True otherwise
        """
        self._merged_total = 0
        self._grid.empty()
        for _ in range(self._start_tiles):
            if not self.insert_random_tile():
                return False
        return True

    def insert_random_tile(self):
        # todo: add a docstring
        tile = self.random_tile()
        if tile:
            self._grid.insert_tile(tile)
            return True
        return False

    def moves_available(self):
        """Pretty expensive check"""

        for direction in Direction:
            for tile in self._grid.tiles:

                if self._farthest_position(tile, direction) != tile.position:
                    return True

                if self._is_merge_available(tile, direction):
                    return True

        return False

    def move(self, direction: Direction):
        """Moves all the tiles in the given direction and merges them if needed.

        :param direction:
        :return: None
        """

        # Remove tiles metadata from the previous move
        self._clean_tiles_metadata()

        for position in self._traversals(direction):
            tile = self._grid.get_cell(position)

            if not tile:
                continue

            # Move the tile to the farthest empty position before the first obstacle
            self._move_tile(tile, self._farthest_position(tile, direction))

            # If the nearest obstacle in that direction is a tile
            # check for merge and merge if possible
            if self._is_merge_available(tile, direction):
                closest = self._next_merge(tile, direction)
                merged = self._merge_tiles(tile, closest)
                self._merged_total += merged.value

        self.insert_random_tile()

    def _next_merge(self, tile: Tile, direction: Direction) -> Optional[Tile]:
        # TODO: add a docstring

        position = _next_position(tile.position, direction)

        if self._grid.is_within(position) and self._grid.is_cell_filled(position):
            candidate = self._grid.get_cell(position)
            if candidate.value == tile.value and not candidate.merged_from:
                return candidate

    def _is_merge_available(self, tile: Tile, direction: Direction) -> bool:
        return self._next_merge(tile, direction) is not None

    def _farthest_position(self, tile: Tile, direction: Direction) -> Position:
        """Returns ``Position`` object of the farthest position before the first obstacle.

        :param direction: direction towards the destination position
        :return: Position object
        """

        current = tile.position
        position = _next_position(current, direction)

        while self._grid.is_within(position) and self._grid.is_cell_empty(position):
            current = position
            position = _next_position(current, direction)

        return current

    def _move_tile(self, tile: Tile, position: Position):
        self._grid.remove_tile(tile)

        tile.save_position()
        tile.position = position
        self._grid.insert_tile(tile)

    def _clean_tiles_metadata(self):
        for tile in self._grid.tiles:
            tile.merged_from = None

    def _merge_tiles(self, a: Tile, b: Tile):
        """Replaces tiles in the grid with a new ``Tile`` object at `b`'s position.

        The merged tile's value is a sum of `a` and `b` values.

        :param a: first Tile
        :param b: second Tile
        :return: new Tile object
        """

        merged = Tile(b.position, a.value + b.value)
        merged.merged_from = [a, b]

        self._grid.remove_tile(a)
        self._grid.insert_tile(merged)

        return merged

    def _traversals(self, direction: Direction) -> Iterator[Position]:
        """Get positions to travers in the given direction.

        Positions are sorted in the bottommost or rightmost
        order for vertical or horizontal directions accordingly.

        :param direction: the direction to travers
        :return: iterator that yields Position objects
                 representing nodes to travers in the given direction.

        """

        xs = list(range(self._grid.width))
        ys = list(range(self._grid.height))

        if direction.value.x == 1:
            xs.reverse()

        if direction.value.y == 1:
            ys.reverse()

        for x, y in product(xs, ys):
            yield Position(x, y)
