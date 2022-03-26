""""""

# Import standardních knihoven

# Import lokálních knihoven
import src.fw.utils.loading.plugin_loader as loader_module
import src.fw.utils.loading.plugin_identifier as pl_identifier
import src.fw.utils.loading.plugin_validator as pl_validator
import src.fw.utils.loading.plugin as plugin_module
import src.fw.robot.program as program_module


_ACCESS_FUN = "get_program"


class ProgramLoader(loader_module.PluginLoader):
    """"""

    def __init__(self, dest_dir: str,
                 identifiers: "tuple[pl_identifier.PluginIdentifier]",
                 validators: "tuple[pl_validator.PluginValidator]"):
        """"""
        loader_module.PluginLoader.__init__(self, dest_dir)
        self.add_all_identifiers(identifiers)
        self.add_all_validators(validators)

    @property
    def programs(self) -> "tuple[program_module.AbstractProgram]":
        """"""
        return tuple(map(
            lambda valid_plugin: valid_plugin.program, self.load()))

    def load(self) -> "tuple[ProgramPlugin]":
        """"""
        valid_plugins = []
        for potential_plg_path in self.potential_plugins:
            plugin = ProgramPlugin(potential_plg_path, self, _ACCESS_FUN)
            if plugin.is_valid_plugin:
                valid_plugins.append(plugin)
            # TODO - log nevalidního pluginu
        return tuple(valid_plugins)


class ProgramPlugin(plugin_module.Plugin):
    """"""

    def __init__(self, abs_path: str,
                 plugin_loader: "ProgramLoader",
                 access_point_fun: str):
        """"""
        plugin_module.Plugin.__init__(self, abs_path, plugin_loader)
        self._access_point_function = access_point_fun

    @property
    def access_point_function(self) -> str:
        """"""
        return self._access_point_function

    @property
    def program(self) -> "program_module.AbstractProgram":
        """"""
        if not self.has_function(self.access_point_function):
            raise plugin_module.PluginError(
                f"Plugin nemá přístupovou funkci názvu "
                f"'{self.access_point_function}'", self)
        return self.get_function(self._access_point_function)()




