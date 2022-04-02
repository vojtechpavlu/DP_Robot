"""Tento modul obsahuje sdružení funkcionality v kontextu platformy.
Obsahuje tedy funkcionalitu ohledně řízení tvorby běhových prostředí,
jejich životní cyklus a vytváření závěrů z jednotlivých běhů.

Především obsahuje definici třídy Platform, která je svým způsobem centrálním
uzlem celého systému."""


# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.utils.loading.unit_factory_loader as ufl_module
import src.fw.utils.loading.runtime_factory_loader as rtf_module
import src.fw.utils.loading.program_loader as program_loader
import src.fw.platform.unit_factories_manager as uf_manager_module
import src.fw.platform.program_manager as prg_manager_module
import src.fw.platform.runtime_factory_manager as rtf_manager_module
import src.fw.platform.runtime as runtime_module
import src.fw.robot.program as program_module
import src.fw.robot.robot as robot_module
import src.fw.robot.unit as unit_module
from src.fw.utils.error import PlatformError


class Platform:
    """Třída Platform definuje protokol takových instancí, které umožňují
    řídit celý životní cyklus běhových prostředí. Od jejich dynamického
    načtení, přes samostatné, izolované spuštění, až po jejich ukončení.

    K tomu jí slouží především správci:
        - Správce továren jednotek (UnitFactoryManager)
        - Správce programů (ProgramManager)
        - Správce továren běhových prostředí (RuntimeFactoryManager)
    """

    def __init__(self,
                 unit_fact_loaders: "Iterable[ufl_module.UnitFactoryLoader]",
                 program_loaders: "Iterable[program_loader.ProgramLoader]",
                 runtime_loader: "rtf_module.RuntimeFactoryLoader"):
        """Initor třídy, který přijímá loadery jednotlivých funkčních
        bloků.

        Konkrétně přijímá instance třídy UnitFactoryLoader, které jsou
        odpovědné za načtení definic všech továren jednotek, dále instance
        ProgramLoader, které jsou odpovědné za načítání odevzdaných programů
        k otestování, a také instanci třídy RuntimeFactoryLoader, která je
        odpovědná za načtení a přípravu běhových prostředí, jenž budou dále
        použita pro ověření správné funkcionality programů (v kontextu plnění
        zadané úlohy).

        Tyto tři prvky si initor převádí do instancí správců:
            - UnitFactoryManager,
            - ProgramManager a
            - RuntimeFactoryManager.

        S těmito správci pak instance této třídy řídí celý proces životního
        cyklu jednotlivých běhových prostředí pro každý program.
        """
        self._unit_factory_manager = uf_manager_module.UnitFactoryManager(
            unit_fact_loaders)
        self._program_manager = prg_manager_module.ProgramManager(
            program_loaders)
        self._runtime_factory_manager = (
                rtf_manager_module.RuntimeFactoryManager(runtime_loader))

        self._runtimes: "list[runtime_module.AbstractRuntime]" = []

    @property
    def unit_factory_manager(self) -> "uf_manager_module.UnitFactoryManager":
        """Vlastnost vrací správce jednotek, který poskytuje reference na
        všechny potenciálně použitelné jednotky prostřednictvím jejich
        továren."""
        return self._unit_factory_manager

    @property
    def program_manager(self) -> "prg_manager_module.ProgramManager":
        """Vlastnost vrací správce programů, který poskytuje všechny načtené
        programy, jenž je třeba otestovat, a které byly kontextově vymezeny
        loaderem dodaným v initoru této třídy.
        """
        return self._program_manager

    @property
    def runtime_factory_manager(
            self) -> "rtf_manager_module.RuntimeFactoryManager":
        """Vlastnost vrací správce továren běhových prostředí, který poskytuje
        všechna běhová prostředí z předepsaného kontextu (definovaného
        loaderem v initoru třídy).
        """
        return self._runtime_factory_manager

    @property
    def runtime_factories(
            self) -> "tuple[runtime_module.AbstractRuntimeFactory]":
        """Vlastnost vrací ntici všech továrních jednotek, které byly v rámci
        dynamického načítání pluginů získány."""
        return self.runtime_factory_manager.registered_factories

    @property
    def programs(self) -> "tuple[program_module.AbstractProgram]":
        """Vlastnost vrací ntici všech programů, které byly v rámci
        dynamického načítání pluginů získány pro dané zadání."""
        return self.program_manager.registered_programs

    @property
    def all_runtimes(self) -> "tuple[runtime_module.AbstractRuntime]":
        """Vlastnost vrací ntici všech běhových prostředí, která byla spuštěna.
        """
        return tuple(self._runtimes)

    @property
    def unit_factories(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """Vlastnost vrací ntici továren jednotek, které byly dynamicky
        načteny z příslušných pluginů."""
        return self.unit_factory_manager.registered_factories

    def load(self):
        """Vlastnost je odpovědná za načtení všech pluginů. Jmenovitě se stará
        o dynamické načítání pluginů továren jednotek, zadání (tedy továren
        běhových prostředí a programů).

        Funkce je také odpovědná za zkontrolování načtených zdrojů. Pokud
        se nepovede některému z správců (pomocí svých příslušných loaderů)
        načíst jediný zdroj, je vyhozena příslušná výjimka."""

        self.unit_factory_manager.load()
        self.runtime_factory_manager.load()
        self.program_manager.load()

        """Kontrola načtených zdrojů co do počtu. Pokud nebyl pro příslušného
        správce načten jediný plugin, je vyhozena příslušná výjimka."""

        # Kontrola načtení továren jednotek
        if len(self.unit_factories) == 0:
            raise PlatformLoadingError(
                f"Nebyla načtena jediná továrna jednotek", self)

        # Kontrola načtení továren běhových prostředí
        elif len(self.runtime_factories) == 0:
            raise PlatformLoadingError(
                f"Nebyla načtena jediná továrna běhových prostředí", self)

        # Kontrola načtení programů
        elif len(self.programs) == 0:
            raise PlatformLoadingError(
                f"Nebyl načten jediný program ke spuštění", self)

    def run(self):
        """Funkce odpovědná za spuštění jednotlivých běhových prostředí.

        V první fázi se funkce stará o načtení všech zdrojů, které jsou pro
        běh nezbytně nutné. To provádí s pomocí funkce 'load()'. Teprve poté
        je tato způsobilá jednotlivá běhová prostředí spouštět.

        Schéma běhů je takové, že pro každou továrnu běhového prostředí je
        pro každý získaný program vytvořeno a v rámci programu také spuštěno
        běhové prostředí.
        """
        # Načtení důležitých zdrojů
        self.load()

        # Výmaz evidovaných běhových prostředí
        self._runtimes: "list[runtime_module.AbstractRuntime]" = []

        """Postupné spouštění všech běhových prostředí"""

        # Pro každou továrnu běhového prostředí
        for runtime_factory in self.runtime_factories:

            # Pro každý program
            for program in self.programs:

                # Vytvoření běhového prostředí
                runtime = runtime_factory.build(self, program)

                # Registrace běhového prostředí
                self._runtimes.append(runtime)

                # Spuštění běhového prostředí
                runtime.run()


class PlatformLoadingError(PlatformError):
    """Výjimka symbolizující vznik problému při načítání platformy a jejích
    potřebných zdrojů.

    Svého předka obohacuje o referenci na instanci třídy Platform, v jejímž
    kontextu došlo k chybě."""

    def __init__(self, message: str, platform: "Platform"):
        """Initor, který přijímá zprávu o chybě a referenci na instanci
        třídy Platform, v jejímž kontextu došlo k chybě. Zpráva je postoupena
        initoru předka.
        """
        # Volání předka
        PlatformError.__init__(self, message)

        # Uložení instance platformy, v jejímž kontextu došlo k chybě
        self._platform = platform

    @property
    def platform(self) -> "Platform":
        """Vlastnost vrací platformu, v jejímž kontextu došlo k chybě."""
        return self._platform
