import pygame
import logging

from abc import ABCMeta
from argparse import Namespace
from pygame.time import Clock

from events import QuitEvent, UserMoveEvent, CPUTickEvent, GridReadyEvent, GridUpdateEvent
from logic import Direction, Logic
from mediator import Listener, Poster, EventManager, EventGroup
from storage import StorageManager


log = logging.getLogger(__name__)


class Controller(Poster, Listener, metaclass=ABCMeta):
    """
    Mixin class for all controllers.
    """
    def __init__(self, event_manager: EventManager):
        super().__init__(event_manager)
        self.event_manager.register(self)


class CPUClockController(Controller):

    def __init__(self, event_manager: EventManager, fps: int = 60):
        super().__init__(event_manager)

        self.clock = Clock()
        self.fps = fps
        self.running = False

    def notify(self, event):
        if isinstance(event, QuitEvent):
            self.running = False

    def tick(self):
        self.clock.tick(self.fps)

    def run(self):
        self.running = True
        try:
            while self.running:
                self.post(CPUTickEvent())
                self.tick()
        except KeyboardInterrupt:
            print('Detected `KeyboardInterrupt`. Attempting graceful shutdown ...')
            self.post(QuitEvent())


class KeyboardController(Controller):

    def _handle_event(self, event):
        response = None

        if event.type == pygame.QUIT or event.key in (pygame.K_ESCAPE, pygame.K_q):
            response = QuitEvent()

        elif event.key in (pygame.K_UP, pygame.K_w):
            response = UserMoveEvent(Direction.UP)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            response = UserMoveEvent(Direction.DOWN)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            response = UserMoveEvent(Direction.LEFT)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            response = UserMoveEvent(Direction.RIGHT)

        if response:
            self.post(response)

    def notify(self, event):
        if isinstance(event, CPUTickEvent):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self._handle_event(event)


class GameController(Controller):

    def __init__(self,
                 params: Namespace,
                 storage: StorageManager,
                 event_manager: EventManager):

        super().__init__(event_manager)

        self._logic = Logic(params)
        self._params = params
        self._storage = storage

        self._running = False
        self._is_resume = False

        self._score = 0
        self._best = 0

    def init_game(self):

        if self._running:
            log.warning("Game can be initialised only once during runtime.")
            return

        checkpoint = self._storage.get(self._params.username)

        if checkpoint:
            self._best = checkpoint.get('best', 0)
            self._is_resume = checkpoint.get('unfinished', False)

        if self._is_resume:
            state = checkpoint['state']
            self._logic.load_state(state)
        else:
            if not self._logic.setup():
                raise RuntimeError("BOOM! MISCONFIGURATION!")

        self._running = True

        self.post(GridReadyEvent(self._logic.grid))

    def notify(self, event):
        if isinstance(event, CPUTickEvent):
            if not self._running:
                self.init_game()
        elif isinstance(event, UserMoveEvent):
            self._logic.move(event.direction)
            self.post(GridUpdateEvent(self._logic.grid))

    def run(self):
        self._running = True
        pass

    def update(self):
        pass