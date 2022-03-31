"""Modul obsahuje prostředky pro dynamické načítání továrních tříd jednotek.

Modul především definuje třídy UnitFactoryLoader a UnitFactoryPlugin. Obě
umožňují identifikaci a validaci pluginů továrních tříd jednotek a jejich
dynamické načítání.
"""

# Prevence cyklických importů
from __future__ import annotations

# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.utils.loading.plugin_loader as loader_module
import src.fw.utils.loading.plugin_identifier as pl_identifier
import src.fw.utils.loading.plugin_validator as pl_validator
import src.fw.utils.loading.plugin as plugin_module
import src.fw.robot.unit as unit_module

from src.fw.utils.filesystem import plugin_path, join_paths


"""Název funkce, která bude volána coby klíčový přístupový bod pro obdržení
instance továrny jednotek"""
_ACCESS_FUN = "get_unit_factory"

"""Název adresáře v rámci adresáře s pluginy, který obsahuje pluginy z
kontextu jednotek a jejich továren"""
_UNITS_DIR_NAME = "units"

"""Absolutní cesta k adresáři, ve kterém jsou pluginy s jednotkami"""
_ABSOLUTE_UNIT_PLUGINS_DIR_PATH = join_paths(plugin_path(), _UNITS_DIR_NAME)

"""Výchozí identifikátory pluginů, které jsou používány pro vytipování
pluginů v kontextu továren jednotek."""
_DEFAULT_IDENTIFIERS = [

    # Zdrojové soubory musí mít koncovku '.py'
    pl_identifier.ExtensionPluginIdentifier(".py"),

    # Zdrojové soubory musí začínat řetězcem 'unit_'
    pl_identifier.PrefixPluginIdentifier("unit_")
]

"""Výchozí validátory pluginů, které jsou používány pro ověření platnosti
a správnosti pluginů v kontextu továren jednotek."""
_DEFAULT_VALIDATORS = [

    # Modul musí být syntakticky validní
    pl_validator.SyntaxValidator(),

    # Modul musí být opatřen neprázdným dokumentačním komentářem
    pl_validator.ModuleDocstringExistenceValidator(),

    # Modul musí obsahovat funkci s definovaným názvem
    pl_validator.FunctionExistenceValidator(_ACCESS_FUN),

    # Modul musí obsahovat funkci vracející hodnotu konkrétního typu
    pl_validator.FunctionReturnValueTypeValidator(
        _ACCESS_FUN, unit_module.AbstractUnitFactory)
]


