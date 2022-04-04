"""Plugin odpovědný za tvorbu instancí jednotek, které umí vracet aktuální
natočení robota.

Jednotka vrací po zavolání funkce 'scan' textový řetězec, který symbolizuje
platný směr.

V defaultním nastavení může vracet hodnoty:

    - 'EAST' - východ
    - 'NORTH' - sever
    - 'WEST' - západ
    - 'SOUTH' - jih
"""

# Import standardních knihoven
from typing import Type

# Import lokálních knihoven
from src.fw.robot.interaction import Interaction, InteractionError
from src.fw.robot.unit import AbstractUnitFactory, Sensor
from src.fw.world.world_interface import WorldInterface


"""Definice proměnných"""
# Název jednotky - ten musí být napříč všemi importovanými jednotkami unikátní
_UNIT_NAME = "CompassUnit"

# Popis jednotky - lidsky čitelný popis
_UNIT_DESCRIPTION = ("Jednotka vrací textový řetězec, který odpovídá názvu "
                     "směru, kterým je právě robot natočen. Tyto směry jsou "
                     "absolutní a ortogonální; "
                     "tedy 'EAST', 'NORTH', 'WEST' a 'SOUTH'.")

# Název továrny jednotek - lidsky čitelný název
_UNIT_FACTORY_NAME = "CompassUnit Factory"

# Název interakce - pokud možno srozumitelný identifikátor toho, co se provádí
_INTERACTION_NAME = "CompassScan"

# Popis interakce - lidsky čitelný popis interakce, která probíhá
_INTERACTION_DESCRIPTION = "Zjišťování, v jakém směru je právě robot natočen."


class CompassSensor(Sensor):
    """Senzory typu CompassSensor jsou odpovědné za poskytování informací
    o tom, v jakém směru je robot právě natočen.

    Tuto hodnotu vrací v podobě textového řetězce."""

    def __init__(self, factory: "AbstractUnitFactory"):
        """Initor senzoru, který z úsporných důvodů používá skromnou
        implementaci. De facto jen iniciuje svého předka názvem jednotky,
        popisem účelu jednotky a referencí na továrnu, která je za vytvoření
        této jednotky odpovědná.
        """
        Sensor.__init__(self, factory.unit_name,
                        _UNIT_DESCRIPTION, factory)

    def build_interaction(self) -> "Interaction":
        """Metoda, která vrací zcela novou instanci interakce kompasu,
        pomocí které jednotka bude interagovat se světem.
        """
        return CompassInteraction(self)


class CompassInteraction(Interaction):
    """Instance této třídy obsahují definici procedury, která má být
    provedena coby reprezentace samotného aktu interagování se světem.

    Konkrétně je tato definována jako navrácení aktuálního směru natočení
    robota.
    """

    def __init__(self, unit: "Sensor"):
        """Initor interakce, který přijímá v parametru jednotku, která
        interakci provedla."""
        Interaction.__init__(self, _INTERACTION_NAME, _INTERACTION_DESCRIPTION,
                             unit, unit.robot.deactivate)

    def execute_interaction(
            self, interface: "WorldInterface") -> object:
        """Tato funkce vrací textovou reprezentaci směru, kterým je daný
        robot v tento moment natočen. K tomu používá referenci rozhraní světa
        na svět a jeho správce stavů robota. Z toho již jen vybírá pro
        příslušného robota jeho směr natočení."""
        return str(interface.world.robot_state_manager.robot_state(
                   self.unit.robot).direction)


class CompassSensorFactory(AbstractUnitFactory):
    """Továrna jednotek, která definuje způsob dynamického obdržení instance
    konkrétní jednotky. Kromě vlastního poskytování těchto instancí je také
    odpovědná za poskytování informací o interakcích, které lze od jednotek
    této továrny čekat.

    Instance této třídy poskytují službu tvorby instancí třídy CompassSensor,
    které zjišťují natočení robota ve světě."""

    def __init__(self):
        """Bezparametrický initor třídy, který iniciuje svého předka s
        hodnotou názvu továrny jednotek a názvem samotné jednotky.
        """
        AbstractUnitFactory.__init__(
            self, _UNIT_FACTORY_NAME, _UNIT_NAME)

    def build(self) -> "Sensor":
        """Funkce odpovědná za vytvoření nové instance příslušného senzoru.
        Tato funkce umožňuje dynamicky získávat instance jednotek.

        Konkrétně poskytuje instance třídy 'CompassSensor'."""
        return CompassSensor(self)

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, který může být od jednotek tvořených
        touto třídou očekáván."""
        return CompassInteraction


def get_unit_factory() -> "AbstractUnitFactory":
    """Hlavní funkce tohoto modulu, která vrací novou instanci továrny
    jednotek."""
    return CompassSensorFactory()


