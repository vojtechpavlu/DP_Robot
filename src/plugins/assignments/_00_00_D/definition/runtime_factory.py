"""Šablonový modul obsahují základní a nejjednodušší definici pluginu pro
tvorbu běhových prostředí.

V tomto modulu je třeba v nejjednodušších implementacích upravit především
pomocné funkce uvedené v horní části (začínající na '_get_').

Dále je vhodné upravit i dokumentaci. Tento dokumentační komentář je také
třeba před použitím upravit.
"""

# Import platformy
from src.fw.platform.platform import Platform
from src.fw.platform.runtime import (AbstractRuntime, AbstractRuntimeFactory,
                                     SingleRobotRuntime)

# Import robota
from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import RobotFactory, EmptyRobotFactory

# Import světa
from src.fw.world.world import World
from src.fw.world.world_factory import WorldFactory, OpenSpaceWorldFactory
from src.fw.world.spawner import SpawnerFactory, CoordinatesSpawnerFactory
from src.fw.world.world_interface import (WorldInterfaceFactory,
                                          DefaultWorldInterfaceFactory)

# Import úlohy
from src.fw.target.target import TargetFactory, Target

# Import pomocných nástrojů
from src.fw.utils.logging.logger import Logger


# *****************************************************************************
# ---------------------------- Pomocné proměnné -------------------------------


# Název úlohy
_TARGET_NAME = "Test Validity pluginu programu"

# Popis úlohy
_TARGET_DESCRIPTION = (
    "Tímto běhovým prostředím je ověřováno, že byl definován validní plugin "
    "programu. Jsou-li splněny všechny požadavky, pak tento program splnil "
    "všechny požadavky na 100 %.")


# *****************************************************************************
# ------------------------ Definice pomocných tříd ----------------------------


class ValidityTestFactory(TargetFactory):
    def build(self, world: "World", logger: "Logger") -> "Target":
        """Nyní je cílem zkontrolovat, že lze úkol splnit. Projde-li validací,
        jsou všechny úkoly splněny."""

        # Lokální import pro zpřehlednění modulu
        from src.fw.target.target import AlwaysCompletedTargetFactory

        # Vytvoření nové instance úlohy na požádání
        return AlwaysCompletedTargetFactory().build(
            world, logger, name=_TARGET_NAME, desc=_TARGET_DESCRIPTION)


class RuntimeFactory(AbstractRuntimeFactory):
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


# *****************************************************************************
# --------------------- Definice přístupových funkcí --------------------------


def _get_unit_names() -> "list[str]":
    """Funkce vrací seznam názvů jednotek, které jsou pro danou úlohu
    povoleny. Tyto názvy musí být doslovné a musí respektovat velikost
    znaků či mezery.

    Alternativou je označení hvězdičkou (znak '*'), který povolí všechny
    jednotky, které jsou načteny."""
    return []


def _get_robot_factory() -> "RobotFactory":
    """Funkce vrací novou instanci továrny robotů, která bude použita
    pro tvorbu robotů v dané úloze."""
    return EmptyRobotFactory()


def _get_spawner_factory() -> "SpawnerFactory":
    """Funkce vrací novou instanci továrny spawnerů, kterých bude použito
    pro zasazování robotů do světa."""
    return CoordinatesSpawnerFactory(1, 1)


def _get_target_factory() -> "TargetFactory":
    """Funkce vrací novou instanci továrny úlohy."""
    return ValidityTestFactory()


def _get_world_interface_factory() -> "WorldInterfaceFactory":
    """Funkce vrací zcela novou instanci továrny rozhraní světa."""
    return DefaultWorldInterfaceFactory()


def _get_world_factory() -> "WorldFactory":
    """Funkce vrací novou instanci továrny světa."""
    return OpenSpaceWorldFactory(5, 5, _get_world_interface_factory(),
                                 _get_spawner_factory())


def get_runtime_factory() -> "RuntimeFactory":
    """Hlavní přístupová funkce, která vrací továrnu běhového prostředí.
    Tato funkce (co do existence, funkce a typu návratové hodnoty) je
    rozhodujícím faktorem pro validátory pluginů v kontextu dynamické
    tvorby běhových prostředí.
    """
    return RuntimeFactory()


