""""""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.world.world as world_module
import src.fw.world.field as field_module
from src.fw.utils.error import PlatformError


class WorldFactory(ABC):
    """Abstraktní tovární třída mající za cíl připravit instanci světa."""

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

    def __init__(self, width: int, height: int):

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
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def build(self) -> "world_module.World":
        """"""
        all_fields = []
        for x in range(self.width):
            for y in range(self.height):
                if x == 0 or y == 0:
                    all_fields.append(field_module.Wall(x, y))
                elif (x == self.width - 1) or (y == self.height - 1):
                    all_fields.append(field_module.Wall(x, y))
                else:
                    all_fields.append(field_module.Path(x, y))
        return world_module.World(all_fields)


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
