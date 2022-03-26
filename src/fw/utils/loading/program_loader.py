"""Modul obsahuje prostředky pro dynamické načítání programů.

Hlavními dvěma klíčovými nástroji jsou třídy:

    - 'PluginLoader', která je odpovědná za řízení načítání a poskytování
      načtených programů

    - 'ProgramPlugin', která rozšiřuje implementaci obecného pluginu o
      schopnost poskytnutí programu, jehož definice je ukryta v modulu
      reprezentujícím daný plugin.
"""

# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.utils.loading.plugin_loader as loader_module
import src.fw.utils.loading.plugin_identifier as pl_identifier
import src.fw.utils.loading.plugin_validator as pl_validator
import src.fw.utils.loading.plugin as plugin_module
import src.fw.robot.program as program_module

"""Název funkce, která bude volána coby klíčový přístupový bod pro obdržení
instance programu robota"""
_ACCESS_FUN = "get_program"


class ProgramLoader(loader_module.PluginLoader):
    """Instance třídy ProgramLoader jsou odpovědné za dynamické načítání
    pluginů obsahujících definici programů.

    Třída poskytuje dynamickou správu načítání pluginů v kontextu získávání
    referencí na objekty reprezentující programy. Oproti abstraktnímu předkovi
    ('PluginLoader') je tato obohacena ještě o implementaci funkce 'load()',
    která vyfiltruje všechny nevalidní pluginy a vrátí množinu pluginů třídy
    ProgramPlugin."""

    def __init__(self, dest_dir: str,
                 identifiers: "Iterable[pl_identifier.PluginIdentifier]",
                 validators: "Iterable[pl_validator.PluginValidator]"):
        """Initor třídy odpovědný za inicializaci předka a uložení všech
        identifikátorů a validátorů pluginů.

        V parametru přijímá absolutní cestu k adresáři, který má být prohledán
        za účelem získání všech pluginů v kontextu dynamického importu
        programů.

        Vedle toho přijímá také množinu identifikátorů, dle kterých budou
        vytipovávány všechny potenciální pluginy, a množinu validátorů, které
        zase stanovují rámec pravidel, která musí všechny pluginy splňovat.
        """
        # Iniciace předka
        loader_module.PluginLoader.__init__(self, dest_dir)

        # Přidání všech dodaných identifikátorů a validátorů
        self.add_all_identifiers(identifiers)
        self.add_all_validators(validators)

    @property
    def programs(self) -> "tuple[program_module.AbstractProgram]":
        """Vlastnost vrací programy ze všech dynamicky importovaných validních
        pluginů.

        Toho dosahuje tím, že pro každý načtený validní plugin
        (získaný voláním funkce 'load()') vybere instanci programu v něm
        obsažený. Tyto programy jsou sdruženy v podobě ntice.
        """
        return tuple(map(
            lambda valid_plugin: valid_plugin.program, self.load()))

    def load(self) -> "tuple[ProgramPlugin]":
        """Implementace abstraktní funkce předka, která načte všechny validní
        pluginy a vrátí je v sdružené do ntice.

        V první řadě si vytipuje pomocí identifikátorů všechny potenciální
        pluginy (vlastnost 'potential_plugins' implementovaná v předkovi) a
        pro každý vybuduje instanci třídy 'ProgramPlugin'. Pokud je tento
        stanoven podle všech validátorů za validní, je zařazen do výstupní
        množiny validních pluginů.
        """
        valid_plugins = []
        for potential_plg_path in self.potential_plugins:
            plugin = ProgramPlugin(potential_plg_path, self, _ACCESS_FUN)
            if plugin.is_valid_plugin:
                valid_plugins.append(plugin)
            # TODO - log nevalidního pluginu
        return tuple(valid_plugins)


class ProgramPlugin(plugin_module.Plugin):
    """Instance třídy ProgramPlugin sdružují funkcionalitu pro získávání
    referencí na programy získané z dynamického načítání pluginů.

    Tato implementace rozšiřující rodičovskou třídu Plugin se striktně
    zaměřuje právě na potomky třídy 'AbstractProgram' a tyto také umožňuje
    z validních pluginů vracet.
    """

    def __init__(self, abs_path: str,
                 plugin_loader: "ProgramLoader",
                 access_point_fun: str):
        """Initor třídy, který je odpovědný za přípravu celé instance.

        Konkrétně přijímá absolutní cestu k souboru modulu, kterým je de facto
        definován plugin, dále referenci na loader (konkrétně instanci třídy
        ProgramLoader), který je odpovědný za vytvoření této instance, a
        název přístupové funkce, která má být zavolána pro získání instance
        programu.
        """
        # Volání předka
        plugin_module.Plugin.__init__(self, abs_path, plugin_loader)

        # Přístupová funkce, která vrací referenci na instanci programu
        self._access_point_function = access_point_fun

    @property
    def access_point_function(self) -> str:
        """Název funkce, která má být zavolána, aby byla vrácena instance
        programu."""
        return self._access_point_function

    @property
    def program(self) -> "program_module.AbstractProgram":
        """Vlastnost vrací referenci na program, jehož definice je obsažena
        v dynamicky načítaném modulu.

        Funkce v první řadě ověří, zda existuje v daném modulu funkce toho
        názvu. Pokud tomu tak není, je vyhozena výjimka. Typicky tato
        poukazuje na nedostatečnou validaci pluginu.

        Jinak se pokusí zavolat bezparametrickou funkci tohoto názvu a její
        návratovou hodnotu vrátit.
        """
        if not self.has_function(self.access_point_function):
            raise plugin_module.PluginError(
                f"Plugin nemá přístupovou funkci názvu "
                f"'{self.access_point_function}'", self)
        return self.get_function(self._access_point_function)()




