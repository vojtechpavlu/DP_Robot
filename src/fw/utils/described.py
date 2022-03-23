""""""


# Import standardních knihoven
from abc import ABC, abstractmethod


class Described(ABC):
    """"""

    def __init__(self, description: str = ""):
        """"""
        self._desc = description

    @property
    def description(self) -> str:
        """"""
        return self._desc
