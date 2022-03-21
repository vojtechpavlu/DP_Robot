"""V tomto modulu je definice kontejneru robotů. Konkrétně jsou zde sdruženy
prostředky pro uchovávání robotů.
"""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.robot.robot as robot_module
from src.fw.utils.error import PlatformError


class RobotContainer(ABC):
    """Abstraktní definice společných rysů všech kontejnerů robotů.

    Počítá se zde s možnou variancí v rámci způsobu implementace a způsobu
    užití jednotlivých potomků této třídy."""

    @property
    @abstractmethod
    def has_any_robot(self) -> bool:
        """Abstraktní vlastnost vrací informaci o tom, zda-li je v tomto
        kontejneru evidován nějaký robot."""

    @abstractmethod
    def has_robot(self, robot: "robot_module.Robot") -> bool:
        """Abstraktní metoda vrací hodnotu je-li v kontejneru evidován dodaný
        robot. Pokud ano, je vrácena hodnota True, jinak False."""


class SingleRobotContainer(RobotContainer):
    """Tento kontejner představuje kontejner, do kterého se 'vejde' pouze
    jeden robot. Způsobem použití je typicky uchování reference na jediného
    robota, přičemž silně apelujem na ochranu před jeho přepsáním."""

    def __init__(self):
        """"""
        self._robot: "robot_module.Robot" = None

    @property
    def robot(self) -> "robot_module.Robot":
        """Vlastnost vrací referenci na robota, který je v této uložen."""
        return self._robot

    @property
    def has_any_robot(self) -> bool:
        """Vlastnost vrací informaci o tom, zda-li je v tomto kontejneru
        robot. Pokud ano, vrací True, jinak False."""
        return self.robot is not None

    @robot.setter
    def robot(self, robot: "robot_module.Robot"):
        """Vlastnost obalující funkci, která má za cíl nastavit jediného
        robota tohoto kontejneru.

        Pokud již jeden robot v tomto kontejneru je nastaven, není možné
        nastavit do tohoto jiného. Při pokusu o přepis je vyhozena výjimka.
        """
        if self.has_any_robot and self.robot is not robot:
            raise RobotContainerError(
                f"Nelze přenastavit robota: {self.robot=} -> {robot=}", self)
        self._robot = robot

    def has_robot(self, robot: "robot_module.Robot") -> bool:
        """Metoda vrací hodnotu je-li v kontejneru evidován dodaný robot.
        Pokud ano, je vrácena hodnota True, jinak False."""
        return self.robot == robot

    def pop_robot(self) -> "robot_module.Robot":
        """Vlastnost vyhodí robota, který je v kontejneru evidován a vrátí ho.
        """
        if not self.has_any_robot:
            raise RobotContainerError(
                f"V kontejneru žádný robot evidován není", self)
        robot = self.robot
        self.robot = None
        return robot


class MultiRobotContainer(RobotContainer):
    """Kontejner robotů, ve kterém umožňujeme uchovávat více robotů zároveň.
    """

    def __init__(self):
        """"""
        self._robots: "list[robot_module.Robot]" = []

    @property
    def has_any_robot(self) -> bool:
        """Vlastnost vrací informaci o tom, zda-li je v tomto kontejneru
        evidován alespoň jeden robot. Pokud ano, vrací True, jinak False."""
        return len(self.robots) > 0

    @property
    def robots(self) -> "tuple[robot_module.Robot]":
        """Vlastnost vrací ntici všech evidovaných robotů."""
        return tuple(self._robots)

    def has_robot(self, robot: "robot_module.Robot") -> bool:
        """Funkce vrací informaci o tom, zda-li dodaný robot již v evidenci
        obsažen je. Pokud ano, je vrácena hodnota True, jinak False."""
        return robot in self.robots

    def add_robot(self, robot: "robot_module.Robot"):
        """Funkce se pokusí zařadit robota do evidence. Pokud již jednou
        evidován tento je, je vyhozena výjimka."""
        if self.has_robot(robot):
            raise RobotContainerError(
                f"Nelze stejného robota evidovat dvakrát: {robot}", self)
        self._robots.append(robot)

    def remove_robot(self, robot: "robot_module.Robot"):
        """Funkce se pokusí vyhodit dodaného robota z evidence.
        Výjimka je vyhozena není-li tento přítomen v kontejneru.
        """
        if not self.has_any_robot:
            raise RobotContainerError(
                f"V evidenci není žádný robot", self)
        elif not self.has_robot(robot):
            raise RobotContainerError(
                f"V evidenci není robot {robot}", self)
        self._robots.remove(robot)


class RobotContainerError(PlatformError):
    """Výjimka reprezentuje ten typ chyby, který kontextově odpovídá chybám
    vzniklým při práci s kontejnery robotů."""

    def __init__(self, message: str, container: RobotContainer):
        PlatformError.__init__(self, message)
        self._container = container

    @property
    def robot_container(self) -> "RobotContainer":
        """Vlastnost vrací kontejner robotů, v jehož kontextu došlo k chybě.
        """
        return self._container



