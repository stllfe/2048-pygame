import logging

from pygame.time import Clock

from common.events import GameTeardownEvent, QuitEvent, CPUTickEvent
from common.mediator import EventManager
from controller.controller import Controller


log = logging.getLogger(__name__)


class CPUClockController(Controller):
    """Produces the ``CPUTickEvent`` :attr:`fps` times per second."""

    def __init__(self, event_manager: EventManager, fps: int = 60):
        super().__init__(event_manager)

        self._clock = Clock()
        self._fps = fps
        self._running = False
        self._ticks = 0

    def notify(self, event):
        if isinstance(event, QuitEvent):
            self._running = False
            self.post(GameTeardownEvent())

    def tick(self):
        self._ticks = self._clock.tick(self._fps)

    def run(self):
        self._running = True
        try:
            while self._running:
                self.post(CPUTickEvent(self._ticks))
                self.tick()
        except KeyboardInterrupt:
            log.info('Detected `KeyboardInterrupt`. Attempting graceful shutdown ...')
            self.post(QuitEvent())
