""""""

# Import standardních knihoven
from abc import ABC, abstractmethod


# Import lokálních knihoven
from ..filesystem import exists, is_file, has_regex_name, file_basename, \
    FileSystemError
from src.fw.utils.named import Named

_MODULE_REGEX = "[a-z]([a-z0-9]|\\_)+\\.py"


class PluginIdentifier(ABC, Named):
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
        Named.__init__(self, "Prefix Plugin Identifier")
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


class ExtensionPluginIdentifier(PluginIdentifier):
    """Třída sloužící jako služebník pro identifikaci pomocných pluginů
    pomocí ověření, zda-li má soubor správnou koncovku (typicky '.py').
    """

    def __init__(self, extension: str = ".py"):
        Named.__init__(self, "Extension Plugin Identifier")
        PluginIdentifier.__init__(self)
        self._extension = extension

    @property
    def extension(self) -> str:
        return self._extension

    def is_plugin(self, filepath: str) -> bool:
        """Funkce ověřuje, zda-li je dodaný soubor zdrojovým souborem pro
        Python a tedy i potenciálním kandidátem na plugin - a to pomocí
        koncovky dodaného souboru.
        """
        if not exists(filepath):
            raise FileSystemError(
                f"Dodaná cesta ke zdrojovému souboru '{filepath}' neexistuje",
                [filepath])
        return file_basename(filepath, True).endswith(self.extension)


class NotStartingWithPluginIdentifier(PluginIdentifier):
    """Identifikátor pluginů 'NotStartingWithPluginIdentifier' ověřuje,
    zda-li dodaná cesta ukazuje na existující soubor, který je možné jako
    plugin načíst a jeho název NEZAČÍNÁ dodaným řetězcem.
    Typickým případem užití je například použití prefixu 'template_' před
    názvy šablonových zdrojových souborů, které však převáděny na pluginy
    (resp. importovány 'as is') být nemají.
    """

    def __init__(self, forbidden_prefix: str):
        Named.__init__(self, "Not Starting With Plugin Identifier")
        PluginIdentifier.__init__(self)
        self._forbidden_prefix = forbidden_prefix

    @property
    def forbidden_prefix(self) -> str:
        return self._forbidden_prefix

    def is_plugin(self, filepath: str):
        """Funkce ověřuje, zda-li dodaná cesta ukazuje na existující soubor,
        který je jako plugin možné načíst.
        Pokud k souboru nemá systém přístup, je vyhozena výjimka.
        """
        if not exists(filepath):
            raise FileSystemError(
                f"Dodaná cesta ke zdrojovému souboru '{filepath}' neexistuje",
                [filepath])

        # Ověření, že název začíná dodaným názvem je obráceno, tedy pokud ano,
        # pak je vráceno False, pokud ne, je prohlášen modul za validní (True)
        return not file_basename(filepath, False).startswith(
            self.forbidden_prefix)



