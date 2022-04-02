"""Tento modul sdružuje funkcionalitu týkající se identifikace potenciálních
pluginů, které je možné identifikovat. Typickým nástrojem je analýza okolností,
které se daného souboru týkají a soubor není nijak hlouběji prozkoumáván co do
obsahu.

Hlavními zástupci jsou třídy operující pouze s názvy daných souborů. Ty mají
za cíl provést prvotní filtraci těch souborů, které mohou a které nemohou
býti pluginy.
"""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.utils.filesystem as fs

from src.fw.utils.described import Described
from src.fw.utils.named import Named

"""Defaultní regulární výraz, dle kterého jsou identifikovány soubory, které
mohou být v nejširším kontextu považovány za pluginy. Tedy dle názvu 
identifikované zdrojové soubory v jazyce Python.

Tento regulární výraz (regular expression nebo také regex) identifikuje
soubory dle standardní naming convention platnou pro tento jazyk, tedy
tzv. snake notation, kdy identifikátory počínají znakem anglické abecedy,
následované libovolně dlouhou řadou znaků anglické abecedy, číslic nebo 
podtržítek. Defaultně zde předpokládáme, že jedinou povolenou koncovkou
je '.py'.

Povolenými názvy tedy mohou být například:
    - 'abcd.py'
    - 'x6.py'
    - 'example_module5.py'

Naopak vyřazenými pak jsou moduly s názvem:
    - '7.py'
    - '_test_module.py'
    - 'ABC.py'
    - ale také '__init__.py'     
"""
_MODULE_REGEX = "[a-z]([a-z0-9]|\\_)+\\.py"


class PluginIdentifier(Named, Described):
    """Identifikátor pluginů, který je odpovědný za vytipování souborů, které
    jsou potenciálními pluginy."""

    def __init__(self, identifier_name: str, identifier_desc: str):
        """Initor pluginů, který přijímá v parametru název a popis.

        Název hraje roli spíše pro lidskou identifikaci, popis plní funkci
        předání podrobnější informace o způsobu identifikace, o podmínkách
        pro úspěšnou identifikaci nebo specifické hodnoty pro tuto konkrétní
        instanci.
        """
        Named.__init__(self, identifier_name)
        Described.__init__(self, identifier_desc)

    @staticmethod
    def formal_check(abs_path: str) -> bool:
        """Formální kontrola, která otestuje, že na dodané cestě je existující
        soubor názvu platného v souladu s definovaným regulárním výrazem.

        Tato formální kontrola je prvním a nejobecnějším sítem před zabýváním
        se dalším zpracováváním potenciálních pluginů."""
        global _MODULE_REGEX
        return (fs.exists(abs_path) and fs.is_file(abs_path) and
                fs.has_regex_name(abs_path, _MODULE_REGEX))

    @abstractmethod
    def is_plugin(self, abs_path: str) -> bool:
        """Abstraktní funkce se pokusí vyzkoušet, zda-li dodaná cesta
        ukazuje na soubor, který by odpovídal pluginu dle vnitřních pravidel
        potomka implementujícího tuto třídu."""


class PrefixPluginIdentifier(PluginIdentifier):
    """Identifikátor, který ověří, že název dodaného souboru začíná
    definovaným řetězcem znaků."""

    def __init__(self, prefix: str):
        """Initor třídy, který je odpovědný za inicializaci svých předků,
        stejně jako za uložení vstupní hodnoty. Ta je prefix (předpona),
        která předurčuje, že jde o plugin v rámci sledovaného kontextu.

        Tato předpona je chápána coby řetězec znaků a odpovídá úvodní části
        názvu souboru (modulu), který reprezentuje sledovaný plugin.

        Příkladně budeme-li sledovat prefix 'program_' (bez uvozovek), pak
        projdou tímto testem soubory s názvy:

            - 'program_1.py'
            - 'program_test1.py'
            - 'program_.py'

        Nikoliv však například soubory s názvy:

            - 'test_program_1.py'
            - 'program.py'
            - '_program_.py'
        """
        PluginIdentifier.__init__(
            self,
            "Prefix Plugin Identifier",
            f"Prefix Plugin Identifier ověřuje, zda má potenciální plugin "
            f"název počínající předponou; v tomto případe '{prefix}'")

        self._prefix = prefix

    @property
    def prefix(self) -> str:
        """Prefix, který název souboru a potenciálního pluginu musí mít."""
        return self._prefix

    def is_plugin(self, abs_path: str) -> bool:
        """Funkce ověřuje, zda-li na dodané cestě je soubor, který má název
        s definovanou předponou."""
        if self.formal_check(abs_path):
            return fs.file_basename(abs_path).startswith(self.prefix)
        return False


