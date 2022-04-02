"""Tento modul obsahuje definici rozhraní světa, se kterým robot pomocí svých
jednotek interaguje.

Rozhraní světa je přidanou vrstvou mezi svět a mezi robota tak, aby bylo možné
zabezpečit svět před nepovolenými interakcemi, pro zajištění jeho integrity a
pro stanovení jednotného a snazšího rozhraní pro manipulaci se světem."""


# Prevence cyklických importů
from __future__ import annotations

# Import standardních knihoven
from abc import ABC, abstractmethod


# Import lokálních knihoven
import src.fw.world.world as world_module
import src.fw.robot.interaction as interaction_module
import src.fw.world.interaction_handler_manager as ihm_module
import src.fw.world.interaction_rules as inter_rls


class WorldInterface(ihm_module.InteractionHandlerManager):
    """Instance této třídy slouží jako jakási fasáda světa. Tato vrstva mezi
    světem a robotem (resp. jeho jednotkami) je navržena tak, aby zpracovávala
    interakce robota a propisovala je do světa, stejně jako o světě vracela
    požadované informace."""

    def __init__(
            self, world: "world_module.World",
            rules_manager_factory: "inter_rls.InteractionRuleManagerFactory"):
        """Initor třídy, který přijímá instanci světa, kterému náleží a se
        kterým bude tato komunikovat. Dále pracuje s továrnou správce
        interakčních pravidel, ze které si vytvoří novou instanci třídy
        'InteractionRuleManager', pomocí které bude ověřovat interakce.
        """

        ihm_module.InteractionHandlerManager.__init__(self)

        self._world = world
        self._rules_manager = rules_manager_factory.build()

    @property
    def world(self) -> "world_module.World":
        """Svět, kterému toto rozhraní náleží."""
        return self._world

    @property
    def interaction_rules_manager(self) -> "inter_rls.InteractionRuleManager":
        """Vlastnost vrací správce interakčních pravidel, který je odpovědný
        za validaci dodaných interakcí podle vnitřního schématu uměle
        vytvořených pravidel (nevycházejících z podmínek integrity světa)."""
        return self._rules_manager

    def violated_rules(self, interaction: "interaction_module.Interaction"
                       ) -> "tuple[inter_rls.InteractionRule]":
        """Funkce vrací ntici všech pravidel, která dodaná interakce porušuje.
        Může jich tedy porušit hned několik zároveň."""
        return self.interaction_rules_manager.violated_rules(interaction)

    def check_interaction(self, interaction: "interaction_module.Interaction"):
        """Funkce se pokusí ověřit platnost interakce.

        V první řadě je ověřena interakce vůči interakčním pravidlům. Pokud
        je množina interakčních pravidel prázdná, je z tohoto pohledu
        interakce validní. V opačném případě je vyhozena výjimka."""

        # Ověření vůči interakčním pravidlům
        violated = self.violated_rules(interaction)
        if len(violated) > 0:
            raise inter_rls.InteractionRulesError(
                f"Byla porušena pravidla pro interakci", violated)
        # TODO - Přidat kontrolu (příslušnost, roboti, jednotky, ...)

    def check_unit(self, interaction: "interaction_module.Interaction"):
        """Funkce se pokusí ověřit, že je interakce platná a validní v
        kontextu jednotky.

        Kontrolována je především existence jednotky, která je za tvorbu
        této interakce odpovědná. Stejně tak je ověřována aktivita jednotky;
        v době vyhodnocování této funkce nesmí být deaktivována. Dále je
        porovnáván typ interakce s typem, který garantuje jednotka.

        Pokud cokoliv není v pořádku, je vyhozena výjimka.
        """

        # Získání reference na jednotku, která bude podrobena zkouškám
        unit = interaction.unit

        # Jednotka není určena
        if unit is None:
            raise interaction_module.InteractionError(
                f"Interakce vznikla bez přičinění jednotky nebo na ni nemá "
                f"referenci", interaction)

        # Jednotka je deaktivována
        elif unit.is_deactivated:
            raise interaction_module.InteractionError(
                f"Daná jednotka je deaktivována", interaction)

        # Jednotka je odpovědná za tvorbu jiného typu interakcí
        elif interaction.interaction_type != unit.interaction_type:
            raise interaction_module.InteractionError(
                f"Jednotka je odpovědná za tvorbu jiného typu interakcí: "
                f"{interaction.interaction_type=} != {unit.interaction_type=}",
                interaction)

    def process_interaction(
            self, interaction: "interaction_module.Interaction") -> object:
        """Funkce odpovědná za zprocesování požadované interakce na úrovni
        světa, resp. jeho rozhraní. Před zpracováním dané interakce je však
        tato podrobena zkouškám ověřujícím její platnost.
        """
        self.check_interaction(interaction)
        return self.get_interaction_handler(interaction).execute(
            interaction, self)


class WorldInterfaceFactory(ABC):
    """Abstraktní továrna rozhraní světa stanovuje obecný protokol pro
    všechny továrny starající se o dynamické poskytování instancí třídy
    WorldInterface.

    Cílem je poskytnout instanci rozhraní světa se všemi potřebnými
    vlastnostmi; typicky především včetně umělých (interakčních) pravidel.
    """

    @abstractmethod
    def build(self, world: "world_module.World") -> "WorldInterface":
        """Abstraktní funkce 'build()' odpovědná za vytvoření rozhraní
        světa. Funkce přijímá referenci na svět, jehož rozhraní má být
        touto funkcí vytvořeno a vráceno jako návratová hodnota funkce.

        Její implementace v potomcích této třídy se musí postarat o vytvoření
        instance schopné přijímat a aplikovat interakce robotů."""


class DefaultWorldInterfaceFactory(WorldInterfaceFactory):
    """Tovární třída odpovědná za poskytování výchozích instancí třídy
    'WorldInterface', tedy s výchozím nastavením."""

    def __init__(self):
        """Jednoduchý initor odpovědný za iniciaci předka."""
        WorldInterfaceFactory.__init__(self)

    def build(self, world: "world_module.World") -> "WorldInterface":
        """Implementace abstraktní funkce předka. Jejím cílem je poskytnutí
        instance rozhraní světa. Konkrétně má tato za cíl poskytnout instanci
        s výchozím nastavením.

        Konkrétněji tedy dodává instanci rozhraní světa pro dodaný svět s
        defaultními interakčními pravidly, resp. s defaultním správcem
        interakčních pravidel."""

        # Definice továrny správce interakčních pravidel; použití výchozí
        ir_manager_factory = inter_rls.DefaultInteractionRuleManagerFactory()

        # Vrácení nově vytvořené instance rozhraní světa
        return WorldInterface(world, ir_manager_factory)

