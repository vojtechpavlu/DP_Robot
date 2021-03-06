"""Modul 'world.py' je odpovědný za definici základních prostředků a způsobu
manipulace s herním světem.
"""

# Import lokálních knihoven
from typing import Callable

import src.fw.world.field as field_mod
import src.fw.world.world_interface as world_inter_module

from src.fw.utils.error import PlatformError
from src.fw.utils.logging.logger import Logger
from src.fw.world.direction import Direction
import src.fw.world.spawner as spawner_module
import src.fw.world.robot_state_manager as rsm_module


class World:
    """Třída světa má za cíl uchovávat konkrétní stav světa a svým způsobem
    působit jako kontextové jádro celého systému.

    Samotný svět sdružuje reference na všechna políčka, přičemž je dává do
    vzájemného kontextu. Je tedy možné mezi nimi vyhledávat či získávat
    sousedy sledovaného políčka.
    """

    def __init__(self, fields: "list[field_mod.Field]",
                 world_if_fact: "world_inter_module.WorldInterfaceFactory",
                 spawner_factory: "spawner_module.SpawnerFactory",
                 logger: "Logger"):
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
                if field.x == next_field.x and field.y == next_field.y:
                    raise WorldError(
                        f"Nelze evidovat dvě políčka se "
                        f"stejnými souřadnicemi: {field.x}, {field.y}", self)

        """Uložení loggeru, který byl této instanci dodán. Z něj je také
        rovnou vytvořena potřebná pipeline pro tuto instanci."""
        self._logger = logger
        self.log: Callable = logger.make_pipeline("world").log

        """Připravení rozhraní světa z dodané továrny"""
        self._world_interface = world_if_fact.build(
            self, self._logger.make_pipeline("w_interface").log)

        """Připravení správce stavů robotů. K tomu je potřeba spawner, který
        řídí přidávání robotů do světa; resp. vytváří stavy robota.
        Dále je instance tohoto spawneru inicializována co do reference na
        tuto instanci, tedy svět, do kterého budou zasazováni roboti.
        """
        spawner = spawner_factory.build()
        self._robot_state_manager = rsm_module.RobotStateManager(
            spawner, self._logger.make_pipeline("r_s_mng").log)
        spawner.world = self

        self.log(f"Vytvořen svět o šířce {self.width} a výšce {self.height}")

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
    def all_marked_fields(self) -> "tuple[field_mod.Field]":
        """Vlastnost vrací ntici všech políček, která jsou opatřena nějakou
        značkou."""
        return tuple(filter(lambda field: field.has_mark, self.fields))

    @property
    def world_interface(self) -> "world_inter_module.WorldInterface":
        """Vlastnost vrací rozhraní světa, které tomuto světu náleží."""
        return self._world_interface

    @property
    def robot_state_manager(self) -> "rsm_module.RobotStateManager":
        """Vlastnost vrací referenci na správce stavů robota, kterého má
        instance tohoto světa v sobě uložený."""
        return self._robot_state_manager

    @property
    def width(self) -> int:
        """Vlastnost vrací šířku světa. Ta je spočítána jako rozdíl maximální
        souřadnice x políčka (tedy políčka nejvíce napravo) a minimální
        souřadnice osy x (tedy políčka nejvíce nalevo). Tento rozdíl je o 1
        navýšen, protože defaultně se indexuje od 0."""

        return (max(self.fields, key=lambda f: f.x).x -
                min(self.fields, key=lambda f: f.x).x) + 1

    @property
    def height(self) -> int:
        """Vlastnost vrací výšku světa. Ta je spočítána jako rozdíl maximální
        souřadnice y políčka (tedy políčka nejvýše) a minimální souřadnice
        osy y (tedy políčka nejníže). Tento rozdíl je o 1 navýšen, protože
        defaultně se indexuje od 0."""
        return (max(self.fields, key=lambda f: f.y).y -
                min(self.fields, key=lambda f: f.y).y) + 1

    @property
    def world_dimensions(self) -> "tuple[int, int]":
        """Vlastnost vrací rozměry světa. Tím je myšleno jakou má šířku a
        výšku, tedy rozdíly mezi nejvyšší a nejnižší hodnotou souřadnice
        navýšeny o 1.

        První hodnota v ntici je šířka (tedy osa 'x'), druhá hodnota je výška
        (tedy osa 'y').
        """
        return self.width, self.height

    def fields_marked_like(self, mark_text: str) -> "tuple[field_mod.Field]":
        """Funkce vrací všechna políčka, která jsou označena specifickým
        textem. Tato vrací v ntici, přičemž může vracet prázdnou."""
        return tuple(filter(lambda f: f.mark.text == mark_text,
                            self.all_marked_fields))

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

    def add_field(self, field: "field_mod.Field"):
        """Funkce se pokusí přidat políčko. Pokud již políčko s takovými
        souřadnicemi má, je vyhozena výjimka."""

        # Ověření, že políčko s takovými souřadnicemi doposud není evidováno
        if self.has_field(field.x, field.y):
            raise WorldError(
                f"Nelze přidat políčko {field}, protože již jedno s těmito "
                f"souřadnicemi má", self)

        # Přidání daného políčka do světa
        self._fields.append(field)

    def remove_field(self, x: int, y: int):
        """Funkce se pokusí odstranit políčko na dodaných souřadnicích.
        Pokud políčko není evidováno, je vyhozena výjimka.
        """

        # Pokud má tento svět políčko [x, y]
        if self.has_field(x, y):

            # Odstraň ho z evidence
            self._fields.remove(self.field(x, y))
            self.log(f"Bylo odebráno políčko [{x}, {y}]")

        # Pokud ne, vyhoď výjimku
        else:
            raise WorldError(f"Políčko na souřadnicích [{x}, {y}] neexistuje "
                             f"a nelze tedy ani odstranit", self)

    def neighbours(self, x: int, y: int) -> "tuple[field_mod.Field]":
        """Funkce se pokusí získat všechna políčka sousedící s tím na dodaných
        souřadnicích ve všech platných směrech. Počet navrácených políček se
        vždy pohybuje mezi 0 a počtem platných směrů, typicky tedy 4.
        Navrácení sousedé mnohou být cesty stejně jako stěny.

        Pokud na dodaných souřadnicích není evidované políčko, je vyhozena
        výjimka.
        """

        # Uložení dodaného políčka
        field = self.field(x, y)

        # Pokud políčko není ve světě evidováno
        if not field:
            raise WorldError(
                f"Nelze najít sousedy pro políčko [{x};{y}], protože není "
                f"ve světě evidováno", self)

        # Iniciace úložiště pro sousedy
        neighbours = []

        # Pro všechny směry
        for direction in Direction:

            # Souřadnice posunutého políčka v daném směru
            moved_coords = field.coordinates.move_in_direction(direction)

            # Zjištění souseda; pokud je obsažen ve světě (není None)
            # je přidán do úložiště sousedů
            neighbour = self.field(moved_coords.x, moved_coords.y)
            if neighbour:
                neighbours.append(neighbour)

        # Navrácení v podobě ntice
        return tuple(neighbours)


class WorldError(PlatformError):
    """Výjimka 'WorldError' svojí podstatou rozšiřuje obecnou výjimku tím, že
    v sobě uchovává referenci na svět, v jehož kontextu došlo k chybě."""

    def __init__(self, message: str, world: "World"):
        """Initor, který přijímá textovou zprávu o chybě a postupuje ji svému
        předkovi, a svět, v jehož kontextu došlo k chybě."""
        PlatformError.__init__(self, message)
        self._world = world

    @property
    def world(self) -> "World":
        """Svět, v jehož kontextu došlo k chybě."""
        return self._world
