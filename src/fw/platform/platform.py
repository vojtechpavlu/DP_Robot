""""""


# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.utils.loading.unit_factory_loader as ufl_module
import src.fw.utils.loading.runtime_factory_loader as rtf_module
import src.fw.utils.loading.program_loader as program_loader
import src.fw.platform.unit_factories_manager as uf_manager_module
import src.fw.platform.program_manager as program_manager_module
import src.fw.platform.runtime as runtime_module


class Platform:
    """"""

    def __init__(self, unit_factory_loader: "ufl_module.UnitFactoryLoader",
                 program_loaders: "Iterable[program_loader.ProgramLoader]",
                 runtime_loader: "rtf_module.RuntimeFactoryLoader"):
        """"""

    @property
    def unit_factory_manager(self) -> "uf_manager_module.UnitFactoryManager":
        """"""

    @property
    def program_manager(self) -> "program_manager_module.ProgramManager":
        """"""

    @property
    def all_runtimes(self) -> "runtime_module.AbstractRuntime":
        """"""



