"""Plugin definující jednotku, která umí posunout robota v jeho aktuálním
směru kupředu o jedno políčko.

Například je-li otočen na východ na souřadnicích (1, 1), přesune se v ose
x o +1, tedy skončí na políčku (2, 1); natočen zůstává pochopitelně stále
ve stejném směru.
"""

# Import standardních knihoven
from typing import Type

# Import lokálních knihoven
from src.fw.robot.interaction import Interaction, InteractionError
from src.fw.robot.unit import Actuator, AbstractUnitFactory, UnitError
from src.fw.world.world_interface import WorldInterface
from src.fw.world.world_events import FieldChangeEvent


"""Definice proměnných"""
# Název jednotky - ten musí být napříč všemi importovanými jednotkami unikátní
_UNIT_NAME = "ForwardMover"

# Popis jednotky - lidsky čitelný popis
_UNIT_DESCRIPTION = "Jednotka, která se stará o posun v aktuálním směru robota"

# Název továrny jednotek - lidsky čitelný název
_UNIT_FACTORY_NAME = "ForwardMover Factory"

# Název interakce - pokud možno srozumitelný identifikátor toho, co se provádí
_INTERACTION_NAME = "ForwardMove"

# Popis interakce - lidsky čitelný popis interakce, která probíhá
_INTERACTION_DESCRIPTION = "Posun robota kupředu v jeho směru"


class ForwardMover(Actuator):
    """Instance této třídy umožňují posun robota v jeho směru o jedno políčko.
    """

    def __init__(self, factory: "AbstractUnitFactory"):
        """Initor aktuátoru, který z úsporných důvodů používá skromnou
        implementaci. De facto jen iniciuje svého předka názvem jednotky,
        popisem účelu jednotky (nezapomenout doplnit) a referencí na továrnu,
        která je za vytvoření této jednotky odpovědná.
        """
        Actuator.__init__(self, factory.unit_name,
                          _UNIT_DESCRIPTION, factory)

    def build_interaction(self) -> "Interaction":
        """Metoda, která vrací zcela novou instanci interakce, pomocí které
        jednotka bude interagovat se světem.
        """
        return MoveForwardInteraction(self)


class MoveForwardInteraction(Interaction):
    """Instance této třídy obsahují definici procedury, která má být
    provedena coby reprezentace samotného aktu interagování se světem.
    Tato nejdůležitější část je reprezentována implementací metody
    'execute_interaction' (doplnit).
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

        V první řadě se zjišťuje správce stavů robotů a stav tohoto robota.
        Dále je na řadě zjištění konkrétního políčka, kam by se měl robot
        přesunout. Podmínky na něj jsou následující:

            - Musí existovat a být evidováno ve světě. Pokud nebude tato
              splněna, je vyhozena výjimka o spadnutí robota ze světa.

            - Políčko nesmí být stěna. Pokud by byla, robot by narazil
              a rozbil se. To je symbolizováno výjimkou.

            - Na daném políčku nesmí být evidován žádný robot. To je
              zjišťováno pomocí stavů robotů; pokud existuje takový stav,
              který by byl spjat s tímto políčkem, robot narazil do jiného.
              Opět je reakcí výjimka.

        Pokud jsou všechny tyto podmínky splněny, je robot přesunut.
        """
        # Získání správce stavů robotů z rozhraní světa
        rs_m = interface.world.robot_state_manager

        # Získání stavu tohoto robota
        rs = rs_m.robot_state(self.robot)

        # Zjištění potenciálního cíle
        field = rs.field.neighbour(rs.direction)

        # Pokud je dané políčko prázdné (není evidované ve světě)
        if field is None:
            raise InteractionError(f"Robot spadl ze světa", self)

        # Pokud je políčko stěna
        elif field.is_wall:
            raise InteractionError(f"Robot narazil do stěny na souřadnicích "
                                   f"{field.coordinates.xy}", self)

        # Uložení souřadnic (v dvě celá čísla v ntici)
        coords = field.coordinates.xy

        # Pokud je na políčku už jeden robot evidován (resp. je k danému
        # políčku na daných souřadnicích evidován stav robota)
        if rs_m.robot_state_by_coords(*coords) is not None:
            raise InteractionError(f"Na políčku {coords} již "
                                   f"robot stojí.", self)

        # Jinak, když je vše v pořádku
        else:
            # Nastavení políčka
            rs.field = field

            # Vytvoření události
            interface.notify_all_event_handlers(
                FieldChangeEvent(field.x, field.y, self.robot))


class ForwardMoverFactory(AbstractUnitFactory):
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

    def build(self) -> "Actuator":
        """Funkce odpovědná za vytvoření nové instance příslušného aktuátoru.
        Tato funkce umožňuje dynamicky získávat instance jednotek."""
        return ForwardMover(self)

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, který může být od jednotek tvořených
        touto třídou očekáván."""
        return MoveForwardInteraction


def get_unit_factory() -> "AbstractUnitFactory":
    """Hlavní funkce tohoto modulu, která vrací novou instanci továrny
    jednotek."""
    return ForwardMoverFactory()


