"""Modul obsahuje prostředky pro dynamické načítání definic továrních tříd
běhových prostředí.

O funkcionalitu se starají především třídy instance RuntimeFactoryLoader,
které ke svému účelu používají především instancí třídy RuntimeFactoryPlugin
coby služebníka.

Pomocí těchto prostředků rozšiřujících třídy Plugin a PluginLoader je možné
dynamické načítání běhových prostředí, včetně definic světů a úloh, které jsou
s daným běhovým prostředím spjaté."""


# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.utils.loading.plugin_loader as loader_module
import src.fw.utils.loading.plugin_identifier as pl_identifier
import src.fw.utils.loading.plugin_validator as pl_validator
import src.fw.utils.loading.plugin as plugin_module
import src.fw.platform.runtime as runtime_module


"""Název přístupové funkce, která má být v modulu reprezentujícím plugin
běhového prostředí zavolána. Její existence by měla být ověřena již na úrovni
pravidla definovaného pomocí validátoru pluginu (instance PluginValidator).
"""
_ACCESS_FUN = "get_runtime_factory"


class RuntimeFactoryLoader(loader_module.PluginLoader):
    """Instance této třídy poskytují funkcionalitu dynamického načítání
    pluginů. Konkrétně se pokusí ze zadané absolutní cesty k adresáři
    hloubkově vyhledat ty soubory, které jsou potenciálními pluginy, a pokud
    jsou tyto pluginy v tomto kontextu validní, jsou z nich vybrány továrny
    běhových prostředí."""

    def __init__(self, dest_dir: str,
                 identifiers: "Iterable[pl_identifier.PluginIdentifier]",
                 validators: "Iterable[pl_validator.PluginValidator]"):
        """Initor třídy přijímá absolutní cestu k adresáři, který má být
        dynamicky načten. Dále pak přijímá množinu identifikátorů a
        validátorů, kterých bude použito pro ověření a zajištění integrity
        načítaných pluginů.
        """

        loader_module.PluginLoader.__init__(self, dest_dir),

        self.add_all_identifiers(identifiers)
        self.add_all_validators(validators)

    @property
    def runtime_factories(
            self) -> "tuple[runtime_module.AbstractRuntimeFactory]":
        """Vlastnost vrací instance továrních tříd běhových prostředí,
        které byly načteny. Přesněji pak ty, které byly identifikovány a také
        validovány. Tyto instance jsou pak postoupeny v podobě ntice.
        """
        return tuple(map(lambda valid_plugin:
                         valid_plugin.runtime_factory, self.load()))

    def load(self) -> "tuple[RuntimeFactoryPlugin]":
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
            plugin = RuntimeFactoryPlugin(
                potential_plg_path, self, _ACCESS_FUN)
            if plugin.is_valid_plugin:
                valid_plugins.append(plugin)
            # TODO - log nevalidního pluginu
        return tuple(valid_plugins)


class RuntimeFactoryPlugin(plugin_module.Plugin):
    """Třída RuntimeFactoryPlugin je odpovědná za zpřístupnění dynamického
    načítání modulů v kontextu továren běhových prostředí.

    Instance této třídy rozšiřují funkcionalitu rodičovské třídy (tedy Plugin)
    a mají nad rámec i vlastnost pro získání dané tovární třídy.

    V rámci kontextového způsobu použití lze mluvit o třídě podle návrhového
    vzoru Služebník."""

    def __init__(self, abs_path: str,
                 plugin_loader: "RuntimeFactoryLoader",
                 access_point_fun: str):
        """Initor třídy odpovědný za iniciaci svého předka a za uložení
        všech potřebných hodnot.

        V parametrech přijímá absolutní cestu k modulu, který má být ověřen a
        z něhož má být čteno, dále referenci na PluginLoader, který tuto
        instanci tvoří (konkrétně instanci třídy RuntimeFactoryLoader), a také
        název přístupové funkce, která vrací instanci tovární třídy jednotky.
        """
        plugin_module.Plugin.__init__(self, abs_path, plugin_loader)

        self._access_point_function = access_point_fun

    @property
    def access_point_function(self) -> str:
        """Vlastnost vrací název funkce, kterou je třeba zavolat, aby byla
        navrácena instance tovární třídy běhového prostředí."""
        return self._access_point_function

    @property
    def runtime_factory(self) -> "runtime_module.AbstractRuntimeFactory":
        """Vlastnost vrací tovární třídu běhového prostředí.

        Funkce přitom ověřuje, zda-li má modul reprezentující daný plugin
        definovánu funkci daného názvu. Pokud tomu tak není, je vyhozena
        výjimka. To se stává typicky v situacích, kdy nejsou dostatečně
        definována pravidla pro validaci pluginů.
        """

        # Přístupová funkce musí být obsažena v daném modulu. Není-li tomu
        # tak, je vyhozena příslušná výjimka.
        if not self.has_function(self.access_point_function):
            raise plugin_module.PluginError(
                f"Plugin nemá přístupovou funkci názvu "
                f"'{self.access_point_function}'", self)

        # Vrácení výstupu volání přístupové funkce
        return self.get_function(self._access_point_function)()

