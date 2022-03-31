"""Tento modul definuje prostředky pro správu továrních instancí jednotek.

Především je zde definována třída UnitFactoryManager, která se stará o
jednotlivé loadery odpovědné za dynamický import továrních tříd, stejně
jako se stará o poskytování registrovaných továren a dalších služeb s
tím spojených.
"""

# Prevence cyklických importů
from __future__ import annotations

# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
from src.fw.utils.error import PlatformError

import src.fw.utils.loading.unit_factory_loader as loader_module
import src.fw.robot.unit as unit_module


class UnitFactoryManager:
    """Tato třída je odpovědná za správu načítání a poskytování instancí
    továrních tříd jednotek.

    Je schopná pracovat s továrnami poskytnutými explicitně v initoru, stejně
    jako umí implicitně donačíst potřebné pomocí dodaných loaderů.

    Ovšem před manipulací je třeba, aby bylo vše načteno (zavolána funkce
    'load()'). Jinak by totiž tato neměla co poskytovat a co spravovat.
    """

    def __init__(
            self, uf_loaders: "Iterable[loader_module.UnitFactoryLoader]" = (),
            default_ufs: "Iterable[unit_module.AbstractUnitFactory]" = ()):
        """Initor třídy je odpovědný za inicializaci. V první řadě si uloží
        všechny hodnoty postoupené v argumentech initoru a dále provede
        test validace.

        Initor přijímá množinu loaderů továrních tříd jednotek. Ty jsou
        použity pro dynamický import všech implicitně dodaných továren. Vedle
        toho přijímá také defaultní tovární třídy jednotek, které jsou dodány
        explicitně 'as is'.

        Po uložení těchto vstupů je proveden test validity. Správce továrních
        tříd jednotek musí mít dostupnou alespoň jednu tovární třídu. Pokud
        není nastavena žádná defaultní a zároveň není ani stanoven jediný
        loader, je vyhozena výjimka.
        """

        # Uložení vstupních parametrů
        self._loaders = list(uf_loaders)
        self._default_ufs = list(default_ufs)

        # Inicializace prázdného seznamu registrovaných jednotek
        self._registered: "list[unit_module.AbstractUnitFactory]" = []

        # Validace, že bude mít správce potenciálně možnost pracovat s
        # alespoň jednou instancí tovární třídy jednotky
        if len(self._loaders) + len(self._default_ufs) == 0:
            raise UnitFactoryManagerError(
                f"Správce továrních jednotek nemá s čím pracovat", self)

    @property
    def loaders(self) -> "tuple[loader_module.UnitFactoryLoader]":
        """Vlastnost vrací v ntici všechny loadery, které má v sobě evidované.
        Těch je použito pro načítání továrních tříd jednotek."""
        return tuple(self._loaders)

    @property
    def registered_factories(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """Vlastnost vrací všechny evidované (tzn. registrované) instance
        továrních tříd jednotek.

        K tomu, aby byl seznam (resp. ntice) neprázdný, musí být nejdříve
        tyto načteny."""
        return tuple(self._registered)

    @property
    def num_of_registered(self) -> int:
        """Vlastnost vrací počet načtených instancí továrních tříd jednotek.
        """
        return len(self.registered_factories)

    def register(self, unit_factory: "unit_module.AbstractUnitFactory"):
        """Registrace nové instance tovární třídy jednotky.

        Registrace podléhá předpokladu, že neexistují dvě továrny tvořící
        jednotky stejného názvu. To znamená, že je-li již jedna továrna
        odpovědná za poskytování jednotek stejného názvu, jako aktuálně
        dodaná, je vyhozena výjimka.
        """
        for registered_factory in self.registered_factories:
            if registered_factory.unit_name == unit_factory.unit_name:
                raise UnitFactoryManagerError(
                    f"Nelze evidovat dvě továrny produkující jednotky stejného"
                    f"názvu '{unit_factory.unit_name=}'", self)
        self._registered.append(unit_factory)

    def load(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """Funkce odpovědná za registraci instancí továrních tříd jednotek.
        Funkce v první řadě vyčistí původní evidenci, pokusí se zaregistrovat
        všechny defaultní (explicitní; dodané v initoru) a dále se pokusí
        zaregistrovat všechny dynamicky načtené ze všech loaderů.
        """
        # Vyprázdnění evidence registrovaných továren jednotek
        self._registered: "list[unit_module.AbstractUnitFactory]" = []

        # Registrace defaultních továren jednotek
        for unit_factory in self._default_ufs:
            self.register(unit_factory)

        # Registrace všech továren jednotek z dodaných loaderů
        for loader in self.loaders:
            for unit_factory in loader.unit_factories:
                self.register(unit_factory)

        # Navrácení všech registrovaných
        return self.registered_factories

    def factory_by_unit_name(self,
                             name: str) -> "unit_module.AbstractUnitFactory":
        """Funkce se pokusí vyhledat instanci tovární třídy jednotek, která je
        odpovědná za tvorbu jednotek dodaného názvu. Pokud je taková nalezena,
        je vrácena.

        Funkce může vyhodit výjimku, a to v případě, že není jediná továrna
        registrována, nebo nebyla-li továrna tvořící jednotky tohoto názvu
        nalezena.
        """
        # Pro správné fungování musí existovat alespoň jedna evidovaná
        # instance tovární třídy jednotek
        if self.num_of_registered == 0:
            raise UnitFactoryManagerError(
                "Neexistuje žádná továrna jednotek, "
                "pravděpodobně nebyly doposud načteny", self)

        # Vyhledávání podle názvu
        for unit_factory in self.registered_factories:
            if unit_factory.unit_name == name:
                return unit_factory

        # Pokud nebyla nalezena, je vyhozena výjimka
        raise UnitFactoryManagerError(
            f"Továrna s názvem '{name}' nebyla nalezena", self)

    def build_units_by_names(
            self, unit_names:
            "Iterable[str]") -> "tuple[unit_module.AbstractUnit]":
        """Funkce je odpovědná za přijetí množiny názvů jednotek a zbrusu
        nové instance jednotek opatřit.
        
        Podrobněji pro každý dodaný název vyhledá instanci tovární třídy,
        která tvoří instance tohoto názvu a tuto požádá o vytvoření jedné.
        Celý seznam reprezentovaný nticí je pak vrácen jako návratová hodnota.
        """
        return tuple(map(
            lambda u_name:
            self.factory_by_unit_name(u_name).build(), unit_names))


class UnitFactoryManagerError(PlatformError):
    """Výjimky tohoto typu jsou vyhazovány pro symbolizaci a rozšíření
    informace, že došlo k chybě v kontextu UnitFactoryManager."""

    def __init__(self, message: str, manager: "UnitFactoryManager"):
        PlatformError.__init__(self, message)
        self._manager = manager

    @property
    def manager(self) -> "UnitFactoryManager":
        """Vlastnost vrací instanci UnitFactoryManager, v jehož kontextu
        došlo k chybě."""
        return self._manager



