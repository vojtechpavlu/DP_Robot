"""
"""


# Import potřebných zdrojů
from src.fw.platform.platform import Platform
from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import RobotFactory, EmptyRobotFactory
from src.fw.utils.logging.logger import Logger
from src.fw.world.world import World
from src.fw.world.world_factory import WorldFactory, OpenSpaceWorldFactory
from src.fw.world.spawner import SpawnerFactory, CoordinatesSpawnerFactory
from src.fw.target.target import TargetFactory, Target
from src.fw.world.world_interface import (
    WorldInterfaceFactory, DefaultWorldInterfaceFactory)
from src.fw.platform.runtime import (
    AbstractRuntime, AbstractRuntimeFactory, SingleRobotRuntime)


# Název úlohy
_TARGET_NAME = "První interakce"

# Popis úlohy
_TARGET_DESCRIPTION = ("Cílem úlohy je")


class CustomTargetFactory(TargetFactory):
    def build(self, world: "World",
              logger: "Logger") -> "Target":
        """Funkce build připraví zcela novou instanci úlohy. V prvním
        kroku je vytvořena prázdná instance úlohy s pouze nutnými
        parametry, v druhém kroku je naplněna požadovanými úkoly a
        v posledním kroku je tato instance vrácena
        """

        # 1) Vytvoření instance úlohy
        target = Target(_TARGET_NAME, _TARGET_DESCRIPTION, world, logger)

        # 2) Doplnění sadou úkolů


        # 3) Vrácení úlohy
        return target


def _get_unit_names() -> "list[str]":
    """Funkce vrací seznam názvů jednotek, které jsou pro danou úlohu
    povoleny."""
    return ["*"]  # TODO - DOPLNIT


def _get_robot_factory() -> "RobotFactory":
    """Funkce vrací novou instanci továrny robotů, která bude použita
    pro tvorbu robotů v dané úloze."""
    return EmptyRobotFactory()  # TODO - DOPLNIT


def _get_spawner_factory() -> "SpawnerFactory":
    """Funkce vrací novou instanci továrny spawnerů, kterých bude použito
    pro zasazování robotů do světa."""
    return CoordinatesSpawnerFactory(1, 1)  # TODO - DOPLNIT


def _get_target_factory() -> "TargetFactory":
    """Funkce vrací novou instanci továrny úlohy."""
    return CustomTargetFactory()  # TODO - DOPLNIT


def _get_world_interface_factory() -> "WorldInterfaceFactory":
    """Funkce vrací zcela novou instanci továrny rozhraní světa."""
    return DefaultWorldInterfaceFactory()  # TODO - DOPLNIT


def _get_world_factory() -> "WorldFactory":  # TODO - DOPLNIT
    """Funkce vrací novou instanci továrny světa."""
    return OpenSpaceWorldFactory(10, 10, _get_world_interface_factory(),
                                 _get_spawner_factory())


class FirstInteractionRuntimeFactory(AbstractRuntimeFactory):  # TODO - DOPLNIT
    """Tato třída slouží k zpřístupnění tvorby co nejjednoduššího běhového
    prostředí. Chování této třídy je silně ovlivněno definicí přístupových
    funkcí v horní části tohoto modulu.

    Samotná implementace slouží spíše k šablonovým účelům."""

    def __init__(self):
        """Initor třídy, který má za cíl jen připravit svého předka."""
        super().__init__(
            _get_unit_names(),
            _get_robot_factory(),
            _get_world_factory(),
            _get_target_factory())

    def build(self, platform: "Platform", program: "AbstractProgram",
              logger: "Logger") -> "AbstractRuntime":
        """Funkce 'build', která implementuje signaturu stanovenou předkem.

        Cílem této funkce je tvorba konkrétních běhových prostředí na
        požádání, resp. na zavolání.
        """
        return SingleRobotRuntime(
            self.world_factory, self.target_factory,
            self.pick_unit_factories(platform, self.available_units_names),
            program, self.robot_factory, platform, logger, self)


def get_runtime_factory() -> "AbstractRuntimeFactory":  # TODO - DOPLNIT
    """Hlavní přístupová funkce, která vrací továrnu běhového prostředí.
    Tato funkce (co do existence, funkce a typu návratové hodnoty) je
    rozhodujícím faktorem pro validátory pluginů v kontextu dynamické
    tvorby běhových prostředí.
    """
    return FirstInteractionRuntimeFactory()


