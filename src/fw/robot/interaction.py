"""Modul sdružuje veškerou funkcionalitu ve vztahu k interakcím mezi robotem
a světem a zpracováním takových interakcí.

Především je zde definice abstraktních tříd samotné interakce, handleru
interakcí a správce handlerů interakcí. Dále obsahuje definici tříd
InteractionFactory a InteractionHandlerFactory."""


# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Type

# Import lokálních knihoven
from src.fw.utils.named import Named
from src.fw.utils.described import Described
from src.fw.utils.identifiable import Identifiable

import src.fw.robot.unit as unit_module
import src.fw.world.world_interface as wrld_interf_module


class Interaction(ABC, Identifiable, Named, Described):
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


class InteractionHandler(ABC):
    """Abstraktní třída InteractionHandler definuje obecný protokol pro
    všechny handlery (zpracovatele) interakcí. To umožňuje dynamické použití
    interakcí podle návrhového vzoru Command.

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

    @abstractmethod
    def execute(self, interaction: "Interaction") -> object:
        """"""


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
    """"""

    def __init__(self):
        """"""
        self.__world_interface: "wrld_interf_module.WorldInterface" = None

    @abstractmethod
    def build_interaction(self) -> "Interaction":
        """"""

    def interact(self) -> object:
        """Funkce odpovědná za provedení interakce, resp. její iniciace."""


class InteractionHandlerManager(ABC):
    """Instance této třídy jsou odpovědné za sdružování a správu handlerů pro
    zpracování interakcí."""

    def __init__(self):
        """Initor třídy, který je odpovědný především za inicializaci
        proměnných, tedy handlerů, které má správce evidovány. V úvodní
        fázi je evidence prázdná, tyto jsou dodávány až za běhu životního
        cyklu instance.
        """
        self._handlers: "list[InteractionHandler]" = []

    @property
    def interaction_handlers(self) -> "tuple[InteractionHandler]":
        """Vlastnost vrací ntici všech handlerů, které má správce v evidenci.
        """
        return tuple(self._handlers)

    def add_interaction_handler(self, handler: "InteractionHandler"):
        """Funkce se pokusí přidat dodaný handler do evidence tohoto správce.
        Pokud již existuje jeden handler pro zpracování interakcí stejného
        typu je v evidenci obsažen, je vyhozena výjimka.
        """
        for i_h in self.interaction_handlers:
            if i_h.interaction_type is handler.interaction_type:
                # TODO - specifikace výjimky
                raise Exception(
                    f"Nelze mít evidovány dva handlery pro stejný typ "
                    f"interakce: '{handler.interaction_type}'")
        self._handlers.append(handler)

    def has_interaction_handler(self, interaction: "Interaction") -> bool:
        """Funkce se pokusí vyhledat handler odpovědný za zpracování interakcí
        daného typu. Pokud-že takový není nalezen, je vráceno False, jinak
        True."""
        for handler in self.interaction_handlers:
            if handler.is_mine(interaction):
                return True
        return False

    def get_interaction_handler(
            self, interaction: "Interaction") -> "InteractionHandler":
        """Funkce se pokusí vrátit pro danou interakci handler, který je za
        zpracování této interakce odpovědný.

        Pokud takový není nalezen, je vyhozena výjimka. To typicky značí
        pokus o podvod nebo chybně definované přidání požadovaných handlerů
        do evidence.
        """
        for handler in self.interaction_handlers:
            if handler.is_mine(interaction):
                return handler
        # TODO - specifikace výjimky
        raise Exception(
            f"Pro interakci '{type(interaction)}' není handler evidován")

    @abstractmethod
    def process_interaction(self, interaction: "Interaction") -> object:
        """Abstraktní funkce se pokusí o zpracování dané interakce."""




