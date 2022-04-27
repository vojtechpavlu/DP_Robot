"""Šablona pluginu definující program. Její význam je v zjednodušení přístupu
k vytváření pluginů tohoto typu.

"""

# Import potřebných zdrojů a nástrojů
from typing import Callable

from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import Robot


# Jméno autora, který je odpovědný za daný program
_AUTHOR_NAME = ""


# class Program(AbstractProgram):
#     """Šablonová třída implementující svého předka ('AbstractProgram'),
#     co do jeho abstraktní funkce 'run(Robot)'.
#     """

def run(self, robot: "Robot", log: Callable):
    """Šablona metody, která se stará o definici sekvence akcí, které
    má robot provést.
    """


def get_program():
    """Tovární (přístupová) funkce, která vrací zcela novou instanci programu.
    """
    return Program(_AUTHOR_NAME)



