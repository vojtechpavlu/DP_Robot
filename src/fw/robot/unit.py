""""""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.robot.mounting_error import MountingError
from src.fw.utils.error import PlatformError
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named

import src.fw.robot.robot as robot_module


class Unit(ABC, Identifiable, Named):
    """"""

    def __init__(self, unit_name: str):
        """"""
        Identifiable.__init__(self)
        Named.__init__(self, unit_name)

        self._robot: "robot_module.Robot" = None

    @property
    def robot(self) -> "robot_module.Robot":
        """Vlastnost vrací robota, kterému je tato jednotka přiřazena."""
        return self._robot

    @property
    @abstractmethod
    def is_sensor(self) -> bool:
        """Abstraktní vlastnost vrací, zda-li jde o senzor či nikoliv."""

    @property
    @abstractmethod
    def is_actuator(self) -> bool:
        """Abstraktní vlastnost vrací, zda-li jde o aktuátor či nikoliv."""

    def mount(self, robot: "robot_module.Robot"):
        """Vlastnost nastavuje robota, kterému je tato jednotka nastavena.
        Nelze však již připojenou jednotku přiřazovat znovu. Při pokusu o
        znovupřiřazení je vyhozena výjimka. Jinak by došlo k přepisu robota.
        """
        if self.robot is not None:
            raise MountingError(
                f"Již jednou osazenou jednotkou {self} není možné osadit "
                f"robota znovu: {self.robot=}, {robot=}")
        self._robot = robot

    def detach(self):
        """Funkce odpojí jednotku od robota z pohledu jednotky."""
        self._robot = None


class UnitError(PlatformError):
    """Výjimka 'UnitError' slouží k symbolizaci chyby, která vznikne při
    manipulaci s jednotkou.
    Oproti obecné 'PlatformError' je tato výjimka opatřena referencí na
    instanci jednotky, v jejímž kontextu k chybě došlo.
    """

    def __init__(self, message: str, unit: "Unit"):
        """Jednoduchý initor třídy, který přijímá v parametru zprávu o chybě a
        jednotku, v souvislosti s kterou došlo k chybě.
        """
        PlatformError.__init__(self, message)
        self._unit = unit

    @property
    def unit(self) -> "Unit":
        """Vlastnost vracející inkriminovanou jednotku, v jejímž kontextu
        došlo k chybě.
        """
        return self._unit

