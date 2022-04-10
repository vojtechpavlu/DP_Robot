"""Plugin obsahuje definici programu, který nesplní úspěšně žádné nebo téměř
žádné úkoly."""

# Import potřebných zdrojů a nástrojů
from typing import Callable

from src.fw.robot.program import AbstractProgram, AbortType
from src.fw.robot.robot import Robot

# Jméno autora, který je odpovědný za daný program
_AUTHOR_NAME = "Vojtěch Pavlů"


class Program(AbstractProgram):
    """Tato instance definuje takový program, který úspěšně nesplní téměř
    žádný nebo vůbec žádný svůj úkol."""

    def run(self, robot: "Robot", log: Callable):
        """Funkce zaloguje jednotky, kterými je robot osazen. Ovšem celou
        kolekci těchto jednotek, nikoliv pouze jejich názvy."""
        log(robot.units)


def get_program():
    """Tovární (přístupová) funkce, která vrací zcela novou instanci programu.

    Tato funkce má pevně stanovený název, čehož se využívá v rámci dynamického
    importování pluginů; v tomto případě pluginu programu. Pokud by se název
    této přístupové funkce neshodoval s předepsaným a vyhledávaným názvem,
    nebude tento modul považovaný za validní a použitelný plugin programu a
    z titulu loaderu programů bude tento vyhodnocen jako potenciálně rizikový.
    """
    return Program(_AUTHOR_NAME)



