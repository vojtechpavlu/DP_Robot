"""Defaultní šablona pluginu pro továrny jednotek.

V tomto dokumentačním komentáři musí být uveden účel jednotky, způsob jejího
chování a doporučený způsob nakládání s ní.

U aktuátorů je vhodné, aby zde byl uveden výsledek po aplikování, stejně jako
možné chyby, k jakým může dojít. U senzorů zase uvedení alespoň typu návratové
hodnoty a nějaký ilustrační příklad."""

# Import standardních knihoven
from typing import Type

# Import lokálních knihoven
from src.fw.robot.interaction import Interaction, InteractionError
from src.fw.robot.unit import AbstractUnitFactory, Sensor
from src.fw.world.world_interface import WorldInterface


"""Definice proměnných"""
# Název jednotky - ten musí být napříč všemi importovanými jednotkami unikátní
_UNIT_NAME = "GPS"

# Popis jednotky - lidsky čitelný popis
_UNIT_DESCRIPTION = ("Jednotka poskytující souřadnice, na kterých se robot "
                     "právě nachází. Ty poskytuje ve formátu ntice dvojčíslí; "
                     "například '(3, 0)'.")

# Název továrny jednotek - lidsky čitelný název
_UNIT_FACTORY_NAME = "Továrna jednotky GPS"

# Název interakce - pokud možno srozumitelný identifikátor toho, co se provádí
_INTERACTION_NAME = "GPSScan"

# Popis interakce - lidsky čitelný popis interakce, která probíhá
_INTERACTION_DESCRIPTION = "Zjišťování aktuálních souřadnic robota"


class GPSSensor(Sensor):
    """Senzory typu GPSSensor umožňují získávat konkrétní aktuální souřadnice
    robota ve světě."""

    def __init__(self, factory: "AbstractUnitFactory"):
        """Initor senzoru, který z úsporných důvodů používá skromnou
        implementaci. De facto jen iniciuje svého předka názvem jednotky,
        popisem účelu jednotky a referencí na továrnu, která je za vytvoření
        této jednotky odpovědná.
        """
        Sensor.__init__(self, factory.unit_name,
                        _UNIT_DESCRIPTION, factory)

    def build_interaction(self) -> "Interaction":
        """Metoda, která vrací zcela novou instanci interakce, pomocí které
        jednotka bude interagovat se světem.
        """
        return GPSInteraction(self)


class GPSInteraction(Interaction):
    """Instance této třídy obsahují definici procedury, která má být
    provedena coby reprezentace samotného aktu interagování se světem.

    Konkrétně je tato definována jako navrácení aktuálních souřadnic
    robota v podobě dvojčíslí reprezentovaného nticí.
    """

    def __init__(self, unit: "Sensor"):
        """Initor interakce, který přijímá v parametru jednotku, která
        interakci provedla."""
        Interaction.__init__(self, _INTERACTION_NAME,
                             _INTERACTION_DESCRIPTION, unit,
                             unit.robot.deactivate)

    def execute_interaction(
            self, interface: "WorldInterface") -> object:
        """Tato funkce vrací ntici dvojčíslí, které reprezentuje aktuální
        souřadnice robota.
        """
        # Správce stavů robotů
        robot_state_mng = interface.world.robot_state_manager

        # Stav tohoto robota
        rs = robot_state_mng.robot_state(self.unit.robot)

        # Získání souřadnic políčka, na kterém robot právě stojí
        return rs.field.coordinates.xy


class GPSSensorFactory(AbstractUnitFactory):
    """Továrna jednotek, která definuje způsob dynamického obdržení instance
    konkrétní jednotky. Kromě vlastního poskytování těchto instancí je také
    odpovědná za poskytování informací o interakcích, které lze od jednotek
    této továrny čekat.

    Instance této třídy poskytují službu tvorby instancí třídy GPSSensor,
    které zjišťují aktuální pozici robota ve světě (jeho souřadnice)."""

    def __init__(self):
        """Bezparametrický initor třídy, který iniciuje svého předka s
        hodnotou názvu továrny jednotek a názvem samotné jednotky.
        """
        AbstractUnitFactory.__init__(
            self, _UNIT_FACTORY_NAME, _UNIT_NAME)

    def build(self) -> "Sensor":
        """Funkce odpovědná za vytvoření nové instance příslušného senzoru.
        Tato funkce umožňuje dynamicky získávat instance jednotek.

        Konkrétně poskytuje instance třídy 'GPSSensor'."""
        return GPSSensor(self)

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, který může být od jednotek tvořených
        touto třídou očekáván."""
        return GPSInteraction


def get_unit_factory() -> "AbstractUnitFactory":
    """Hlavní funkce tohoto modulu, která vrací novou instanci továrny
    jednotek."""
    return GPSSensorFactory()


