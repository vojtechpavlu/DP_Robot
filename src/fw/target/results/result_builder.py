"""V tomto modulu je obsažena definice základních prostředků pro budování
výstupů z výsledků jednotlivých běhů."""


# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.platform.platform as platform_module
import src.fw.platform.runtime as runtime_module
import src.fw.robot.program as program_module
import src.fw.robot.robot as robot_module
import src.fw.robot.unit as unit_module
import src.fw.target.target as target_module
import src.fw.world.world as world_module
import src.fw.utils.logging.logger as logger_module
import src.fw.utils.loading.runtime_factory_loader as rt_loader_module
import src.fw.utils.loading.program_loader as p_loader_module
import src.fw.utils.loading.unit_factory_loader as uf_loader_module
from src.fw.utils.error import PlatformError


class ResultBuilder(ABC):
    """Abstraktní třída ResultBuilder, která má za cíl stanovit obecný
    a společný protokol pro všechny zpracovatele výstupů."""

    @abstractmethod
    def build(self):
        """Abstraktní funkce, která stanovuje signaturu pro všechny své
        potomky, kteří se starají o vybudování výstupu."""


class RuntimeResultBuilder(ResultBuilder):
    """Abstraktní třída, která definuje společný protokol pro všechny
    budovatele, kteří se specializují na vybudování výstupu běhového
    prostředí.
    """

    def __init__(self, runtime: "runtime_module.AbstractRuntime"):
        """Initor třídy, který přijímá běhové prostředí, pro které
        má vybudovat výstup.
        """
        self._runtime = runtime

    @property
    def runtime_id(self) -> str:
        """Vlastnost vrací ID, které bylo běhovému prostředí přiděleno."""
        return self.runtime.hex_id

    @property
    def runtime(self) -> "runtime_module.AbstractRuntime":
        """Vlastnost, která vrací běhové prostředí, pro které má být
        vybudován výstup."""
        return self._runtime

    @property
    def program(self) -> "program_module.AbstractProgram":
        """Vlastnost vrací program, který běžel v daném běhovém prostředí."""
        return self.runtime.program

    @property
    def author_name(self) -> str:
        """Vlastnost vrací jméno autora programu, pro který běželo běhové
        prostředí."""
        return self.program.author_name

    @property
    def robots(self) -> "tuple[robot_module.Robot]":
        """Vlastnost vrací ntici robotů, kteří byli v běhovém prostředí
        spuštěni."""
        return self.runtime.robots

    @property
    def target(self) -> "target_module.Target":
        """Vlastnost vrací úlohu, pro kterou bylo běhové prostředí spuštěno.
        """
        return self.runtime.target

    @property
    def world(self) -> "world_module.World":
        """Vlastnost vrací program, nad kterým běhové prostředí běželo."""
        return self.runtime.world

    @property
    def logger(self) -> "logger_module.Logger":
        """Vlastnost vrací logger, který byl pro běhové prostředí použit."""
        return self.runtime.logger

    @property
    def unit_factories(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """Vlastnost vrací ntici všech továren jednotek, kterými bylo možné
        v rámci daného běhového prostředí osadit roboty."""
        return self.runtime.unit_factories

    @abstractmethod
    def build(self):
        """Abstraktní funkce, která stanovuje signaturu pro všechny své
        potomky, kteří se starají o vybudování výstupu."""


class PlatformResultBuilder(ResultBuilder):
    """Instance této třídy slouží k tvorbě výsledných výstupů na úrovni
    platformy."""

    def __init__(self, platform: "platform_module.Platform"):
        """Initor třídy, který přijímá v parametru platformu, pro kterou
        má být vybudován výsledný výstup."""
        self._platform = platform

    @property
    def platform(self) -> "platform_module.Platform":
        """Vlastnost vrací platformu, pro kterou má být vybudován výstup."""
        return self._platform

    @property
    def runtimes(self) -> "tuple[runtime_module.AbstractRuntime]":
        """Vlastnost vrací všechna běhová prostředí, která byla v rámci
        platformy spuštěna. Tyto vrací v ntici."""
        return self.platform.all_runtimes

    @property
    def unit_factories(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """Vlastnost vrací ntici všech dynamicky načtených továren jednotek.
        """
        return self.platform.unit_factories

    @property
    def runtime_factory_loader(
            self) -> "rt_loader_module.RuntimeFactoryLoader":
        """Vlastnost vrací loader, kterého bylo použito pro dynamické načtení
        továren běhových prostředí."""
        return self.platform.runtime_factory_manager.loader

    @property
    def unit_factories_loaders(
            self) -> "tuple[uf_loader_module.UnitFactoryLoader]":
        """Vlastnost vrací loadery, kterých bylo použito pro dynamické načtení
        továren jednotek."""
        return self.platform.unit_factory_manager.loaders

    @property
    def program_loaders(self) -> "tuple[p_loader_module.ProgramLoader]":
        """Vlastnost vrací loadery, kterých bylo použito pro dynamické načtení
        jednotlivých programů."""
        return self.platform.program_manager.program_loaders

    @abstractmethod
    def build(self):
        """Abstraktní funkce, která stanovuje signaturu pro všechny své
        potomky, kteří se starají o vybudování výstupu."""


class ResultBuilderError(PlatformError):
    """"""

    def __init__(self, message: str, builder: ResultBuilder):
        """"""
        PlatformError.__init__(self, message)
        self._builder = builder

    @property
    def builder(self) -> ResultBuilder:
        """"""
        return self._builder


