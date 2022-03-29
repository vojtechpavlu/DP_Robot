"""Modul 'world.py' je odpovědný za definici základních prostředků a způsobu
manipulace s herním světem.
"""

# Import lokálních knihoven
import src.fw.world.field as field_mod
import src.fw.world.world_interface as world_inter_module

from src.fw.utils.error import PlatformError
from src.fw.world.direction import Direction


class World:
    """Třída světa má za cíl uchovávat konkrétní stav světa a svým způsobem
    působit jako kontextové jádro celého systému.

    Samotný svět sdružuje reference na všechna políčka, přičemž je dává do
    vzájemného kontextu. Je tedy možné mezi nimi vyhledávat či získávat
    sousedy sledovaného políčka.
    """

    def __init__(self, fields: "list[field_mod.Field]",
                 world_if_fact: "world_inter_module.WorldInterfaceFactory"):
        """Initor třídy je odpovědný za přijetí všech parametrů a jejich
        uložení.

        Hlavním parametrem je seznam políček, která mají prostor světa tvořit.
        Tento seznam musí mít délku alespoň jednoho políčka, jinak je vyhozena
        výjimka o nesmyslnosti takového světa. Stejně tak nesmí existovat dvě
        políčka se stejnými souřadnicemi, neboť to by způsobovalo mnoho
        problémů s konzistencí světa.

        Dalším krokem je nastavení reference na tuto instanci světa pro každé
        políčko pro snazší manipulaci v kontextu políček světa.

        Dalším významným parametrem je továrna rozhraní světa (world_if_fact),
        která je odpovědná za vytvoření rozhraní světa, které bude tomuto
        světu náležet a které se bude starat o zajištění integrity světa při
        interakcích se světem.
        """
        self._fields = fields

        """Nastavení reference na tuto instanci světa všem políčkům světa."""
        for field in self._fields:
            field.world = self

        """Kontrola, že počet dodaných políček je větší než nula. Svět bez
        políčka nemá smysl."""
        if len(fields) < 1:
            raise WorldError("Nelze vytvořit svět bez políčka", self)

        """Kontrola unikátnosti souřadnic. Pokud existují dvě políčka se
        stejnými souřadnicemi, znamená to narušení konzistence. Pokud dvě 
        políčka mají stejné souřadnice, je vyhozena výjimka."""
        for index, field in enumerate(self._fields):
            for next_field in self._fields[index + 1:]:
                if field.x == next_field.x or field.y == next_field.y:
                    raise WorldError(
                        f"Nelze evidovat dvě políčka se "
                        f"stejnými souřadnicemi", self)

        """Připravení rozhraní světa z dodané továrny"""
        self._world_interface = world_if_fact.build(self)

    @property
    def fields(self) -> "tuple[field_mod.Field]":
        """Vlastnost vrací ntici ze seznamu všech políček, která má svět
        evidována."""
        return tuple(self._fields)

    @property
    def all_paths(self) -> "tuple[field_mod.Field]":
        """Vlastnost vrací ntici ze seznamu všech políček, která jsou cestou,
        tedy potomky třídy Path."""
        return tuple(filter(lambda field: field.is_path, self.fields))

    @property
    def all_paths(self) -> "tuple[field_mod.Field]":
        """Vlastnost vrací ntici ze seznamu všech políček, která jsou stěnou,
        tedy potomky třídy Wall."""
        return tuple(filter(lambda field: field.is_wall, self.fields))

    @property
    def world_interface(self) -> "world_inter_module.WorldInterface":
        """Vlastnost vrací rozhraní světa, které tomuto světu náleží."""
        return self._world_interface

    def has_field(self, x: int, y: int) -> bool:
        """Funkce vrací boolovskou informaci o tom, zda-li je v daném světě
        evidováno políčko se zadanými souřadnicemi.

        Funkce se pokusí políčko vyhledat a nebude-li takové s dodanými
        souřadnicemi nalezeno, je vrácena hodnota False, jinak True.
        """
        return self.field(x, y) is not None

    def field(self, x: int, y: int) -> "field_mod.Field":
        """Funkce vrací referenci na políčko na dodaných souřadnicích. Pokud
        pro tyto souřadnice žádné políčko není nalezeno, je vrácena hodnota
        None."""
        for field in self.fields:
            if field.x == x and field.y == y:
                return field

    def neighbours(self, x: int, y: int) -> "tuple[field_mod.Field]":
        """Funkce se pokusí získat všechna políčka sousedící s tím na dodaných
        souřadnicích ve všech platných směrech. Počet navrácených políček se
        vždy pohybuje mezi 0 a počtem platných směrů, typicky tedy 4.
        Navrácení sousedé mnohou být cesty stejně jako stěny.

        Pokud na dodaných souřadnicích není evidované políčko, je vyhozena
        výjimka.
        """
        field = self.field(x, y)
        if not field:
            raise WorldError(
                f"Nelze najít sousedy pro políčko [{x};{y}], protože není "
                f"ve světě evidováno", self)

        neighbours = []
        for direction in Direction:
            moved_coords = field.coordinates.move_in_direction(direction)
            neighbour = self.field(moved_coords.x, moved_coords.y)
            if neighbour:
                neighbours.append(neighbour)
        return tuple(neighbours)


class WorldError(PlatformError):
    """Výjimka 'WorldError' svojí podstatou rozšířuje obecnou výjimku tím, že
    v sobě uchovává referenci na svět, v jehož kontextu došlo k chybě."""

    def __init__(self, message: str, world: "World"):
        PlatformError.__init__(self, message)
        self._world = world

    @property
    def world(self) -> "World":
        """Svět, v jehož kontextu došlo k chybě."""
        return self._world
