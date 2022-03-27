""""""

# Import standardních knihoven


# Import lokálních knihoven
import src.fw.world.world as world_module


class WorldInterface:
    """"""

    def __init__(self, world: "world_module.World"):
        """"""
        self._world = world

    @property
    def world(self) -> "world_module.World":
        """"""
        return self._world




