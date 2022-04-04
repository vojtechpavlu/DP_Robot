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
_UNIT_NAME = "IsWallSensor"

# Popis jednotky - lidsky čitelný popis
_UNIT_DESCRIPTION = ("Senzor vracející boolovskou hodnotu o tom, zda-li je "
                     "aktuálně před robotem stěna.")

# Název továrny jednotek - lidsky čitelný název
_UNIT_FACTORY_NAME = "Továrna jednotky IsWallSensor"

# Název interakce - pokud možno srozumitelný identifikátor toho, co se provádí
_INTERACTION_NAME = "IsWallScan"

# Popis interakce - lidsky čitelný popis interakce, která probíhá
_INTERACTION_DESCRIPTION = "Zjišťování, zda-li je před robotem stěna"


class IsWallSensor(Sensor):
    """Sensor tohoto typu vrací boolovskou hodnotu, zda-li robot aktálně
    stojí před stěnou v daném směru, či nikoliv."""

    def __init__(self, factory: "AbstractUnitFactory"):
        """Initor senzoru, který z úsporných důvodů používá skromnou
        implementaci. De facto jen iniciuje svého předka názvem jednotky,
        popisem účelu jednotky (nezapomenout doplnit) a referencí na továrnu,
        která je za vytvoření této jednotky odpovědná.
        """
        Sensor.__init__(self, factory.unit_name,
                        _UNIT_DESCRIPTION, factory)

    def build_interaction(self) -> "Interaction":
        """Metoda, která vrací zcela novou instanci interakce, pomocí které
        jednotka bude interagovat se světem.
        """
        return IsWallInteraction(self)


class IsWallInteraction(Interaction):
    """Instance této třídy obsahují definici procedury, která má být
    provedena coby reprezentace samotného aktu interagování se světem.
    Tato nejdůležitější část je reprezentována implementací metody
    'execute_interaction' (doplnit).
    """

    def __init__(self, unit: "Sensor"):
        """Initor interakce, který přijímá v parametru jednotku, která
        interakci provedla."""
        Interaction.__init__(self, _INTERACTION_NAME,
                             _INTERACTION_DESCRIPTION, unit,
                             unit.robot.deactivate)

    def execute_interaction(
            self, interface: "WorldInterface") -> object:
        """Tato funkce definuje samotný akt interakce se světem, resp. jeho
        rozhraním. V této šablonové implementaci pouze vyhazuje výjimku, aby
        se nezapomnělo tuto implementovat.
        """
        # Získání stavu robota z dodaného rozhraní světa
        rs = interface.world.robot_state_manager.robot_state(self.robot)

        # Získání políčka ve směru robota
        field = rs.field.neighbour(rs.direction)

        # Pokud políčko není známo, vrátit False, jinak jestli je
        # nebo není stěna
        return False if not field else field.is_wall


class IsWallSensorFactory(AbstractUnitFactory):
    """Továrna jednotek, která definuje způsob dynamického obdržení instance
    konkrétní jednotky. Kromě vlastního poskytování těchto instancí je také
    odpovědná za poskytování informací o interakcích, které lze od jednotek
    této továrny čekat."""

    def __init__(self):
        """Bezparametrický initor třídy, který iniciuje svého předka s
        hodnotou názvu továrny jednotek a názvem samotné jednotky.
        """
        AbstractUnitFactory.__init__(
            self, _UNIT_FACTORY_NAME, _UNIT_NAME)

    def build(self) -> "Sensor":
        """Funkce odpovědná za vytvoření nové instance příslušného senzoru.
        Tato funkce umožňuje dynamicky získávat instance jednotek."""
        return IsWallSensor(self)

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, který může být od jednotek tvořených
        touto třídou očekáván."""
        return IsWallInteraction


def get_unit_factory() -> "AbstractUnitFactory":
    """Hlavní funkce tohoto modulu, která vrací novou instanci továrny
    jednotek."""
    return IsWallSensorFactory()


