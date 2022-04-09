"""Tento modul je odpovědný za definici továrních tříd světů. Jejich účelem
je dynamicky tvořit na požádání nové instance světa."""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from typing import Iterable

import src.fw.world.world as world_module
import src.fw.world.world_interface as world_if_module
import src.fw.world.field as field_module
import src.fw.world.spawner as spawner_module

from src.fw.utils.error import PlatformError
from src.fw.utils.logging.logger import Logger
from src.fw.world.mark import Mark


class WorldFactory(ABC):
    """Abstraktní tovární třída mající za cíl připravit instanci světa."""

    def __init__(self,
                 world_if_factory: "world_if_module.WorldInterfaceFactory",
                 spawner_factory: "spawner_module.SpawnerFactory"):
        """Initor přijímá v initoru továrnu rozhraní světa, která bude použita
        pro vytvoření instance 'WorldInterface' příslušné tvořenému světu. Dále
        přijímá spawner, který bude použit pro zasazování nových robotů do
        tohoto světa."""
        # Továrna rozhraní světa
        self._world_if_fact = world_if_factory

        # Spawner pro zasazování robotů do světa
        self._spawner_factory = spawner_factory

    @property
    def world_interface_fact(self) -> "world_if_module.WorldInterfaceFactory":
        """Vlastnost odpovědná za poskytnutí uložené instance továrny rozhraní
        světa, která je použita pro potřeby tvorby instancí 'WorldInterface'.
        """
        return self._world_if_fact

    @property
    def spawner_factory(self) -> "spawner_module.SpawnerFactory":
        """Vlastnost vrací továrnu spawnerů, která byla instanci přidělena."""
        return self._spawner_factory

    @abstractmethod
    def build(self, logger: "Logger") -> "world_module.World":
        """Abstraktní metoda stanovující protokol abstraktní třídy
        WorldFactory. Funkce je odpovědná za generování instance světa v
        závislosti na parametrech dodaných v konstruktoru."""


class WorldFactoryOverride(WorldFactory):
    """Továrna světa, která formou dekorátoru (resp. podle návrhového vzoru
    Dekorátor) obaluje funkcionalitu továrny světa a upravuje tak svět
    vytvořený."""

    def __init__(self, world_factory: WorldFactory):
        """Initor, který je odpovědný za zavolání předka a poskytnutí mu
        dodaných hodnot parametrů. Dále také ukládá dodanou továrnu světa,
        kterou má za cíl obohatit a doplnit."""

        # Volání initoru předka
        WorldFactory.__init__(self, world_factory.world_interface_fact,
                              world_factory.spawner_factory)

        # Uložení továrny, kterou má tato instance upravit
        self._world_factory = world_factory

    @property
    def world_factory(self) -> WorldFactory:
        """Vlastnost vrací továrnu, kterou má tato instance doplnit."""
        return self._world_factory

    @abstractmethod
    def build(self, logger: "Logger") -> "world_module.World":
        """Abstraktní metoda stanovující protokol abstraktní třídy
        WorldFactory. Funkce je odpovědná za generování instance světa v
        závislosti na parametrech dodaných v konstruktoru.

        Konkrétně jsou instance implementující tento protokol odpovědné
        za vytvoření světa z dodané továrny a za jeho upravení."""


