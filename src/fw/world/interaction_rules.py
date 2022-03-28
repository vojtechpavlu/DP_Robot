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