class ExtensionPluginIdentifier(PluginIdentifier):
    """Třída sloužící jako služebník pro identifikaci pomocných pluginů
    pomocí ověření, zda-li má soubor správnou koncovku (defaultně '.py').
    """

    def __init__(self, extension: str = ".py"):
        """Jednoduchý initor třídy odpovědný za volání svých předků. Dále také
        za uložení koncovky (extension), která je dodána v parametru funkce.

        Její defaultní hodnota je '.py'.
        """
        PluginIdentifier.__init__(
            self, "Extension Plugin Identifier",
            f"Tento identifikátor je odpovědný za ověření, že dodaný soubor "
            f"má název končící koncovkou; v tomto případe '{extension}'"
        )

        self._extension = extension

    @property
    def extension(self) -> str:
        return self._extension

    def is_plugin(self, filepath: str) -> bool:
        """Funkce ověřuje, zda-li je dodaný soubor zdrojovým souborem pro
        Python a tedy i potenciálním kandidátem na plugin - a to pomocí
        koncovky dodaného souboru.
        """
        if not fs.exists(filepath):
            raise fs.FileSystemError(
                f"Dodaná cesta ke zdrojovému souboru '{filepath}' neexistuje",
                [filepath])
        return fs.file_basename(filepath, True).endswith(self.extension)


class NotStartingWithPluginIdentifier(PluginIdentifier):
    """Identifikátor pluginů 'NotStartingWithPluginIdentifier' ověřuje,
    zda-li dodaná cesta ukazuje na existující soubor, který je možné jako
    plugin načíst a jeho název NEZAČÍNÁ dodaným řetězcem.
    Typickým případem užití je například použití prefixu 'template_' před
    názvy šablonových zdrojových souborů, které však převáděny na pluginy
    (resp. importovány 'as is') být nemají.
    """

    def __init__(self, forbidden_prefix: str):
        """Jednoduchý initor třídy odpovědný za volání initorů svých předků.
        Dále také za uložení vstupního zakázaného prefixu (předložky) názvu
        souboru. Jeho přítomnost v názvu pochopitelně daný soubor zamítne z
        užšího výběru potenciálních pluginů.

        Důvodem k použití je například definování šablonového modulu, jehož
        název může počínat řetězcem 'template_' a zcela jistě ho dále nemá
        smysl uvažovat jako validní a kompletní plugin.
        """
        PluginIdentifier.__init__(
            self, "Not Starting With Plugin Identifier",
            f"Tento identifikátor potenciálních pluginů je odpovědný za "
            f"vytipování takových souborů, které nesou název nezačínající"
            f"konkrétní předponou, v tomto případě '{forbidden_prefix}'."
        )
        self._forbidden_prefix = forbidden_prefix

    @property
    def forbidden_prefix(self) -> str:
        return self._forbidden_prefix

    def is_plugin(self, filepath: str):
        """Funkce ověřuje, zda-li dodaná cesta ukazuje na existující soubor,
        který je jako plugin možné načíst.
        Pokud k souboru nemá systém přístup, je vyhozena výjimka.
        """
        if not fs.exists(filepath):
            raise fs.FileSystemError(
                f"Dodaná cesta ke zdrojovému souboru '{filepath}' neexistuje",
                [filepath])

        """Ověření, že název začíná dodaným názvem je obráceno, 
        tedy pokud ano, pak je vráceno False, pokud ne, je prohlášen 
        modul za validní (True)"""
        return not fs.file_basename(filepath, False).startswith(
            self.forbidden_prefix)


class MaxFilesizePluginIdentifier(PluginIdentifier):
    """"""

    def __init__(self, max_size: int):
        """"""
        PluginIdentifier.__init__(
            self, "Max Filesize in Bytes",
            f"Identifikátor pluginů, který je odpovědný za kontrolu, že "
            f"soubor reprezentující plugin není větší, než {max_size} bytů.")
        self._max_size = max_size

    @property
    def max_size(self) -> int:
        """"""
        return self._max_size

    def is_plugin(self, abs_path: str) -> bool:
        """"""
        return self._max_size <= fs.filesize(abs_path)