class OpenSpaceWorldFactory(WorldFactory):
    """Instance této třídy tvoří jednoduché obdélníkové světy s otevřeným
    prostorem. Z dodaných parametrů o šířce a výšce se vygeneruje obdélníková
    plocha složená z navštivitelných políček (cest). Ta je obehnána stěnami
    ze všech 4 stran."""

    def __init__(self, width: int, height: int,
                 world_if_fact: "world_if_module.WorldInterfaceFactory",
                 spawner_factory: "spawner_module.SpawnerFactory"):
        """Initor třídy, který přijímá šířku a výšku tvořeného světa a továrnu
        rozhraní světa.

        Šířka a výška v sobě již má započítány okolní stěny, tedy počet cest
        vypočítáme jako ((width - 2) * (height - 2)). Oba tyto parametry musí
        mít hodnotu větší nebo rovnu 3, jinak je vyhozena výjimka.

        Továrna rozhraní světa je odpovědná za tvorbu instancí třídy
        'WorldInterface', které jsou pro takový svět mezivrstvou chránící
        svět před nekonzistentními a neintegritními stavy při interakci.

        Dále initor přijímá spawner, který bude použit pro zasazování robotů
        do vytvořeného světa.
        """

        # Volání initoru předka
        WorldFactory.__init__(self, world_if_fact, spawner_factory)

        # Uložení šířky a výšky světa
        self._width = width
        self._height = height

        """Kontrola, že je svět alespoň 3 políčka široký. Při alespoň
        třech totiž je možné, aby horizontální řez světem byl WALL-PATH-WALL.
        Jiný svět by neměl smysl."""
        if self._width < 3:
            raise WorldFactoryError(
                f"Nelze vytvořit svět o šířce menší, než 3 "
                f"(obdrženo {self._width})", self)

        """Kontrola, že je svět alespoň 3 políčka vysoký. Při alespoň
        třech je totiž možné, aby vertikální řez světem byl WALL-PATH-WALL.
        Jiný svět by neměl smysl."""
        if self._height < 3:
            raise WorldFactoryError(
                f"Nelze vytvořit svět o výšce menší, než 3 "
                f"(obdrženo {self._height})", self)

    @property
    def width(self) -> int:
        """Šířka, jakou generovaný svět má. Dvě políčka z této šířky zabírá
        okolní zeď."""
        return self._width

    @property
    def height(self) -> int:
        """Výška, jakou generovaný svět má. Dvě políčka z této výšky zabírá
        okolní zeď."""
        return self._height

    def build(self, logger: Logger) -> "world_module.World":
        """Funkce, která vygeneruje obdélníkový svět obehnaný stěnou. Ten
        je z povahy implementace OpenSpace, tedy otevřený prostor.

        Funkce proiteruje všechny kombinace souřadnic. Pokud jsou souřadnice
        hraniční (minimální nebo maximální hodnota výšky nebo šířky), je
        na tuto pozici umístěna stěna, jinak cesta.
        """
        # Seznam všech políček, ze kterých se svět bude sestávat
        all_fields = []

        # Proiterování všemi kombinacemi souřadnic ( O(šířka * výška) )
        for x in range(self.width):
            for y in range(self.height):
                """Naplnění světa políčky stěn a cest"""
                if x == 0 or y == 0:
                    """Levá a dolní hranice - stěna"""
                    all_fields.append(field_module.Wall(x, y))
                elif (x == self.width - 1) or (y == self.height - 1):
                    """Pravá a horní hranice - stěna"""
                    all_fields.append(field_module.Wall(x, y))
                else:
                    """Cokoliv mezi hranicemi - cesta"""
                    all_fields.append(field_module.Path(x, y))

        """Vrácení vytvořené instance světa se všemi políčky a s továrnou
        rozhraní světa"""
        return world_module.World(all_fields, self.world_interface_fact,
                                  self.spawner_factory, logger)


