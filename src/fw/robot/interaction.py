"""Modul sdružuje veškerou funkcionalitu ve vztahu k interakcím mezi robotem
a světem a zpracováním takových interakcí.

Především je zde definice abstraktních tříd samotné interakce, handleru
interakcí a správce handlerů interakcí. Dále obsahuje definici tříd
InteractionFactory a InteractionHandlerFactory."""


# Prevence cyklických importů
from __future__ import annotations

# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Type

# Import lokálních knihoven
from src.fw.utils.error import PlatformError
from src.fw.utils.named import Named
from src.fw.utils.described import Described
from src.fw.utils.identifiable import Identifiable

import src.fw.robot.unit as unit_module
import src.fw.world.world_interface as wrld_interf_module


class Interaction(Identifiable, Named, Described):
    """Abstraktní třída interakce, která definuje nejzákladnější protokol
    pro všechny interakce, se kterými je možné se v systému setkat.

    Tato třída obsahuje definici způsobu správy jednotky, která je původcem
    této interakce, stejně jako abstraktní protokol pro funkci, která se
    stará (podle návrhového vzoru Command) o samotné provedení akce v
    souvislosti se světem, resp. jeho rozhraním."""

    def __init__(self, name: str, desc: str, unit: "unit_module.AbstractUnit"):
        """"""
        Identifiable.__init__(self)
        Named.__init__(self, name)
        Described.__init__(self, desc)

        self._unit = unit

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ, kterého daná interakce je."""
        return type(self)

    @property
    def unit(self) -> "unit_module.AbstractUnit":
        """Vlastnost vrací jednotku, která je původcem této interakce. Pomocí
        toho je také možné získat referenci na robota, který danou interakci
        ze svého programu inicioval.
        """
        return self._unit

    @abstractmethod
    def execute_interaction(
            self, interface: "wrld_interf_module.WorldInterface") -> object:
        """Abstraktní funkce, která se pokusí podle vzoru Command provést
        danou interakci a vrátit výsledek."""


class InteractionHandler:
    """Třída InteractionHandler definuje obecný protokol pro všechny handlery
    (zpracovatele) interakcí. To umožňuje dynamické použití interakcí podle
    návrhového vzoru Command.

    Základním předpokladem je schopnost rozlišení jednotlivých interakcí,
    za jejichž zpracování je tento handler odpovědný, stejně jako existence
    autority (kontejneru), který jejich zpracování řídí.
    """

    def __init__(self, interaction_type: "Type"):
        """Initor třídy, který je odpovědný za uložení dodaného typu interakce,
        za jejíž zpracování je tento handler odpovědný.
        """
        self._interaction_type = interaction_type

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, za který je tento handler odpovědný.
        """
        return self._interaction_type

    def is_mine(self, interaction: "Interaction") -> bool:
        """Funkce vrací, zda-li dodaný handler je odpovědný za zpracování
        dodané interakce."""
        return type(interaction) is self.interaction_type

    def execute(self, interaction: "Interaction",
                interface: "wrld_interf_module.WorldInterface") -> object:
        """"""
        if self.is_mine(interaction):
            return interaction.execute_interaction(interface)
        else:
            raise Exception(
                f"Interakce typu '{type(interaction)}' nelze zpracovávat "
                f"tímto handlerem: '{self}'")


