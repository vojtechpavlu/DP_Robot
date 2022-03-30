""""""


# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven


class LoggingOutput(ABC):
    """"""

    def __init__(self):
        """"""
        self._contexts: "list[str]" = []

    @property
    def contexts(self) -> "tuple[str]":
        """"""
        return tuple(self._contexts)

    def add_context(self, context_name: str):
        """"""
        if context_name not in self.contexts:
            self._contexts.append(context_name)

    @abstractmethod
    def log(self, context: str, message: str):
        """"""



