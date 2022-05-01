"""Tento modul je odpovědný za řízení testování splnění stanovených cílů
robota v dodaném prostředí.

Především je zde připravena třída Target odpovědná za sdružování a celkovou
evaluaci, vedle toho i abstraktní třída TargetFactory, která je odpovědná za
tvorbu a přípravu takových instancí.
"""

# Prevence cyklických importů
from __future__ import annotations

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.utils.described import Described
from src.fw.utils.error import PlatformError
from src.fw.utils.named import Named

import src.fw.target.task as task_module
import src.fw.world.world as world_module
import src.fw.utils.logging.logger as logger_module
import src.fw.platform.runtime as runtime_module


class Target(Named, Described):
    """Instance třídy Target reprezentují konkrétní úlohu, která má být řešena.
    Z důvodu potřeby variability slouží tyto instance coby kontejnery pro
    jednotlivé úkoly (jmenovitě instance třídy Task).

    Úloze vedle toho náleží i potřeba být pojmenována. Proto dědí protokol
    třídy 'Named'. Stejně tak vyžadujeme, aby byla úloha i popsána, co do
    jejího účelu, lidsky čitelných cílů a případně co úloha testuje. Proto
    dědí také tentokrát třídu Described.
    """

    def __init__(self, target_name: str, target_description: str,
                 world: "world_module.World", logger: "logger_module.Logger"):
        """Initor třídy, který přijímá název úlohy a její popis. Obé je v
        podobě textového řetězce.

        Název by měl sloužit spíše k jednoduché, člověku srozumitelné
        identifikaci, přičemž popis by v sobě měl nést informace o podstatě,
        smyslu a požadovaném výstupu řešení pro tuto úlohu.
        """
        Named.__init__(self, target_name)
        Described.__init__(self, target_description)

        """Reference na svět, který má za úkol daná úloha sledovat. Díky tomu
        je schopná úloha kontrolovat naplnění svého cíle testování."""
        self._world = world

        """Reference na běhové prostředí, které může vydávat své vlastní
        události."""
        self._runtime: runtime_module.AbstractRuntime = None

        """Příprava seznamu, který bude použit pro ukládání úkolů ke splnění.
        V úvodní fázi životního cyklu je pochopitelně tento seznam defaultně
        prázdný. Instance třídy 'Task' jsou do něj dodávány až za běhu."""
        self._tasks: "list[task_module.Task]" = []

        """Uložení dodaného loggeru. Toho je použito hlavně pro zaznamenání,
        že některý úkol (či jeho součást) byl splněn."""
        self._logger = logger

    @property
    def tasks(self) -> "tuple[task_module.Task]":
        """Vlastnost vrací ntici úkolů v rámci úlohy, které mají být
        testovány."""
        return tuple(self._tasks)

    @property
    def world(self) -> "world_module.World":
        """Vlastnost vrací svět, pro který je tato úloha definována."""
        return self._world

    @property
    def logger(self) -> "logger_module.Logger":
        """Vlastnost vrací logger, kterého je použito pro zaznamenávání
        údajů v případě splnění nějakého úkolu nebo podúkolu."""
        return self._logger

    @property
    def evaluate(self) -> float:
        """Vlastnost vrací celkovou evaluaci úlohy co do jejího splnění.
        Vrací podíl míry naplnění úkolů, tedy hodnoty z intervalu [0, 1].
        """
        all_summed = 0
        for task in self.tasks:
            all_summed += task.numeric_evaluation
        return all_summed / len(self.tasks)

    @property
    def runtime(self) -> runtime_module.AbstractRuntime:
        """Vlastnost vrací nastavené běhové prostředí."""
        return self._runtime

    @runtime.setter
    def runtime(self, new_runtime: runtime_module.AbstractRuntime):
        """Setter pro běhové prostředí. Pokud je již nastaveno, je vyhozena
        výjimka, stejně jako pokud se pokusí uložit hodnotu None."""

        if new_runtime is None:
            raise TargetError(
                "Nově nastavovaná hodnota běhového prostředí nesmí být None",
                self)
        elif self.runtime is not None:
            raise TargetError(
                "Běhové prostředí nelze přenastavovat", self)
        else:
            self._runtime = new_runtime

    def add_task(self, task: "task_module.Task"):
        """Metoda přidává úkol ke splnění do této úlohy."""
        # Uložení do evidence úkolů
        self._tasks.append(task)

        # Nastavení této instance úlohy do úkolu
        task.target = self

        # Přiřazení loggeru k použití
        task.log = self.logger.make_pipeline("task").log


class TargetFactory(ABC):
    """Abstraktní třída TargetFactory se zaměřuje na poskytování služby tvorby
    instancí úloh, tedy instancí třídy 'Target'."""

    @abstractmethod
    def build(self, world: "world_module.World",
              logger: "logger_module.Logger") -> "Target":
        """Abstraktní metoda 'build' se zabývá tvorbou zadání úlohy.
        Funkce přijímá referenci na svět, který má za úkol úloha sledovat
        co do jejího splnění."""


class AlwaysCompletedTargetFactory(TargetFactory):
    """Tovární třída, která vytváří automaticky splněnou úlohu. Její smysl
    je spíše pro potřeby testování a debugging.

    Úloha je naplněna pouze jediným úkolem, který je považován automaticky
    za splněný, neboť má tak nastavenu i evaluační funkci vracející za všech
    okolností hodnotu True."""

    def build(
            self, world: "world_module.World",logger: "logger_module.Logger",
            name: str = "Always successful target",
            desc: str = "Úloha, která je automaticky splněna") -> "Target":
        """Funkce odpovědná za vytvoření úlohy, která je automaticky
        považována za splněnou, neboť má jediný úkol, který je de facto
        také automaticky splněn.
        """
        target = Target(name, desc, world, logger)
        target.add_task(task_module.always_true_task())
        return target


class TargetError(PlatformError):
    """"""
    def __init__(self, message: str, target: Target):
        PlatformError.__init__(self, message)
        self.target = target


