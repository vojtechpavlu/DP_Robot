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
    WorldFactory, OpenSpaceWorldFactory, WallRebuilder, FieldPremarker)
from src.fw.world.spawner import SpawnerFactory, CoordinatesSpawnerFactory
from src.fw.world.world_interface import (WorldInterfaceFactory,
                                          DefaultWorldInterfaceFactory)

# Import úlohy
from src.fw.target.target import TargetFactory, Target
from src.fw.target.task import EndedAtCoords, AbortedWith

# Import pomocných nástrojů
from src.fw.utils.logging.logger import Logger

# *****************************************************************************
# ---------------------------- Pomocné proměnné -------------------------------

# Název robota
_ROBOT_NAME = "maze-runner"

# Názvy jednotek k osazení
_AVAILABLE_UNITS = ("*",)

# Název úlohy
_TARGET_NAME = f"Maze"

# Popis úlohy
_TARGET_DESCRIPTION = (
    f"Úkolem robota je najít cestu v bludišti. Konkrétně musí najít políčko, "
    f"na kterém je značka s textem 'CIL'. Pak se musí program ukončit.")


# *****************************************************************************
# ------------------------ Definice pomocných tříd ----------------------------


class AisleWalkerTestFactory(TargetFactory):
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
        # Kontrola, že se robot zjistil a vypsal délku chodby
        target.add_task(EndedAtCoords(11, 2))
        target.add_task(AbortedWith("SUCCESS"))

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

    # Robot se objeví na souřadnicích [1, 5] natočen na jih
    return CoordinatesSpawnerFactory(1, 5, Direction.SOUTH)


def _get_target_factory() -> "TargetFactory":
    """Funkce vrací novou instanci továrny úlohy."""
    return AisleWalkerTestFactory()


def _get_world_interface_factory() -> "WorldInterfaceFactory":
    """Funkce vrací zcela novou instanci továrny rozhraní světa."""
    return DefaultWorldInterfaceFactory()


def _get_world_factory() -> "WorldFactory":
    """Funkce vrací novou instanci továrny světa."""

    # Dekorátor světa přidávající značku
    return FieldPremarker(

        # Dekorátor světa budující stěny
        WallRebuilder(

            # Původní svět k překreslení
            OpenSpaceWorldFactory(
                13, 7, _get_world_interface_factory(), _get_spawner_factory()),

            # Nové zdi pro bludiště
            [(2, 5), (2, 4), (2, 3), (3, 4), (3, 1),
             (5, 5), (5, 4), (5, 3), (5, 2), (6, 2),
             (7, 4), (8, 4), (8, 3), (8, 2), (8, 1),
             (10, 5), (10, 3), (10, 2), (11, 3)]
        ),

        # Značka cíle a značky pro "zmatení" programu
        [("CIL", 11, 2), ("NOT", 4, 3), ("NOT", 11, 5), ("NOT", 3, 5)]
    )


def get_runtime_factory() -> "RuntimeFactory":
    """Hlavní přístupová funkce, která vrací továrnu běhového prostředí.
    Tato funkce (co do existence, funkce a typu návratové hodnoty) je
    rozhodujícím faktorem pro validátory pluginů v kontextu dynamické
    tvorby běhových prostředí.
    """
    return RuntimeFactory()
