""""""


# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Type

# Import lokálních knihoven
from src.fw.utils.named import Named
from src.fw.utils.described import Described
from src.fw.utils.identifiable import Identifiable

import src.fw.robot.unit as unit_module
import src.fw.world.world_interface as world_interface_module


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


class InteractionHandlerManager(ABC):
    """"""

    def __init__(self):
        """"""
        self._world_interface = None
        self._handlers: "list[InteractionHandler]" = []

    @property
    def interaction_handlers(self) -> "tuple[InteractionHandler]":
        """"""
        return tuple(self._handlers)

    @property
    def world_interface(self) -> "world_interface_module.WorldInterface":
        """"""
        return self._world_interface

    @world_interface.setter
    def world_interface(
            self, world_interface: "world_interface_module.WorldInterface"):
        """"""
        if self.has_world_interface:
            raise Exception("Rozhraní světa nelze znovu měnit")
        self._world_interface = world_interface

    @property
    def has_world_interface(self) -> bool:
        """"""
        return self._world_interface is not None

    def add_interaction_handler(self, handler: "InteractionHandler"):
        """"""
        for i_h in self.interaction_handlers:
            if i_h.interaction_type is handler.interaction_type:
                # TODO - specifikace výjimky
                raise Exception(
                    f"Nelze mít evidovány dva handlery pro stejný typ "
                    f"interakce: '{handler.interaction_type}'")

    def has_handler(self, interaction: "Interaction") -> bool:
        """"""
        for handler in self.interaction_handlers:
            if handler.is_mine(interaction):
                return True
        return False

    def get_handler(self, interaction: "Interaction") -> "InteractionHandler":
        """"""
        for handler in self.interaction_handlers:
            if handler.is_mine(interaction):
                return handler
        # TODO - specifikace výjimky
        raise Exception(
            f"Pro interakci '{type(interaction)}' není handler evidován")

    @abstractmethod
    def process_interaction(self, interaction: "Interaction") -> object:
        """"""




