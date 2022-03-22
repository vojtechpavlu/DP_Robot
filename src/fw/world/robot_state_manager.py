""""""


# Import standardních knihoven


# Import lokálních knihoven
import src.fw.world.robot_state as robot_state_module
import src.fw.robot.robot as robot_module

from src.fw.utils.error import PlatformError


class RobotStateManager:
    """"""

    def __init__(self):
        self._robot_states: "list[robot_state_module.RobotState]" = []

    @property
    def robot_states(self) -> "tuple[robot_state_module.RobotState]":
        """"""
        return tuple(self._robot_states)

    def has_robot(self, robot: "robot_module.Robot") -> bool:
        """"""
        return robot in self.robot_states

    def register_robot(self, robot: "robot_module.Robot"):
        """"""
        if self.has_robot(robot):
            raise RobotStateManagerError(
                f"Správce stavů robotů již robota '{robot.name}' "
                f"s ID '{robot.id}' evidovaného má", self)
        robot_state = self.spawner.spawn(robot)     # TODO - Spawner
        self._robot_states.append(robot_state)
        return robot_state

    def robot_state(self, robot: "robot_module.Robot"
                    ) -> "robot_state_module.RobotState":
        """"""
        for robot_state in self.robot_states:
            if robot_state.robot == robot:
                return robot_state
        raise RobotStateManagerError(
            f"Neexistuje stav robota pro robota '{robot.id}'", self)


class RobotStateManagerError(PlatformError):
    """"""

    def __init__(self, message: str, robot_state_manager: RobotStateManager):
        """"""
        PlatformError.__init__(self, message)
        self._robot_state_manager = robot_state_manager

    @property
    def robot_state_manager(self) -> RobotStateManager:
        return self._robot_state_manager


