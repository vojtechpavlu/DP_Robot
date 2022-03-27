""""""


# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.utils.loading.unit_factory_loader as ufl_module
import src.fw.utils.loading.runtime_factory_loader as rtf_module
import src.fw.utils.loading.program_loader as program_loader
import src.fw.platform.unit_factories_manager as uf_manager_module
import src.fw.platform.program_manager as prg_manager_module
import src.fw.platform.runtime_factory_manager as rtf_manager_module
import src.fw.platform.runtime as runtime_module


class Platform:
    """"""

    def __init__(self,
                 unit_fact_loaders: "Iterable[ufl_module.UnitFactoryLoader]",
                 program_loaders: "Iterable[program_loader.ProgramLoader]",
                 runtime_loader: "rtf_module.RuntimeFactoryLoader"):
        """"""
        self._unit_factory_manager = uf_manager_module.UnitFactoryManager(
            unit_fact_loaders)
        self._program_manager = prg_manager_module.ProgramManager(
            program_loaders)
        self._runtime_factory_manager = (
                rtf_manager_module.RuntimeFactoryManager(runtime_loader))

        self._runtimes: "list[runtime_module.AbstractRuntime]" = []

    @property
    def unit_factory_manager(self) -> "uf_manager_module.UnitFactoryManager":
        """"""
        return self._unit_factory_manager

    @property
    def program_manager(self) -> "prg_manager_module.ProgramManager":
        """"""
        return self._program_manager

    @property
    def runtime_factory_manager(
            self) -> "rtf_manager_module.RuntimeFactoryManager":
        """"""
        return self._runtime_factory_manager

    @property
    def all_runtimes(self) -> "tuple[runtime_module.AbstractRuntime]":
        """"""
        return tuple(self._runtimes)



