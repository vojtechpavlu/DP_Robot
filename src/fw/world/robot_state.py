"""V modulu 'robot_state' je definován protokol pro práci a manipulaci se
stavem robota.

Stav robota se stará o umístění robota ve světě, co do jeho:

    - pozice (na kterém políčku právě stojí)
    - otočení (kterým povoleným směrem je otočen)
"""

# Import standardních knihoven


# Import lokálních knihoven
import src.fw.world.world as world_module
import src.fw.world.field as field_module
import src.fw.robot.robot as robot_module

from src.fw.utils.error import PlatformError
from src.fw.world.direction import Direction


class RobotState:
    """Instance této třídy slouží k evidenci toho, jak který robot se kde
    a v jaké pozici nachází.

    Stav robota se stará o umístění robota ve světě, co do jeho:
    - pozice (na kterém políčku právě stojí)
    - otočení (kterým povoleným směrem je otočen)
    """

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
        """Svět, ve kterém robot je."""
        return self._world

    @property
    def robot(self) -> "robot_module.Robot":
        """Robot, kterého tato instance sleduje."""
        return self._robot

    @property
    def direction(self) -> "Direction":
        """Směr, kterým je robot natočen"""
        return self._direction

    @direction.setter
    def direction(self, direction: "Direction"):
        """Vlastnost nastavuje směr, kterým je robot natočen"""
        self._direction = direction

    @property
    def field(self) -> "field_module.Field":
        """Políčko, na kterém robot stojí."""
        return self._field

    @field.setter
    def field(self, field: "field_module.Field"):
        """Funkce nastavuje políčko, na kterém má robot stát. Funkce vyhazuje
        výjimku:
            - je-li políčko None
            - není-li políčko v daném světě evidováno
            - je-li políčko stěna
            - je-li na dodaném políčku již umístěn nějaký robot

        Pokud ani jeden z těchto nepříznivých stavů nenastane, stavu robota
        je toto políčko přiřazeno."""
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
        elif field.has_any_robot and field.robot != self.robot:
            raise RobotStateError(
                f"Nelze robota umístit na políčko, na kterém již jeden robot "
                f"umístěn je: {field.robot} @ [{field.x}, {field.y}]", self)
        self._field = field


class RobotStateError(PlatformError):
    """Výjimka typu RobotStateError odpovídá chybám vzniklým v kontextu
    práce se stavem robota.

    Typicky je tak označena situace, kdy se zaznamená pokus o převod systému
    do nekonzistentního stavu.
    """

    def __init__(self, message: str, robot_state: RobotState):
        PlatformError.__init__(self, message)

        self._robot_state = robot_state

    @property
    def robot_state(self) -> RobotState:
        """Stav robota, v jehož kontextu došlo k chybě."""
        return self._robot_state




