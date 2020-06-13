from abc import ABCMeta

from common.mediator import Listener, Poster, EventManager


class Controller(Poster, Listener, metaclass=ABCMeta):
    """
    Mixin class for all controllers.
    """
    def __init__(self, event_manager: EventManager):
        super().__init__(event_manager)
        self.event_manager.register(self)


