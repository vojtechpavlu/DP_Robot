""""""


# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Iterable

# Import lokálních knihoven
from src.fw.utils.identifiable import Identifiable

import src.fw.world.world as world_module
import src.fw.world.world_factory as world_fact_module
import src.fw.robot.robot as robot_module
import src.fw.target.target as target_module
import src.fw.robot.program as program_module
import src.fw.robot.unit as unit_module


class AbstractRuntime(ABC, Identifiable):
    """Abstraktní třída reprezentující běhové prostředí. Cílem této třídy
    je stanovit obecný protokol, který je společný pro všechny své potomky.

    Náplní této třídy jsou především obecné a pomocné nástroje pro vybudování
    a řízení běhu celého systému. Konkrétně zde udržuje odkaz na platformu,
    jíž tato instance náleží. Dále referenci na program, který má být spuštěn,
    stejně jako instance továrních tříd pro svět, úlohu a její úkoly a
    jednotlivé instance továrních tříd jednotek, které jsou pro tuto úlohu
    povoleny a kterými je možné robota osadit.
    """

    def __init__(self, world_factory: "world_fact_module.WorldFactory",
                 target_factory: "target_module.TargetFactory",
                 unit_factories: "Iterable[unit_module.AbstractUnitFactory]",
                 program: "program_module.AbstractProgram"):
        """Initor funkce, který přijímá tovární třídu světa, tovární třídu
        úlohy, množinu povolených továrních tříd jednotek a referenci na
        program."""

        # TODO - doplnit integraci na platformu

        Identifiable.__init__(self)

        self._target_factory = target_factory
        self._world_factory = world_factory
        self._unit_factories = tuple(unit_factories)
        self._program = program

        self._world = None
        self._target = None

    @property
    def world(self) -> "world_module.World":
        """Svět, který byl vygenerován pro toto běhové prostředí."""
        return self._world

    @property
    def world_factory(self) -> "world_fact_module.WorldFactory":
        """Instance tovární třídy světa, která umí instanci světa poskytnout.
        """
        return self._world_factory

    @property
    def target(self) -> "target_module.Target":
        """Úloha, která má být splněna."""
        return self._target

    @property
    def target_factory(self) -> "target_module.TargetFactory":
        """Instance tovární třídy úlohy, která má být splněna."""
        return self._target_factory

    @property
    def unit_factories(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """Množina všech instancí továrních tříd, které byly poskytnuty a jsou
        povoleny pro plnění této úlohy."""
        return self._unit_factories

    @property
    def program(self) -> "program_module.AbstractProgram":
        """Vlastnost vrací referenci na program, který má být spuštěn pro
        každého robota."""
        return self._program

    def prepare(self):
        """Funkce připravující svět a úlohu ke spuštění. V podstatě si z
        dodaných továren nechá příslušné instance vygenerovat.
        """
        self._world = self.world_factory.build()
        self._target = self.target_factory.build()

    @abstractmethod
    def run(self):
        """Abstraktní funkce odpovědná za běh a řízení běhu daného prostředí.
        """


class AbstractRuntimeFactory(ABC):
    """Tovární třída běhových prostředí je odpovědná za budování instancí
    potomků třídy AbstractRuntime.

    Tato je odpovědná za poskytnutí a dodání všech potřebných zdrojů pro
    vytvoření a běh běhového prostředí.

    Instance této třídy musí být schopny na požádání vytvořit novou instanci
    běhového prostředí tak, aby ji bylo možné spustit a ověřit tak plnění
    úlohy robotem s dodaným programem."""

    def __init__(self, robot_factory: "robot_module.RobotFactory",
                 world_factory: "world_fact_module.WorldFactory",
                 target_factory: "target_module.TargetFactory"):
        """"""
        self._robot_factory = robot_factory
        self._world_factory = world_factory
        self._target_factory = target_factory

    @abstractmethod
    def build(self) -> "AbstractRuntime":
        """Abstraktní funkce odpovědná za vybudování nové instance potomka
        třídy AbstractRuntime."""


