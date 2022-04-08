"""Jednotka 'Demarker' slouží k odznačkování políček. Jde o aktuátor, který
odstraní značku z políčka, na kterém robot právě stojí.

Způsob použití tedy je například:

    robot.get_unit("Demarker").execute()

Jednotka vyhazuje chybu, pokud na políčku žádná značka není.
"""

# Import standardních knihoven
from typing import Type

# Import lokálních knihoven
from src.fw.robot.interaction import Interaction, InteractionError
from src.fw.robot.unit import Actuator, AbstractUnitFactory, Sensor
from src.fw.world.world_interface import WorldInterface


"""Definice proměnných"""
# Název jednotky - ten musí být napříč všemi importovanými jednotkami unikátní
_UNIT_NAME = "Demarker"

# Popis jednotky - lidsky čitelný popis
_UNIT_DESCRIPTION = "Jednotka odstraňuje značky"

# Název továrny jednotek - lidsky čitelný název
_UNIT_FACTORY_NAME = "DemarkerFactory"

# Název interakce - pokud možno srozumitelný identifikátor toho, co se provádí
_INTERACTION_NAME = "Demark"

# Popis interakce - lidsky čitelný popis interakce, která probíhá
_INTERACTION_DESCRIPTION = "Odstranění značky z políčka"


class Demarker(Actuator):
    """Jednotky této třídy jsou odpovědné za poskytnutí funkcionality
    odstranění značky z políčka, na kterém právě robot stojí."""

    def __init__(self, factory: "AbstractUnitFactory"):
        """Initor, který postupuje svému předkovi základní údaje, především
        od své továrny, ale také popis jednotky."""
        Actuator.__init__(self, factory.unit_name,
                          _UNIT_DESCRIPTION, factory)

    def build_interaction(self) -> "Interaction":
        """Metoda, která vrací zcela novou instanci interakce, pomocí které
        jednotka bude interagovat se světem.
        """
        return DemarkInteraction(self)


class DemarkInteraction(Interaction):
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

    def execute_interaction(
            self, interface: "WorldInterface") -> object:
        """Tato funkce definuje samotný akt interakce se světem, resp. jeho
        rozhraním.

        Funkce se pokusí ověřit, zda je políčko platné a zda-li je opatřeno
        nějakou značkou. Tu se pak pokusí odstranit. Pokudže není některá z
        podmínek naplněna, je vyhozena výjimka.
        """

        # Získání stavu robota a políčka, na kterém stojí
        rs = interface.world.robot_state_manager.robot_state(self.robot)
        field = rs.field

        # Pokud políčko není evidováno
        if field is None:
            raise InteractionError(
                f"Políčko, na kterém robot stojí je None", self)

        # Pokud na políčku žádná značka není
        elif not field.has_mark:
            raise InteractionError(
                f"Na políčku {field} nebyla žádná značka nalezena", self)

        # Jinak, když je vše v pořádku
        else:
            field.pop_mark


class DemarkerFactory(AbstractUnitFactory):
    """Továrna jednotek, která definuje způsob dynamického obdržení instance
    konkrétní jednotky. Kromě vlastního poskytování těchto instancí je také
    odpovědná za poskytování informací o interakcích, které lze od jednotek
    této továrny čekat.

    Tato továrna je odpovědná za dynamické poskytování jednotek typu
    'Demarker', které slouží k odstraňování značek z políček."""

    def __init__(self):
        """Bezparametrický initor třídy, který iniciuje svého předka s
        hodnotou názvu továrny jednotek a názvem samotné jednotky.
        """
        AbstractUnitFactory.__init__(
            self, _UNIT_FACTORY_NAME, _UNIT_NAME)

    def build(self) -> "Actuator":
        """Funkce odpovědná za vytvoření nové instance příslušného aktuátoru.
        Tato funkce umožňuje dynamicky získávat instance jednotek."""
        return Demarker(self)

    @property
    def interaction_type(self) -> "Type":
        """Vlastnost vrací typ interakce, který může být od jednotek tvořených
        touto třídou očekáván."""
        return DemarkInteraction


def get_unit_factory() -> "AbstractUnitFactory":
    """Hlavní funkce tohoto modulu, která vrací novou instanci továrny
    jednotek."""
    return DemarkerFactory()


