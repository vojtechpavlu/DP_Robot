""""""


# Import standardních knihoven
from abc import ABC, abstractmethod


class EventHandler(ABC):
    """"""

    @abstractmethod
    def update(self):
        """"""


class EventEmitor:
    """"""

    def __init__(self):
        self._event_handlers: "list[EventHandler]" = []

    def register_event_handler(self, handler: "EventHandler"):
        """"""
        self._event_handlers.append(handler)

    def notify_all_event_handlers(self):
        """"""
        for handler in self._event_handlers:
            handler.update()


