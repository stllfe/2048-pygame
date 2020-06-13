import pygame

from common.events import QuitEvent, UserRestartEvent, UserMoveEvent, CPUTickEvent
from controller.controller import Controller
from model.grid import Direction


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
        elif event.key == pygame.K_r:
            response = UserRestartEvent()

        if response:
            self.post(response)

    def notify(self, event):
        if isinstance(event, CPUTickEvent):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self._handle_event(event)
