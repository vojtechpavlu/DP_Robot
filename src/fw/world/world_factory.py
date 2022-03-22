""""""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.world.world as world_module
from src.fw.utils.error import PlatformError


class WorldFactory(ABC):
    """Abstraktní tovární třída mající za cíl připravit instanci světa."""

    @abstractmethod
    def build(self) -> "world_module.World":
        """Abstraktní metoda stanovující protokol abstraktní třídy
        WorldFactory. Funkce je odpovědná za generování instance světa v
        závislosti na parametrech dodaných v konstruktoru."""


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
