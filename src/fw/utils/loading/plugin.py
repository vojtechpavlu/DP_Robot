"""Modul 'plugin' je odpovědný za sdružení všech potřebných protokolů pro
práci s pluginy."""

# Import standardních knihoven
import importlib
from abc import ABC, abstractmethod
from inspect import getmembers, isfunction
from types import ModuleType
from typing import Callable

# Import lokálních knihoven
import src.fw.utils.loading.plugin_loader as pl_loader
import src.fw.utils.loading.plugin_validator as validator

from ..filesystem import module_path_from_abs, exists, is_file
from ..error import PlatformError


class Plugin(ABC):
    """Abstraktní třída Plugin je odpovědná za sdružování základního protokolu
    pluginu, coby nástroje pro dynamické importování funkcionality.

    Cílem instancí potomků této třídy je udržovat základní popisné údaje o
    pluginu, vedle sdružování funkcí, které s tímto úkolem souvisí.

    Konkrétněji jsou instance opatřeny funkcionalitou pro ověřování validity
    pluginů, stejně jako funkcionalitou pro práci s přístupovými body; typicky
    lze pomocí instancí potomků této třídy volat funkce, které jsou v rámci
    modulu reprezentujícího daný plugin.
    """

    def __init__(self, abs_path: str, plugin_loader: pl_loader.PluginLoader):
        """"""
        self._absolute_path = abs_path
        self._module_path = module_path_from_abs(abs_path)
        self._plugin_loader = plugin_loader

        if not (exists(abs_path) and is_file(abs_path)):
            raise PluginError(
                f"Na dodané cestě '{abs_path}' není existující soubor", self)

    @property
    def plugin_loader(self) -> pl_loader.PluginLoader:
        """Loader, který je odpovědný za načtení tohoto pluginu."""
        return self._plugin_loader

    @property
    def absolute_path(self) -> str:
        """Absolutní cesta k souboru, který reprezentuje daný plugin."""
        return self._absolute_path

    @property
    def module_path(self) -> str:
        """Balíčková cesta k modulu, který reprezentuje daný plugin."""
        return self._module_path

    @property
    def validators(self) -> "tuple[validator.PluginValidator]":
        """Ntice validátorů, které reprezentují pravidla pro přijetí modulu
        jako validní plugin v definovaném kontextu.
        """
        return self.plugin_loader.validators

    @property
    def violated_validators(self) -> "tuple[validator.PluginValidator]":
        """Vlastnost vrací množinu validátorů, jejichž podmínky nebyly tímto
        pluginem naplněny."""
        violated_validators = []
        for val in self.validators:
            try:
                if not val.is_valid_plugin(self):
                    violated_validators.append(val)
            except Exception as e:
                print(f"VIOLATED VALIDATORS: {e}")
                violated_validators.append(val)
        return tuple(violated_validators)

    @property
    def is_valid_plugin(self) -> bool:
        """Vlastnost vrací informaci o tom, zda-li je dodaný plugin validní
        oproti definovaným pravidlům."""
        return len(self.violated_validators) == 0

    @property
    def module(self) -> "ModuleType":
        """Vlastnost se pokusí načíst modul, kterým je plugin reprezentován.
        Pokud se načíst modul nepovede (typicky z důvodu syntaktické chyby),
        je vyhozena výjimka PluginError."""
        try:
            return importlib.import_module(self.module_path)
        except Exception as e:
            raise PluginError(
                f"Při načítání modulu '{self.module_path}' na cestě "
                f"'{self.absolute_path}' došlo k chybě:\n"
                f"\t'{type(e).__name__}': '{str(e)}'", self)

    @property
    def all_attributes(self) -> "tuple[tuple[str, object]]":
        """"""
        attrs = dir(self.module)
        return tuple(map(
            lambda key: (str(key), attrs.key,), attrs))

    @property
    def all_functions(self) -> "tuple[tuple[str, Callable]]":
        """Tato funkce vrátí všechny funkce, kterými je modul pluginu opatřen.
        Vrací je v podobě ntice ntic, přičemž každá vnitřní obsahuje textový
        řetězec reprezentující název funkce a referenci na danou funkci.
        """
        return tuple(getmembers(self.module, isfunction))

    @property
    def all_function_names(self) -> "tuple[str]":
        """Vlastnost vrací ntici utvořenou ze seznamu názvů všech funkcí,
        které jsou v modulu pluginu.
        """
        return tuple(map(lambda fun_desc: fun_desc[0], self.all_functions))

    @property
    def docstring(self) -> str:
        """Vlastnost vrací dokumentační komentář modulu, který reprezentuje
        plugin."""
        return self.module.__doc__

    def has_attribute(self, attr_name: str) -> bool:
        """Funkce vrací informaci o tom, zda-li daný plugin má nebo nemá
        atribut daného názvu.
        """
        return hasattr(self.module, attr_name)

    def has_function(self, fun_name: str) -> bool:
        """Funkce vrací informaci o tom, zda-li daný obsahuje funkci daného
        názvu."""
        for func_desc in self.all_functions:
            if func_desc[0] == fun_name:
                return True
        return False

    def get_attribute(self, attr_name: str) -> object:
        """Funkce vrací atribut (resp. jeho hodnotu), kterým je daný modul
        opatřen. Pokud daný atribut nemá, je vyhozena výjimka.
        """
        if self.has_attribute(attr_name):
            return self.module.__getattribute__(attr_name)
        else:
            raise PluginError(f"Plugin atribut '{attr_name}' nemá", self)

    def get_function(self, fun_name: str):
        """Tato funkce se pokusí vyhledat funkci daného názvu uvnitř modulu
        pluginu.

        Pokud není taková funkce nalezena, je vyhozena příslušná výjimka.
        """
        for fun_description in self.all_functions:
            if fun_description[0] == fun_name:
                return fun_description[1]
        raise PluginError(
            f"Funkce názvu '{fun_name}' nebyla nalezena", self)


class PluginError(PlatformError):
    """Třída PluginError definuje výjimky, které jsou vyhazovány, dojde-li
    k chybě v kontextu pluginu."""

    def __init__(self, message: str, plugin: Plugin):
        PlatformError.__init__(self, message)
        self._plugin = plugin

    @property
    def plugin(self) -> Plugin:
        """Plugin, v jehož kontextu došlo k chybě."""
        return self._plugin



