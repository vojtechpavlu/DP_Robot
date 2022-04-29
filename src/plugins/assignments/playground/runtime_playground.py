"""Šablonový modul obsahují základní a nejjednodušší definici pluginu pro
tvorbu běhových prostředí.

V tomto modulu je třeba v nejjednodušších implementacích upravit především
pomocné funkce uvedené v horní části (začínající na '_get_').

Dále je vhodné upravit i dokumentaci. Tento dokumentační komentář je také
třeba před použitím upravit.
"""


# Import potřebných zdrojů
from src.fw.platform.platform import Platform
from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import RobotFactory, EmptyRobotFactory
from src.fw.target.task import VisitAllTask, AddedMarkAtTask, \
    RemovedMarkAtTask, LoggedAnythingInContext, LoggedMessageInContext
from src.fw.utils.logging.logger import Logger
from src.fw.world.world import World
from src.fw.world.world_factory import WorldFactory, OpenSpaceWorldFactory, \
    WallRebuilder
from src.fw.world.spawner import SpawnerFactory, CoordinatesSpawnerFactory
from src.fw.target.target import TargetFactory, AlwaysCompletedTargetFactory, \
    Target
from src.fw.world.world_interface import (WorldInterfaceFactory,
                                          DefaultWorldInterfaceFactory)
from src.fw.platform.runtime import (AbstractRuntime, AbstractRuntimeFactory,
                                     SingleRobotRuntime)


class CustomTargetFactory(TargetFactory):

    def build(self, world: "World",
              logger: "Logger") -> "Target":
        target = Target("CustomTarget", "no desc", world, logger)
        target.add_task(VisitAllTask())
        return target


def _get_unit_names() -> "list[str]":
    """Funkce vrací seznam názvů jednotek, které jsou pro danou úlohu
    povoleny.

    V tomto případě mají roboti možnost být osazeni všemi jednotkami, které
    jsou v rámci načtených pluginů dostupné."""
    return ["*"]


def _get_robot_factory() -> "RobotFactory":
    """Funkce vrací novou instanci továrny robotů, která bude použita
    pro tvorbu robotů v dané úloze.

    Roboti zde nemají žádnou speciální osazovací proceduru, ani nejsou nijak
    zvlášť pojmenováváni.
    """
    return EmptyRobotFactory()


def _get_spawner_factory() -> "SpawnerFactory":
    """Funkce vrací novou instanci továrny spawnerů, kterých bude použito
    pro zasazování robotů do světa.

    Robot je vždy usazen pevně na pozici [1; 1]."""
    return CoordinatesSpawnerFactory(1, 1)


def _get_target_factory() -> "TargetFactory":
    """Funkce vrací novou instanci továrny úlohy.

    Úloha je v tomto podání vždy per definitionem splněna."""
    return CustomTargetFactory()


def _get_world_interface_factory() -> "WorldInterfaceFactory":
    """Funkce vrací zcela novou instanci továrny rozhraní světa.
    """
    return DefaultWorldInterfaceFactory()


def _get_world_factory() -> "WorldFactory":
    """Funkce vrací novou instanci továrny světa.

    Na hřišti je vždy rozhraní světa 10x10 políček (resp. otevřený prostor
    8x8 cest a tento čtverec obehnaný zdí.
    """
    return WallRebuilder(OpenSpaceWorldFactory(
        8, 8, _get_world_interface_factory(),_get_spawner_factory()),
        ((5, 5),))


class PlaygroundRuntimeFactory(AbstractRuntimeFactory):
    """Třída definující továrnu běhového prostředí sloužícího jako hřiště.
    Běhová prostředí tohoto typu jsou zcela výchozí, velmi jednoduchá a co
    do funkcionality a pestrosti značně omezená."""

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


def get_runtime_factory() -> "AbstractRuntimeFactory":
    """Hlavní přístupová funkce, která vrací továrnu běhového prostředí.
    Tato funkce (co do existence, funkce a typu návratové hodnoty) je
    rozhodujícím faktorem pro validátory pluginů v kontextu dynamické
    tvorby běhových prostředí.
    """
    return PlaygroundRuntimeFactory()


