"""Tento modul reprezentuje plugin programu, který je dynamicky načítán,
validován a robotem spuštěn.

Tento modul je rozdělen do několika hlavních bloků:
    - Stanovení proměnných, kde jsou uvedeny jejich inicializace

    - Definice hlavních funkcí, kde je uvedena hlavní funkce programu a
      volitelná funkce osazení robota jednotkami.

    - Definice podprogramů, tedy prostor pro definici vlastních funkcí pro
      lepší strukturování celého programu robota.

Co je třeba upravit:
    - upravit ID a jméno autora v proměnných AUTHOR_ID a AUTHOR_NAME

    - upravit tělo funkce 'run', která reprezentuje program robota

    - upravit tělo funkce 'mount', která specifikuje osazení robota [volitelné]
"""

# Import podpůrných knihoven
from typing import Callable
from src.fw.robot.robot import Robot
from src.fw.robot.program import AbortType
# from src.fw.robot.unit import AbstractUnit


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

    terminate("ÚSPĚCH", SUCCESS)


"""Funkce upravující výchozí osazení robota. Její uvedení je typicky 
volitelné. Pokud ji chcete upravit, odstraňte její zakomentování."""
# def mount(robot: "Robot", available_units: "tuple[AbstractUnit]"):
#     """Funkce pro osazení robota. Tato přijímá robota, který má být osazen,
#     a sadu jednotek, kterými je robota možné osadit. Aktuální tělo funkce
#     odpovídá výchozímu procesu osazování."""
#     for unit in available_units:
#         robot.mount(unit)


# *****************************************************************************
# ------------------------- Definice podprogramů ------------------------------


"""Zde je prostor pro definici vlastních funkcí, pomocí kterých lze hlavní 
program strukturovat. Zde by měly být uvedeny funkce rozpadající celou
funkcionalitu na menší a často opakované bloky."""

# def auxiliary_function(log: Callable):
#     log('Hello World!')
