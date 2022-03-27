""""""


# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Type

# Import lokálních knihoven
from src.fw.utils.named import Named
from src.fw.utils.described import Described
from src.fw.utils.identifiable import Identifiable

import src.fw.robot.unit as unit_module


class Interaction(ABC, Identifiable, Named, Described):
    """"""

    def __init__(self, name: str, desc: str, unit: "unit_module.AbstractUnit"):
        """"""
        Identifiable.__init__(self)
        Named.__init__(self, name)
        Described.__init__(self, desc)

        self._unit = unit

    @property
    def unit(self) -> "unit_module.AbstractUnit":
        """"""
        return self._unit

    @abstractmethod
    def run(self) -> object:
        """"""
        # TODO - nastavení rozhraní světa


class InteractionHandler(ABC):
    """"""

    def __init__(self, interaction_type: "Type"):
        """"""
        self._interaction_type = interaction_type

    @property
    def interaction_type(self) -> "Type":
        """"""
        return self._interaction_type

    def is_mine(self, interaction: "Interaction") -> bool:
        """"""
        return type(interaction) is self._interaction_type




