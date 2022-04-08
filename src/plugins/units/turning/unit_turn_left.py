"""Jednotka, pro kterou je vytvořen tento plugin, se stará o poskytnutí
možnosti otočit robota doleva o 90°, tedy ortogonálně o jeden díl proti směru
hodinových ručiček.

Příkladně, je-li robot před použitím této funkce otočen na východ, po aplikaci
bude tento otočen na sever.

Jelikož jde o funkci, která čistě jen provádí konkrétní operaci, ale nevrací
žádnou informaci o světě, je tato jednotka realizována jako aktuátor."""

# Import standardních knihoven
from typing import Type

# Import lokálních knihoven
from src.fw.robot.interaction import Interaction, InteractionError
from src.fw.robot.unit import Actuator, AbstractUnitFactory, Sensor
from src.fw.world.world_events import DirectionChangeEvent
from src.fw.world.world_interface import WorldInterface


"""Definice proměnných"""
# Název jednotky - ten musí být napříč všemi importovanými jednotkami unikátní
_UNIT_NAME = "TurnLeft"

# Popis jednotky - lidsky čitelný popis
_UNIT_DESCRIPTION = ("Jednotka se pokusí otočit robota doleva, "
                     "tedy proti směru hodinových ručiček")

# Název továrny jednotek - lidsky čitelný název
_UNIT_FACTORY_NAME = "TurningLeftFactory"

# Název interakce - pokud možno srozumitelný identifikátor toho, co se provádí
_INTERACTION_NAME = "TurningLeft"

# Popis interakce - lidsky čitelný popis interakce, která probíhá
_INTERACTION_DESCRIPTION = ("Otočení robota doleva "
                            "(proti směru hodinových ručiček)")


class LeftTurner(Actuator):
    """Třída definuje jednotku, která otáčí robota o 90° proti směru
    hodinových ručiček.
    """

    def __init__(self, factory: "AbstractUnitFactory"):
        """Initor aktuátoru, který z úsporných důvodů používá skromnou
        implementaci. De facto jen iniciuje svého předka názvem jednotky,
        popisem účelu jednotky a referencí na továrnu, která je za vytvoření
        této jednotky odpovědná.
        """
        Actuator.__init__(self, factory.unit_name,
                          _UNIT_DESCRIPTION, factory)

    def build_interaction(self) -> "Interaction":
        """Metoda, která vrací zcela novou instanci interakce, pomocí které
        jednotka bude interagovat se světem.
        """
        return TurnLeftInteraction(self)


class TurnLeftInteraction(Interaction):
    """Instance této třídy obsahují definici procedury, která má být
    provedena coby reprezentace samotného aktu interagování se světem.
    Tato nejdůležitější část je reprezentována implementací metody
    'execute_interaction'.

    Tato interakce má za cíl samotné provedení změny ve světě ve vztahu k
    robotovi, který tuto interakci iniciuje.
    """

    def __init__(self, unit: "Actuator"):
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
        # Získání stavu robota z rozhraní světa
        rs = interface.world.robot_state_manager.robot_state(self.robot)

        # Samotné otočení doleva
        rs.direction = rs.direction.turn_left()

        # Vytvoření události
        interface.notify_all_event_handlers(
            DirectionChangeEvent(self.robot, rs.direction))


class LeftTurnerFactory(AbstractUnitFactory):
    """Továrna jednotek, která definuje způsob dynamického obdržení instance
    konkrétní jednotky. Kromě vlastního poskytování těchto instancí je také
    odpovědná za poskytování informací o interakcích, které lze od jednotek
    této továrny čekat.

    Tato továrna je odpovědná za tvorbu jednotek, které jsou schopny otočit
    robota o 90° doleva."""

    def __init__(self):
        """Bezparametrický initor třídy, který iniciuje svého předka s
        hodnotou názvu továrny jednotek a názvem samotné jednotky.
        """
        AbstractUnitFactory.__init__(
            self, _UNIT_FACTORY_NAME, _UNIT_NAME)

    def build(self) -> "Actuator":
        """Funkce odpovědná za vytvoření nové instance příslušného aktuátoru.
        Tato funkce umožňuje dynamicky získávat instance jednotek."""
        return LeftTurner(self)

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, který může být od jednotek tvořených
        touto třídou očekáván. Konkrétně zde třídu 'TurnLeftInteraction'."""
        return TurnLeftInteraction


def get_unit_factory() -> "AbstractUnitFactory":
    """Hlavní funkce tohoto modulu, která vrací novou instanci továrny
    jednotek."""
    return LeftTurnerFactory()


