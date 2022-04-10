"""Ukázkový program, který schválně ústí v chybu.
"""

# Import potřebných zdrojů a nástrojů
from typing import Callable

from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import Robot

# Jméno autora, který je odpovědný za daný program
_AUTHOR_NAME = "Vojtěch Pavlů"


class RobotIntroductionProgram(AbstractProgram):
    """Zde je uvedena implementace programu pro robota, který má za úkol
    vypsat do výstupu jméno robota.

    Tato implementace je ovšem úmyslně chybná.
    """

    def run(self, robot: "Robot", log: Callable):
        """Samotná realizace programu. Nesplní však jediný z úkolů. Přesto,
        že do konzole vypsal požadovaný text, nevypsal ho přes logovací
        potrubí, tedy funkci 'log'.

        K tomu navíc udělá syntaktickou chybu.
        """
        # Chybový program
        robot.log(name)


def get_program():
    """Požadovaná funkce pluginu, která vrací novou instanci programu robota.
    """
    return RobotIntroductionProgram(_AUTHOR_NAME)



