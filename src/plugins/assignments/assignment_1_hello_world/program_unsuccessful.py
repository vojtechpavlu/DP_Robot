"""Ukázkový program, který vůbec nesplní požadované zadání.
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

    Tento program je však neúspěšný; nesplní žádný z úkolů.
    """

    def run(self, robot: "Robot", log: Callable):
        """Samotná realizace programu. Nesplní však jediný z úkolů. Přesto,
        že do konzole vypsal požadovaný text, nevypsal ho přes logovací
        potrubí, tedy funkci 'log'.
        """
        # Vypsání řetězce na konzoli
        print("Hello World!")


def get_program():
    """Požadovaná funkce pluginu, která vrací novou instanci programu robota.
    """
    return HelloWorld(_AUTHOR_NAME)



