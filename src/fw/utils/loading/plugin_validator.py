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
from abc import abstractmethod
from typing import Type, Callable

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
            f"typu '{to_be_class.__name__}'. Pokud ne, bude prohlášen plugin "
            f"za nevalidní, stejně tak nebude-li mít funkci daného názvu."
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
        """Vlastnost vrací jednoduše počet definovaných vstupních parametrů.
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
        except pl.PluginError:
            return False
        except Exception:
            return False


class HasAttributePluginValidator(PluginValidator):
    """Třída odpovědná za kontrolu programů co do existence atributu. Pokud
    není atribut daného přítomný, vyhodnotí tento modul jako nevalidní."""

    def __init__(self, attr_name: str):
        """Initor instancí třídy, který přijímá název požadovaného atributu.
        Pokud tento není v modulu přítomný, bude vyhodnocen jako nevalidní.
        """

        # Volání initoru předka
        PluginValidator.__init__(
            self, "Has Attribute",
            "Validátor ověřující, že má plugin reprezentovaný daným souborem "
            f"požadovaný atribut s názvem '{attr_name}'.")

        # Uložení názvu požadovaného atributu
        self._attr_name = attr_name

    @property
    def attribute_name(self) -> str:
        """Vlastnost vrací název požadovaného atributu. Pokud tento v modulu
        není, nebude prohlášen za validní."""
        return self._attr_name

    def is_valid_plugin(self, plugin: "pl.Plugin") -> bool:
        """Kontrola, že dodaný plugin reprezentovaný modulem obsahuje atribut
        specifického názvu. Pokud tomu tak není, je vrácena hodnota False."""
        try:
            return plugin.has_attribute(self.attribute_name)
        except pl.PluginError:
            return False
        except Exception:
            return False


class CustomAttributePluginValidator(PluginValidator):
    """Třída reprezentující validátor atributu pomocí dodané funkce. Zde je
    ověřováno, že nejen, že dodaný modul daný atribut obsahuje, ale také že
    je tento atribut dle dodané funkce validní."""

    def __init__(
            self, attr_name: str, validation_function: Callable,
            validator_name: str="Custom Attribute Check",
            validator_desc: str="Kontrola, že specifikovaný atribut modulu "
                                "je dle dodané funkce validní."):
        """Initor, který přijímá název sledovaného atributu a hodnotící funkci.
        Předpokladem je, že je tato funkce validní a že vrací hodnotu True či
        False."""

        # Volání initoru předka
        PluginValidator.__init__(self, validator_name, validator_desc)

        # Uložení požadovaných hodnot
        self._attr_name = attr_name
        self._validation_fun = validation_function

    @property
    def attr_name(self) -> str:
        """Název atributu, který má být sledován."""
        return self._attr_name

    @property
    def validation_function(self) -> Callable:
        """Validační funkce, která ověřuje, že atribut má požadovanou podobu.
        """
        return self._validation_fun

    def is_valid_plugin(self, plugin: "pl.Plugin") -> bool:
        """Metoda, která se pokusí vyhledat v modulu reprezentujícím plugin
        atribut daného názvu. Pokud ho neobsahuje nebo je dle dodané funkce
        vyhodnocen jako neplatný, je vrácena hodnota False, stejně tak,
        dojde-li během vyhodnocování k chybě. Jinak vrací True."""
        try:
            if plugin.has_attribute(self.attr_name):
                return self.validation_function(
                    plugin.get_attribute(self.attr_name))
            else:
                return False
        except pl.PluginError:
            return False
        except Exception:
            return False


class RegexAttributePluginValidator(CustomAttributePluginValidator):
    """Validátor textových řetězců uložených v atributech modulu
    reprezentujícího plugin. Tento atribut musí být přítomen a musí být
    typu `str`."""

    def __init__(self, attr_name: str, regex: str):
        """Initor, který přijímá název sledovaného atributu a regulární
        výraz, kterým má být text v atributu ověřen."""

        # Volání initoru předka
        CustomAttributePluginValidator.__init__(
            self, attr_name, self._regex_check, "Regex Attribute Validator",
            f"Kontrola, že atribut obsahuje textový řetězec a že ten odpovídá "
            f"regulárnímu výrazu: '{regex}' (bez uvozovek).")

        # Uložení regulárního výrazu
        self._regex = regex

    def _regex_check(self, value: str):
        """Metoda, které bude použito pro kontrolu, že atribut obsahující
        textový řetězec odpovídá danému regulárnímu výrazu."""

        # Lokální import knihovny re
        import re

        # Kontrola, že je obsah daného atributu skutečně textový řetězec
        if type(value) != str:
            return False

        # Vrácení výsledku
        return bool(re.match(self._regex, value))

