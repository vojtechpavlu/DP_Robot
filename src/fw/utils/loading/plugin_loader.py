"""Modul 'plugin_loader' sdružuje všechny obecné nástroje pro správu
dynamického načítání modulů s cílem upravovat funkcionalitu za běhu programu.
"""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.utils.loading.plugin_identifier as identifier
import src.fw.utils.loading.plugin_validator as validator
import src.fw.utils.loading.plugin as pl
import src.fw.utils.error as error

from ..filesystem import exists, is_directory, deep_list_files


class PluginLoader(ABC):
    """Abstrkatní třída PluginLoader definuje obecný protokol pro práci s
    pluginy (instancemi třídy Plugin), tedy pro dynamické načítání zdrojových
    souborů.
    """

    def __init__(self, destination: str):
        """"""
        self._destination: str = destination

        self._plugin_identifiers: "list[identifier.PluginIdentifier]" = []
        self._plugin_validators: "list[validator.PluginValidator]" = []
        self._plugins: "list[pl.Plugin]" = []

        if not (exists(destination) and is_directory(destination)):
            raise PluginLoaderError(
                f"Dodaná cesta neukazuje na existující adresář: {destination}",
                self)

    @property
    def destination(self) -> str:
        """"""
        return self._destination

    @property
    def identifiers(self) -> "tuple[identifier.PluginIdentifier]":
        """"""
        return tuple(self._plugin_identifiers)

    @property
    def validators(self) -> "tuple[validator.PluginValidator]":
        """"""
        return tuple(self._plugin_validators)

    @property
    def potential_plugins(self) -> "tuple[str]":
        """Vlastnost obaluje funkci, která má za cíl vytipovat ty moduly,
        které jsou potenciálními pluginy, resp. soubory odpovídající pravidlům
        definovaným identifikátory pluginů.

        Proces je proveden tak, že je hloubkově prozkoumán dodaný adresář
        (viz proměnná 'destination') a z něj jsou všechny soubory podrobeny
        zkoušce, zda jsou potenciálními pluginy.
        """
        potential_plugins = []
        for file in deep_list_files(self.destination, False):
            if self.is_potential_plugin(file):
                potential_plugins.append(file)
        return tuple(potential_plugins)

    @property
    def valid_plugins(self) -> "tuple[pl.Plugin]":
        """Vlasnost se pokusí vyextrahovat ty pluginy, které jsou nejen
        identifikovány, ale které jsou validní.

        Nejsou-li žádné identifikované, je vyhozena výjimka.
        """
        if len(self._plugins) == 0:
            raise PluginLoaderError(
                f"Nebyly nalezeny žádné identifikované pluginy. Možná "
                f"nebyly doposud žádné hledány (volání funkce 'load').", self)
        else:
            return tuple(filter(
                lambda plugin: plugin.is_valid_plugin,
                self._plugins))

    def add_identifier(self, plugin_ident: "identifier.PluginIdentifier"):
        """"""
        self._plugin_identifiers.append(plugin_ident)

    def add_validator(self, plugin_validator: "validator.PluginValidator"):
        """"""
        self._plugin_validators.append(plugin_validator)

    def violated_identifiers(
            self, abs_path: str) -> "tuple[identifier.PluginIdentifier]":
        """Funkce vrací ntici všech identifikátorů, které prohlašují dodaný
        soubor za neplatný.
        """
        return tuple(filter(
            lambda ident: not ident.is_plugin(abs_path), self.identifiers))

    def is_potential_plugin(self, abs_path: str) -> bool:
        """Funkce vrací, zda-li je na dodané cestě potenciální plugin. To je
        zjištěno tak, že se zjistí počet porušených pravidel, tedy je-li počet
        identifikátorů, které soubor na dodané cestě prohlásily za neplatný
        roven nule, pak je dodaný soubor potenciálním pluginem.
        """
        return len(self.violated_identifiers(abs_path)) == 0

    def flush_plugins(self):
        """Funkce vyprázdní doposud identifikované pluginy."""
        self._plugins = []

    @abstractmethod
    def load(self) -> "tuple[pl.Plugin]":
        """Abstraktní funkce load je odpovědná za načtení všech nových
        potenciálních pluginů. To znamená, že původní seznam musí být
        vyčištěn a musí se vytipovat všechny nové pluginy z dodaného
        adresáře."""



class PluginLoaderError(error.PlatformError):
    """Třída definuje výjimku, která značí vznik chyby v kontextu načítání
    pluginů."""

    def __init__(self, message: str, plugin_loader: PluginLoader):
        error.PlatformError.__init__(self, message)
        self._plugin_loader = plugin_loader

    @property
    def plugin_loader(self) -> PluginLoader:
        """Vlasnost vrací PluginLoader, v jehož kontextu došlo k chybě."""
        return self._plugin_loader

