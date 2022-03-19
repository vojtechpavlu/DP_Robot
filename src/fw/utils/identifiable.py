"""V tomto modulu je definován obecný protokol pro manipulaci s
identifikovatelnými instancemi. Samotný institut identifikace vychází z
potřeby jednoznačně rozlišit dvě (byť jinak identické) instance. To je např.
také hlavní rozdíl od instancí typu 'Named', které svůj název unikátní mít
nemusí."""

from abc import ABC
import uuid


class Identifiable(ABC):
    """Instance třídy Identifiable si udržují informaci o unikátním
    identifikátoru, který jim byl přiřazen.

    Samotná identifikace je postavena na Universally Unique Identifier (UUID),
    konkrétně ve verzi 4. Důvodem je minimalizace rizika existence dvou
    identických ID. UUID je 128-bitová značka umožňující identifikaci v co
    nejširším kontextu. Riziko kolize dvou identických ID je pro verzi 4 tak
    malá, že je zanedbatelná a typicky zanedbávána (1 : 2.7 * 10^18);
    viz https://en.wikipedia.org/wiki/Universally_unique_identifier. """

    def __init__(self):
        self.__id = uuid.uuid4()

    @property
    def id(self) -> "uuid.UUID":
        """Vlastnost vrací celou instanci třídy UUID."""
        return self.__id

    @property
    def hex_id(self) -> str:
        """Vlasnost vrací identifikátor převedený na textovou reprezentaci."""
        return self.id.hex

    @property
    def int_id(self) -> int:
        """Vlasnost vrací identifikátor převedený na celé číslo."""
        return self.id.int