class WorldWithHolesFactory(WorldFactoryOverride):
    """Instance této třídy rozšiřuje funkcionalitu běžné továrny světů o
    díry ve světě. Pomocí nich lze testovat schopnost robota se těmto políčkům
    vyhýbat.

    Tato schopnost je realizována podle návrhového vzoru Dekorátor."""

    def __init__(self, world_factory: WorldFactory,
                 holes: "Iterable[tuple[int, int]]"):
        """Initor, který přijímá referenci na továrnu světa, kterou bude
        tato instance rozšiřovat a iterovatelnou množinu děr. Tyto díry
        jsou chápány jako ntice souřadnic. Příkladnou definicí děr pak je:

            >>> [(1, 1), (2, 5), (2, 2)]

        Pokud některá z dodaných děr neodpovídá požadovanému formátu, je
        vyhozena výjimka.

        Je také důležité dbát na synchronizaci se spawnerem - pokud totiž
        ten zjistí, že by měl zasadit robota do světa na políčko, které
        neexistuje (tedy na díru), bude vyhozena výjimka také; jen později.

        Dále je dobré také uvažovat i rozměry dekorovaného světa; políčko,
        které není ve světě evidováno, nemůže být nahrazeno dírou, stejně
        jako políčko, které by mělo být proděravěno opakovaně. V obou
        případěch by byla vyhozena tatáž výjimka.
        """

        # Volání initoru předka
        WorldFactoryOverride.__init__(self, world_factory)

        # Uložení jednotlivých děr
        self._holes = tuple(holes)

        # Kontrola formátu
        for hole in holes:
            if len(hole) != 2:
                raise WorldFactoryError(
                    f"Díry musí být jasně specifikovány souřadnicemi [x, y]",
                    self)

    @property
    def holes(self) -> "tuple[tuple[int, int]]":
        """Vlastnost vrací ntici souřadnic, na kterých má být díra."""
        return self._holes

    def build(self, logger: "Logger") -> "world_module.World":
        """Implementace metody předka, která se stará o poskytnutí instance
        světa.

        Proces 'proděravění' světa zde spočívá v tom, že se vytvoří původní
        svět, který má být dekorován, a z něj jsou postupně odstraněna všechna
        políčka, která byla označena v initoru této instance jako díry.

        Pokud nelze políčko na souřadnicích některé díry odstranit (políčko
        původní svět nevytvořil nebo se díry opakují) je vyhozena výjimka."""

        # Vytvoření původního světa, který bude proděravěn
        world = self.world_factory.build(logger)

        # Pro každou díru odstraň políčko ze světa
        for hole in self.holes:
            world.remove_field(hole[0], hole[1])

        # Vrať upravený svět
        return world


class FieldPremarker(WorldFactoryOverride):
    """Instance této třídy slouží jako dekorátory světa, který má být
    upraven. Tato úprava spočívá v označení políček ještě předtím, než
    je do tohoto světa vpuštěn robot.

    Příkladně lze tyto instance použít pro označení políčka, které je
    cílovou destinací robota."""

    def __init__(self, world_factory: WorldFactory,
                 marks: "Iterable[tuple[str, int, int]]"):
        """Initor, který přijímá továrnu světa, jejíž vytvořený svět má
        být upraven. Tento initor dále přijímá sadu předpisů značek, které
        se sestávají z názvu značky a souřadnic políčka, které by mělo být
        opatřeno takovou značkou.

        Je však nutné dbát na správnou formu těchto předpisů. Musí jít o
        iterovatelnou množinu jednotlivých předpisů v podobě ntice, které
        se sestávají z názvu značky (resp. jejího textu) a dvoučíslí
        souřadnic specifikujícího políčko. Příkladně by mohl tento parametr
        vypadat následovně:

            >>> [("M", 1, 2), ("M", 3, 5), ("C", 5, 5)]

        čímž by byly stanoveny například políčka, která by měla být navštívena
        (označena "M") cestou ke stanovenému cíli (označen "C").
        """

        # Volání initoru předka
        WorldFactoryOverride.__init__(self, world_factory)

        # Uložení předpisů značek
        self._mark_tuples = tuple(marks)

        # Kontrola značek
        for mark in self._mark_tuples:
            if not len(mark) == 3:
                raise WorldFactoryError(
                    f"Každá značka musí mít 3 parametry: název, x a y. "
                    f"Obdrženo: {mark}", self)
            elif ((type(mark[0]) != str) or (type(mark[1]) != int) or
                  (type(mark[2]) != int)):
                raise WorldFactoryError(
                        f"Nesprávný formát značky; požadovaný formát je: "
                        f"(str, int, int); tedy "
                        f"(název značky, souřadnice x, souřadnice y).", self)

    @property
    def mark_tuples(self) -> "tuple[tuple[str, int, int]]":
        """Vlastnost vrací všechny předpisy značek, které mají být vytvořeny.
        """
        return self._mark_tuples

    def build(self, logger: "Logger") -> "world_module.World":
        """Tato metoda implementuje protokol předka tím, že poskytuje
        schopnost dynamicky tvořit instance světa.

        Konkrétní postup je takový, že si získá instanci dodané továrny,
        kterou hodlá tato továrna upravit. Postupně pak specifikovaná pole
        označkuje dle dodaných parametrů v initoru.

        Pokud políčko, které má být označeno neexistuje či již značku má,
        je vyhozena výjimka. Jinak se označkují všechna specifikovaná políčka.
        """

        # Připravení základu, který bude dekorován
        world = self.world_factory.build(logger)

        # Pro všechny předpisy značek
        for mark in self.mark_tuples:

            # Získej pomocí souřadnic políčko, které bude označeno
            field = world.field(mark[1], mark[2])

            # Pokud políčko s takovými souřadnicemi není
            if not field:
                raise WorldFactoryError(
                    f"Políčko na souřadnicích {list(mark[1:])} neexistuje.",
                    self)

            # Pokud již políčko označeno je
            elif field.has_mark:
                raise WorldFactoryError(
                    f"Políčko {field} již jednou označeno je: "
                    f"{field.mark.text}", self)

            # Označkuj políčko
            field.mark_yourself(str(mark[0]))

        # Vrať dekorovaný svět
        return world


