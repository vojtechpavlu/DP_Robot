""""""


# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.utils.loading.plugin_loader as loader_module
import src.fw.utils.loading.plugin_identifier as pl_identifier
import src.fw.utils.loading.plugin_validator as pl_validator
import src.fw.utils.loading.plugin as plugin_module
import src.fw.platform.runtime as runtime_module


_ACCESS_FUN = "get_runtime_factory"


class RuntimeFactoryLoader(loader_module.PluginLoader):
    """"""

    def __init__(self, dest_dir: str,
                 identifiers: "Iterable[pl_identifier.PluginIdentifier]",
                 validators: "Iterable[pl_validator.PluginValidator]"):
        """"""

        loader_module.PluginLoader.__init__(self, dest_dir),

        self.add_all_identifiers(identifiers)
        self.add_all_validators(validators)

    @property
    def runtime_factories(
            self) -> "tuple[runtime_module.AbstractRuntimeFactory]":
        """"""
        return tuple(map(lambda valid_plugin:
                         valid_plugin.runtime_factory, self.load()))

    def load(self) -> "tuple[RuntimeFactoryPlugin]":
        """"""
        valid_plugins = []

        # Pro všechny identifikované (a tedy potenciální) pluginy
        for potential_plg_path in self.potential_plugins:
            plugin = RuntimeFactoryPlugin(
                potential_plg_path, self, _ACCESS_FUN)
            if plugin.is_valid_plugin:
                valid_plugins.append(plugin)
            # TODO - log nevalidního pluginu
        return tuple(valid_plugins)


class RuntimeFactoryPlugin(plugin_module.Plugin):
    """"""

    def __init__(self, abs_path: str,
                 plugin_loader: "RuntimeFactoryLoader",
                 access_point_fun: str):
        """"""
        plugin_module.Plugin.__init__(self, abs_path, plugin_loader)

        self._access_point_function = access_point_fun

    @property
    def access_point_function(self) -> str:
        """Vlastnost vrací název funkce, kterou je třeba zavolat, aby byla
        navrácena instance tovární třídy běhového prostředí."""
        return self._access_point_function

    @property
    def runtime_factory(self) -> "runtime_module.AbstractRuntimeFactory":
        """"""
        # Přístupová funkce musí být obsažena v daném modulu. Není-li tomu
        # tak, je vyhozena příslušná výjimka.
        if not self.has_function(self.access_point_function):
            raise plugin_module.PluginError(
                f"Plugin nemá přístupovou funkci názvu "
                f"'{self.access_point_function}'", self)

        # Vrácení výstupu volání přístupové funkce
        return self.get_function(self._access_point_function)()

