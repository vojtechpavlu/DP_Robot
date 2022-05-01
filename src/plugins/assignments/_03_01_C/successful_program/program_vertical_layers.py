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
    - upravit název tohoto modulu (vždy musí začínat 'program_')
    - upravit název balíčku programu dle stanovených pravidel
    - upravit tělo funkce 'mount', která specifikuje osazení robota [volitelné]
"""

# Import podpůrných knihoven
from typing import Callable
from src.fw.robot.robot import Robot
from src.fw.robot.program import AbortType


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

    total = 0

    while True:
        total = total + go_to_the_end(robot)
        turn(robot)
        check_wall(robot, log, terminate, total)
        turn(robot)
        go_to_the_end(robot)
        turn_right(robot)
        move(robot)
        turn_right(robot)


# *****************************************************************************
# ------------------------- Definice podprogramů ------------------------------


def check_wall(robot: Robot, log, terminate: Callable, total: int):
    """Funkce, která zjistí, zda-li je před robotem stěna"""
    if robot.get_unit("IsWallSensor").scan():
        log(total)
        terminate("Došel jsem konce!", SUCCESS)


def turn(robot: Robot):
    """Funkce, která otáčí robota doleva."""
    robot.get_unit("TurnLeft").execute()


def turn_right(robot: Robot):
    """Funkce, která otočí robota doprava."""
    turn(robot)
    turn(robot)
    turn(robot)

def move(robot: Robot):
    """Funkce, která posune robota kupředu."""
    robot.get_unit("ForwardMover").execute()


def go_to_the_end(robot) -> int:
    """Funkce, která zajistí, že robot dojde až na konec, tedy dokud
    nebude stát před stěnou.

    Při průchodu tato funkce počítá navštívená políčka."""

    length = 1

    # Dokud předemnou není zeď
    while not robot.get_unit("IsWallSensor").scan():

        # Zvýšení počtu
        length = length + 1

        # Popojdi dopředu
        robot.get_unit("ForwardMover").execute()

    # Navrácení počtu políček, která byla navštívena
    return length



