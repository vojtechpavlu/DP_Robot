""""""

# Import standardních knihoven

# Import lokálních knihoven
from src.fw.robot.mounting_error import MountingError
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named

import src.fw.robot.unit as unit_module


class Robot(Identifiable, Named):
    """"""

    def __init__(self, robot_name: str):
        """"""
        Identifiable.__init__(self)
        Named.__init__(self, robot_name)

        self._units: "list[unit_module.AbstractUnit]" = []

    @property
    def units(self) -> "tuple[unit_module.AbstractUnit]":
        """Vlastnost vrací ntici všech jednotek, kterými je robot osazen."""
        return tuple(self._units)

    @property
    def number_of_units(self) -> int:
        """Vlastnost vrací počet jednotek, kterými je robot osazen."""
        return len(self.units)

    @property
    def unit_names(self) -> "tuple[str]":
        """Vlastnost vrací ntici názvů jednotek, kterými je robot osazen."""
        return tuple(map(lambda unit: str(unit.name), self.units))

    @property
    def unit_ids(self) -> "tuple[str]":
        """Vlastnost vrací ntici textových řetězců, které reprezentují
        unikátní identifikátory jednotlivých jednotek."""
        return tuple(map(lambda unit: str(unit.hex_id), self.units))

    def mount(self, unit: "unit_module.AbstractUnit"):
        """Funkce se pokusí osadit robota dodanou jednotkou."""
        # TODO - kontrola, zda-li je jednotka validní
        self._units.append(unit)
        unit.mount(self)

    def detach(self, unit: "unit_module.AbstractUnit"):
        """Funkce se pokusí odpojit jednotku od robota."""
        if unit.robot == self:
            self._units.remove(unit)
            unit.detach()
        else:
            raise MountingError(
                f"Robot, ke kterému je napojena jednotka {unit} není "
                f"tento: {unit.robot=}, {self}")



