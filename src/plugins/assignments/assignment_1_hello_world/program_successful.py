"""Ukázkový program, který plní zadání 'Hello World!' v plném rozsahu.
"""

# Import potřebných zdrojů a nástrojů
from typing import Callable

from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import Robot

# Jméno autora, který je odpovědný za daný program
_AUTHOR_NAME = "Vojtěch Pavlů"


class HelloWorld(AbstractProgram):
    """Zde je uvedena implementace programu pro robota, který má za úkol
    realizaci programu 'Hello World!', tedy vypsání textu 'Hello World!'.
    """

    def run(self, robot: "Robot", log: Callable):
        """Samotná realizace programu, který pouze zaloguje požadovaný
        text 'Hello World!' do dodaného potrubí loggeru."""

        # Splnění úkolu zalogováním požadovaného textu
        log("Hello World!")
        #log("Hello World!")


def get_program():
    """Požadovaná funkce pluginu, která vrací novou instanci programu robota.
    """
    return HelloWorld(_AUTHOR_NAME)



