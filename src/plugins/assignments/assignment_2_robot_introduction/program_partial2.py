"""Ukázkový program, který částečně plní zadání, tedy splní jen některé své
úkoly.

Od programu v modulu 'program_partial.py' se liší tím, že vypisuje sice jméno
robota, ale používá k tomu konkrétní, absolutní literál, projde tedy pouze
jedním z testů správnosti.
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

        Tento program projde jedním z testů v rámci běhového prostředí, neboť
        vypisuje jméno "Karel". Neprojde ovšem druhým běhovým prostředím,
        protože tam je již robotovi předepsáno jméno ELIZA.
        """
        # Zalogování jména "Karel"
        log("Karel")


def get_program():
    """Požadovaná funkce pluginu, která vrací novou instanci programu robota.
    """
    return RobotIntroductionProgram(_AUTHOR_NAME)



