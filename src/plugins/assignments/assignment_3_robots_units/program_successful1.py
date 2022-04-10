"""Plugin obsahuje definici programu, který zcela úspěšně projde úlohou."""

# Import potřebných zdrojů a nástrojů
from typing import Callable

from src.fw.robot.program import AbstractProgram, AbortType
from src.fw.robot.robot import Robot

# Jméno autora, který je odpovědný za daný program
_AUTHOR_NAME = "Vojtěch Pavlů"


class Program(AbstractProgram):
    """Tato instance definuje takový program, který zcela jistě úspěšně splní
    všechny své úkoly."""

    def run(self, robot: "Robot", log: Callable):
        """Funkce se snaží proiterovat všemi jednotkami, kterými je robot
        osazen. Pro každou pak zaloguje její název."""
        log(robot.units[0].name)
        log(robot.units[1].name)
        log(robot.units[2].name)


def get_program():
    """Tovární (přístupová) funkce, která vrací zcela novou instanci programu.

    Tato funkce má pevně stanovený název, čehož se využívá v rámci dynamického
    importování pluginů; v tomto případě pluginu programu. Pokud by se název
    této přístupové funkce neshodoval s předepsaným a vyhledávaným názvem,
    nebude tento modul považovaný za validní a použitelný plugin programu a
    z titulu loaderu programů bude tento vyhodnocen jako potenciálně rizikový.
    """
    return Program(_AUTHOR_NAME)


