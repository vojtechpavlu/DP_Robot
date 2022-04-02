"""Tento modul je odpovědný za definici protokolu běhového prostředí a
protokolu jeho tovární třídy. Je zde tedy obsažena definice AbstractRuntime
(abstraktní třída běhového prostředí) a AbstractRuntimeFactory (abstraktní
třída továrny běhových prostředí).
"""


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
import src.fw.robot.robot_container as robot_cont_module
import src.fw.platform.platform as platform_module
import src.fw.platform.unit_factories_manager as uf_manager_module


class AbstractRuntime(Identifiable):
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
                 program: "program_module.AbstractProgram",
                 robot_factory: "robot_module.RobotFactory",
                 platform: "platform_module.Platform"):
        """Initor funkce, který přijímá tovární třídu světa, tovární třídu
        úlohy, množinu povolených továrních tříd jednotek a referenci na
        program."""

        Identifiable.__init__(self)

        self._target_factory = target_factory
        self._world_factory = world_factory
        self._unit_factories = tuple(unit_factories)
        self._program = program
        self._robot_factory = robot_factory
        self._platform = platform

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

    @property
    def robot_factory(self) -> "robot_module.RobotFactory":
        """Vlastnost vrací referenci na dodanou instanci továrny robotů."""
        return self._robot_factory

    @property
    def platform(self) -> "platform_module.Platform":
        """Vlastnost vrací platformu, které tato instance běhového prostředí
        náleží."""
        return self._platform

    @property
    def units(self) -> "tuple[unit_module.AbstractUnit]":
        """Vlastnost vrací zcela nově vytvořené jednotky z uložených továren
        jednotek."""
        return tuple(uf.build() for uf in self.unit_factories)

    def prepare(self):
        """Funkce připravující svět a úlohu ke spuštění. V podstatě si z
        dodaných továren nechá příslušné instance vygenerovat.
        """
        # Tvorba světa
        self._world = self.world_factory.build()

        # Dodání reference světa pro přípravu úlohy; aby úloha mohla být
        # provázána se světem a sledovat v něm plnění úkolů této úlohy
        self._target = self.target_factory.build(self._world)

    @abstractmethod
    def run(self):
        """Abstraktní funkce odpovědná za běh a řízení běhu daného prostředí.
        """


class SingleRobotRuntime(AbstractRuntime):
    """Třída definuje speciální typ svého předka, tedy běhové prostředí, ve
    kterém je pouze jediný robot.

    Toto běhové prostředí se liší především implementací instanční metody
    'run', která operuje jen a pouze na úrovni jediného robota."""

    def __init__(self, world_factory: "world_fact_module.WorldFactory",
                 target_factory: "target_module.TargetFactory",
                 unit_factories: "Iterable[unit_module.AbstractUnitFactory]",
                 program: "program_module.AbstractProgram",
                 robot_factory: "robot_module.RobotFactory",
                 platform: "platform_module.Platform"):
        """Initor třídy, který přijímá tovární třídy (továrnu světa, úlohy,
        robotů a továrny jednotek) a referenci na program, který má být pro
        jediného robota spuštěn. Dále přijímá referenci na platformu, pod
        kterou je toto běhové prostředí spuštěno.
        """
        # Volání předka
        AbstractRuntime.__init__(
            self, world_factory, target_factory, unit_factories, program,
            robot_factory, platform)

        # Příprava kontejneru robota
        self.__robot_container = robot_cont_module.SingleRobotContainer()
        self.__robot_container.robot = self.robot_factory.build()

    @property
    def robot(self) -> "robot_module.Robot":
        """Vlastnost vrací jediného robota, kterého toto prostředí má. Ten
        je uložen v privátním kontejneru typu 'SingleRobotContainer', který
        co nejvíce znesnadňuje jakoukoliv nepravou manipulaci."""
        return self.__robot_container.robot

    def run(self):
        """Hlavní funkce třídy, která se stará o řízení běhu jediného robota.
        """
        self.prepare()
        self.program.mount(self.robot, self.units)
        for unit in self.robot.units:
            unit.set_world_interface(self.world.world_interface)
            self.world.world_interface.add_interaction_handler(
                unit.unit_factory.interaction_handler)
        # TODO - kontrola osazení
        try:
            self.program.run(self.robot)
        except Exception as e:
            for unit in self.robot.units:
                unit.deactivate()
            raise e
        # TODO - kontrola Targetu a jeho vyhodnocení


