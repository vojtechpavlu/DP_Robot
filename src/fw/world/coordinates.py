"""Modul 'coordinates.py' obsahuje základní nástroje pro práci s dvourozměrným,
diskrétním prostorem, resp. jeho souřadnicovým systémem.

Především pak definuje způsob, jakým lze uchovat hodnoty na osách x a y pro
zobrazení bodu. Stejně tak obsahuje i posuvník v dodaném směru (podle definice
v modulu 'direction.py'), dle kterého lze získat souřadnice bodu relativně
vůči počátečnímu bodu a směru posunu.
"""

from .direction import Direction
from ..utils.error import PlatformError


class DirectionMover:
    """Třídy instance DirectionMover slouží k zjištění souřadnic bodu nového
    z předcházejícího bodu a dodaného směru.

    Instance této třídy toho docílí pomocí dodaného schématu posunu, tedy co
    do inkrementu v jednotlivých osách pro dodané směry.

    Aplikace je realizována podle návrhového vzoru Multiton, resp. Originál,
    kde platí, že pro každý klíč existuje příslušná instance na tomto klíči
    závislá.
    """

    """Schémata, kterých je používáno k zjištění, o kolik se v dané ose má
    posunout. Důležitou složkou je vedle kombinace posunu v tom kterém směru
    (zvýšení nebo snížení) pro danou osu (x nebo y) i směr, pro který jsou
    tyto přírustky platné. Realizace je provedena slovníkem.
    """
    __schemas = {
        Direction.EAST: (1, 0),
        Direction.NORTH: (0, 1),
        Direction.WEST: (-1, 0),
        Direction.SOUTH: (0, -1)
    }

    def __init__(self, direction: "Direction"):
        """Initor, který je schopen z dodaného směru za pomoci stanovených
        schémat zjistit, v kterých osách se jak změní hodnota dané souřadnice,
        a to z dodaného směru, ve kterém má být posunováno.
        """
        self._direction = direction
        self._x_increment: int = DirectionMover.__schemas.get(direction)[0]
        self._y_increment: int = DirectionMover.__schemas.get(direction)[1]

    @property
    def direction(self) -> "Direction":
        """Vlastnost vrací směr, ve kterém je posouváno."""
        return self._direction

    @property
    def x_incr(self) -> int:
        """Vlastnost vrací inkrement v ose x při posunu v daném směru."""
        return self._x_increment

    @property
    def y_incr(self) -> int:
        """Vlastnost vrací inkrement v ose y při posunu v daném směru."""
        return self._y_increment


"""Proměnná '_MOVERS' je sadou všech přípustných posuvníků, tedy pro každý
platný směr jedna instance třídy 'DirectionMover'. Této proměnné je užíváno
pro realizaci návrhového vzoru Multiton (Originál).
"""
_MOVERS = (
    DirectionMover(Direction.EAST),
    DirectionMover(Direction.NORTH),
    DirectionMover(Direction.WEST),
    DirectionMover(Direction.SOUTH)
)


def _get_mover(direction: "Direction") -> "DirectionMover":
    """Funkce pro příslušný směr vyhledá správný posuvník. Využívá přitom
    existující proměnné '_MOVERS', která pro všechny platné směry posuvník
    uchovává.

    Pokud není dodán validní směr (typicky hodnota None), je vyhozena výjimka
    'CoordinatesError', která v tomto kontextu značí nenalezení příslušného
    posuvníku a nelze tedy posun provést.
    """
    for mover in _MOVERS:
        if mover.direction == direction:
            return mover
    raise CoordinatesError(
        f"Pro dodaný směr '{direction}' nebyl žádný validní "
        f"posuvník nalezen.")


class Coordinates:
    """Instance třídy Coordinates slouží jako uchovatelé hodnot na dvou osách.
    Důvodem je potřeba udržovat informace o bodě ve dvourozměrném prostoru.

    Sestávají se z dvou celočíselných hodnot, které reprezentují hodnotu na
    příslušné ose x a y. Jejich celočíselnost vyjadřuje diskrétní povahu
    takového prostoru.

    Kromě uchování těchto hodnot také třída definuje způsob změny těchto
    hodnot. Konkrétně pak funkcí 'move_in_direction', která je realizována
    podle návrhového vzoru Stav (resp. State). Ta umí poskytnout instanci
    reprezentující sousední bod v takto diskrétním a dvourozměrném prostoru
    na základě udaného směru.

    Pochopitelnou součástí je i schopnost pracovat se zápornými hodnotami,
    pokud zůstanou celočíselné.
    """

    def __init__(self, x: int, y: int):
        """Initor, který přijímá hodnoty 'x' a 'y' a které si uvnitř instance
        uloží a dále s nimi poskytuje definované služby.

        Přijatelné jsou pro obě proměnné libovolné hodnoty z definičního oboru
        celých čísel, tedy i záporná čísla či pochopitelně nula. Vyňata jsou
        pak především čísla reálná.
        """
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        """Vlastnost vrací souřadnici na ose x."""
        return self._x

    @property
    def y(self) -> int:
        """Vlastnost vrací souřadnici na ose y."""
        return self._y

    @property
    def xy(self) -> "tuple[int, int]":
        """Vlastnost vrací obě hodnoty ('x' a 'y') v podobě ntice."""
        return self.x, self.y,

    def move_in_direction(self, direction: "Direction") -> "Coordinates":
        """Funkce má za cíl podle návrhového vzoru Stav vrátit instanci té
        samé třídy s upravenými parametry.

        Konkrétně je zde cílem vytvořit souřadnicový bod sousední v daném
        směru. Do parametru funkce je postoupen směr, ve kterém se takový bod
        má hledat. Je-li tento platným směrem, ve kterém se má posouvat, vždy
        funkce navrátí novou instanci této třídy po posunutí. Není-li dodaný
        směr platný, je vyhozena výjimka 'CoordinatesError'; více ve funkci
        '_get_mover(Direction)' v tomto modulu.
        """
        dm = _get_mover(direction)
        return Coordinates(self.x + dm.x_incr, self.y + dm.y_incr)


class CoordinatesError(PlatformError):
    """Instance třídy CoordinatesError odpovídají výjimkám, které jsou
    vyhazovány coby informace o vzniklé chybě v kontextu manipulace se
    souřadnicovým subsystémem.

    Typicky se s výjimkou tohoto typu dá setkat při posunu v nevalidním směru.
    """

    def __init__(self, message: str):
        PlatformError.__init__(self, message)