class InteractionHandlerFactory(ABC):
    """Abstraktní třída InteractionHandlerFactory slouží k tvorbě handlerů,
    které jsou odpovědné za zpracování příslušných interakcí.

    Tato třída stanovuje obecný protokol sestávající se ze dvou základních
    (abstraktních) funkcí, které je třeba v potomcích implementovat."""

    @property
    @abstractmethod
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, za jehož typ je daný handler co do
        zpracování odpovědný."""

    @abstractmethod
    def interaction_handler(self) -> "InteractionHandler":
        """Abstraktní funkce vrací handler, který je odpovědný za zpracování
        příslušného typu interakce."""


class InteractionFactory(ABC):
    """Abstraktní třída InteractionFactory definuje způsob, jakým mají být
    vytvářeny a postupovány interakce se světem, resp. jeho rozhraním.

    Kromě rozhraní světa v sobě instance této třídy uchovávají i informaci
    o svém stavu co do deaktivace. Deaktivace této továrny interakcí má za
    následek totální zneschopnění provádění jakýchkoliv interakcí s rozhraním
    světa, přichází o odkaz na něj a sama se převádí do stavu mimo provoz."""

    def __init__(self):
        """Initor třídy, který je odpovědná především za připravení prázdných
        polí. Konkrétně o privátní uložení reference na rozhraní světa; tak,
        aby byl co nejvíce znepříjemněn pokus o její získání.

        Kromě rozhraní světa tato továrna definuje ve svém initoru i pole pro
        informaci o své deaktivaci. Pokud je tato továrna deaktivována, ztrácí
        svoji schopnost interakce s rozhraním světa.
        """
        # Nastavení rozhraní světa
        self.__world_interface: "wrld_interf_module.WorldInterface" = None

        # Nastavení defaultní hodnoty deaktivace
        self.__is_deactivated = False

    @property
    def is_deactivated(self) -> bool:
        """Vlastnost vrací informaci o tom, zda-li byla tato továrna interakcí
        deaktivována. Její deaktivace je pro tuto instanci nevratný proces."""
        return self.__is_deactivated

    def set_world_interface(
            self, world_interface: "wrld_interf_module.WorldInterface"):
        """Funkce se pokusí nastavit rozhraní světa (se kterým má být
        interagováno). Pokud je postoupena prázdná instance (None), je
        vyhozena výjimka; stejně tak v případě, že by zde byl pokus o
        znovunastavení již existujícího rozhraní.
        """
        if self.is_deactivated:
            # Pokud je továrna interakcí deaktivována
            raise InteractionFactoryError(
                "Nelze měnit rozhraní světa deaktivované továrně interakcí",
                self)

        elif world_interface is None:
            # Pokud je dodané rozhraní světa None
            raise InteractionFactoryError(
                "Nelze nastavit prázdné rozhraní světa", self)

        elif self.__world_interface is not None:
            # Pokud již jednou rozhraní světa bylo nastaveno
            raise InteractionFactoryError(
                "Rozhraní světa již jednou nastaveno bylo", self)

        # Jinak nastav nové rozhraní světa
        self.__world_interface = world_interface

    def interact(self) -> object:
        """Funkce odpovědná za provedení interakce, resp. její iniciace.
        Ta je odeslána na objekt rozhraní světa, které je z titulu
        'InteractionHandlerManager' odpovědné za její zprocesování.

        Pokud je v době volání této funkce továrna interakcí nevratně
        deaktivována, ztratila v ten moment schopnost provádění interakcí a
        tato funkce vyhazuje výjimku.
        """
        if self.is_deactivated:
            raise InteractionFactoryError(
                "Nelze interagovat po deaktivaci", self)
        return self.__world_interface.process_interaction(
            self.build_interaction())

    def deactivate(self):
        """Funkce nastaví továrnu interakcí jako neaktivní. Tato továrna po
        zavolání této funkce ztrácí jakoukoliv schopnost interakce s rozhraním
        světa."""
        self.__world_interface = None
        self.__is_deactivated = True

    @abstractmethod
    def build_interaction(self) -> "Interaction":
        """Abstraktní funkce, která definuje protokol způsobu získávání
        instance interakce."""


class InteractionFactoryError(PlatformError):
    """Instance této třídy reprezentují upozornění na chybu v kontextu
    továrny interakcí. Svého předka tyto obohacují o udržení reference na
    továrnu interakcí, v jejímž kontextu došlo k chybě."""

    def __init__(self, message: str, factory: "InteractionFactory"):
        """Initor, který přijímá zprávu o chybě, kterou postupuje svému
        předkovi, a továrnu interakcí, v jejímž kontextu došlo k chybě."""
        # Volání předka
        PlatformError.__init__(self, message)

        # Uložení reference na továrnu interakcí
        self._factory = factory

    @property
    def interaction_factory(self) -> "InteractionFactory":
        """Vlastnost vrací továrnu interakcí, v jejímž kontextu došlo k chybě.
        """
        return self._factory




