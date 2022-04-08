"""
Modul 'direction.py' obsahuje výčtový typ Direction definující čtyři světové
strany a k nim příslušné metody vzájemně je propojující (co do otáčení).
"""

# Import standardních knihoven
from enum import Enum


class Direction(Enum):
    """Výčtový typ definující čtyři světové strany EAST, NORTH, WEST, SOUTH
    (v tomto pořadí).
    Každé z těchto čtyř instancí je přidělena sada metod operujících nad
    podstatou této množiny, především pak navrácení kandidáta reprezentujícího
    souseda po otočení o 90° doprava (otočení po směru hodinových ručiček) či
    doleva (otočení proti směru hodinových ručiček). Jde tedy o realizaci
    pomocí návrhového vzoru Stav.
    """
    EAST, NORTH, WEST, SOUTH = range(4)

    def turn_left(self) -> 'Direction':
        """Metoda vrací směr reprezentující otočení o 90° proti směru
        hodinových ručiček. Příkladně pro NORTH bude vrácena instance WEST.
        """
        return (Direction(self.value + 1) if self.value < 3
                else Direction(0))

    def turn_right(self) -> 'Direction':
        """Metoda vrací směr reprezentující otočení o 90° po směru
        hodinových ručiček. Příkladně pro NORTH bude vrácena instance EAST.
        """
        return (Direction(self.value - 1) if self.value > 0
                else Direction(3))

    def about_face(self) -> 'Direction':
        """Metoda vrací směr reprezentující otočení o 180°. Příkladně pro
        NORTH bude vrácena instance SOUTH.
        """
        return self.turn_right().turn_right()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def list() -> 'list[Direction]':
        """Metoda vrací seznam směrů seřazených proti směru hodinových
        ručiček počínaje východem."""
        return [
            Direction.EAST,
            Direction.NORTH,
            Direction.WEST,
            Direction.SOUTH,
        ]

    @staticmethod
    def direction_by_name(direction_name: str) -> "Direction":
        """Funkce vrací konkrétní směr, který názvem odpovídá dodanému názvu.
        Pokud takový směr není, je vrácena hodnota None.

        Název může být celým názvem (např. 'NORTH'), nebo pouze počáteční
        písmeno (např. 'N'). Zároveň nezáleží na velikosti písmen; vždy je
        název převeden na kapitálky.

        Validní řetězce tedy jsou:

            - 'EAST', 'NORTH', 'WEST' a 'SOUTH',
            - 'E', 'N', 'W' a 'S',
            -  a všechny výše uvedené řetězce v libovolném casingu
        """

        # Převod názvu na kapitálky (pro jistotu)
        direction_name = direction_name.upper()

        # Pro každý směr ze všech směrů
        for direction in Direction.list():

            # Pokud se název směru nebo jeho první písmeno shoduje s dodaným
            # názvem, pak tento směr vrať
            if (direction.name == direction_name or
                    direction.name[0] == direction_name):
                return direction

    @staticmethod
    def direction_names() -> "tuple[str]":
        """Funkce vrací názvy všech směrů."""
        # Redundantní přetypování pro potřeby správné kontroly typů IDE,
        # která mají problém s lambdami
        return tuple(map(lambda d: str(d.name), Direction.list()))

