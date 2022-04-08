"""Jednotka 'Marker' slouží k značkování políček. Jde o aktuátor, který
dodá políčku, na kterém robot právě stojí, značku.

Jde o jednotku, která vyžaduje parametr. Konkrétním parametrem, který je
jednotce dodáván je označen klíčovým slovem 'mark'.

Způsob použití tedy je například:

    robot.get_unit("Marker").execute(mark="A")

Po aplikaci tohoto příkazu bude políčko opatřeno značkou "A".

Jednotka může vyústit v chybu, pokud:

    - Text značky neodpovídá definovaným (defaultním) pravidlům:
        - Delší než 3 znaky
        - Kratší než 1 znak
        - Obsahuje znaky jiné, než:
            - Kapitálky bez diakritiky anglické abecedy, nebo
            - Číslice 0-9;
          tedy řetězce definovatelné regulárním výrazem [A-Z0-9]{1,3}

    - Políčko již značku obsahuje
"""

# Import standardních knihoven
from typing import Type

# Import lokálních knihoven
from src.fw.robot.interaction import Interaction, InteractionError
from src.fw.robot.unit import Actuator, AbstractUnitFactory
from src.fw.world.world_interface import WorldInterface
from src.fw.world.mark import Mark
from src.fw.world.world_events import MarkChangeEvent


"""Definice proměnných"""
# Název jednotky - ten musí být napříč všemi importovanými jednotkami unikátní
_UNIT_NAME = "Marker"

# Popis jednotky - lidsky čitelný popis
_UNIT_DESCRIPTION = "Jednotka, která označí dané políčko textem"

# Název továrny jednotek - lidsky čitelný název
_UNIT_FACTORY_NAME = "MarkerFactory"

# Název interakce - pokud možno srozumitelný identifikátor toho, co se provádí
_INTERACTION_NAME = "Mark"

# Popis interakce - lidsky čitelný popis interakce, která probíhá
_INTERACTION_DESCRIPTION = "Označení políčka"


class Marker(Actuator):
    """Třída značkovače, což je jednotka poskytující funkcionalitu označkování
    políčka textovým řetězcem."""

    def __init__(self, factory: "AbstractUnitFactory"):
        """Initor aktuátoru, který z úsporných důvodů používá skromnou
        implementaci. De facto jen iniciuje svého předka názvem jednotky,
        popisem účelu jednotky (nezapomenout doplnit) a referencí na továrnu,
        která je za vytvoření této jednotky odpovědná.
        """
        Actuator.__init__(self, factory.unit_name,
                          _UNIT_DESCRIPTION, factory)

    def build_interaction(self, **kwargs) -> "Interaction":
        """Metoda, která vrací zcela novou instanci interakce, pomocí které
        jednotka bude interagovat se světem.
        """
        return MarkingInteraction(self, **kwargs)


class MarkingInteraction(Interaction):
    """Instance této třídy obsahují definici procedury, která má být
    provedena coby reprezentace samotného aktu interagování se světem.
    Tato nejdůležitější část je reprezentována implementací metody
    'execute_interaction'.
    """

    def __init__(self, unit: "Actuator", **kwargs):
        """Initor interakce, který přijímá v parametru jednotku, která
        interakci provedla."""
        Interaction.__init__(self, _INTERACTION_NAME,
                             _INTERACTION_DESCRIPTION, unit,
                             unit.robot.deactivate, **kwargs)

        if "mark" not in self.kwargs.keys():
            raise InteractionError(
                f"Nebyl dodán keyworded atribut 'mark'", self)
        else:
            self.mark = Mark(self.kwargs["mark"])

    def execute_interaction(
            self, interface: "WorldInterface") -> object:
        """Tato funkce definuje samotný akt interakce se světem, resp. jeho
        rozhraním.

        Je zde kontrolováno, zda robot stojí na platném políčku, zda je toto
        políčko vybaveno funkcionalitou značkování a zda značka na tomto
        políčku již jedna není. Pokud některá z těchto podmínek není splněna,
        je vyhozena výjimka.
        """

        # Získání stavu robota a políčka, na kterém stojí
        rs = interface.world.robot_state_manager.robot_state(self.robot)
        field = rs.field

        # Pokud políčko není evidováno
        if field is None:
            raise InteractionError(
                f"Políčko, na kterém robot stojí je None", self)

        # Pokud políčko nelze označit
        elif not field.can_be_marked:
            raise InteractionError(
                f"Políčko na souřadnicích {field.coordinates.xy} nemůže být "
                f"označeno", self)

        # Pokud políčko již jednou označeno je
        elif field.has_mark:
            raise InteractionError(
                f"Políčko již jednou označeno je: '{field.mark}'", self)

        # Pokud značka neodpovídá pravidlům značení políček
        elif not field.check_mark(self.mark):
            raise InteractionError(
                f"Nelze použít značku '{self.mark}', neboť porušuje pravidla: "
                f"{field.violated_mark_rules(self.mark)}", self)

        # Jinak, když je již vše v pořádku
        else:

            # Označkování daným textem
            field.mark_yourself(self.mark.text)

            # Vytvoření události na změnu značky políčka a upozornění na ni
            interface.notify_all_event_handlers(MarkChangeEvent(field))


class MarkerFactory(AbstractUnitFactory):
    """Továrna jednotek, která definuje způsob dynamického obdržení instance
    konkrétní jednotky. Kromě vlastního poskytování těchto instancí je také
    odpovědná za poskytování informací o interakcích, které lze od jednotek
    této továrny čekat.

    Instance této třídy poskytují funkcionalitu dynamické tvorby jednotek
    třídy Marker."""

    def __init__(self):
        """Bezparametrický initor třídy, který iniciuje svého předka s
        hodnotou názvu továrny jednotek a názvem samotné jednotky.
        """
        AbstractUnitFactory.__init__(
            self, _UNIT_FACTORY_NAME, _UNIT_NAME)

    def build(self) -> "Actuator":
        """Funkce odpovědná za vytvoření nové instance příslušného aktuátoru.
        Tato funkce umožňuje dynamicky získávat instance jednotek."""
        return Marker(self)

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, který může být od jednotek tvořených
        touto třídou očekáván."""
        return MarkingInteraction


def get_unit_factory() -> "AbstractUnitFactory":
    """Hlavní funkce tohoto modulu, která vrací novou instanci továrny
    jednotek."""
    return MarkerFactory()


