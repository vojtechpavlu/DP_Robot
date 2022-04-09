"""V tomto modulu je uvedena základní definice pro vypisování výsledků výstupů
do konzole."""

# Import standardních knihoven
import math
from typing import Iterable

# Import lokálních knihoven
from src.fw.target.evaluation_function import EvaluationFunctionJunction
from src.fw.target.results.result_builder import (
    PlatformResultBuilder, RuntimeResultBuilder)

import src.fw.platform.platform as platform_module
import src.fw.platform.runtime as runtime_module

# Stanovená doporučená délka řádku
_LINE_LENGTH = 80


class RuntimeResultPrinter(RuntimeResultBuilder):
    """Instance této třídy jsou odpovědné za vypsání všech výsledků
    na konzoli."""

    def __init__(self, runtime: "runtime_module.AbstractRuntime"):
        """Initor, který přijímá běhové prostředí, které má být zhodnoceno."""
        RuntimeResultBuilder.__init__(self, runtime)

    def build(self):
        """Tato metoda se stará o vypsání výsledků běhového prostředí
        do konzole."""

        print("\n")
        print(_LINE_LENGTH * "-")
        print("VYHODNOCENÍ BĚHOVÉHO PROSTŘEDÍ".center(_LINE_LENGTH, "-"))
        print(_LINE_LENGTH * "-", "\n")
        print("Autor:".ljust(8), self.author_name)
        print("Plugin:".ljust(8), self.program.path)
        print("Úloha:".ljust(8), self.target.name, "-",
              self.target.description)
        print("Plnění úkolů".center(_LINE_LENGTH, "-"))

        for task in self.target.tasks:
            print(f"+ {task.name.ljust(70, '-')}{'✓' if task.eval() else '✗'}")
            ef = task.evaluation_function
            print(f"\t- {ef.name.ljust(66, '.')}{'✓' if ef.eval() else '✗'}")
            if isinstance(ef, EvaluationFunctionJunction):
                for subef in ef.evaluation_functions:
                    print(f"\t\t{subef.name.ljust(64, '.')}"
                          f"{'✓' if subef.eval() else '✗'}")
            print()

        print("Úspěšnost:", int((self.target.evaluate * 100) + 0.5), "%")

        outputs = self.runtime.logger.outputs
        output_logger = None

        for o in outputs:
            if o.has_memo and (o.has_context("OUTPUT") or o.takes_all):
                output_logger = o

        print("Výstupy programu".center(_LINE_LENGTH, "-"))
        for log in output_logger.filter_by_context("OUTPUT"):
            print(f"[{log.time}] '{log.message}'")
        print()
        print(_LINE_LENGTH*"-")
        print("KONEC VYHODNOCENÍ RUNTIME".center(_LINE_LENGTH, "-"))
        print(_LINE_LENGTH*"-")


class PlatformResultPrinter(PlatformResultBuilder):
    """Instance této třídy jsou odpovědné za vypsání všech výsledků na
    konzoli."""

    def __init__(self, platform: "platform_module.Platform",
                 uf_loading: bool = True, rt_loading: bool = True,
                 p_loading: bool = True):
        """Initor, který přijímá platformu, která má být zhodnocena."""
        PlatformResultBuilder.__init__(self, platform)
        self._uf_loading = uf_loading
        self._rt_loading = rt_loading
        self._p_loading = p_loading

    def build(self):
        """Funkce vypíše na konzoli celkové vyhodnocení platformy.
        """

        print("\n")
        print(_LINE_LENGTH * "=")
        print("VYHODNOCENÍ PLATFORMY".center(_LINE_LENGTH, "="))
        print(_LINE_LENGTH * "=")

        if self._uf_loading:
            # NAČÍTÁNÍ TOVÁREN JEDNOTEK
            print("\n")
            print(_LINE_LENGTH * "-")
            print("NAČTENÉ TOVÁRNY JEDNOTEK".center(_LINE_LENGTH))
            print(_LINE_LENGTH * "-")
            self._build_plugins(self.unit_factories_loaders)

        if self._rt_loading:
            # NAČÍTÁNÍ TOVÁREN BĚHOVÝCH PROSTŘEDÍ
            print("\n")
            print(_LINE_LENGTH * "-")
            print("NAČTENÁ BĚHOVÁ PROSTŘEDÍ".center(_LINE_LENGTH))
            print(_LINE_LENGTH * "-")
            self._build_plugins([self.runtime_factory_loader])

        if self._p_loading:
            # NAČÍTÁNÍ PROGRAMŮ
            print("\n")
            print(_LINE_LENGTH * "-")
            print("NAČTENÉ PROGRAMY".center(_LINE_LENGTH))
            print(_LINE_LENGTH * "-")
            self._build_plugins(self.program_loaders)

        # Zhodnocení jednotlivých běhových prostředí
        print("\n")
        print(_LINE_LENGTH * "-")
        print("BĚHOVÁ PROSTŘEDÍ".center(_LINE_LENGTH))
        print(_LINE_LENGTH * "-")
        self._runtimes_evaluation()

    @staticmethod
    def _build_plugins(loaders: Iterable):
        """Funkce je odpovědná za vypsání proces dynamického načítání
        pluginů. Celý proces je unifikován pro všechny loadery, díky
        společnému předkovi PluginLoader.
        """

        # Pro každý loader
        for loader in loaders:

            # Výpis cesty, ze které bylo načítáno
            print("Destinace:", loader.destination)

            # Výpis validních a tedy použitelných pluginů
            print("\tValidní pluginy:")
            for plugin in loader.valid_plugins:
                print("\t\t +-", plugin.absolute_path)

            # Výpis identifikovaných, ale nevalidních pluginů
            print("\n\tNevalidní pluginy:")
            for plugin in loader.not_valid_plugins:
                print("\t +-", plugin.absolute_path)
                print("\t\t", list(map(
                    lambda v: v.name, plugin.violated_validators)))

            # Výpis neidentifikovaných a tedy jistě nevalidních pluginů
            print("\n\tNeidentifikované pluginy:")
            for plugin in loader.not_identified_plugins:
                print("\t +-", plugin)
                print("\t\t", list(map(
                    lambda i: i.name, loader.violated_identifiers(plugin))))

    def _runtimes_evaluation(self):
        """V této funkci je postaráno o vypisování stručného zhodnocení
        všech běhových prostředí dané platformy."""
        for runtime in self.runtimes:
            print(40*"-")
            print("Název úlohy:", runtime.target.name)
            print("Popis úlohy:", runtime.target.description)
            print("Jméno autora:", runtime.program.author_name)
            print("Úspěšnost:", math.floor(runtime.target.evaluate*100), "%")





























