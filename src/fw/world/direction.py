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
