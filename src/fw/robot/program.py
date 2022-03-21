"""Modul 'program.py' je odpovědný za sdružování základních prostředků pro
manipulaci a běh programu, který řídí robota."""

# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Iterable

# Import lokálních knihoven
import src.fw.robot.robot as robot_module
import src.fw.robot.unit as unit_module


class AbstractProgram(ABC):
    """Abstraktní třída definující protokol programu robota. Ten je definován
    několika základími atributy:

        - jménem autora, ve kterém se autor programu podepisuje

        - procedurou osazování, která definuje, jakými jednotkami by měl být
          robot osazen

        - procedurou spouštějící program, v níž je implementován způsob
          dosažení požadovaného cíle programu pomocí dodaného robota

        - procedurou ukončení programu, která způsobuje předčasné ukončení
          programu. Toho se dá využít v případě, že program rozpozná, že:
              - úspěšně splnil svůj cíl
              - cíle se dosáhnout nedá
              - narazil na chybu
    """

    def __init__(self, author_name: str):
        """Jednoduchý initor funkce, který slouží k uchování svých
        potřebných atributů. Jmenovitě jde především o jméno autora programu.
        """
        self._author_name = author_name

    @property
    def author_name(self) -> str:
        """Funkce vrací jméno autora tohoto programu."""
        return self._author_name

    @abstractmethod
    def mount(self, robot: "robot_module.Robot",
              available_units: "Iterable[unit_module.Unit]"):
        """Abstraktní metoda reprezentující proceduru nastavení osazení
        robota požadovanými jednotkami."""

    @abstractmethod
    def run(self, robot: "robot_module.Robot"):
        """Hlavní metoda, kterou program má. Implementace této abstraktní
        metody slouží k obsluze celého robota při interakci se světem.
        """

    @abstractmethod
    def terminate(self):
        """Metoda slouží k předčasnému ukončení robota. Přesněji tím
        program vyjadřuje své ukončení, neboť rozpoznal situaci, kdy je
        vhodné se ukončit. Především je tento způsob vhodný tehdy, když
        robot úspěšně splní svůj cíl, když zjistí, že cíl je nedosažitelný
        nebo když narazí na neřešitelnou chybu."""


