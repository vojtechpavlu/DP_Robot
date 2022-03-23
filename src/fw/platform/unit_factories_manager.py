"""Tento modul definuje prostředky pro správu továrních instancí jednotek.

Především je zde definována třída UnitFactoryManager, která se stará o
jednotlivé loadery odpovědné za dynamický import továrních tříd, stejně
jako se stará o poskytování registrovaných továren a dalších služeb s
tím spojených.
"""


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
            self, uf_loaders: "Iterable[loader_module.UnitFactoryLoader]",
            default_ufs: "Iterable[unit_module.AbstractUnitFactory]" = ()):
        """Initor třídy je odpovědný za inicializaci. V první řadě si uloží
        všechny """

        self._loaders = list(uf_loaders)
        self._default_ufs = list(default_ufs)
        self._registered: "list[unit_module.AbstractUnitFactory]" = []

        if len(self._loaders) + len(self._default_ufs) == 0:
            raise UnitFactoryManagerError(
                f"Správce továrních jednotek nemá s čím pracovat", self)

    @property
    def loaders(self) -> "tuple[loader_module.UnitFactoryLoader]":
        """"""
        return tuple(self._loaders)

    @property
    def registered_factories(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """"""
        return tuple(self._registered)

    @property
    def num_of_registered(self) -> int:
        """"""
        return len(self.registered_factories)

    def register(self, unit_factory: "unit_module.AbstractUnitFactory"):
        """"""
        for registered_factory in self.registered_factories:
            if registered_factory.unit_name == unit_factory.unit_name:
                raise UnitFactoryManagerError(
                    f"Nelze evidovat dvě továrny produkující jednotky stejného"
                    f"názvu '{unit_factory.unit_name=}'", self)
        self._registered.append(unit_factory)

    def load(self):
        """"""
        # Vyprázdnění evidence registrovaných továren jednotek
        self._registered: "list[unit_module.AbstractUnitFactory]" = []

        # Registrace defaultních továren jednotek
        for unit_factory in self._default_ufs:
            self.register(unit_factory)

        # Registrace všech továren jednotek z dodaných loaderů
        for loader in self.loaders:
            for unit_factory in loader.unit_factories:
                self.register(unit_factory)

    def factory_by_unit_name(self,
                             name: str) -> "unit_module.AbstractUnitFactory":
        """"""
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
        """"""
        return tuple(map(
            lambda u_name:
            self.factory_by_unit_name(u_name).build(), unit_names))


class UnitFactoryManagerError(PlatformError):
    """"""

    def __init__(self, message: str, manager: "UnitFactoryManager"):
        """"""
        PlatformError.__init__(self, message)
        self._manager = manager

    @property
    def manager(self) -> "UnitFactoryManager":
        """"""
        return self._manager