class WallRebuilder(WorldFactoryOverride):
    """Instance této továrny jsou odpovědné za dekorování světa, který je
    vytvořen dodanou továrnou světů.

    Konkrétně se stará o přidání stěn dle dodaného schématu. Políčka na daných
    souřadnicích jsou nahrazeny políčky stěn (instance třídy 'Wall')."""

    def __init__(self, world_factory: WorldFactory,
                 walls: "Iterable[tuple[int, int]]"):
        """Initor, který přijímá továrnu světa, jejíž světy mají být upraveny,
        a schéma stěn.

        Toto schéma musí mít stanovenou podobu, tedy iterovatelnou množinu
        souřadnic, na kterých mají políčka být. Například lze tuto použít
        následovně:

            >>> [(1, 3), (2, 5), (3, 3)]

        Pokud bude jednotlivý předpis stěny obsahovat více nebo méně souřadnic,
        vyústí tento intior ve výjimku.
        """

        # Volání initoru předka
        WorldFactoryOverride.__init__(self, world_factory)

        # Předpisy stěn
        self._walls = tuple(walls)

        for wall in self._walls:
            if not len(wall) == 2:
                raise WorldFactoryError(
                    f"Stěna musí být specifikována dvěma souřadnicemi, tedy "
                    f"(x, y). Dodáno bylo: {wall}", self)

    @property
    def walls(self) -> "tuple[tuple[int, int]]":
        """Vlastnost vrací ntici ntic, které obsahují obě souřadnice políček.
        """
        return self._walls

    def build(self, logger: "Logger") -> "world_module.World":
        """Implementace abstraktní metody předka, která má za cíl dle dodaného
        schématu stěn odstranit původní políčka ze světa a nahradit je stěnami.

        Funkce postupuje tak, že je získána instance nově vytvořeného světa z
        dodané továrny světa a ta je postupně upravována.

        Při splnění požadovaných podmínek na formu dodaného schématu stěn by
        funkce neměla vyhazovat výjimku."""

        # Získání světa, který bude upravován
        world = self.world_factory.build(logger)

        # Pro všechny předpisy stěn
        for wall in self.walls:

            # Pokud je políčko v tomto světě evidováno
            if world.has_field(wall[0], wall[1]):

                # Odstraň políčko na souřadnicích dle předpisu
                world.remove_field(wall[0], wall[1])

            # Přidej novou stěnu
            world.add_field(field_module.Wall(wall[0], wall[1]))

        # Vrať nově vytvořený svět
        return world


class WorldFactoryError(PlatformError):
    """Výjimka rozšiřující obecnou o referenci na továrnu světa, v jejímž
    kontextu došlo k chybě.
    """

    def __init__(self, message: str, world_factory: "WorldFactory"):
        PlatformError.__init__(self, message)
        self._world_factory = world_factory

    @property
    def world_factory(self) -> "WorldFactory":
        """Továrna světa, v jejímž kontextu došlo k chybě."""
        return self._world_factory
