""""""


# Import standardních knihoven

# Import lokálních knihoven
import src.fw.utils.loading.plugin_loader as loader_module
import src.fw.utils.loading.plugin_identifier as pl_identifier
import src.fw.utils.loading.plugin_validator as pl_validator
import src.fw.utils.loading.plugin as plugin_module
import src.fw.robot.unit as unit_module


"""Název funkce, která bude volána coby klíčový přístupový bod pro obdržení
instance továrny jednotek"""
_ACCESS_FUN = "get_unit_factory"


class UnitFactoryLoader(loader_module.PluginLoader):
    """Loader továren jednotek UnitFactoryLoader je odpovědný za dynamické
    načítání pluginů obsahujících definici továrních tříd jednotek.

    Třída poskytuje dynamickou správu načítání pluginů v kontextu získávání
    továrních jednotek. Oproti abstraktnímu předkovi ('PluginLoader') je tato
    obohacena ještě o implementaci funkce 'load()', která vyfiltruje všechny
    nevalidní pluginy a vrátí množinu pluginů třídy UnitFactoryPlugin."""

    def __init__(self, dest_dir: str,
                 identifiers: "tuple[pl_identifier.PluginIdentifier]",
                 validators: "tuple[pl_validator.PluginValidator]"):
        """Initor třídy odpovědný za inicializaci předka a uložení
        všech identifikátorů a validátorů pluginů."""

        # Volání initoru předka
        loader_module.PluginLoader.__init__(self, dest_dir)

        # Přidání všech dodaných identifikátorů a validátorů
        self.add_all_identifiers(identifiers)
        self.add_all_validators(validators)

    def load(self) -> "tuple[UnitFactoryPlugin]":
        """Funkce se stará o načtení všech validních pluginů a ty dále vrací
        uspořádané v ntici.

        V první řadě si vytipuje potenciální pluginy (tedy ty soubory, které
        se zdají býti dle pravidel identifikace jako zdrojové soubory v rámci
        daného kontextu) a ty dále ověřuje, zda-li jsou platné.

        Vrací pak vrací pouze ty, které projdou testem validity, tedy všemi
        validačními procedurami definovanými instancemi třídy PluginValidator.
        """
        valid_plugins = []

        # Pro všechny identifikované (a tedy potenciální) pluginy
        for potential_plg_path in self.potential_plugins:
            plugin = UnitFactoryPlugin(potential_plg_path, self, _ACCESS_FUN)
            if plugin.is_valid_plugin:
                valid_plugins.append(plugin)
            # TODO - log nevalidního pluginu
        return tuple(valid_plugins)

    def load_unit_factories(self) -> "tuple[unit_module.AbstractUnitFactory]":
        """Funkce obsluhuje načítání všech továrních tříd jednotek tak.
        Tyto načtené továrny pak vrací v podobě ntice."""
        return tuple(map(lambda valid_plugin:
                         valid_plugin.unit_factory, self.load()))


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
        instanci tvoří, a také název přístupové funkce, která vrací instanci
        tovární třídy jednotky.
        """
        plugin_module.Plugin.__init__(self, abs_path, plugin_loader)

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