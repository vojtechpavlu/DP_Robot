""""""


# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.utils.identifiable import Identifiable

import src.fw.world.world as world_module
import src.fw.target.target as target_module


class AbstractRuntime(ABC, Identifiable):
    """"""

    def __init__(self):
        """"""

        Identifiable.__init__(self)

    @property
    def world(self) -> "world_module.World":
        """"""

    @world.setter
    def world(self, new_world: "world_module.World"):
        """"""
        if self.world:
            # TODO - Specifikace konkrétní výjimky
            raise Exception(
                f"Nelze nastavovat již nastavený svět", self)
        # TODO - nastavení proměnné světa

    @property
    def target(self) -> "target_module.Target":
        """"""

    @target.setter
    def target(self, new_target: "target_module.Target"):
        """"""
        if self.target:
            # TODO - Specifikace konkrétní výjimky
            raise Exception(
                f"Nelze nastavovat již nastavený target", self)
        # TODO - nastavení proměnné světa

    @abstractmethod
    def run(self):
        """"""




