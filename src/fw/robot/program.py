"""Modul 'program.py' je odpovědný za sdružování základních prostředků pro
manipulaci a běh programu, který řídí robota."""

# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Iterable
from enum import Enum

# Import lokálních knihoven
import src.fw.robot.robot as robot_module
import src.fw.robot.unit as unit_module

from src.fw.utils.error import PlatformError


class AbortType(Enum):
    """Výčtový typ 'AbortType' definuje podrobnější specifikaci, s jakou
    byl program ukončen.

    Uvažujeme zde 3 typy ukončení programu z vlastní vůle:
        - SUCCESS:  Program splnil svůj cíl, splnění rozpoznal a tímto
                    ukončuje svoji činnost.

        - FAILURE:  Program rozpoznal, že cíle se dosáhnout za daných
                    okolností nedá; přesto je jeho chování validní.

        - ERROR:    Program se ukončuje, neboť narazil na chybu a upozorňuje
                    na ní tímto prohlášením.
    """
    SUCCESS, FAILURE, ERROR = range(3)


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
    def terminate(self, message: str = "",
                  abort_type: "AbortType" = AbortType.ERROR):
        """Metoda slouží k předčasnému ukončení robota. Přesněji tím
        program vyjadřuje své ukončení, neboť rozpoznal situaci, kdy je
        vhodné se ukončit. Především je tento způsob vhodný tehdy, když
        robot úspěšně splní svůj cíl, když zjistí, že cíl je nedosažitelný
        nebo když narazí na neřešitelnou chybu.

        Kromě způsobu ukončení ('abort_type') je v parametru funkce dodána
        i podrobnější zpráva, proč k ukončení došlo ('message'). Tím je
        umožněna lepší klasifikace, k čemu vlastně došlo."""
        raise ProgramTermination(message, self, abort_type)


class ProgramTermination(PlatformError):
    """Výjimka reprezentující ukončení z vůle programu. Kromě zprávy je tato
    výjimka nosičem reference na program, který se ukončil, a na typ ukončení.
    """

    def __init__(self, message: str, program: AbstractProgram,
                 abort_type: AbortType):
        """Initor třídy výjimky, který má za cíl v první řadě zavolat
        initor předka a uložit potřebné atributy.

        Atributy této výjimky jsou především reference na program, který
        se rozhodl předčasně ukončit a typ, s jakým se rozhodl program
        ukončit.
        """
        PlatformError.__init__(self, message)

        self._program = program
        self._abort_type = abort_type

    @property
    def program(self) -> AbstractProgram:
        """Vlastnost vrací referenci na program, který se ukončil."""
        return self._program

    @property
    def abort_type(self) -> AbortType:
        """Vlastnost vrací typ, s jakým se program ukončil."""
        return self._abort_type

