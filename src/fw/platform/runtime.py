""""""


# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Iterable

# Import lokálních knihoven
from src.fw.utils.identifiable import Identifiable

import src.fw.world.world as world_module
import src.fw.world.world_factory as world_fact_module
import src.fw.target.target as target_module
import src.fw.robot.program as program_module
import src.fw.robot.unit as unit_module


class AbstractRuntime(ABC, Identifiable):
    """"""

    def __init__(self, target_factory: "target_module.TargetFactory",
                 world_factory: "world_fact_module.WorldFactory",
                 unit_factories: "Iterable[unit_module.AbstractUnitFactory]",
                 program: "program_module.AbstractProgram"):
        """"""

        Identifiable.__init__(self)

        self._target_factory = target_factory
        self._world_factory = world_factory
        self._unit_factories = tuple(unit_factories)
        self._program = program

        self._world = None
        self._target = None

    @property
    def world(self) -> "world_module.World":
        """"""
        return self._world

    @property
    def world_factory(self) -> "world_fact_module.WorldFactory":
        """"""
        return self._world_factory

    @property
    def target(self) -> "target_module.Target":
        """"""
        return self._target

    @property
    def target_factory(self) -> "target_module.TargetFactory":
        """"""
        return self._target_factory

    @property
    def unit_factories(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """"""
        return self._unit_factories

    @property
    def program(self) -> "program_module.AbstractProgram":
        """"""
        return self._program

    def generate(self):
        """"""
        self._world = self.world_factory.build()
        self._target = self.target_factory.build()

    @abstractmethod
    def run(self):
        """"""


class AbstractRuntimeFactory(ABC):
    """"""

    def __init__(self):
        """"""

    @abstractmethod
    def build(self):
        """"""


