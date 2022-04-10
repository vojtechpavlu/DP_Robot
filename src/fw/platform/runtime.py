"""Tento modul je odpovědný za definici protokolu běhového prostředí a
protokolu jeho tovární třídy. Je zde tedy obsažena definice AbstractRuntime
(abstraktní třída běhového prostředí) a AbstractRuntimeFactory (abstraktní
třída továrny běhových prostředí).
"""


# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Iterable, Callable
from threading import Thread

# Import lokálních knihoven
from src.fw.platform.robot_program_executor import RobotProgramExecutor
from src.fw.robot.mounting_error import MountingError
from src.fw.utils.error import PlatformError
from src.fw.utils.identifiable import Identifiable

import src.fw.world.world as world_module
import src.fw.world.world_factory as world_fact_module
import src.fw.robot.robot as robot_module
import src.fw.target.target as target_module
import src.fw.robot.program as program_module
import src.fw.robot.unit as unit_module
import src.fw.robot.robot_container as robot_cont_module
import src.fw.platform.platform as platform_module
import src.fw.target.event_handling as event_module
import src.fw.platform.runtime_events as runtime_events
import src.fw.utils.logging.logger as logger_module


class AbstractRuntime(Identifiable, event_module.EventEmitter):
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
                 platform: "platform_module.Platform",
                 logger: "logger_module.Logger"):
        """Initor funkce, který přijímá tovární třídu světa, tovární třídu
        úlohy, množinu povolených továrních tříd jednotek a referenci na
        program."""

        Identifiable.__init__(self)
        event_module.EventEmitter.__init__(self)

        self._target_factory = target_factory
        self._world_factory = world_factory
        self._unit_factories = tuple(unit_factories)
        self._program = program
        self._robot_factory = robot_factory
        self._platform = platform
        self._logger = logger

        self._world = None
        self._target = None

        # Příprava logovacího potrubí
        self._logger_pipeline = logger.make_pipeline("runtime").log

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

    @property
    def logger(self) -> "logger_module.Logger":
        """"""
        return self._logger

    @property
    def log(self) -> "Callable":
        """Vlastnost vrací funkci reprezentující potrubí, pomocí kterého lze
        vytvářet záznamy."""
        return self._logger_pipeline

    @property
    @abstractmethod
    def robots(self) -> "tuple[robot_module.Robot]":
        """Abstraktní vlastnost definuje protokol, který umožňuje získat
        referenci na všechny roboty, kteří se v kontextu tohoto běhového
        prostředí vyskytovali."""

    def prepare(self):
        """Funkce připravující svět a úlohu ke spuštění. V podstatě si z
        dodaných továren nechá příslušné instance vygenerovat.
        """
        # Tvorba světa
        self._world = self.world_factory.build(self.logger)

        # Dodání reference světa pro přípravu úlohy; aby úloha mohla být
        # provázána se světem a sledovat v něm plnění úkolů této úlohy
        self._target = self.target_factory.build(self._world, self.logger)

        # Vytvoření a vyhození události, že běhové prostředí bylo připraveno
        self.notify_all_event_handlers(
            runtime_events.RuntimePreparedEvent(self))

    def check_mounting(self, robot: "robot_module.Robot"):
        """Funkce se pokusí ověřit, že je osazení platné. Robot může být
        po ukončení osazovací procedury pouze povolenými jednotkami. Pokud
        tomu tak není, je vyhozena výjimka."""

        self.log("Kontroluji osazení robota jednotkami")

        # Pro každou jednotku, kterou je dodaný robot osazen
        for unit in robot.units:

            # Pro každou továrnu jednotek, které jsou povolené
            for uf in self.unit_factories:

                # Pokud je továrna jednotek a továrna té dané jednotky
                # identická instance, ukonči vnitřní cyklus
                if unit.unit_factory.int_id == uf.int_id:
                    self.log(f"Jednotka", unit.name, "je v pořádku")

                    # Jelikož si odpovídá továrna jednotek a jednotka, přeruš
                    break

            # Pokud nebyl vnitřní cyklus předčasně ukončen, vyhoď výjimku
            else:
                raise MountingError(
                    f"Jednotka '{unit.name}' není pro toto běhové prostředí "
                    f"povolena", robot, unit)

    def connect_with_interface(self, robot: "robot_module.Robot"):
        """Funkce je odpovědná za napojení všech jednotek dodaného robota na
        rozhraní světa.
        """

        self.log("Propojuji jednotky robota s rozhraním světa")

        # Pro každou jednotku robota
        for unit in robot.units:

            # Nastav jednotce rozhraní světa
            unit.set_world_interface(self.world.world_interface)

            # Přidej mu z titulu dědění 'InteractionHandlerManager'
            # požadovaný handler interakcí
            self.world.world_interface.add_interaction_handler(
                unit.unit_factory.interaction_handler)

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
                 platform: "platform_module.Platform",
                 logger: "logger_module.Logger"):
        """Initor třídy, který přijímá tovární třídy (továrnu světa, úlohy,
        robotů a továrny jednotek) a referenci na program, který má být pro
        jediného robota spuštěn. Dále přijímá referenci na platformu, pod
        kterou je toto běhové prostředí spuštěno.
        """
        # Volání předka
        AbstractRuntime.__init__(
            self, world_factory, target_factory, unit_factories, program,
            robot_factory, platform, logger)

        # Příprava kontejneru robota
        self.__robot_container = robot_cont_module.SingleRobotContainer()
        self.__robot_container.robot = self.robot_factory.build(
            self.logger.make_pipeline("robot").log)

    @property
    def robots(self) -> "tuple[robot_module.Robot]":
        """Vlastnost vrací jediného robota, který je v této instanci evidován,
        a to obaleného nticí."""
        return tuple([self.robot])

    @property
    def robot(self) -> "robot_module.Robot":
        """Vlastnost vrací jediného robota, kterého toto prostředí má. Ten
        je uložen v privátním kontejneru typu 'SingleRobotContainer', který
        co nejvíce znesnadňuje jakoukoliv nepravou manipulaci."""
        return self.__robot_container.robot

    def run(self):
        """Hlavní funkce třídy, která se stará o řízení běhu jediného robota.
        """

        self.log("Příprava běhového prostředí")

        # Příprava prostředí
        self.prepare()

        self.log("Osazování robota")

        # Nastavení programu pro robota
        self.robot.program = self.program

        # Spuštění přípravné procedury pro osazování robota
        self.program.mount(self.robot, self.units)

        try:
            # Kontrola osazení
            self.check_mounting(self.robot)

            # Napojení všech jednotek robota na rozhraní světa
            self.connect_with_interface(self.robot)

            # Zasazení robota do světa pomocí registrace jeho stavu
            self.world.robot_state_manager.register_robot(self.robot)

            # Vytvoření exekutoru, pomocí kterého bude program robota spuštěn
            executor = RobotProgramExecutor(
                self.program, self.robot, self.logger.make_pipeline("output"))

            # Spuštění běhu programu přes exekutor ve vlákně
            robot_thread = Thread(target=executor.run_program)

            # Odeslání události o počátku běhu robota
            self.notify_all_event_handlers(
                runtime_events.RuntimeStartedEvent(self))

            self.log("Spouštím program robota")

            # Samotné spuštění programu robota (ve vlákně) a join vlákna
            robot_thread.start()
            robot_thread.join()

            # Vyhození výjimek reprezentující chyby, ke kterým došlo při
            # běhu programu exekutorem
            if executor.raised_any:
                raise executor.raised_exception

        # Pokud dojde k chybě při osazení; když se při osazování podvádí
        except MountingError as e:
            for unit in self.robot.units:
                unit.deactivate()

        # Předčasné ukončení programu
        except program_module.ProgramTermination as pt:
            if pt.abort_type == program_module.AbortType.SUCCESS:
                self.log("Program se předčasně ukončil po dokončení cíle:",
                         pt.message)
            elif pt.abort_type == program_module.AbortType.FAILURE:
                self.log("Program narazil na neřešitelný problém:", pt.message)
            elif pt.abort_type == program_module.AbortType.ERROR:
                self.log("Program vyústil v chybu:", f"'{pt.message}'")

        except PlatformError as pe:
            self.robot.deactivate()

            import traceback
            import sys

            self.log(f"Byla vyhozena výjimka: '{pe}'")
            traceback.print_exception(*sys.exc_info())

        # Libovolná jiná chyba; je vyhozena nová výjimka
        except Exception as e:
            self.robot.deactivate()

            import traceback
            import sys

            self.log(f"Byla vyhozena výjimka: '{e}'")
            traceback.print_exception(*sys.exc_info())

        # Ať už došlo k chybě či nikoliv, proveď výstup
        finally:
            self.log(50*"=")
            self.log("EVALUATION:")

            for task in self.target.tasks:
                self.log(task.name)
                from src.fw.target.evaluation_function import EvaluationFunctionJunction
                if isinstance(task.evaluation_function, EvaluationFunctionJunction):
                    junction = task.evaluation_function
                    for ef in junction.evaluation_functions:
                        self.log("\t", ef.name, ef.eval())
                else:
                    ef = task.evaluation_function
                    self.log("\t", ef.name, ef.eval())

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
              program: "program_module.AbstractProgram",
              logger: "logger_module.Logger") -> "AbstractRuntime":
        """Abstraktní funkce odpovědná za vybudování nové instance potomka
        třídy AbstractRuntime.

        V parametru přijímá instanci platformy, které toto běhové prostředí
        náleží, vedle reference na program, který mají roboti mít a dle
        kterého se mají chovat.

        Dále je této funkci poskytnut logger, pomocí kterého budou schopny
        jednotlivé významné komponenty dělat záznamy o své aktivitě."""

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

        Speciálním případem použití je, bude-li mezi názvy továrních jednotek
        uveden řetězec sestávající se z pouze hvězdičky ('*'). Pak budou
        vráceny všechny továrny jednotek
        """

        # Pokud je mezi předepsanými názvy požadovaných továren jednotek
        # hvězdička, budou vráceny všechny dostupné továrny jednotek
        if "*" in unit_names:
            return platform.unit_factories

        # V opačném případě bude provedena selekce dle požadovaných názvů
        else:

            # Seznam továrních jednotek
            uf = []
            # Pro každý název jednotky
            for unit_name in unit_names:

                # Přidej získanou továrnu
                uf.append(platform.unit_factory_manager.factory_by_unit_name(
                    unit_name))

            # Vrácení naplněného seznamu továrnami jednotek
            return uf




