"""V tomto modulu je upravena základní podstata robota, tedy jedna z
klíčových tříd celého systému."""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.robot.mounting_error import MountingError
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named

import src.fw.robot.unit as unit_module


class Robot(Identifiable, Named):
    """Třída Robot je jednou z klíčových tříd celého systému. Její podstata
    je postavena na kombinaci jednotek, kterými je robot osazen a řízení
    jejich osazování."""

    def __init__(self, robot_name: str):
        """Jednoduchý initor, který má za cíl iniciovat své předky a
        připravit si prázdný seznam pro jednotky, kterými bude robot osazován.
        """
        Identifiable.__init__(self)
        Named.__init__(self, robot_name)

        """Seznam jednotek, kterými je robot osazen. Na začátku jeho 
        životního cyklu je pochopitelně seznam prázdný."""
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


class RobotFactory(ABC):
    """Abstraktní třída RobotFactory je odpovědná za poskytování instancí
    třídy Robot a jejich předpřipravení pomocí specifických procedur.

    Tyto procedury jsou definovány zde jako funkce. Hlavní funkcí v kontextu
    tovární třídy je zde funkce 'build()', která poskytuje novou instanci
    robota."""

    @property
    @abstractmethod
    def robot_name(self) -> str:
        """Abstraktní vlastnost 'robot_name' je odpovědná za dodání názvu pro
        robota. Její implementace by se měly postarat o poskytnutí textového
        řetězce, který by symbolizoval název robota."""

    @abstractmethod
    def premount(self, robot: "Robot") -> "Robot":
        """Abstraktní funkce 'premount(Robot)' (resp. její implementace) je
        odpovědná za 'předosazení' robota definovanými jednotkami.

        Zatímco součástí programu robota je i definice jednotek, kterými má
        být robot osazen, v rámci zjednodušení celého procesu lze některé
        jednotky předdefinovat jako výchozí."""

    @abstractmethod
    def build(self) -> "Robot":
        """Implementace této funkce jsou odpovědné za připravení instance
        robota a její vrácení.

        Typicky k tomu je použito funkcí (resp. vlastností) 'robot_name' a
        'premount(Robot)'."""


class EmptyRobotFactory(RobotFactory):
    """Třída EmptyRobotFactory připravuje prázdného robota bez specifického
    názvu a specifických jednotek, kterými ho v rámci přípravy osadí."""

    @property
    def robot_name(self) -> str:
        """Vlastnost vrací defaultní název robota, který je pro všechny roboty
        vytvořené touto tovární třídou identický."""
        return "«no_name»"

    def premount(self, robot: "Robot") -> "Robot":
        """Tato funkce nijak robota neosazuje. Pouze vrátí nezměněného robota,
        kterého přijala.
        """
        return robot

    def build(self) -> "Robot":
        """Funkce vrací instanci nově vytvořeného robota včetně předosazení
        defaultními jednotkami.
        """
        return self.premount(Robot(self.robot_name))




