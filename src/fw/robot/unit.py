"""V modulu 'unit.py' jsou definovány všechny prostředky pro reprezentaci
a manipulaci v kontextu jednotek robota."""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.robot.mounting_error import MountingError
from src.fw.utils.error import PlatformError
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named

import src.fw.robot.robot as robot_module


class AbstractUnit(ABC, Identifiable, Named):
    """Abstraktní třída AbstractUnit definuje základní společný protokol
    pro všechny jednotky, kterými je možné robota osadit.

    Jádrem je rozlišitelnost senzorů a aktuátorů, stejně jako udržování
    reference na robota, který je instancí této jednotky osazen."""

    def __init__(self, unit_name: str, unit_factory: "AbstractUnitFactory"):
        """Jednoduchý initor, který přijímá v parametru název, který je
        jednotce přiřazen. Stejně tak jednotka vrací referenci na svého
        tvůrce, tedy instanci továrny jednotek, která tuto vytvořila.

        Kromě uložení těchto informací je dále initor odpovědný za iniciaci
        svých předků a připravení pole pro robota, kterým je jednotka osazena.
        Ten je pochopitelně v úvodní fázi neurčený.
        """
        Identifiable.__init__(self)
        Named.__init__(self, unit_name)

        self._robot: "robot_module.Robot" = None
        self._unit_factory = unit_factory

    @property
    def robot(self) -> "robot_module.Robot":
        """Vlastnost vrací robota, kterému je tato jednotka přiřazena."""
        return self._robot

    @property
    def unit_factory(self) -> "AbstractUnitFactory":
        """Vlastnost vrací referenci na instanci tovární třídy jednotek,
        která je za vznik této instance odpovědná."""
        return self._unit_factory

    @property
    @abstractmethod
    def is_sensor(self) -> bool:
        """Abstraktní vlastnost vrací, zda-li jde o senzor či nikoliv."""

    @property
    @abstractmethod
    def is_actuator(self) -> bool:
        """Abstraktní vlastnost vrací, zda-li jde o aktuátor či nikoliv."""

    @abstractmethod
    def execute(self):
        """Abstraktní funkce odpovědná za stanovení protokolu provedení
        interakce se světem."""

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


class Actuator(ABC, AbstractUnit):
    """"""

    def __init__(self, unit_name: str, unit_factory: "AbstractUnitFactory"):
        """"""
        AbstractUnit.__init__(self, unit_name, unit_factory)

    def is_sensor(self) -> bool:
        """Funkce vrací informaci o tom, že tato jednotka není senzorem."""
        return False

    def is_actuator(self) -> bool:
        """Funkce vrací informaci o tom, že je aktuátorem."""
        return True


class AbstractUnitFactory(ABC, Identifiable, Named):
    """Abstraktní třída 'UnitFactory' definuje obecný protokol pro své
    potomky, tedy již konkrétní tovární třídy jednotlivých jednotek.

    Koncepce tovární třídy umožňuje standardizaci definice a znovupoužití
    procesu tvorby instancí jednotek (instancí třídy 'Unit').
    """

    def __init__(self, factory_name: str, unit_name: str):
        """Initor třídy, který volá initory svých předků a přijímá v
        parametru název tovární třídy a název, který přijmou jednotlivé
        jednotky."""

        Identifiable.__init__(self)
        Named.__init__(self, factory_name)

        """Název, který budou jednotlivé jednotky nést."""
        self._unit_name = unit_name

    @property
    def unit_name(self) -> str:
        """Vlastnost vrací název, který je jednotkám stanoven."""
        return self._unit_name

    @property
    def unit_description(self) -> str:
        """Vlastnost vrací popis, který je jednotkám stanoven."""
        return self._unit_desc

    @abstractmethod
    def build(self) -> "Unit":
        """Abstraktní metoda 'build()' slouží jako přístupová tovární metoda
        pro standardizaci protokolu tovární třídy. Implementace této metody
        mají za cíl tvořit jim příslušné jednotky.
        Nesmí se opomenout nutnost registrace jednotek do evidence, aby byl
        systém kompletní. To je nutné provádět uvnitř těla této funkce, resp.
        v rámci implementací."""


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
        došlo k chybě."""
        return self._unit

