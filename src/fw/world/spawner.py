""""""


# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.world.robot_state as rs_module
import src.fw.world.world as world_module
import src.fw.robot.robot as robot_module

from src.fw.utils.error import PlatformError
from src.fw.utils.named import Named


class Spawner(ABC, Named):
    """Abstraktní třída definující způsob zasazení robota do světa. Tento
    protokol má za cíl definovat obecné zdroje pro přidávání robotů do světů.
    """

    def __init__(self, name: str):
        """"""
        Named.__init__(self, name)
        self._world: "world_module.World" = None

    @property
    def world(self) -> "world_module.World":
        """Vlastnost vrací odkaz na svět, do kterého jsou roboti zasazování.
        """
        return self._world

    @world.setter
    def world(self, world: "world_module.World"):
        """Setter pro svět. Ten může být nastaven jen jednou. Při opakovaném
        pokusu o změnu světa musí být vyhozena výjimka."""
        if self.world:
            raise SpawnerError(
                f"Svět již jednou byl nastaven: "
                f"{self.world=} -> {world=}", self)
        self._world = world

    @abstractmethod
    def spawn(self, robot: "robot_module.Robot") -> "rs_module.RobotState":
        """Implementace této funkce jsou odpovědné za vytvoření stavu robota.
        De facto jde o tovární funkci, která vytvoří pro dodaného robota
        instanci třídy 'RobotState' a nastaví robota do světa.

        Při zasazování robota do světa musí být dbáno na to, aby nebyla
        porušena integrita světa, především tedy aby nebylo možné přepsat
        jednoho robota jiným tím, že by byli dva nastavení na jedno políčko,
        stejně jako nesmí dojít k nastavení robota na políčko zdi."""


class SpawnerFactory(ABC):
    """Abstraktní třída SpawnerFactory má za cíl připravit instanci spawneru,
    který bude obsluhovat zasazování robota do světa."""

    @abstractmethod
    def build(self) -> Spawner:
        """Tato abstraktní funkce definuje protokol, který bude závazný
        pro všechny své potomky.

        Konkrétně je tato funkce odpovědná za přípravu instance spawneru,
        který bude schopen zasazovat roboty do světa."""


class SpawnerError(PlatformError):
    """Výjimka rozšiřující obecnou výjimku tím, že v sobě uchovává referenci
    na spawner, v jehož kontextu došlo k chybě."""

    def __init__(self, message: str, spawner: "Spawner"):
        PlatformError.__init__(self, message)
        self._spawner = spawner

    @property
    def spawner(self) -> "Spawner":
        """Vlastnost vrací referenci na spawner, v jehož kontextu došlo
        k chybě."""
        return self._spawner



