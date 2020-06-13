import sys
import yaml
import pygame

from argparse import Namespace

from controller.keyboard import KeyboardController
from controller.cpu import CPUClockController
from controller.game import GameController

from common.mediator import EventManager
from storage.local import LocalStorageManager
from view.ui import UserInterface


if __name__ == "__main__":
    pygame.init()

    # Load user defined game settings
    with open('config.yaml', 'r') as config:
        params = yaml.safe_load(config)

    params = Namespace(**params)
    storage = LocalStorageManager(path='./.games', hide_files=False)
    ui = UserInterface(width=640, height=1024)

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