class AbstractRuntimeFactory(ABC):
    """Tovární třída běhových prostředí je odpovědná za budování instancí
    potomků třídy AbstractRuntime.

    Tato je odpovědná za poskytnutí a dodání všech potřebných zdrojů pro
    vytvoření a běh běhového prostředí.

    Instance této třídy musí být schopny na požádání vytvořit novou instanci
    běhového prostředí tak, aby ji bylo možné spustit a ověřit tak plnění
    úlohy robotem s dodaným programem."""

    def __init__(self, available_units_names: "Iterable[str]",
                 robot_factory: "robot_module.RobotFactory",
                 world_factory: "world_fact_module.WorldFactory",
                 target_factory: "target_module.TargetFactory"):
        """Initor třídy, který přijímá instance továren, které budou dále
        použity pro přípravu běhového prostředí.

        V první řadě přijímá seznam názvů jednotek, kterými je možné robota
        osadit. Jejich továrny musí být k dispozici, jinak tato továrna musí
        při tvorbě instance běhového prostředí vyhazovat výjimku.

        Vedle toho přijímá initor továrnu robotů, která slouží ke generování
        a úvodní přípravě instancí robotů, kteří se budou v běhovém prostředí
        vyskytovat.

        Dále přijímá továrnu světa, které bude použito pro generování světa,
        s nímž bude robot interagovat a v kterém bude plnit svoji úlohu.

        Konečně přijímá i instanci samotné úlohy, která má být v rámci tohoto
        běhového prostředí splněna a která testuje kvalitu programu.
        """

        # Evidence všech jednotek, kterými je možné robota osadit
        self._available_units_names = list(available_units_names)

        # Uložení potřebných továren - robotů, světa a úlohy
        self._robot_factory = robot_factory
        self._world_factory = world_factory
        self._target_factory = target_factory

    @property
    def available_units_names(self) -> "tuple[str]":
        """Funkce vrací názvy všech jednotek, které by měly být robotům k
        dispozici pro plnění jejich cílů a kterými je možné tyto roboty osadit.
        """
        return tuple(self._available_units_names)

    @property
    def robot_factory(self) -> "robot_module.RobotFactory":
        """Vlastnost vrací továrnu robotů, které bude použito pro tvorbu
        robotů."""
        return self._robot_factory

    @property
    def world_factory(self) -> "world_fact_module.WorldFactory":
        """Vlastnost vrací továrnu světa, která je použita pro tvorbu světa,
        se kterým bude robot interagovat."""
        return self._world_factory

    @property
    def target_factory(self) -> "target_module.TargetFactory":
        """Vlastnost vrací továrnu úlohy, které bude použito pro tvorbu úlohy.
        """
        return self._target_factory

    @abstractmethod
    def build(self, platform: "platform_module.Platform",
              program: "program_module.AbstractProgram") -> "AbstractRuntime":
        """Abstraktní funkce odpovědná za vybudování nové instance potomka
        třídy AbstractRuntime.

        V parametru přijímá instanci platformy, které toto běhové prostředí
        náleží, vedle reference na program, který mají roboti mít a dle
        kterého se mají chovat."""

    @staticmethod
    def pick_unit_factories(platform: "platform_module.Platform",
                            unit_names: "Iterable[str]"):
        """Statická funkce se pokusí vybrat z dodané platformy všechny
        tovární třídy jednotek tak, aby byl zjednodušen přenos z jejich
        názvu na konkrétní instance.

        K seznamu registrovaných a použitelných továren jednotek se přistupuje
        přes správce továren jednotek a jeho funkci pro vyhledávání těchto
        továren dle názvu ('factory_by_unit_name(str)'). Ta vyhazuje výjimku,
        není-li taková jednotka k nalezení. V takovém případě není odchycena
        a tato probublává výše.
        """

        # Seznam továrních jednotek
        uf = []

        # Pro každý název jednotky
        for unit_name in unit_names:

            # Přidej získanou továrnu
            uf.append(platform.unit_factory_manager.factory_by_unit_name(
                unit_name))

        # Vrácení naplněného seznamu továrnami jednotek
        return uf




