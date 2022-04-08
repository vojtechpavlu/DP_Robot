"""Jednotka 'HasMark' je odpovědná za poskytnutí funkcionality zjišťování,
zda-li je políčko opatřeno značkou či nikoliv. Tuto informaci vrací v prosté
podobě boolovské hodnoty, tedy True nebo False.

Ukázkový způsob použití je:

    robot.get_unit("HasMark").scan()
"""

# Import standardních knihoven
from typing import Type

# Import lokálních knihoven
from src.fw.robot.interaction import Interaction, InteractionError
from src.fw.robot.unit import AbstractUnitFactory, Sensor
from src.fw.world.world_interface import WorldInterface


"""Definice proměnných"""
# Název jednotky - ten musí být napříč všemi importovanými jednotkami unikátní
_UNIT_NAME = "HasMark"

# Popis jednotky - lidsky čitelný popis
_UNIT_DESCRIPTION = ("Jednotka vrací, zda-li je na políčku, na kterém robot "
                     "právě stojí, nějaká značka")

# Název továrny jednotek - lidsky čitelný název
_UNIT_FACTORY_NAME = "HasMarkFactory"

# Název interakce - pokud možno srozumitelný identifikátor toho, co se provádí
_INTERACTION_NAME = "HasMarkInteraction"

# Popis interakce - lidsky čitelný popis interakce, která probíhá
_INTERACTION_DESCRIPTION = "Zjištění, zda robot nestojí na značce"


class HasMark(Sensor):
    """Instance této třídy umožňují opatřit robota funkcionalitou zjišťování,
    zda-li právě nestojí na nějaké značce."""

    def __init__(self, factory: "AbstractUnitFactory"):
        """Initor třídy, který postupuje svému předkovi továrnu, která je
        odpovědná za vytvoření této instance. Dále předkovi postupuje název
        jednotky také její popis.
        """
        Sensor.__init__(self, factory.unit_name,
                        _UNIT_DESCRIPTION, factory)

    def build_interaction(self) -> "Interaction":
        """Metoda, která vrací zcela novou instanci interakce, pomocí které
        jednotka bude interagovat se světem.
        """
        return HasMarkInteraction(self)


class HasMarkInteraction(Interaction):
    """Instance této třídy obsahují definici procedury, která má být
    provedena coby reprezentace samotného aktu interagování se světem.
    Tato nejdůležitější část je reprezentována implementací metody
    'execute_interaction'.

    Samotná interakce spočívá v navrácení informace o tom, zda-li právě robot
    nestojí na políčku, které je vybaveno značkou.
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

        Interakce pouze zjistí ze stavu robota, na kterém políčku právě stojí
        a zda toto neobsahuje značku. Tuto informaci poté vrací zpět.
        """

        # Získání stavu robota a políčka, na kterém robot právě stojí
        rs = interface.world.robot_state_manager.robot_state(self.robot)

        # Vrácení informace o tom, zda-li má políčko značku či nikoliv
        return rs.field.has_mark


class HasMarkFactory(AbstractUnitFactory):
    """Továrna jednotek, která je odpovědná za poskytování funkcionality
    dynamické tvorby jednotek 'HasMark'. Tyto slouží robotovi k tomu, aby
    zjistil, zda-li nestojí na nějaké značce."""

    def __init__(self):
        """Bezparametrický initor třídy, který iniciuje svého předka s
        hodnotou názvu továrny jednotek a názvem samotné jednotky.
        """
        AbstractUnitFactory.__init__(
            self, _UNIT_FACTORY_NAME, _UNIT_NAME)

    def build(self) -> "Sensor":
        """Funkce odpovědná za vytvoření nové instance příslušného senzoru.
        Tato funkce umožňuje dynamicky získávat instance jednotek."""
        return HasMark(self)

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, který může být od jednotek tvořených
        touto třídou očekáván."""
        return HasMarkInteraction


def get_unit_factory() -> "AbstractUnitFactory":
    """Hlavní funkce tohoto modulu, která vrací novou instanci továrny
    jednotek."""
    return HasMarkFactory()


