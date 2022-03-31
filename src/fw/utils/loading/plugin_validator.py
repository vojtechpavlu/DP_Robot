"""Tento modul sdružuje základní funkcionalitu ve vztahu k validaci pluginů.
Typicky provádí podrobnější průzkum obsahu souborů, které byly identifikovány
jako potenciální pluginy, zda splňují podrobnější nároky.

Typicky se zde pracuje s průzkumem kódu a to co do ze statického pohledu
(např. existuje-li dokumentace modulu), tak i funkčního ověřování (např.
je-li v modulu definována funkce daného názvu či jaká je návratová funkce
daného názvu).

Cílem je vytřídit jen ty pluginy (moduly), které jsou zcela validní a které
mají příslušný požadovaný protokol a lze s nimi bezpečně pracovat.
"""

# Prevence cyklických importů
from __future__ import annotations

# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Type

# Import lokálních knihoven
import src.fw.utils.loading.plugin as pl

from src.fw.utils.described import Described
from src.fw.utils.named import Named


class PluginValidator(Named, Described):
    """Validátor pluginů, který ověřuje, že dodané pluginy jsou skutečně
    dle dodaných pravidel validní a použitelné v daném kontextu."""

    def __init__(self, validator_name: str, validator_desc: str):
        """Initor třídy, který je odpovědný za přijetí názvu a popisu
        validátoru potenciálních pluginů.

        Zatímco název plní funkci spíše lidsky čitelného identifikátoru, popis
        plní roli předání podrobnějších informaci o validátoru. V popisu by
        měl být uveden alespoň stručně způsob vyhodnocování, zda je plugin
        validní či nikoliv, případně pro danou instanci konkrétní specifické
        hodnoty.
        """
        Named.__init__(self, validator_name)
        Described.__init__(self, validator_desc)

    @abstractmethod
    def is_valid_plugin(self, plugin: "pl.Plugin") -> bool:
        """Abstraktní funkce ověřuje, zda-li je dodaný plugin validní oproti
        pravidlům definovaným instancemi implementujícími tuto třídu."""


class SyntaxValidator(PluginValidator):
    """Validátor syntaxe. Validátor funguje tak, že se pokusí načíst modul.
    Pokud modul není validní (obsahuje syntaktické chyby na úrovni modulu),
    je vyhozena výjimka. Na základě toho lze rozlišit nevalidní moduly."""

    def __init__(self):
        PluginValidator.__init__(
            self, "Syntax Validator",
            f"Syntax Validator se pokusí plugin načíst. Dojde-li během "
            f"načítání k chybě (typicky syntaktické), bude daný plugin "
            f"vyhodnocen jako nevalidní."
        )

    def is_valid_plugin(self, plugin: "pl.Plugin") -> bool:
        """Implementace metody je odpovědná za provedení kontroly syntaxe.
        V této podobě stačí odzkoušet, zda-li dodaný modul lze jako validní
        modul načíst."""
        try:
            return plugin.module is not None
        except Exception as e:  # TODO - LOG CHYBNÉHO MODULU
            return False


class FunctionExistenceValidator(PluginValidator):
    """PluginValidator 'FunctionExistenceValidator' ověřuje, že sledovaný
    plugin obsahuje funkci daného názvu."""

    def __init__(self, function_name: str):
        """Jednoduchý initior, který přijímá v parametru název funkce, která
        má být dle pravidel tohoto validátoru v rámci modulu reprezentujícího
        daný plugin přítomna.

        Pokud funkce tohoto názvu (jsou rozlišována malá a velká písmena) není
        přítomna, testem, který je touto instancí realizován, tento plugin
        úspěšně neprojde. Stejně tak v případě, kdy sice modul obsahuje
        atribut tohoto názvu, nikoliv však volatenou funkci.
        """
        PluginValidator.__init__(
            self, "Function Existence Validator",
            f"Validátor ověřuje, že modul reprezentující daný plugin má v "
            f"sobě obsaženu funkci názvu '{function_name}'. Důvodem je snaha "
            f"o zajištění přístupnosti k některým údajům."
        )

        self._function_name = function_name

    @property
    def function_name(self) -> str:
        """Vlastnost vrací název funkce, která má být hledána."""
        return self._function_name

    def is_valid_plugin(self, plugin: "pl.Plugin") -> bool:
        """Zde je ověřováno, že dodaný plugin ukazuje na modul, který v sobě
        má funkci se specifickým názvem."""
        return self.function_name in plugin.all_function_names


