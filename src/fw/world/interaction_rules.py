""""""


# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Iterable

# Import lokálních knihoven
import src.fw.robot.interaction as interaction_module


class InteractionRule(ABC):
    """"""

    @abstractmethod
    def check(self, interaction: "interaction_module.Interaction") -> bool:
        """Abstraktní funkce definuje způsob ověření, že je interakce z
        formálního hlediska akceptovatelná."""


class LimitedCounter(InteractionRule):
    """"""

    def __init__(self, num_of_allowed: int = 100_000):
        """"""
        self.__num_of_allowed = num_of_allowed
        self.__current_state = 0

        if self.num_of_allowed < 0:
            raise Exception(f"Nelze mít záporný počet povolených "
                            f"interakcí: {self.num_of_allowed}")

    @property
    def num_of_allowed(self) -> int:
        """"""
        return self.__num_of_allowed

    @property
    def current_state(self) -> int:
        """"""
        return self.__current_state

    @property
    def have_left(self) -> int:
        """"""
        return self.num_of_allowed - self.current_state

    def tick(self) -> int:
        """"""
        self.__current_state += 1
        return self.current_state

    def check(self, interaction: "interaction_module.Interaction") -> bool:
        """"""
        self.tick()
        return self.have_left > 0





