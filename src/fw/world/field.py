"""Modul 'field.py' je odpovědný za stanovení základních prostředků pro
manipulaci políčky, ze kterých se sestává prostor herního světa.
"""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.utils.error import PlatformError
from src.fw.world.coordinates import Coordinates


class Field(ABC):
    """Abstraktní třída 'Field' je odpovědná za stanovení základního
    společného protokolu pro všechny své potomky.

    Kromě abstraktních vlastností, které obalují funkce vracející jednoduché
    informace o podstatě políčka (zda-li jde o cestu či stěnu) jsou potomci
    opatřeni i společným mechanismem pro návrat souřadnic v prostoru světa.
    """

    def __init__(self, x: int, y: int):
        """"""
        self._coordinates = Coordinates(x, y)

    @property
    @abstractmethod
    def is_wall(self) -> bool:
        """Abstraktní vlastnost vrací informaci o tom, zda-li je toto políčko
        stěnou či nikoliv."""

    @property
    @abstractmethod
    def is_path(self) -> bool:
        """Abstraktní vlastnost vrací informaci o tom, zda-li je toto políčko
        cestou či nikoliv."""

    @property
    @abstractmethod
    def can_go_to(self) -> bool:
        """Abstraktní vlastnost vrací informaci o tom, zda-li může robot
        vstoupit na toto políčko."""

    @property
    def coordinates(self) -> "Coordinates":
        """Vlastnost vrací referenci na instanci reprezentující souřadnice
        tohoto políčka."""
        return self._coordinates

    @property
    def x(self) -> int:
        """Vlastnost vrací hodnotu souřadnice na ose x, kde se políčko nachází.
        """
        return self.coordinates.x

    @property
    def y(self) -> int:
        """Vlastnost vrací hodnotu souřadnice na ose y, kde se políčko nachází.
        """
        return self.coordinates.y


class Wall(Field):
    """Reprezentace políčka ve světě, které není navštivitelné. Tato
    reprezentace stěny značí úmyslnou a nepřekonatelnou překážku ve světě.

    Jde o políčko, které nelze navštívit (funkce vlastnosti 'can_go_to' vrací
    False).
    """

    def __init__(self, x: int, y: int):
        """"""
        Field.__init__(self, x, y)

    @property
    def is_wall(self) -> bool:
        """Abstraktní vlastnost vrací informaci o tom, zda-li je toto políčko
        stěnou či nikoliv."""
        return True

    @property
    def is_path(self) -> bool:
        """Abstraktní vlastnost vrací informaci o tom, zda-li je toto políčko
        cestou či nikoliv."""
        return False

    @property
    def can_go_to(self) -> bool:
        """Abstraktní vlastnost vrací informaci o tom, zda-li může robot
        vstoupit na toto políčko."""
        return False


class Path(Field):
    """Reprezentace základního políčka, které lze navštívit. Jeho podstata
    je v průchodnosti a umožnění pohybu v prostoru světa.

    Jeho průchodnosti a navštivitelnosti odpovídá i funkce obalená vlastností
    'can_go_to', která vrací hodnotu True.
    """

    def __init__(self, x: int, y: int):
        """"""
        Field.__init__(self, x, y)

    @property
    def is_wall(self) -> bool:
        """Abstraktní vlastnost vrací informaci o tom, zda-li je toto políčko
        stěnou či nikoliv."""
        return False

    @property
    def is_path(self) -> bool:
        """Abstraktní vlastnost vrací informaci o tom, zda-li je toto políčko
        cestou či nikoliv."""
        return True

    @property
    def can_go_to(self) -> bool:
        """Abstraktní vlastnost vrací informaci o tom, zda-li může robot
        vstoupit na toto políčko."""
        return True


class FieldError(PlatformError):
    """Výjimka 'FieldError' je obohacuje tu obecnou o referenci na políčko,
    v jehož kontextu došlo k chybě."""

    def __init__(self, message: str, field: "Field"):
        """Jednoduchý initor volající initor předka a ukládající poskytnuté
        políčko, k němuž je přiřazena přístupová vlastnost."""
        PlatformError.__init__(self, message)
        self._field = field

    @property
    def field(self) -> "Field":
        """Políčko, v jehož kontextu došlo k chybě."""
        return self._field


