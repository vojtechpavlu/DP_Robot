"""Tento modul obsahuje definici událostí, které mohou vzniknout v kontextu
manipulace se světem.

Těchto událostí je používáno v kontextu práce se sledováním světa co do
plnění úkolů."""


# Import standardních knihoven
from dataclasses import dataclass


# Import lokálních knihoven
import src.fw.target.event_handling as event_module
import src.fw.robot.robot as robot_module


@dataclass(frozen=True)
class FieldChangeEvent(event_module.Event):
    """Datová třída umožňuje zachytit požadované atributy, které jsou v
    kontextu změny políčka důležité.

    Příklad použití:
        >>> FieldChangeEvent(x, y, robot)

    Tato si uchovává pro snazší manipulaci celočíselné souřadnice 'x' a 'y', a
    dále referenci na robota, kterému se změnilo políčko.

    Kromě toho uchovává (resp. postupuje předkovi) název události."""

    # Souřadnice nového políčka
    x: int
    y: int

    # Reference na robota, který se přesunul
    robot: "robot_module.Robot"


@dataclass(frozen=True)
class SpawnRobotEvent(event_module.Event):
    """Datová třída reprezentující událost zasazení robota do světa.

    Příklad použití:
        >>> SpawnRobotEvent(x, y, robot)
    """
    x: int
    y: int

    robot: "robot_module.Robot"


