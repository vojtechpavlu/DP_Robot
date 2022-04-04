""""""

# Import standardních knihoven
from typing import Type

# Import lokálních knihoven
from src.fw.robot.interaction import Interaction, InteractionError
from src.fw.robot.unit import Actuator, AbstractUnitFactory, Sensor
from src.fw.world.world_interface import WorldInterface


class TemplateActuator(Actuator):
    """"""

    def __init__(self, factory):
        """"""
        Actuator.__init__(self, factory.unit_name,
                          "Template description of Template unit", factory)

    def build_interaction(self) -> "Interaction":
        """"""
        return TemplateInteraction(self)


class TemplateInteraction(Interaction):
    """"""

    def __init__(self, unit: "Actuator"):
        """"""
        Interaction.__init__(self, "Template Interaction name",
                             "TemplateInteraction description", unit,
                             unit.robot.deactivate)

    def execute_interaction(
            self, interface: "WorldInterface") -> object:
        """"""
        raise InteractionError(
            f"«NO INTERACTION SPECIFIED: '{type(self)}'»", self)


class TemplateActuatorFactory(AbstractUnitFactory):
    """"""

    def __init__(self):
        """"""
        AbstractUnitFactory.__init__(
            self, "Template Factory name", "TemplateActuator")

    def build(self) -> "Actuator":
        """"""
        return TemplateActuator(self)

    @property
    def interaction_type(self) -> "Type":
        """"""
        return TemplateInteraction


def get_unit_factory() -> "":
    """Hlavní funkce tohoto modulu, která vrací novou instanci továrny
    jednotek."""


