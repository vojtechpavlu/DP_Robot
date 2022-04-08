"""Jednotka 'MarkReader' umožňuje robotovi číst značky, na které se postaví.

Pokud je políčko opatřeno značkou, dokáže tato jednotka přečíst tuto značku
a vrátit text této značky. Pokud na políčku značka není, vrací None.

Ukázkový způsob použití:

    robot.get_unit("MarkReader").scan()

Jednotka tedy vrací typicky textový řetězec nebo hodnotu None (to v případě,
že na daném políčku žádná značka není).
"""

# Import standardních knihoven
from typing import Type

# Import lokálních knihoven
from src.fw.robot.interaction import Interaction, InteractionError
from src.fw.robot.unit import AbstractUnitFactory, Sensor
from src.fw.world.world_interface import WorldInterface


"""Definice proměnných"""
# Název jednotky - ten musí být napříč všemi importovanými jednotkami unikátní
_UNIT_NAME = "MarkReader"

# Popis jednotky - lidsky čitelný popis
_UNIT_DESCRIPTION = ("Jednotka slouží ke čtení obsahu značky políčka, "
                     "na kterém právě robot stojí")

# Název továrny jednotek - lidsky čitelný název
_UNIT_FACTORY_NAME = "MarkReaderFactory"

# Název interakce - pokud možno srozumitelný identifikátor toho, co se provádí
_INTERACTION_NAME = "ReadMark"

# Popis interakce - lidsky čitelný popis interakce, která probíhá
_INTERACTION_DESCRIPTION = ("Čtení značky z políčka, na kterém robot "
                            "právě stojí")


class MarkReader(Sensor):
    """Jednotky tohoto typu umožňují robotům číst značky, na kterých právě
    stojí."""

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
        return ReadMarkInteraction(self)


class ReadMarkInteraction(Interaction):
    """Instance této třídy obsahují definici procedury, která má být
    provedena coby reprezentace samotného aktu interagování se světem.
    Tato nejdůležitější část je reprezentována implementací metody
    'execute_interaction'.
    """

    def __init__(self, unit: "Sensor", **kwargs):
        """Initor interakce, který přijímá v parametru jednotku, která
        interakci provedla."""
        Interaction.__init__(self, _INTERACTION_NAME,
                             _INTERACTION_DESCRIPTION, unit,
                             unit.robot.deactivate, **kwargs)

    def execute_interaction(
            self, interface: "WorldInterface") -> object:
        """Tato funkce definuje samotný akt interakce se světem, resp. jeho
        rozhraním.

        Funkce se pokusí v první řadě zjistit políčko, na kterém robot stojí,
        poté se pokusí přečíst daný text značky. Pokud na políčku žádná značka
        není, je vrácena hodnota None.
        """

        # Získání stavu robota a políčka, na kterém stojí
        rs = interface.world.robot_state_manager.robot_state(self.robot)
        field = rs.field

        # Vrácení textu značky
        return field.mark.text if field.has_mark else None


class MarkReaderFactory(AbstractUnitFactory):
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
        return MarkReader(self)

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, který může být od jednotek tvořených
        touto třídou očekáván."""
        return ReadMarkInteraction


def get_unit_factory() -> "AbstractUnitFactory":
    """Hlavní funkce tohoto modulu, která vrací novou instanci továrny
    jednotek."""
    return MarkReaderFactory()


