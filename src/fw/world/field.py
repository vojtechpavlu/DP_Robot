"""Modul 'field.py' je odpovědný za stanovení základních prostředků pro
manipulaci políčky, ze kterých se sestává prostor herního světa.
"""

# Import standardních knihoven
from abc import abstractmethod

# Import lokálních knihoven
from src.fw.utils.error import PlatformError
from src.fw.world.coordinates import Coordinates
from src.fw.world.direction import Direction

import src.fw.world.mark as mark_module
import src.fw.world.world as world_mod
import src.fw.robot.robot_container as rc_module


class Field(rc_module.SingleRobotContainer, mark_module.Markable):
    """Abstraktní třída 'Field' je odpovědná za stanovení základního
    společného protokolu pro všechny své potomky.

    Kromě abstraktních vlastností, které obalují funkce vracející jednoduché
    informace o podstatě políčka (zda-li jde o cestu či stěnu) jsou potomci
    opatřeni i společným mechanismem pro návrat souřadnic v prostoru světa.

    Stejně tak si obecné políčko udržuje informaci o světě, ke kterému náleží.
    Tento svět však lze nastavit políčku maximálně jednou; při pokusu o
    znovunastavení je vyhozena výjimka.

    Políčko je také svým způsobem kontejnerem robotů; v konkrétní implementaci
    chápeme jako kontejner jediného robota v daném okamžiku. Proto je také
    třída Field potomkem třídy SingleRobotContainer.
    """

    def __init__(self, x: int, y: int):
        """Initor políčka, který je odpovědný za nastavení defaultních hodnot,
        stejně jako je odpovědný za volání initorů svých předků.
        """
        # Volání předků, tedy kontejneru jediného robota a označení
        rc_module.SingleRobotContainer.__init__(self)
        mark_module.Markable.__init__(self)

        """Nastavení souřadnicového identifikátoru z dodaných hodnot."""
        self._coordinates = Coordinates(x, y)

        """Reference na svět, ke kterému políčko náleží. Zprvu None; nastavena
        je až během životního cyklu instance. Zároveň tento svět může být
        nastaven maximálně jednou."""
        self._world = None

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

    @property
    def world(self) -> "world_mod.World":
        """Vlastnost vrací instanci světa, kterému dané políčko náleží."""
        return self._world

    @world.setter
    def world(self, world: "world_mod.World"):
        """Vlastnost nastavuje dodanou instanci světa jako svět, kterému toto
        políčko náleží a na který se má obracet v rámci kontextových operací.

        Pokud již jednou svět nastaven je, je vyhozena výjimka pro zajištění
        konzistence."""
        if self.world is not None:
            raise FieldError(
                f"Nelze přenastavovat již jednou určenou instanci světa",
                self)
        self._world = world

    @property
    def neighbours(self) -> "tuple[Field]":
        """Vlastnost se pokusí vyhledat všechny sousedy daného políčka ve
        všech platných směrech. Jejich počet je vždy mezi 0 a počtem platných
        směrů (typicky 4).

        K tomu je zapotřebí reference na svět. Pokud tato není nastavena,
        je vyhozena výjimka."""
        if self.world is None:
            raise FieldError(
                f"Nelze zjistit sousedy, když není nastaven svět", self)
        return self.world.neighbours(self.x, self.y)

    def neighbour(self, direction: "Direction") -> "Field":
        """Funkce vrací referenci na políčko, které s tímto sousedí v daném
        směru."""
        if self.world is None:
            raise FieldError(
                f"Nelze zjistit souseda, když není nastaven svět", self)
        elif direction is None:
            raise FieldError(
                f"Dodaný směr nesmí být None", self)
        # Vyhledání sousedního políčka dle dodaných sousedních souřadnic
        return self.world.field(
            *self.coordinates.move_in_direction(direction).xy)

    def __str__(self) -> str:
        """Funkce vrací textovou reprezentaci políčka."""
        return (f"{type(self).__name__} @ [{self.x}, {self.y}]"
                f"{' ' + str(self.mark) if self.mark else ''}")


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

    @property
    def can_be_marked(self) -> bool:
        """Vlastnost vrací hodnotu False, neboť tato instance nemůže být
        označkována."""
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

    @property
    def can_be_marked(self) -> bool:
        """Vlastnost vrací hodnotu True, neboť tato instance může být
        označkována."""
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


