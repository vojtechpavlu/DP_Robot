""""""


# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.world.robot_state as rs_module
import src.fw.world.world as world_module
import src.fw.robot.robot as robot_module
import src.fw.world.field as field_module

from src.fw.utils.error import PlatformError
from src.fw.utils.named import Named
from src.fw.world.direction import Direction


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


class CoordinatesSpawner(Spawner):
    """Spawner, který zasadí robota na pevně stanovené souřadnice s předem
    stanoveným směrem.

    Nejjednodušší spawner. Jeho problémem však je, že nemůže zasazovat na
    stejné souřadnice jednoho a toho samého robota. Pokud-že se o to pokusí,
    je vyhozena výjimka. Podobným problémem je situace, kdy dojde k pokusu
    o zasazení robota na políčko stěny.

    Pro předcházení některým těmto chybám je možné tyto souřadnice a směr
    natočení měnit během životního cyklu instance.
    """

    def __init__(self, x: int, y: int,
                 default_direction: "Direction" = Direction.EAST):
        """Jednoduchý initor funkce, který volá svého předka a ukládá dodané
        hodnoty.

        V parametrech přijímá souřadnice políčka, na které má být robot při
        registraci ve světě usazen a výchozí směr, kterým má být otočen. Ten
        je defaultně nastaven na východ, tedy 'Direction.EAST'.
        """
        Spawner.__init__(self, "CoordinatesSpawner")

        self._x = x
        self._y = y
        self._direction = default_direction

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, x: int):
        self._x = x

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, y: int):
        self._y = y

    @property
    def default_direction(self) -> "Direction":
        """Výchozí směr, na který bude zasazený robot namířen."""
        return self._direction

    @default_direction.setter
    def default_direction(self, default_direction: "Direction"):
        """Setter pro výchozí směr, tedy směr, kterým bude robot natočen."""
        self._direction = default_direction

    def spawn(self, robot: "robot_module.Robot") -> "rs_module.RobotState":
        """Funkce je odpovědná za zasazení robota do světa na definované
        souřadnice v definovaném směru.

        V první řadě funkce ověřuje, zda-li dané políčko odpovídá obecným
        požadavkům na konzistenci a integritu.

        Dále se funkce pokouší o zasazení robota do daného políčka a o
        vytvoření a vrácení stavu robota.
        """
        if self.world is None:
            raise SpawnerError(
                f"Svět nebyl doposud nastaven", self)

        field = self.world.field(self.x, self.y)

        if not field:
            raise SpawnerError(
                f"Svět nemá políčko o souřadnicích [{self.x};{self.y}]", self)
        elif field.is_wall:
            raise SpawnerError(
                f"Dodané souřadnice [{self.x};{self.y}] patří zdi", self)
        elif field.has_any_robot:
            raise SpawnerError(
                f"Na dodaných souřadnicích [{self.x};{self.y}] "
                f"již je robot '{field.robot}'", self)
        else:
            path: "field_module.Path" = field
            path.robot = robot
            return rs_module.RobotState(robot, self.world,
                                        self.default_direction, path)


class CoordinatesSpawnerFactory(SpawnerFactory):
    """Třída je odpovědná za tvorbu instancí spawnerů s vazbou na souřadnice.
    """

    def __init__(self, x: int = 1, y: int = 1,
                 direction: "Direction" = Direction.EAST):
        """Initor funkce, který v první řadě volá initor předka a dále
        ukládá dostupné parametry.

        Vstupními hodnotami jsou souřadnice, kam má být robot zasazen
        (defaultně [1; 1]), a směr, kterým má být po zasazení natočen
        (defaultně východ, tedy 'Direction.EAST'). Tyto hodnoty je možné
        dále měnit; na úrovni konkrétní instance spawneru.
        """
        SpawnerFactory.__init__(self)

        self._x = x
        self._y = y
        self._direction = direction

    def build(self) -> Spawner:
        """Prostá funkce odpovědná za vytvoření instance spawneru; konkrétně
        instance třídy CoordinatesSpawner."""
        return CoordinatesSpawner(self._x, self._y, self._direction)


class RandomSpawner(Spawner):
    """Spawner, který zasadí robota na náhodné políčko světa."""

    def __init__(self):
        Spawner.__init__(self, "RandomSpawner")

    def spawn(self, robot: "robot_module.Robot") -> "rs_module.RobotState":
        """Funkce vybere náhodné políčko (cestu) a pokusí se robota usadit.
        V první řadě si získá všechny cesty. Poté náhodně vybírá, kam by
        robota zasadil. Pokud se to na vybrané políčko nepovede, proces
        náhodného výběru a pokusu o zasazení se opakuje. A to do té doby,
        dokud nebudou vyzkoušena všechna políčka. Pokud se to ani po posledním
        nepovede, je vyhozena výjimka o nesplnitelnosti.
        """
        if self.world is None:
            raise SpawnerError(
                f"Svět nebyl doposud nastaven", self)

        """Import funkce pro náhodný výběr"""
        from random import choice
        fields = list(self.world.all_paths)

        while len(fields) > 0:
            field = choice(fields)
            if field.has_robot:
                fields.remove(field)
                continue
            else:
                field.robot = robot
                direction = choice(Direction.list())
                return rs_module.RobotState(
                    robot, self.world, direction, field)

        raise SpawnerError(
            "Neexistuje políčko, do kterého by bylo možné robota vložit", self)


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



