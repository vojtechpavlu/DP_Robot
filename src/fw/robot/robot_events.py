"""Modul sdružuje události, které mohou vzniknout v rámci působení robota a
jeho součástí.
"""

# Import standardních knihoven
from dataclasses import dataclass


# Import lokálních knihoven
import src.fw.target.event_handling as event_module
import src.fw.robot.interaction as interaction_module


@dataclass(frozen=True)
class InteractionUsageEvent(event_module.Event):
    """Jednoduchá událost, která značí, že nastal moment použití dané
    interakce.

    Příklad použití:
        >>> InteractionUsageEvent(interaction)
    """

    # Interakce, která byla použita
    interaction: "interaction_module.Interaction"





