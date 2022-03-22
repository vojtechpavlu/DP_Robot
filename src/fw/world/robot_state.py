""""""

# Import standardních knihoven


# Import lokálních knihoven
import src.fw.world.world as world_module
import src.fw.world.field as field_module
import src.fw.robot.robot as robot_module
from src.fw.utils.error import PlatformError

from src.fw.world.direction import Direction


class RobotState:
    """"""

    def __init__(self, robot: "robot_module.Robot",
                 world: "world_module.World",
                 direction: "Direction" = None,
                 field: "field_module.Field" = None):

        self._world: "world_module.World" = world
        self._robot: "robot_module.Robot" = robot
        self._direction: "Direction" = direction
        self._field: "field_module.Field" = field

    @property
    def world(self) -> "world_module.World":
        """"""
        return self._world

    @property
    def robot(self) -> "robot_module.Robot":
        """"""
        return self._robot

    @property
    def direction(self) -> "Direction":
        """"""
        return self._direction

    @direction.setter
    def direction(self, direction: "Direction"):
        """"""
        self._direction = direction

    @property
    def field(self) -> "field_module.Field":
        """"""
        return self._field

    @field.setter
    def field(self, field: "field_module.Field"):
        """"""
        if not field:
            raise RobotStateError(
                f"Políčko nemůže být None", self)
        elif not self.world.has_field(field.x, field.y):
            raise RobotStateError(
                f"Robota není možné umístit na neexistující políčko", self)
        elif field.is_wall:
            raise RobotStateError(
                f"Robota nelze umístit na stěnu na souřadnicích "
                f"[{field.x}, {field.y}]", self)
        self._field = field


class RobotStateError(PlatformError):
    """"""

    def __init__(self, message: str, robot_state: RobotState):
        """"""
        PlatformError.__init__(self, message)
        self._robot_state = robot_state

    @property
    def robot_state(self) -> RobotState:
        return self._robot_state




