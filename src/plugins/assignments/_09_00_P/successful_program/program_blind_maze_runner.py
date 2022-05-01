"""Tento modul reprezentuje plugin programu, který je dynamicky načítán,
validován a robotem spuštěn.
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
"""
SUCCESS = AbortType.SUCCESS

"""Uložení reference na robota, která bude globální. Tato musí být iniciována
na začátku programu."""
ROBOT: Robot = None


"""Uložení reference na funkci pro ukončení programu, která bude globální. 
Tato musí být iniciována na začátku programu."""
END: Callable = None

"""Uložení reference na záznamník, který bude globální. Tato proměnná musí být 
iniciována na začátku programu."""
LOG: Callable = None

# *****************************************************************************
# ------------------------ Definice hlavních funkcí ---------------------------


def run(robot: Robot, log: Callable, terminate: Callable):
    """Hlavní funkce programu, která řídí všechny ostatní.

    V prvním kroku jsou iniciovány pomocné zdroje. Teprve poté se robot
    začíná samostatně pohybovat.
    """

    # Spuštění inicializace
    init(robot, log, terminate)

    # 'Nekonečný' cyklus slepého prohledávání
    while True:
        check_mark()
        if not check_left():
            if not check_forward():
                turn_right()


# *****************************************************************************
# ------------------------- Definice podprogramů ------------------------------

"""Specifikace pomocných funkcí pro lepší čitelnost programu"""


# Definice funkce otočení doleva
def turn_left(): ROBOT.get_unit("TurnLeft").execute()


# Definice funkce otočení doprava
def turn_right(): ROBOT.get_unit("TurnRight").execute()


# Definice funkce posunu ve směru robota kupředu
def move(): ROBOT.get_unit("ForwardMover").execute()


# Definice funkce zjišťující, zda-li před robotem není stěna
def is_wall(): return ROBOT.get_unit("IsWallSensor").scan()


# Definice funkce zjišťující, zda-li pod robotem neleží značka
def is_mark(): return ROBOT.get_unit("HasMark").scan()


# Definice funkce, která dokáže přečíst značku
def read_mark(): return ROBOT.get_unit("MarkReader").scan()


"""Definice podprogramů, kterých robot ve svém programu využívá"""


def check_mark():
    """Funkce starající se o otestování, zda-li robot nestojí na požadované
    značce. Pokud ano, program se ukončí."""

    # Otestuj, zda-li nejsi na značce
    if is_mark():
        if read_mark() == "CIL":
            END("Robot došel do cíle!", SUCCESS)
        else:
            LOG("Planý poplach:", read_mark())


def check_left() -> bool:
    """Funkce se otočí doleva a ověří, zda-li nestojí před stěnou. Pokud ano,
    otočí se zpět. Pokud ne, popojde krok daným směrem."""
    turn_left()
    if not is_wall():
        move()
        return True
    else:
        turn_right()
        return False


def check_right() -> bool:
    """Funkce se otočí doprava a ověří, zda-li nestojí před stěnou. Pokud ano,
    otočí se zpět. Pokud ne, popojde krok daným směrem."""
    turn_right()
    if not is_wall():
        move()
        return True
    else:
        turn_left()
        return False


def check_forward() -> bool:
    """Funkce ověří, zda-li nestojí před stěnou. Pokud ano, vrátí False, jinak
    se posune."""
    if not is_wall():
        move()
        return True
    return False


def init(robot: Robot, log, terminate):
    """Funkce, která se stará o inicializaci všech pomocných funkcí."""
    global ROBOT, END, LOG
    ROBOT = robot
    END = terminate
    LOG = log





