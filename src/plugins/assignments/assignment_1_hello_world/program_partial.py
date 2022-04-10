"""Ukázkový program, který částečně plní zadání 'Hello World!'.
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

    Implementace je však úmyslně částečně dokončena; nevypisuje správný
    řetězec.
    """

    def run(self, robot: "Robot", log: Callable):
        """Samotná realizace programu, který pouze zaloguje text do dodaného
        potrubí loggeru; tento text ale není ten požadovaný."""

        # Splnění úkolu zalogování nějakého textu, ale ne požadovaného
        log("Ahoj světe!")


def get_program():
    """Požadovaná funkce pluginu, která vrací novou instanci programu robota.
    """
    return HelloWorld(_AUTHOR_NAME)



