""""""

# Import standardních knihoven
from abc import ABC, abstractmethod


# Import lokálních knihoven
from ..filesystem import exists, is_file, has_regex_name, file_basename

# Definice proměnných
_MODULE_REGEX = "[a-z]([a-z0-9]|\\_)+\\.py"


class PluginIdentifier(ABC):
    """Identifikátor pluginů, který je odpovědný za vytipování souborů, které
    jsou potenciálními pluginy."""

    @staticmethod
    def formal_check(abs_path: str) -> bool:
        """"""
        global _MODULE_REGEX
        return (exists(abs_path) and is_file(abs_path) and
                has_regex_name(abs_path, _MODULE_REGEX))

    @abstractmethod
    def is_plugin(self, abs_path: str) -> bool:
        """Abstraktní funkce se pokusí vyzkoušet, zda-li dodaná cesta
        ukazuje na soubor, který by odpovídal pluginu dle vnitřních pravidel
        potomka implementujícího tuto třídu."""


class PrefixPluginIdentifier(PluginIdentifier):
    """Identifikátor, který ověří, že název dodaného souboru začíná
    definovaným řetězcem znaků."""

    def __init__(self, prefix: str):
        PluginIdentifier.__init__(self)
        self._prefix = prefix

    @property
    def prefix(self) -> str:
        """Prefix, který název souboru a potenciálního pluginu musí mít."""
        return self._prefix

    def is_plugin(self, abs_path: str) -> bool:
        """Funkce ověřuje, zda-li na dodané cestě je soubor, který má název
        s definovanou předponou."""
        if self.formal_check(abs_path):
            return file_basename(abs_path).startswith(self.prefix)
        return False





