"""V tomto modulu jsou sdružovány třídy výjimek, které mohou být vyhozeny
v případě chyby v kontextu osazování robota."""

# Import standardních knihoven

# Import lokálních knihoven
from src.fw.utils.error import PlatformError

import src.fw.robot.robot as robot_module
import src.fw.robot.unit as unit_module


class MountingError(PlatformError):
    """Výjimky tohoto typu specifikují narušení integrity nebo základních
    pravidel v kontextu osazování robota jednotkami."""

    def __init__(self, message: str, robot: "robot_module.Robot",
                 unit: "unit_module.AbstractUnit"):
        """Initor, který přijímá textovou zprávu o chybě, instanci robota,
        v jehož kontextu došlo při osazování k problému, a inkriminovanou
        jednotku. Textová zpráva je postoupena předkovi, přičemž robot a
        dodaná jednotka jsou uloženy do této výjimky a jsou poskytovány
        pomocí vlastností.
        """

        # Volání initoru předka
        PlatformError.__init__(self, message)

        # Uložení robota a jednotky
        self._robot = robot
        self._unit = unit

    @property
    def robot(self) -> "robot_module.Robot":
        """Vlastnost vrací robota, v jehož kontextu došlo k chybě."""
        return self._robot

    @property
    def unit(self) -> "unit_module.AbstractUnit":
        """Vlastnost vrací jednotku, v jejímž kontextu došlo k chybě."""
        return self._unit



