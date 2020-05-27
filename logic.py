import random

from argparse import Namespace
from itertools import product
from typing import Optional

from grid import (
    Direction,
    Position,
    Grid,
    Tile,
)


def _next_position(position: Position, direction: Direction):
    x = position.x + direction.value.x
    y = position.y + direction.value.y
    return Position(x, y)


class Logic:

    def __init__(self, params: Namespace):
        self.grid = Grid(width=params.width, height=params.height)
        self.start_tiles = params.start_tiles
        self.win_score = params.win_score
        self.score = 0
        self.setup()

    def random_tile(self):
        if self.grid.has_available_cells():
            value = 4 if random.random() < 0.1 else 2
            return Tile(self.grid.get_empty_cell(), value)

    def setup(self):
        self.grid.empty()
        for _ in range(self.start_tiles):
            if not self.insert_random_tile():
                return

    def insert_random_tile(self):
        tile = self.random_tile()
        # todo: add a docstring
        if tile:
            self.grid.insert_tile(tile)
            return True
        return False

    def right(self):
        self._move(Direction.RIGHT)

    def left(self):
        self._move(Direction.LEFT)

    def down(self):
        self._move(Direction.DOWN)

    def up(self):
        self._move(Direction.UP)

    def _next_merge(self, tile: Tile, direction: Direction) -> Optional[Tile]:
        position = _next_position(tile.position, direction)

        if self.grid.is_within(position) and self.grid.is_cell_filled(position):
            candidate = self.grid.get_cell(position)
            if candidate.value == tile.value and not candidate.merged_from:
                return candidate

    def _is_merge_available(self, tile: Tile, direction: Direction) -> bool:
        return self._next_merge(tile, direction) is not None

    def _farthest_position(self, tile: Tile, direction: Direction) -> Position:
        # todo: update docstring
        """
        Returns the farthest position before an obstacle.
        :param direction:
        :return:
        """

        current = tile.position
        position = _next_position(current, direction)

        while self.grid.is_within(position):
            if self.grid.is_cell_filled(position):
                break
            current = position
            position = _next_position(current, direction)

        return current

    def _move_tile(self, tile: Tile, position: Position):
        self.grid.remove_tile(tile)
        tile.position = position
        self.grid.insert_tile(tile)

    def _clean_metadata(self):
        for tile in self.grid.tiles:
            tile.merged_from = None

    def _merge_tiles(self, a, b):
        merged = Tile(b.position, a.value * 2)
        merged.merged_from = [a, b]

        self._move_tile(merged, b.position)
        self.grid.remove_tile(a)
        return merged

    def _traversals(self, direction: Direction):
        xs = list(range(self.grid.width))
        ys = list(range(self.grid.height))

        if direction.value.x == 1:
            xs.reverse()

        if direction.value.y == 1:
            ys.reverse()

        for x, y in product(xs, ys):
            yield Position(x, y)

    def _move(self, direction: Direction):
        self._clean_metadata()

        for position in self._traversals(direction):
            tile = self.grid.get_cell(position)

            if not tile:
                continue

            self._move_tile(tile, self._farthest_position(tile, direction))

            if self._is_merge_available(tile, direction):
                closest = self._next_merge(tile, direction)
                merged = self._merge_tiles(tile, closest)
                self.score += merged.value

            if self.score == self.win_score:
                pass

        self.insert_random_tile()
