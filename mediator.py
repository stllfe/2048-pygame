from enum import Enum, auto
from abc import ABC, abstractmethod


class EventGroup(Enum):

    CONTROLLERS = auto()
    UI = auto()
    CPU = auto()


class Listener(ABC):

    @abstractmethod
    def notify(self, event):
        pass


class Poster(ABC):

    def __init__(self, event_manager):
        self.event_manager = event_manager

    def post(self, event, event_group: EventGroup = None):
        self.event_manager.post(event, event_group)


class EventManager(object):

    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()

    def register(self, listener: Listener, group=None):
        self.listeners[listener] = group

    def unregister(self, listener: Listener):
        if listener in self.listeners:
            del self.listeners[listener]

    def post(self, event, event_group: EventGroup = None):
        for listener, group in self.listeners.items():
            if group is event_group:
                listener.notify(event)
