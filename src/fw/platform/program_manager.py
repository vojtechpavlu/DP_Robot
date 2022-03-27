""""""


# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.utils.loading.program_loader as pl_module
import src.fw.robot.program as program_module


class ProgramManager:
    """"""

    def __init__(self, program_loaders: "Iterable[pl_module.ProgramLoader]"):
        """"""

        self._loaders = tuple(program_loaders)
        self._registered: "list[program_module.AbstractProgram]" = []

    @property
    def program_loaders(self) -> "tuple[pl_module.ProgramLoader]":
        """"""
        return self._loaders

    @property
    def registered_programs(self) -> "tuple[program_module.AbstractProgram]":
        """"""
        return self._registered

    @property
    def num_of_registered(self) -> int:
        """"""
        return len(self.registered_programs)

    @property
    def list_authors(self) -> "tuple[str]":
        """"""
        return tuple(map(lambda program: str(program.author_name),
                         self.registered_programs))

    def register(self, program: "program_module.AbstractProgram"):
        """"""
        if program not in self.registered_programs:
            self._registered.append(program)
        # TODO - LOG pokusu o znovupřidání programu

    def load(self):
        """"""
        # Vyprázdnění evidence registrovaných programů
        self._registered: "list[program_module.AbstractProgram]" = []

        # Registrace všech programů načtených ze všech loaderů
        for loader in self.program_loaders:
            for program in loader.programs:
                self.register(program)

        if self.num_of_registered == 0:
            raise Exception(
                f"Žádný loader nebyl schopen načíst žádný program: "
                f"{self.program_loaders=}")


