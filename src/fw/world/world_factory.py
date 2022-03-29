"""Tento modul je odpovědný za definici továrních tříd světů. Jejich účelem
je dynamicky tvořit na požádání nové instance světa."""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.world.world as world_module
import src.fw.world.world_interface as world_if_module
import src.fw.world.field as field_module
from src.fw.utils.error import PlatformError


class WorldFactory(ABC):
    """Abstraktní tovární třída mající za cíl připravit instanci světa."""

    def __init__(self,
                 world_if_factory: "world_if_module.WorldInterfaceFactory"):
        """Initor přijímá v initoru továrnu rozhraní světa, která bude použita
        pro vytvoření instance 'WorldInterface' příslušné tvořenému světu."""
        self._world_if_fact = world_if_factory

    @property
    def world_interface_fact(self) -> "world_if_module.WorldInterfaceFactory":
        """Vlastnost odpovědná za poskytnutí uložené instance továrny rozhraní
        světa, která je použita pro potřeby tvorby instancí 'WorldInterface'.
        """
        return self._world_if_fact

    @abstractmethod
    def build(self) -> "world_module.World":
        """Abstraktní metoda stanovující protokol abstraktní třídy
        WorldFactory. Funkce je odpovědná za generování instance světa v
        závislosti na parametrech dodaných v konstruktoru."""


class OpenSpaceWorldFactory(WorldFactory):
    """Instance této třídy tvoří jednoduché obdélníkové světy s otevřeným
    prostorem. Z dodaných parametrů o šířce a výšce se vygeneruje obdélníková
    plocha složená z navštivitelných políček (cest). Ta je obehnána stěnami
    ze všech 4 stran."""

    def __init__(self, width: int, height: int,
                 world_if_fact: "world_if_module.WorldInterfaceFactory"):
        """Initor třídy, který přijímá šířku a výšku tvořeného světa a továrnu
        rozhraní světa.

        Šířka a výška v sobě již má započítány okolní stěny, tedy počet cest
        vypočítáme jako ((width - 2) * (height - 2)). Oba tyto parametry musí
        mít hodnotu větší nebo rovnu 3, jinak je vyhozena výjimka.

        Továrna rozhraní světa je odpovědná za tvorbu instancí třídy
        'WorldInterface', které jsou pro takový svět mezivrstvou chránící
        svět před nekonzistentními a neintegritními stavy při interakci.
        """

        # Volání initoru předka
        WorldFactory.__init__(self, world_if_fact)

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

    def build(self) -> "world_module.World":
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
        return world_module.World(all_fields, self.world_interface_fact)


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
