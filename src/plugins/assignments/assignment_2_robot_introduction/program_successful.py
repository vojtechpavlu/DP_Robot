"""Ukázkový program, který plní zadání v plném rozsahu.
"""

# Import potřebných zdrojů a nástrojů
from typing import Callable

from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import Robot

# Jméno autora, který je odpovědný za daný program
_AUTHOR_NAME = "Vojtěch Pavlů"


class RobotIntroductionProgram(AbstractProgram):
    """Zde je uvedena implementace programu pro robota, který má za úkol
    vypsat jméno robota.
    """

    def run(self, robot: "Robot", log: Callable):
        """Samotná realizace programu v očekávané podobě, tedy vypsání
        jména robota.
        """
        # Získání jména robota a jeho vypsání
        robot_name = robot.name
        log(robot_name)


def get_program():
    """Požadovaná funkce pluginu, která vrací novou instanci programu robota.
    """
    return RobotIntroductionProgram(_AUTHOR_NAME)



