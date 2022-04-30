"""Tento modul reprezentuje plugin programu, který je dynamicky načítán,
validován a robotem spuštěn.
"""

# Import podpůrných knihoven
from typing import Callable

from src.fw.robot.program import AbortType
from src.fw.robot.robot import Robot


# *****************************************************************************
# -------------------------- Stanovení proměnných -----------------------------


"""Informace o autorovi programu"""
AUTHOR_ID = "pavv04"
AUTHOR_NAME = "Vojtěch Pavlů"


"""Způsoby předčasného ukončení programu. Těchto je použito pro specifikaci
za jakých okolností k ukončení došlo.

    - SUCCESS je použito, pokud program rozpozná, že své úkoly splnil
    - FAILURE je použito, pokud program rozpozná, že úkol splnit nelze
    - ERROR je použito, pokud program rozpozná porušení nějakých pravidel

Doporučené použití ve funkci programu:

    run(robot: Robot, log: Callable, terminate: Callable):
        terminate("Zpráva o úspěšném dokončení úkolu, SUCCESS)
"""
SUCCESS = AbortType.SUCCESS
FAILURE = AbortType.FAILURE
ERROR = AbortType.ERROR

# *****************************************************************************
# ------------------------ Definice hlavních funkcí ---------------------------


def run(robot: Robot, log: Callable, terminate: Callable):
    """Hlavní funkce reprezentující program robota. Tato funkce je robotu
    předána ke spuštění jako jeho samotný program.

    parametry:
        - robot:        pro kterého bude program spuštěn. Tento je osazen
                        specifickými jednotkami

        - log:          funkce pro tvorbu záznamů. Tato funkce rozšiřuje
                        působnost built-in funkce `print`, lze ji i stejným
                        způsobem použít

        - terminate:    funkce pro předčasné ukončení programu. Pokud robot
                        svým programem dojde do stavu, kdy již nemá smysl
                        pokračovat, lze upozornit systém zavoláním této funkce
    """
    # Pokud před robotem není stěna
    if not robot.get_unit("IsWallSensor").scan():

        # Jdi dopředu
        robot.get_unit("ForwardMover").execute()

        # Ukonči program
        terminate("Nalezl jsem cestu!", SUCCESS)

    # Pokud před robotem je stěna
    else:
        # Otoč se
        robot.get_unit("TurnLeft").execute()

    # Ukonči program, protože cesta nebyla nalezena
    terminate("Nenalezl jsem cestu", FAILURE)

