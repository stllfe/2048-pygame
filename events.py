from grid import Direction, Grid, Tile


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


class CPUTickEvent(Event):

    def __init__(self):
        super().__init__("CPU frame update event")


class GridReadyEvent(Event):

    def __init__(self, grid: Grid):
        super().__init__("Grid object initialized")
        self.grid = grid


class TilesMergeEvent(Event):

    def __init__(self, tile: Tile):
        super().__init__("Two tiles have merged")
        self.tile = tile


class GridUpdateEvent(Event):

    def __init__(self, grid: Grid):
        super().__init__("Grid object have been updated")
        self.grid = grid
