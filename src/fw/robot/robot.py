"""V tomto modulu je upravena základní podstata robota, tedy jedna z
klíčových tříd celého systému."""

# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Iterable, Callable

# Import lokálních knihoven
import src.fw.robot.mounting_error as mounting_error_module
from src.fw.utils.error import PlatformError
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named

import src.fw.robot.unit as unit_module
import src.fw.robot.robot_name_generator as name_gnrtr_module
import src.fw.robot.program as program_module


class Robot(Identifiable, Named):
    """Třída Robot je jednou z klíčových tříd celého systému. Její podstata
    je postavena na kombinaci jednotek, kterými je robot osazen a řízení
    jejich osazování."""

    def __init__(self, robot_name: str, logger_pipeline: Callable):
        """Jednoduchý initor, který má za cíl iniciovat své předky a
        připravit si prázdný seznam pro jednotky, kterými bude robot osazován.
        """
        Identifiable.__init__(self)
        Named.__init__(self, robot_name)

        """Seznam jednotek, kterými je robot osazen. Na začátku jeho 
        životního cyklu je pochopitelně seznam prázdný."""
        self._units: "list[unit_module.AbstractUnit]" = []

        """Připravení proměnné, která je odpovědná za udržení reference
        na program, který byl robotovi přiřazen. V úvodní části životního
        cyklu robota je tato proměnná nenaplněna."""
        self._program: "program_module.AbstractProgram" = None

        """Uložení potrubí loggeru pro potřeby tvorby záznamů na úrovni
        robota."""
        self.__log = logger_pipeline

    def set_robot_name(self, new_name: str):
        """Funkce, která umožňuje nastavit jméno robota."""
        self._name = new_name

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

    @property
    def program(self) -> "program_module.AbstractProgram":
        """Vlastnost vrací program, který byl tomuto roboti přiřazen."""
        return self._program

    @program.setter
    def program(self, program: "program_module.AbstractProgram"):
        """Vlastnost nastavuje program, který má být robotovi přiřazen.
        Tento program lze nastavit pouze jednou. Nesmí být tedy None a
        nesmí být již jednou nastaven na neprázdnou hodnotu."""

        # Pokud je program None
        if program is None:
            raise RobotError(f"Dodaný program nesmí být None", self)

        # Pokud již jednou program byl nastaven
        elif self.program is not None:
            raise RobotError(f"Dodaný program nelze přenastavovat", self)

        # Nastavení programu
        self._program = program
        self.__log("Program autora", program.author_name, "byl nastaven")

    def is_mounted_with(self, unit: "unit_module.AbstractUnit") -> bool:
        """Vlastnost vrací, je-li robot osazen dodanou jednotkou."""
        for mounted_unit in self.units:
            if unit.int_id == mounted_unit.int_id:
                return True
        return False

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
            raise mounting_error_module.MountingError(
                f"Tento robot a robot, ke které je jednotka připojena, není "
                f"tentýž", self, unit)

    def get_unit(self, unit_name: str) -> "unit_module.AbstractUnit":
        """Funkce vrátí jednotku dle zadaného názvu. Pokud taková není
        nalezena, vyhazuje výjimku."""

        # Pro všechny jednotky, kterými je robot osazen
        for unit in self.units:
            # Pokud se jednotka názvem shoduje s dodaným názvem
            if unit.name == unit_name:
                return unit

        # Pokud nebyla nalezena příslušná jednotka, vyhodí výjimku s
        # informacemi o těch platných
        raise RobotError(
            f"Robot není osazen jednotkou '{unit_name}' a nemůže na ni vrátit "
            f"odkaz. Zkuste některou z: "
            f"{list(map(lambda u: u.name, self.units))}", self)

    def deactivate(self):
        """Funkce deaktivuje všechny jednotky. To znamená, že je robot již
        nevratně nefunkční."""
        self.__log("Robot", self.name, "se deaktivuje...")
        for unit in self.units:
            unit.deactivate()


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
    def build(self, logger_pipeline: Callable) -> "Robot":
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

    def build(self, logger_pipeline: Callable) -> "Robot":
        """Funkce vrací instanci nově vytvořeného robota včetně předosazení
        defaultními jednotkami.
        """
        return self.premount(Robot(self.robot_name, logger_pipeline))


class CompleteRobotFactory(EmptyRobotFactory):
    """Třída CompleteRobotFactory je odpovědná za vytváření instancí robotů
    pomocí kompletních procedur pojmenování a osazení výchozími jednotkami.
    """

    def __init__(self,
                 unit_factories: "Iterable[unit_module.AbstractUnitFactory]",
                 name_generator: "name_gnrtr_module.RobotNameGenerator"):
        """Initor třídy přijímá množinu všech továrních tříd jednotek, kterými
        je možné robota osadit. Dále přijímá generátor názvů robotů, kterého
        bude použito pro pojmenovávání robotů."""

        EmptyRobotFactory.__init__(self)

        self._unit_factories = list(unit_factories)
        self._name_generator = name_generator

    @property
    def unit_factories(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """Vlastnost vrací ntici všech továren jednotek, kterými bude v úvodní
        fázi robot osazen."""
        return tuple(self._unit_factories)

    @property
    def robot_name(self) -> str:
        """Vlastnost vrací název, který byl pro robota vygenerován. Typicky
        se odvíjí od náhodně zvoleného textového řetězce; pochopitelně vychází
        z implementace dodaného generátoru."""
        return self._name_generator.get()

    def premount(self, robot: "Robot") -> "Robot":
        """Funkce odpovědná za přípravu robota co do osazení výchozími
        jednotkami. Napříč všemi továrními třídami jednotek je robot osazen
        každou z těchto jednotek. Vrácen je osazený robot.
        """
        for unit_factory in self.unit_factories:
            robot.mount(unit_factory.build())
        return robot


class RobotError(PlatformError):
    """"""

    def __init__(self, message: str, robot: Robot):
        """"""
        PlatformError.__init__(self, message)
        self._robot = robot

    @property
    def robot(self) -> Robot:
        """"""
        return self._robot
