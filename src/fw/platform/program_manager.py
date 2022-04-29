"""Modul je odpovědný za definici správce programů robotů."""


# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.utils.loading.program_loader as pl_module
import src.fw.robot.program as program_module


class ProgramManager:
    """Správce programů ProgramManager je odpovědný za správu načítání
    a poskytování základních prostředků pro manipulaci s programy.

    Cílem je přijmout všechny loadery (instance třídy ProgramLoader) a pomocí
    nich získat reference na všechny programy, které tyto označí za platné a
    validní."""

    def __init__(self, program_loaders: "Iterable[pl_module.ProgramLoader]"):
        """Initor přijímá v parametru iterovatelnou množinu všech loaderů
        programů, ze kterých dále dynamicky načte všechny programy."""

        # Uložení všech loaderů programů
        self._loaders = list(program_loaders)

        # Iniciace prázdného seznamu registrovaných programů
        self._registered: "list[program_module.AbstractProgram]" = []

    @property
    def program_loaders(self) -> "tuple[pl_module.ProgramLoader]":
        """Vlastnost vrací všechny loadery, kterých bude použito pro
        získání všech programů."""
        return tuple(self._loaders)

    @property
    def registered_programs(self) -> "tuple[program_module.AbstractProgram]":
        """Vlastnost vrací ntici všech doposud řádně registrovaných programů.
        """
        return tuple(self._registered)

    @property
    def num_of_registered(self) -> int:
        """Vlastnost vrací počet registrovaných programů."""
        return len(self.registered_programs)

    @property
    def list_authors(self) -> "tuple[str]":
        """Vlastnost vrací jména všech autorů, jejichž programy jsou
        registrovány."""
        return tuple(map(lambda program: str(program.author_name),
                         self.registered_programs))

    def register(self, program: "program_module.AbstractProgram"):
        """Funkce se pokusí zaregistrovat dodaný program. To provede jen tehdy,
        není-li již tento v evidenci registrován.
        """
        if program not in self.registered_programs:
            self._registered.append(program)

    def load(self):
        """Hlavní funkce třídy, která se pokusí načíst všechny programy pomocí
        všech loaderů.

        V první řadě se musí provést vyčištění evidence registrovaných
        programů, dále pro každý loader se pokusí získat všechny programy,
        které loader získat dokáže.

        Pokud žádný program nebyl nalezen (registrován), je vyhozena výjimka.
        """
        # Vyprázdnění evidence registrovaných programů
        self._registered: "list[program_module.AbstractProgram]" = []

        # Registrace všech programů načtených ze všech loaderů
        for loader in self.program_loaders:
            for program in loader.programs:
                self.register(program)

        if self.num_of_registered == 0:
            raise Exception(
                f"Žádný loader nebyl schopen načíst žádný program pro "
                f"stanovené zadání '{self.program_loaders[0].destination}': "
                f"{self.program_loaders=}")