class ModuleDocstringExistenceValidator(PluginValidator):
    """Instance této třídy validují, zda-li modul, na který je dodaným
    pluginem odkazováno, obsahuje neprázdný dokumentační komentář.
    Za neprázdný se považuje takový, který obsahuje alespoň jeden tisknutelný
    znak, tedy z tohoto pohledu tzv. 'bílé znaky' nejsou přípustným znakem.
    """

    def __init__(self):
        """Jednoduchý initor odpovědný za volání initorů svých předků.
        """
        PluginValidator.__init__(
            self, "Module Docstring Existence Validator",
            f"Validátor ověřuje, že modul reprezentovaný dodaným pluginem "
            f"je opatřen neprázdným dokumentačním komentářem."
        )

    def is_valid_plugin(self, plugin: "pl.Plugin") -> bool:
        """Funkce ověřuje, zda-li dodaný plugin odkazuje na modul s
        existujícím neprázdným dokumentačním komentářem."""
        return plugin.docstring and len(plugin.docstring.strip()) > 0


class FunctionReturnValueTypeValidator(PluginValidator):
    """Validátor, který ověřuje, zda-li modul obsahuje požadovanou funkci s
    příslušnou návratovou hodnotou. K tomu je tento validátor opatřen i
    možností použití vstupních parametrů.
    """

    def __init__(self, function_name: str, to_be_class: Type,
                 params: "tuple[object]" = ()):
        """Initor třídy odpovědný kromě volání svých předků také za uložení
        dodaných hodnot v parametrech funkce.

        Konkrétně zde v parametru přijímá:
            - název funkce, která má být volána
            - typ návratové hodnoty
            - ntici parametrů, které mají být do funkce vloženy pro
              očekávaný efekt
        """
        PluginValidator.__init__(
            self, "Function Return Value Type Validator",
            f"Validátor ověřuje, že zavolání funkce s názvem "
            f"'{function_name}' s dodanými parametry '{params}' vrátí hodnotu "
            f"typu '{to_be_class}'. Pokud ne, bude prohlášen plugin za "
            f"nevalidní, stejně tak nebude-li mít funkci daného názvu."
        )

        self._function_name: str = function_name
        self._to_be_class: Type = to_be_class
        self._params = params

    @property
    def function_name(self) -> str:
        """Vlastnost vrací název funkce, která má být ověřována, že vrací
        správný typ."""
        return self._function_name

    @property
    def to_be_class(self) -> Type:
        """Vlastnost vrací očekávaný typ navrácené hodnoty."""
        return self._to_be_class

    @property
    def params(self) -> "tuple[object]":
        """Vlastnost vrací parametry, které mají být do funkce postoupeny.
        """
        return self._params

    @params.setter
    def params(self, new_params: "tuple[object]"):
        """Vlastnost přijímá v parametru novou ntici parametrů, které
        postoupí do dodané funkce."""
        self._params = new_params

    @property
    def num_of_params(self) -> int:
        """Vlasnost vrací jednoduše počet definovaných vstupních parametrů.
        """
        return len(self.params)

    def is_valid_plugin(self, plugin: "pl.Plugin") -> bool:
        """Funkce ověřuje, zda-li sledovaná funkce v modulu vrací hodnotu
        správného typu. Pokud ano, vrací True, jinak False.
        Pokud v modulu funkce není definována, je odchycena výjimka a vrácena
        hodnota False. Podobně je tomu i v dalších chybových případech; třeba
        když atribut není volatelný nebo vyžaduje parametry.
        """
        try:
            if plugin.has_function(self.function_name):
                func = plugin.get_function(self.function_name)
                return isinstance(func(*self.params), self.to_be_class)
            else:
                # Funkce daného názvu není přítomna
                return False
        except pl.PluginError as ple:
            print(f"CHYBA PŘI VALIDACI NÁVRATOVÉ HODNOTY {ple}")
            return False
        except Exception as e:
            print(f"OBECNÁ CHYBA PŘI VALIDACI NÁVRATOVÉ HODNOTY {e}")
            return False





