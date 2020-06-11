import sys
import yaml
import pygame

from argparse import Namespace

from controller import KeyboardController
from controller import CPUClockController
from controller import GameController

from mediator import EventManager
from storage import LocalStorageManager
from ui import UserInterface


if __name__ == "__main__":
    pygame.init()

    with open('config.yaml', 'r') as config:
        defaults = yaml.safe_load(config)

    params = Namespace(**defaults)
    storage = LocalStorageManager()
    ui = UserInterface(640, 960)

    # Event broker that serves MVC entities
    event_manager = EventManager()

    # Main controllers
    keyboard = KeyboardController(event_manager)
    spinner = CPUClockController(event_manager)
    game = GameController(params, storage, event_manager)

    # User interface needs to be attached explicitly
    # since it doesn't post any events and only listens to them
    event_manager.register(ui)

    spinner.run()
    pygame.quit()
    sys.exit()
