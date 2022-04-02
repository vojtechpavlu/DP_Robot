"""V modulu 'unit.py' jsou definovány všechny prostředky pro reprezentaci
a manipulaci v kontextu jednotek robota."""


# Prevence cyklických importů
from __future__ import annotations

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.robot.mounting_error import MountingError
from src.fw.utils.error import PlatformError
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named
from src.fw.utils.described import Described

import src.fw.robot.robot as robot_module
import src.fw.robot.interaction as interaction_module


class AbstractUnit(Identifiable, Named, Described,
                   interaction_module.InteractionFactory):
    """Abstraktní třída AbstractUnit definuje základní společný protokol
    pro všechny jednotky, kterými je možné robota osadit.

    Jádrem je rozlišitelnost senzorů a aktuátorů, stejně jako udržování
    reference na robota, který je instancí této jednotky osazen.

    Kromě toho zastávají jednotky i roli tzv. 'InteractionFactory'. Z titulu
    rodičovství této třídy vůči abstraktní jednotce jsou potomci třídy
    AbstractUnit opatřeni schopností interagovat s rozhraním světa, tedy
    budovat a posílat instance interakcí na toto rozhraní, které tyto zpracuje.
    """

    def __init__(self, unit_name: str, unit_desc: str,
                 unit_factory: "AbstractUnitFactory"):
        """Jednoduchý initor, který přijímá v parametru název, který je
        jednotce přiřazen. Dále přijímá popis jednotky, kterým bude tato dále
        schopna sebe sama popsat co do jejího účelu, způsobu použití nebo
        různých omezení.

        Stejně tak jednotka vrací referenci na svého tvůrce, tedy instanci
        továrny jednotek, která tuto vytvořila. Proto tuto referenci v
        parametru také vyžaduje.

        Kromě uložení těchto informací je dále initor odpovědný za iniciaci
        svých předků a připravení pole pro robota, kterým je jednotka osazena.
        Ten je pochopitelně v úvodní fázi neurčený.
        """
        Identifiable.__init__(self)
        Named.__init__(self, unit_name)
        Described.__init__(self, unit_desc)
        interaction_module.InteractionFactory.__init__(self)

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

    @abstractmethod
    def scan(self) -> object:
        """Abstraktní funkce odpovědná za stanovení protokolu pro provedení
        interakce se světem a navrácení informace o něm.

        Ta může být různé podoby; v závislosti na konkrétní implementaci
        jednotky."""

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


class Actuator(AbstractUnit):
    """Actuator je abstraktní třída definující společný protokol pro všechny
    aktuátory. Především tedy definuje jednoduché pomocné funkce, které
    není dále nutné definovat ve všech potomcích.

    Hlavní podstata je však ve způsobu manipulace s instancemi této třídy.
    Aktuátory mají za cíl provádět jednorázové operace v rámci světa. Tyto
    interakce mohou vyústit v chybu. To je rozdíl od senzorů, které naopak
    žádnou chybu vyhazovat nemohou, zato vrací informaci o světě a změnu v
    něm neprovádí.

    Instance třídy Actuator mají silnou vazbu na funkci 'execute()', která
    je na abstraktní úrovni definována předkem.
    """

    def __init__(self, unit_name: str, unit_desc: str,
                 unit_factory: "AbstractUnitFactory"):
        """Jednoduchý initor odpovědný za volání předka."""
        AbstractUnit.__init__(self, unit_name, unit_desc, unit_factory)

    def is_sensor(self) -> bool:
        """Funkce vrací informaci o tom, že tato jednotka není senzorem."""
        return False

    def is_actuator(self) -> bool:
        """Funkce vrací informaci o tom, že tato jednotka je aktuátorem."""
        return True


class Sensor(AbstractUnit):
    """Sensor je abstraktní třída definující společný protokol pro všechny
    senzory. Především tedy definuje jednoduché pomocné funkce, které není
    dále nutné definovat ve všech potomcích.

    Hlavní podstata je však ve způsobu manipulace s instancemi této třídy.
    Senzory mají za cíl získávat informaci o světě, ve kterém se robot
    vyskytuje a jejich působení na svět nemůže samo o sobě vyústit v chybu.
    Opakem je tomu u aktuátorů, které naopak žádnou informaci nevrací, zato
    provádí ve světě operace, které v chybu vyústit mohou.

    Instance třídy Sensor mají silnou vazbu na funkci 'scan()', která je
    na abstraktní úrovni definována předkem."""

    def __init__(self, unit_name: str, unit_desc: str,
                 unit_factory: "AbstractUnitFactory"):
        """Jednoduchý initor odpovědný za volání předka."""
        AbstractUnit.__init__(self, unit_name, unit_desc, unit_factory)

    def is_sensor(self) -> bool:
        """Funkce vrací informaci o tom, že tato jednotka je senzorem."""
        return True

    def is_actuator(self) -> bool:
        """Funkce vrací informaci o tom, že tato jednotka není aktuátorem."""
        return False


class AbstractUnitFactory(Identifiable, Named,
                          interaction_module.InteractionHandlerFactory):
    """Abstraktní třída 'UnitFactory' definuje obecný protokol pro své
    potomky, tedy již konkrétní tovární třídy jednotlivých jednotek.

    Koncepce tovární třídy umožňuje standardizaci definice a znovupoužití
    procesu tvorby instancí jednotek (instancí třídy 'Unit').

    Kromě toho zastává roli také tzv. 'InteractionHandlerFactory', tedy že
    jsou instance této třídy odpovědné za poskytování instancí handlerů. Tím
    je zajištěno, že lze obdržet nástroje pro zpracování interakcí vytvořených
    jednotkou vytvořenou touto továrnou.
    """

    def __init__(self, factory_name: str, unit_name: str):
        """Initor třídy, který volá initory svých předků a přijímá v
        parametru název tovární třídy a název, který přijmou jednotlivé
        jednotky."""

        Identifiable.__init__(self)
        Named.__init__(self, factory_name)
        interaction_module.InteractionHandlerFactory.__init__(self)

        """Název, který budou jednotlivé jednotky nést."""
        self._unit_name = unit_name

    @property
    def unit_name(self) -> str:
        """Vlastnost vrací název, který je jednotkám stanoven."""
        return self._unit_name

    @abstractmethod
    def build(self) -> "AbstractUnit":
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

    def __init__(self, message: str, unit: "AbstractUnit"):
        """Jednoduchý initor třídy, který přijímá v parametru zprávu o chybě a
        jednotku, v souvislosti s kterou došlo k chybě.
        """
        PlatformError.__init__(self, message)
        self._unit = unit

    @property
    def unit(self) -> "AbstractUnit":
        """Vlastnost vracející inkriminovanou jednotku, v jejímž kontextu
        došlo k chybě."""
        return self._unit

