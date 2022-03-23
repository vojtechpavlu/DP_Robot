"""Tento modul je odpovědný za řízení testování splnění stanovených cílů
robota v dodaném prostředí.

Především je zde připravena třída Target odpovědná za sdružování a celkovou
evaluaci, vedle toho i abstraktní třída TargetFactory, která je odpovědná za
tvorbu a přípravu takových instancí.
"""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.utils.described import Described
from src.fw.utils.named import Named
import src.fw.target.task as task_module


class Target(Named, Described):
    """Instance třídy Target reprezentují konkrétní úlohu, která má být řešena.
    Z důvodu potřeby variability slouží tyto instance coby kontejnery pro
    jednotlivé úkoly (jmenovitě instance třídy Task).

    Úloze vedle toho náleží i potřeba být pojmenována. Proto dědí protokol
    třídy 'Named'. Stejně tak vyžadujeme, aby byla úloha i popsána, co do
    jejího účelu, lidsky čitelných cílů a případně co úloha testuje. Proto
    dědí také tentokrát třídu Described.
    """

    def __init__(self, target_name: str, target_description: str):
        """Initor třídy, který přijímá název úlohy a její popis. Obé je v
        podobě textového řetězce.

        Název by měl sloužit spíše k jednoduché, člověku srozumitelné
        identifikaci, přičemž popis by v sobě měl nést informace o podstatě,
        smyslu a požadovaném výstupu řešení pro tuto úlohu.
        """
        Named.__init__(self, target_name)
        Described.__init__(self, target_description)

        """Příprava seznamu, který bude použit pro ukládání úkolů ke splnění.
        V úvodní fázi životního cyklu je pochopitelně tento seznam defaultně
        prázdný. Instance třídy 'Task' jsou do něj dodávány až za běhu."""
        self._tasks: "list[task_module.Task]" = []

    @property
    def tasks(self) -> "tuple[task_module.Task]":
        """Vlastnost vrací ntici úkolů v rámci úlohy, které mají být
        testovány."""
        return tuple(self._tasks)

    def add_task(self, task: "task_module.Task"):
        """Metoda přidává úkol ke splnění do této úlohy."""
        self._tasks.append(task)


class TargetFactory(ABC):
    """Abstraktní třída TargetFactory se zaměřuje na poskytování služby tvorby
    instancí úloh, tedy instancí třídy 'Target'."""

    @abstractmethod
    def build(self) -> "Target":
        """Abstraktní metoda 'build' se zabývá tvorbou zadání úlohy."""

