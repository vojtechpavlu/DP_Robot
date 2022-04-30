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
from src.fw.robot.robot import RobotFactory, CompleteRobotFactory

# Import světa
from src.fw.world.world import World
from src.fw.world.world_factory import (
    WorldFactory, OpenSpaceWorldFactory, FieldPremarker)
from src.fw.world.spawner import SpawnerFactory, CoordinatesSpawnerFactory
from src.fw.world.world_interface import (WorldInterfaceFactory,
                                          DefaultWorldInterfaceFactory)

# Import úlohy
from src.fw.target.target import TargetFactory, Target
from src.fw.target.task import VisitAllTask, LoggedMessageInContext

# Import pomocných nástrojů
from src.fw.utils.logging.logger import Logger


# *****************************************************************************
# ---------------------------- Pomocné proměnné -------------------------------

# Název robota
_ROBOT_NAME = "KAREL-JAROMIR-ERBOT"

# Názvy jednotek k osazení
_AVAILABLE_UNITS = ("IsWallSensor", "ForwardMover", "TurnLeft", "HasMark",
                    "MarkReader")

# Název úlohy
_TARGET_NAME = f"6x6"

# Popis úlohy
_TARGET_DESCRIPTION = (
    f"Sběr pohádek není žádný med. {_ROBOT_NAME} by mohl povídat... "
    f"Nyní ale není úkolem sběr lidové slovesnosti, nýbrž značek. Robot nyní "
    f"musí projít celý svět a zaznamenávat si značky, na které narazil.")


# *****************************************************************************
# ------------------------ Definice pomocných tříd ----------------------------


class FirstInteractionTestFactory(TargetFactory):
    def build(self, world: "World", logger: "Logger") -> "Target":
        """Nyní je cílem zkontrolovat, že program zaznamenal textový
        řetězec odpovídající jménu robota.

        V prvním kroku je vytvořena prázdná instance úlohy s pouze nutnými
        parametry, v druhém kroku je naplněna požadovanými úkoly a v posledním
        kroku je tato instance vrácena
        """

        """ 1) Vytvoření instance úlohy """
        target = Target(_TARGET_NAME, _TARGET_DESCRIPTION, world, logger)

        """ 2) Doplnění úlohy sadou úkolů """
        # Kontrola, že robot navštívil všechna políčka
        target.add_task(VisitAllTask())
        target.add_task(LoggedMessageInContext("X"))
        target.add_task(LoggedMessageInContext("Y"))
        target.add_task(LoggedMessageInContext("AB"))
        target.add_task(LoggedMessageInContext("DC"))
        target.add_task(LoggedMessageInContext("ZG1"))

        """ 3) Vrácení nové instance úlohy """
        return target


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


def _get_unit_names() -> "tuple[str]":
    """Funkce vrací seznam názvů jednotek, které jsou pro danou úlohu
    povoleny. Tyto názvy musí být doslovné a musí respektovat velikost
    znaků či mezery.

    Alternativou je označení hvězdičkou (znak '*'), který povolí všechny
    jednotky, které jsou načteny."""
    return _AVAILABLE_UNITS


def _get_robot_factory() -> "RobotFactory":
    """Funkce vrací novou instanci továrny robotů, která bude použita
    pro tvorbu robotů v dané úloze."""

    # Lokální import pro zjednodušení přístupu
    from src.fw.robot.robot_name_generator import ConstantRobotNameGenerator

    # Vrácení robota s předdefinovaným názem robota
    return CompleteRobotFactory([], ConstantRobotNameGenerator(_ROBOT_NAME))


def _get_spawner_factory() -> "SpawnerFactory":
    """Funkce vrací novou instanci továrny spawnerů, kterých bude použito
    pro zasazování robotů do světa."""
    from src.fw.world.direction import Direction

    return CoordinatesSpawnerFactory(1, 1, Direction.EAST)


def _get_target_factory() -> "TargetFactory":
    """Funkce vrací novou instanci továrny úlohy."""
    return FirstInteractionTestFactory()


def _get_world_interface_factory() -> "WorldInterfaceFactory":
    """Funkce vrací zcela novou instanci továrny rozhraní světa."""
    return DefaultWorldInterfaceFactory()


def _get_world_factory() -> "WorldFactory":
    """Funkce vrací novou instanci továrny světa."""

    # Dekorátor světa
    return FieldPremarker(

        # Definice světa k dekoraci
        OpenSpaceWorldFactory(
            8, 8, _get_world_interface_factory(), _get_spawner_factory()),

        # Definice značek
        [("X", 3, 5), ("Y", 1, 4), ("AB", 6, 6), ("DC", 5, 2), ("ZG1", 1, 1)])


def get_runtime_factory() -> "RuntimeFactory":
    """Hlavní přístupová funkce, která vrací továrnu běhového prostředí.
    Tato funkce (co do existence, funkce a typu návratové hodnoty) je
    rozhodujícím faktorem pro validátory pluginů v kontextu dynamické
    tvorby běhových prostředí.
    """
    return RuntimeFactory()


