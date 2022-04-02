"""Modul sdružuje veškerou funkcionalitu náležící správě zpracovatelů
interakcí."""


# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.robot.interaction as inter_module
from src.fw.utils.error import PlatformError


class InteractionHandlerManager(ABC):
    """Instance této třídy jsou odpovědné za sdružování a správu handlerů pro
    zpracování interakcí."""

    def __init__(self):
        """Initor třídy, který je odpovědný především za inicializaci
        proměnných, tedy handlerů, které má správce evidovány. V úvodní
        fázi je evidence prázdná, tyto jsou dodávány až za běhu životního
        cyklu instance.
        """
        self._handlers: "list[inter_module.InteractionHandler]" = []

    @property
    def interaction_handlers(self) -> "tuple[inter_module.InteractionHandler]":
        """Vlastnost vrací ntici všech handlerů, které má správce v evidenci.
        """
        return tuple(self._handlers)

    def add_interaction_handler(self,
                                handler: "inter_module.InteractionHandler"):
        """Funkce se pokusí přidat dodaný handler do evidence tohoto správce.
        Pokud již existuje jeden handler pro zpracování interakcí stejného
        typu je v evidenci obsažen, je vyhozena výjimka.
        """
        for i_h in self.interaction_handlers:
            if i_h.interaction_type is handler.interaction_type:
                raise InteractionHandlerManagerError(
                    f"Nelze mít evidovány dva handlery pro stejný typ "
                    f"interakce: '{handler.interaction_type}'", self)
        self._handlers.append(handler)

    def has_interaction_handler(self, interaction: "inter_module.Interaction") -> bool:
        """Funkce se pokusí vyhledat handler odpovědný za zpracování interakcí
        daného typu. Pokud-že takový není nalezen, je vráceno False, jinak
        True."""
        for handler in self.interaction_handlers:
            if handler.is_mine(interaction):
                return True
        return False

    def get_interaction_handler(self, interaction: "inter_module.Interaction"
                                ) -> "inter_module.InteractionHandler":
        """Funkce se pokusí vrátit pro danou interakci handler, který je za
        zpracování této interakce odpovědný.

        Pokud takový není nalezen, je vyhozena výjimka. To typicky značí
        pokus o podvod nebo chybně definované přidání požadovaných handlerů
        do evidence.
        """
        for handler in self.interaction_handlers:
            if handler.is_mine(interaction):
                return handler
        raise InteractionHandlerManagerError(
            f"Pro interakci '{type(interaction)}' není handler evidován", self)

    @abstractmethod
    def process_interaction(self,
                            interaction: "inter_module.Interaction") -> object:
        """Abstraktní funkce se pokusí o zpracování dané interakce."""


class InteractionHandlerManagerError(PlatformError):
    """Výjimka značící vznik problému v souvislosti se správcem zpracovatelů
    interakcí. Své předky rozšiřuje právě o referenci na instanci správce,
    v jehož kontextu došlo k chybě."""

    def __init__(self, message: str, manager: "InteractionHandlerManager"):
        """Initor, který přijímá zprávu o chybě a referenci na správce
        zpracovatelů interakcí, v jehož kontextu došlo k chybě.
        """
        PlatformError.__init__(self, message)
        self._manager = manager

    @property
    def interaction_handler_manager(self) -> "InteractionHandlerManager":
        """Vlastnost vrací správce zpracovatelů interakcí, v jehož kontextu
        došlo k chybě."""
        return self._manager



