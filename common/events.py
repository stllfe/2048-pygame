from model.grid import Direction, Grid, Tile


class Event:
    """Base class for all events.

    Holds a message and event-specific attributes.
    """

    def __init__(self, message):
        self.message = message


class QuitEvent(Event):

    def __init__(self):
        super().__init__("Quit game event")


class UserMoveEvent(Event):

    def __init__(self, direction: Direction):
        super().__init__("User move request event")
        self.direction = direction


class UserRestartEvent(Event):

    def __init__(self):
        super().__init__("User restart request event")


class CPUTickEvent(Event):

    def __init__(self, ticks: int = 0):
        super().__init__("CPU frame update event")
        self.ticks = ticks


class GameReadyEvent(Event):

    def __init__(self, grid: Grid, score: int, best: int):
        super().__init__("Game object has initialized")
        self.grid = grid
        self.score = score
        self.best = best


class TilesMergeEvent(Event):

    def __init__(self, tile: Tile):
        super().__init__("Two tiles have merged")
        self.tile = tile


class GridUpdateEvent(Event):

    def __init__(self, grid: Grid):
        super().__init__("Grid object have been updated")
        self.grid = grid


class ScoreUpdateEvent(Event):

    def __init__(self, score: int, best: int):
        super().__init__("User score has changed")
        self.best = best
        self.score = score


class GameTeardownEvent(Event):

    def __init__(self):
        super().__init__("Last chance to release any resources before game quits")


class GameOverEvent(Event):

    def __init__(self, username: str, score: int, best: int):
        super().__init__("User has lost")
        self.username = username
        self.score = score
        self.best = best
