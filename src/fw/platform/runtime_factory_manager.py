""""""


# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.platform.runtime as runtime_module
import src.fw.utils.loading.runtime_factory_loader as loader_module


class RuntimeFactoryManager:
    """"""

    def __init__(self, rf_loader: "loader_module.RuntimeFactoryLoader"):
        """"""
        self._loader = rf_loader
        self._registered: "list[runtime_module.AbstractRuntimeFactory]" = []

    @property
    def loader(self) -> "loader_module.RuntimeFactoryLoader":
        """"""
        return self._loader

    @property
    def registered_factories(
            self) -> "tuple[runtime_module.AbstractRuntimeFactory]":
        """"""
        return tuple(self._registered)

    @property
    def num_of_registered(self) -> int:
        """"""
        return len(self.registered_factories)

    def register(self, rt_factory: "runtime_module.AbstractRuntimeFactory"):
        """"""
        if rt_factory not in self.registered_factories:
            self._registered.append(rt_factory)
        # TODO - LOG již evidované továrny běhových prostředí

    def load(self):
        """"""
        self._registered: "list[runtime_module.AbstractRuntimeFactory]" = []

        for runtime_factory in self.loader.runtime_factories:
            self.register(runtime_factory)

        if self.num_of_registered == 0:
            # TODO - specifikace výjimky
            raise Exception(
                "Nebyla načtena jediná továrna běhových prostředí.")

