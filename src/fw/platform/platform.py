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
    def all_runtimes(self) -> "tuple[runtime_module.AbstractRuntime]":
        """Vlastnost vrací ntici všech běhových prostředí, která byla spuštěna.
        """
        return tuple(self._runtimes)



