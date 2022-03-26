""""""

# Import standardních knihoven

# Import lokálních knihoven
import src.fw.utils.loading.plugin_loader as loader_module
import src.fw.utils.loading.plugin_identifier as pl_identifier
import src.fw.utils.loading.plugin_validator as pl_validator
import src.fw.utils.loading.plugin as plugin_module


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
    def programs(self):
        """"""

    def load(self):
        """"""


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
    def program(self):
        """"""
