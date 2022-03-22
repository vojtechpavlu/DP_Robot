""""""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.utils.named import Named


class Target(Named):
    """Instance třídy Target reprezentují konkrétní úlohu, která má být řešena.
    Z důvodu potřeby variability slouží tyto instance coby kontejnery pro
    jednotlivé úkoly (jmenovitě instance třídy Task).

    Úloze vedle toho náleží i potřeba být pojmenována. Proto dědí protokol
    třídy 'Named'.
    """

    def __init__(self, name: str):
        """"""
        Named.__init__(self, name)
        self._tasks: "list[Task]" = []

    @property
    def tasks(self) -> "tuple[Task]":
        """Vlastnost vrací ntici úkolů v rámci úlohy, které mají být
        testovány."""
        return tuple(self._tasks)

    def add_task(self, task: "Task"):
        """Metoda přidává úkol ke splnění do této úlohy."""
        self._tasks.append(task)


class TargetFactory(ABC):
    """Abstraktní třída TargetFactory se zaměřuje na poskytování služby tvorby
    instancí úloh, tedy instancí třídy 'Target'."""

    @abstractmethod
    def build(self) -> "Target":
        """Abstraktní metoda 'build' se zabývá tvorbou zadání úlohy."""

