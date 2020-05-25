import random
from enum import Enum


class Direction(Enum):
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP = (0, -1)
    DOWN = (0, 1)


class Grid:

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._grid = None

        self.clear()
        self.add_tile()

    def __str__(self):
        s = ''
        for row in self._grid:
            for t in row:
                s += '[{}]'.format(t if t else ' ')
            s += '\n'
        return s

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def clear(self):
        """
        Fill the entire grid with empty slots.
        :return: None
        """
        self._grid = [[0 for _ in range(self._width)]
                      for _ in range(self._height)]

    def merge_up(self):
        self._merge(Direction.UP)

    def merge_down(self):
        self._merge(Direction.DOWN)

    def merge_left(self):
        self._merge(Direction.LEFT)

    def merge_right(self):
        self._merge(Direction.RIGHT)

    def add_tile(self):
        """
        Insert new tile if there is an empty slot.
        :return: bool True if inserted, False otherwise
        """
        next_val = self._get_next_value()
        next_pos = self._get_next_empty()

        if next_pos:
            x, y = next_pos
            self._grid[y][x] = next_val
            return True

        return False

    @staticmethod
    def _get_next_value():
        """
        Get next random value for a new tile.
        :return: int 2 or 4
        """
        return random.choice([2, 4])

    def _get_next_empty(self):
        """
        Get next empty slot in the grid.
        :return: tuple (x, y) of a randomly chosen empty position
                 bool False if there are no empty slots
        """
        empty_tiles = list()

        for y, row in enumerate(self._grid):
            for x, tile in enumerate(row):
                if tile == 0:
                    empty_tiles.append((x, y))

        if empty_tiles:
            return random.choice(empty_tiles)

        return False

    def _merge_up(self, x, y, value):
        if y == 0:
            return False

        for ty in range(y - 1, -1, -1):
            if self._grid[ty][x] not in (0, value):
                return False

            self._grid[y][x] = 0
            self._grid[ty][x] += value
            y = ty

        return True

    def _merge_down(self, x, y, value):
        if y == self._height - 1:
            return False

        for dy in range(y + 1, self._height):
            if self._grid[dy][x] not in (0, value):
                return False

            self._grid[y][x] = 0
            self._grid[dy][x] += value
            y = dy

        return True

    def _merge_left(self, x, y, value):
        if x == 0:
            return False

        for lx in range(x - 1, -1, -1):
            if self._grid[y][lx] not in (0, value):
                return False

            self._grid[y][x] = 0
            self._grid[y][lx] += value
            x = lx

        return True

    def _merge_right(self, x, y, value):
        if x == self._width - 1:
            return False

        for rx in range(x + 1, self._width):
            if self._grid[y][rx] not in (0, value):
                return False

            self._grid[y][x] = 0
            self._grid[y][rx] += value
            x = rx

        return True

    def _merge(self, direction: Direction):
        merge_func = None

        if direction is Direction.LEFT:
            merge_func = self._merge_left
        elif direction is Direction.RIGHT:
            merge_func = self._merge_right
        elif direction is Direction.UP:
            merge_func = self._merge_up
        elif direction is Direction.DOWN:
            merge_func = self._merge_down
        else:
            raise TypeError(f"Expected type `{Direction}`, "
                            f"got {type(direction)} instead.")

        for y, row in enumerate(self._grid):
            for x, value in enumerate(row):
                if value:
                    merge_func(x, y, value)
