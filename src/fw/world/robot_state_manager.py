"""V tomto modulu jsou definovány nástroje pro správu stavů robotů ve světě.
"""


# Import standardních knihoven


# Import lokálních knihoven
from typing import Callable

import src.fw.world.robot_state as rs_module
import src.fw.robot.robot as robot_module
import src.fw.world.spawner as spawner_module
import src.fw.target.event_handling as event_handling
import src.fw.world.world_events as world_events

from src.fw.utils.error import PlatformError


class RobotStateManager(event_handling.EventEmitter):
    """Správce stavů robotů je odpovědný za řízení jejich životního cyklu.
    Především je pro ně přepravkou, stejně jako má schopnost tyto vytvářet,
    tedy registrovat.

    Registrace probíhá v součinnosti s instancí třídy Spawner."""

    def __init__(self, spawner: "spawner_module.Spawner", log: Callable):
        """Jednoduchý initor třídy, který se stará o iniciaci pole pro stavy
        robotů, které bude následně evidovat. Tento seznam stavů je v úvodní
        fázi pochopitelně defaultně prázdný.

        Kromě toho však přijímá v argumentu spawner, který má být použit
        pro zasazování robotů do světa při jejich registraci.
        """
        # Volání předka
        event_handling.EventEmitter.__init__(self)

        # Iniciace vlastních polí
        self._spawner = spawner

        # Iniciace vlastní evidence stavů robota
        self._robot_states: "list[rs_module.RobotState]" = []

        # Uložení potrubí loggeru
        self._logger_pipeline = log

    @property
    def log(self) -> Callable:
        """Logger, kterého má být použito pro tvorbu záznamů."""
        return self._logger_pipeline

    @property
    def robot_states(self) -> "tuple[rs_module.RobotState]":
        """Vlastnost vrací ntici ze seznamu všech stavů robota, které
        má správce evidovány."""
        return tuple(self._robot_states)

    @property
    def spawner(self) -> "spawner_module.Spawner":
        """Spawner, který je používán pro zasazování robotů do světa."""
        return self._spawner

    def has_robot(self, robot: "robot_module.Robot") -> bool:
        """Funkce se pokusí projít stavy robotů a vyhledat ten, který
        by v sobě popisoval stav dodaného robota. Pokud je takový nalezen,
        je vrácena hodnota True, jinak False.
        """
        for robot_state in self.robot_states:
            if robot_state.robot == robot:
                return True
        return False

    def register_robot(self, robot: "robot_module.Robot"):
        """Tato funkce zaregistruje nového robota. Pokud již pro tohoto
        robota již jeden stav evidován je, je vyhozena výjimka.

        O tvorbu stavu robota se stará instance třídy Spawner, která
        robota hypoteticky usadí do políčka na příslušných souřadnicích
        a natočí ho výchozím směrem.
        """
        # Pokud již jednou tento robot je evidován
        if self.has_robot(robot):
            self.log("Robot", robot.name, "je již jednou evidován")
            raise RobotStateManagerError(
                f"Správce stavů robotů již robota '{robot.name}' "
                f"s ID '{robot.id}' evidovaného má", self)

        # Vytvoření stavu robota
        robot_state = self.spawner.spawn(robot)

        # Přidání do vlastní evidence
        self._robot_states.append(robot_state)

        # Vytvoření události
        field = robot_state.field
        self.notify_all_event_handlers(
            world_events.SpawnRobotEvent(field.x, field.y, robot))

        self.log("Právě byl zasazen robot", robot.name, "do světa")

        # Vrácení stavu robota
        return robot_state

    def robot_state(self, robot: "robot_module.Robot"
                    ) -> "rs_module.RobotState":
        """Funkce se pokusí dohledat stav dodaného robota. Pokud tento není
        nalezen, je vyhozena příslušná výjimka."""
        for robot_state in self.robot_states:
            if robot_state.robot == robot:
                return robot_state
        raise RobotStateManagerError(
            f"Neexistuje stav robota pro robota '{robot}'", self)

    def robot_state_by_coords(
            self, x: int, y: int) -> "rs_module.RobotState":
        """Funkce se pokusí vrátit stav robota, který je na daných
        souřadnicích. Pokud takového robota není, je vráceno None, jinak
        je vrácena instance stavu robota ('RobotState')"""
        for robot_state in self.robot_states:
            field = robot_state.field
            if (field.x == x) and (field.y == y):
                return robot_state


class RobotStateManagerError(PlatformError):
    """Výjimka RobotStateManager je odpovědná za symbolizaci chyby, ke
    které došlo v kontextu správce stavů robota ve světě.

    Typicky se používá tam, kde dojde k identifikaci vzniku nekonzistentního
    stavu systému."""

    def __init__(self, message: str, robot_state_manager: RobotStateManager):
        """"""
        PlatformError.__init__(self, message)
        self._robot_state_manager = robot_state_manager

    @property
    def robot_state_manager(self) -> RobotStateManager:
        """Instance třídy RobotStateManager, v jejímž kontextu došlo k chybě.
        """
        return self._robot_state_manager


