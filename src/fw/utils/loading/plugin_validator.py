""""""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from typing import Type

import src.fw.utils.loading.plugin as pl
from src.fw.utils.named import Named


class PluginValidator(ABC, Named):
    """Validátor pluginů, který ověřuje, že dodané pluginy jsou skutečně
    dle dodaných pravidel validní a použitelné v daném kontextu."""

    @abstractmethod
    def is_valid_plugin(self, plugin: "pl.Plugin") -> bool:
        """Abstraktní funkce ověřuje, zda-li je dodaný plugin validní oproti
        pravidlům definovaným instancemi implementujícími tuto třídu."""


class SyntaxValidator(PluginValidator):
    """Validátor syntaxe. Validátor funguje tak, že se pokusí načíst modul.
    Pokud modul není validní (obsahuje syntaktické chyby na úrovni modulu),
    je vyhozena výjimka. Na základě toho lze rozlišit nevalidní moduly."""

    def __init__(self):
        Named.__init__(self, "Syntax Validator")
        PluginValidator.__init__(self)

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
        Named.__init__(self, "Function Existence Validator")
        PluginValidator.__init__(self)
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
        Named.__init__(self, "Module Docstring Existence Validator")
        PluginValidator.__init__(self)

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
        """"""
        Named.__init__(self, "Function Return Value Type Validator")
        PluginValidator.__init__(self)
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
        except pl.PluginError as ple:
            print(f"CHYBA PŘI VALIDACI NÁVRATOVÉ HODNOTY {ple}")
            return False
        except Exception as e:
            print(f"OBECNÁ CHYBA PŘI VALIDACI NÁVRATOVÉ HODNOTY {e}")
            return False





