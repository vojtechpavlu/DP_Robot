"""Ukázkový program, který částečně plní zadání, tedy splní jen některé své
úkoly.
"""

# Import potřebných zdrojů a nástrojů
from typing import Callable

from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import Robot

# Jméno autora, který je odpovědný za daný program
_AUTHOR_NAME = "Vojtěch Pavlů"


class RobotIntroductionProgram(AbstractProgram):
    """Zde je uveden částečně správný program. Splní jen část svých úkolů.
    """

    def run(self, robot: "Robot", log: Callable):
        """Samotná realizace programu, který pouze zaloguje text do dodaného
        potrubí loggeru; tento text ale není ten požadovaný.

        Zatímco měl vypsat jméno robota, vypíše textovou reprezentaci robota.
        """

        log(robot)


def get_program():
    """Požadovaná funkce pluginu, která vrací novou instanci programu robota.
    """
    return RobotIntroductionProgram(_AUTHOR_NAME)



