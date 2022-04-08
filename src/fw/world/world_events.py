"""Tento modul obsahuje definici událostí, které mohou vzniknout v kontextu
manipulace se světem.

Těchto událostí je používáno v kontextu práce se sledováním světa co do
plnění úkolů."""


# Import standardních knihoven
from dataclasses import dataclass


# Import lokálních knihoven
import src.fw.target.event_handling as event_module
import src.fw.robot.robot as robot_module
import src.fw.world.field as field_module
import src.fw.world.direction as direction_module


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
    # Souřadnice políčka
    x: int
    y: int

    # Robot, který byl přiřazen
    robot: "robot_module.Robot"


@dataclass(frozen=True)
class MarkChangeEvent(event_module.Event):
    """Datová třída reprezentující událost změny označkování políčka. Tato
    událost by měla symbolizovat vznik značky na políčku, stejně jako její
    odebrání.

    Příklad použití:
        >>> MarkChangeEvent(field)
    """

    field: "field_module.Field"


@dataclass(frozen=True)
class DirectionChangeEvent(event_module.Event):
    """Datová třída reprezentující událost změny směru robota. Tato událost
    by měla symbolizovat změnu natočení robota do směru.

    K tomu, aby byla událost co nejužitečnější, nosí v sobě informaci o
    robotovi, s kterým tato událost souvisí, stejně jako směr, ve kterém
    je robot nově natočen.

    Příklad použití:
        >>> DirectionChangeEvent(robot, direction)
    """

    robot: "robot_module.Robot"
    direction: "direction_module.Direction"