class UnitFactoryLoader(loader_module.PluginLoader):
    """Loader továren jednotek UnitFactoryLoader je odpovědný za dynamické
    načítání pluginů obsahujících definici továrních tříd jednotek.
    Třída poskytuje dynamickou správu načítání pluginů v kontextu získávání
    továrních jednotek. Oproti abstraktnímu předkovi ('PluginLoader') je tato
    obohacena ještě o implementaci funkce 'load()', která vyfiltruje všechny
    nevalidní pluginy a vrátí množinu pluginů třídy UnitFactoryPlugin."""

    def __init__(self, dest_dir: str,
                 identifiers: "Iterable[pl_identifier.PluginIdentifier]",
                 validators: "Iterable[pl_validator.PluginValidator]"):
        """Initor třídy odpovědný za inicializaci předka a uložení
        všech identifikátorů a validátorů pluginů.

        V parametru přijímá absolutní cestu k adresáři, který má být prohledán
        po pluginech. Dále v parametru přijímá množiny identifikátorů a
        validátorů, které mají být použity pro zajištění co nejvyšší míry
        integrity systému."""

        # Volání initoru předka
        loader_module.PluginLoader.__init__(self, dest_dir)

        # Přidání všech dodaných identifikátorů a validátorů
        self.add_all_identifiers(identifiers)
        self.add_all_validators(validators)

    @property
    def unit_factories(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """Funkce obsluhuje načítání všech továrních tříd jednotek. Tyto
        načtené továrny pak vrací v podobě ntice."""
        return tuple(map(lambda valid_plugin:
                         valid_plugin.unit_factory, self.load()))

    @property
    def not_valid_plugins(self) -> "tuple[UnitFactoryPlugin]":
        """Vlastnost implementuje protokol předka. Tato funkce vrací ntici
        všech pluginů, které sice prošly identifikací, ale nebyly validní.

        Této vlastnosti lze využít ke zpětnému odhalování, co s nebylo s
        těmito pluginy v pořádku."""
        invalid_plugins = []
        for path in self.potential_plugins:
            plugin = UnitFactoryPlugin(path, self, _ACCESS_FUN)
            if not plugin.is_valid_plugin:
                invalid_plugins.append(plugin)
        return tuple(invalid_plugins)

    def load(self) -> "tuple[UnitFactoryPlugin]":
        """Funkce se stará o načtení všech validních pluginů a ty dále vrací
        uspořádané v ntici.

        V první řadě si vytipuje potenciální pluginy (tedy ty soubory, které
        se zdají býti dle pravidel identifikace jako zdrojové soubory v rámci
        daného kontextu) a ty dále ověřuje, zda-li jsou platné.

        Vrací pak pouze ty, které projdou všemi validačními procedurami
        definovanými sadou instancí třídy PluginValidator dodaných v initoru.
        """
        valid_plugins = []

        # Pro všechny identifikované (a tedy potenciální) pluginy
        for potential_plg_path in self.potential_plugins:
            plugin = UnitFactoryPlugin(potential_plg_path, self, _ACCESS_FUN)
            if plugin.is_valid_plugin:
                valid_plugins.append(plugin)
            # TODO - log nevalidního pluginu
        return tuple(valid_plugins)


class UnitFactoryPlugin(plugin_module.Plugin):
    """Třída UnitFactoryPlugin je odpovědná za zpřístupnění dynamického
    načítání modulů v kontextu továren jednotek.

    Instance této třídy rozšiřují funkcionalitu rodičovské třídy (tedy Plugin)
    a mají nad rámec i vlastnost pro získání dané tovární třídy.

    V rámci kontextového způsobu použití lze mluvit o třídě podle návrhového
    vzoru Služebník."""

    def __init__(self, abs_path: str,
                 plugin_loader: "UnitFactoryLoader",
                 access_point_fun: str):
        """Initor třídy odpovědný za iniciaci svého předka a za uložení
        všech potřebných hodnot.

        V parametrech přijímá absolutní cestu k modulu, který má být ověřen a
        z něhož má být čteno, dále referenci na PluginLoader, který tuto
        instanci tvoří (konkrétně instanci třídy UnitFactoryLoader), a také
        název přístupové funkce, která vrací instanci tovární třídy jednotky.
        """
        # Iniciace předka
        plugin_module.Plugin.__init__(self, abs_path, plugin_loader)

        # Název přístupové funkce, která má být v modulu zavolána
        self._access_point_function = access_point_fun

    @property
    def access_point_function(self) -> str:
        """Vlastnost vrací název funkce, kterou je třeba zavolat, aby byla
        navrácena instance tovární třídy jednotek."""
        return self._access_point_function

    @property
    def unit_factory(self) -> "unit_module.AbstractUnitFactory":
        """Vlastnost vrací tovární třídu jednotky, která poskytuje jednotky
        daného typu.
        """
        # Přístupová funkce musí být obsažena v daném modulu. Není-li tomu
        # tak, je vyhozena příslušná výjimka.
        if not self.has_function(self.access_point_function):
            raise plugin_module.PluginError(
                f"Plugin nemá přístupovou funkci názvu "
                f"'{self.access_point_function}'", self)

        # Vrácení výstupu volání přístupové funkce
        return self.get_function(self._access_point_function)()


class DefaultUnitFactoryLoader(UnitFactoryLoader):
    """Třída defaultního loaderu instancí továrních tříd jednotek, která
    má za cíl rozšířit obecnějšího předka o výchozí hodnoty.

    Konkrétně je tato opatřena výchozí cestou k adresáři k pluginům tohoto
    kontextu, dále výchozími identifikátory a výchozími validátory."""

    def __init__(self):
        """Bezparametrický initor, který je odpovědný za zavolání předka
        s výchozími hodnotami."""
        UnitFactoryLoader.__init__(self, _ABSOLUTE_UNIT_PLUGINS_DIR_PATH,
                                   _DEFAULT_IDENTIFIERS, _DEFAULT_VALIDATORS)



