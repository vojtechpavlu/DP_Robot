"""Ukázkový program, který vůbec nesplní požadované zadání, ale nevyústí také
v žádnou chybu.
"""

# Import potřebných zdrojů a nástrojů
from typing import Callable

from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import Robot

# Jméno autora, který je odpovědný za daný program
_AUTHOR_NAME = "Vojtěch Pavlů"


class RobotIntroductionProgram(AbstractProgram):
    """Zde je uvedena implementace programu pro robota, který má za úkol
    vypsání jména robota, pro který tento program běží.

    Tento program je však neúspěšný; nesplní žádný z úkolů. Také ale
    nezpůsobuje žádnou chybu.
    """

    def run(self, robot: "Robot", log: Callable):
        """Samotná realizace programu. Nesplní však jediný z úkolů. Přesto,
        že do konzole vypsal požadovaný text, nevypsal ho přes logovací
        potrubí, tedy funkci 'log'.

        Ovšem také nezpůsobí žádnou chybu.
        """
        # Vypsání řetězce na konzoli
        print(robot.name)


def get_program():
    """Požadovaná funkce pluginu, která vrací novou instanci programu robota.
    """
    return RobotIntroductionProgram(_AUTHOR_NAME)



