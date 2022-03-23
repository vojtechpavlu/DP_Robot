""""""


# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Type

# Import lokálních knihoven
import src.fw.utils.loading.plugin_loader as loader_module
import src.fw.utils.loading.plugin_identifier as pl_identifier
import src.fw.utils.loading.plugin_validator as pl_validator
import src.fw.utils.loading.plugin as plugin_module
import src.fw.robot.unit as unit_module


_ACCESS_FUN = "get_program"


class UnitFactoryLoader(loader_module.PluginLoader):
    """"""

    def __init__(self, dest_dir: str,
                 identifiers: "tuple[pl_identifier.PluginIdentifier]",
                 validators: "tuple[pl_validator.PluginValidator]"):
        """"""

        """Volání initoru předka"""
        loader_module.PluginLoader.__init__(self, dest_dir)

        """Přidání všech dodaných identifikátorů a validátorů"""
        self.add_all_identifiers(identifiers)
        self.add_all_validators(validators)

    def load(self) -> "tuple[UnitFactoryPlugin]":
        """Funkce se stará o načtení všech validních pluginů a ty dále vrací
        uspořádané v ntici.

        V první řadě si vytipuje potenciální pluginy (tedy ty soubory, které
        se zdají býti dle pravidel identifikace jako zdrojové soubory v rámci
        daného kontextu) a ty dále ověřuje, zda-li jsou platné.

        Vrací pak vrací pouze ty, které projdou testem validity, tedy všemi
        validačními procedurami definovanými instancemi třídy PluginValidator.
        """
        valid_plugins = []
        for potential_plg_path in self.potential_plugins:
            plugin = UnitFactoryPlugin(potential_plg_path, self, _ACCESS_FUN)
            if plugin.is_valid_plugin:
                valid_plugins.append(plugin)
        return tuple(valid_plugins)


class UnitFactoryPlugin(plugin_module.Plugin):
    """"""

    def __init__(self, abs_path: str,
                 plugin_loader: "UnitFactoryLoader",
                 access_point_fun: str):
        """"""
        plugin_module.Plugin.__init__(self, abs_path, plugin_loader)
        self._access_point_function = access_point_fun

    @property
    def access_point_function(self) -> str:
        """"""
        return self._access_point_function

    @property
    def unit_factory(self) -> "unit_module.AbstractUnitFactory":
        """Vlastnost vrací tovární třídu jednotky, která poskytuje jednotky
        daného typu.
        """

        """Přístupová funkce musí být obsažena v daném modulu. Není-li
        tomu tak, je vyhozena příslušná výjimka."""
        if not self.has_function(self.access_point_function):
            raise plugin_module.PluginError(
                f"Plugin nemá přístupovou funkci názvu "
                f"'{self.access_point_function}'", self)

        """Vrácení výstupu volání přístupové funkce."""
        return self.get_function(self._access_point_function)()



