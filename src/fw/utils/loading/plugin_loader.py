"""Modul 'plugin_loader' sdružuje všechny obecné nástroje pro správu
dynamického načítání modulů s cílem upravovat funkcionalitu za běhu programu.
"""

# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Iterable

# Import lokálních knihoven
import src.fw.utils.loading.plugin_identifier as identifier
import src.fw.utils.loading.plugin_validator as validator
import src.fw.utils.loading.plugin as pl
import src.fw.utils.error as error
from ..filesystem import exists, is_directory, deep_list_files


class PluginLoader(ABC):
    """Abstrakatní třída PluginLoader definuje obecný protokol pro práci s
    pluginy (instancemi třídy Plugin), tedy pro dynamické načítání zdrojových
    souborů.
    """

    def __init__(self, destination: str):
        """Initor třídy, který přijímá v parametru absolutní cestu k
        adresáři, který obsahuje moduly, jenž reprezentují dané pluginy.

        Pokud tato cesta neexistuje nebo není adresářem, je vyhozena výjimka.
        Dále jsou instance odpovědné za uložení všech identifikátorů a
        validátorů pluginů. Ty jsou v úvodní fázi prázdné a dodávají se až
        dynamicky.
        """
        self._destination: str = destination

        """Kontrola, že dodaná cesta, která bude co do potenciálních pluginů 
        prohledávána, skutečně odkazuje na existující adresář."""
        if not (exists(destination) and is_directory(destination)):
            raise PluginLoaderError(
                f"Dodaná cesta neukazuje na existující adresář: {destination}",
                self)

        """Příprava seznamů pro identifikátory a validátory pluginů; v úvodní
        fázi jsou tyto seznamy prázdné a lze je dodat dynamicky."""
        self._plugin_identifiers: "list[identifier.PluginIdentifier]" = []
        self._plugin_validators: "list[validator.PluginValidator]" = []

    @property
    def destination(self) -> str:
        """Vlastnost vrací absolutní cestu k adresáři, který má být prohledán.
        """
        return self._destination

    @property
    def identifiers(self) -> "tuple[identifier.PluginIdentifier]":
        """Vlastnost vrací ntici identifikátorů, které budou použity pro
        úvodní vyfiltrování potenciálních pluginů.
        Tyto obvykle pracují jen na úrovni obecných popisných znaků; typicky
        zkoumají pouze název souboru, zda odpovídá definovaným konvencím.
        """
        return tuple(self._plugin_identifiers)

    @property
    def validators(self) -> "tuple[validator.PluginValidator]":
        """Vlastnost vrací ntici validátorů, kterých bude použito pro ověření,
        že potenciální plugin je skutečným validním pluginem.
        Tyto obvykle pracují na úrovni přečtení modulu co do vnitřního kódu;
        typicky je-li syntakticky validní, zda obsahuje předepsané atributy
        a funkce a zda návratové hodnoty daných funkcí odpovídají předepsaným
        požadavkům.
        """
        return tuple(self._plugin_validators)

    @property
    def potential_plugins(self) -> "tuple[str]":
        """Vlastnost obaluje funkci, která má za cíl vytipovat ty moduly,
        které jsou potenciálními pluginy, resp. soubory odpovídající pravidlům
        definovaným identifikátory pluginů.
        Proces je proveden tak, že je hloubkově prozkoumán dodaný adresář
        (viz proměnná 'destination') a z něj jsou všechny soubory podrobeny
        zkoušce, zda jsou potenciálními pluginy.
        """
        potential_plugins = []
        for file in deep_list_files(self.destination, False):
            if self.is_potential_plugin(file):
                potential_plugins.append(file)
        return tuple(potential_plugins)

    @property
    def valid_plugins(self) -> "tuple[pl.Plugin]":
        """Vlastnost se pokusí vyextrahovat ty pluginy, které jsou nejen
        identifikovány, ale které jsou validní.
        Nejsou-li žádné identifikované, je vyhozena výjimka.
        K tomu využívá abstraktní funkce 'load()' obstarávající identifikaci
        potenciálních pluginů a vytvoření instancí potomků třídy Plugin.
        """
        return tuple(filter(lambda plg: plg.is_valid_plugin, self.load()))

    def add_identifier(self, plugin_ident: "identifier.PluginIdentifier"):
        """Funkce přidává identifikátor pluginů, který bude použit pro
        vytipování potenciálních pluginů."""
        self._plugin_identifiers.append(plugin_ident)

    def add_all_identifiers(self, plugin_idents:
                            "Iterable[identifier.PluginIdentifier]"):
        """Funkce přidá všechny dodané identifikátory."""
        for i in plugin_idents:
            self.add_identifier(i)

    def add_validator(self, plugin_validator: "validator.PluginValidator"):
        """Funkce přidává validátor pluginů, který bude použit pro ověření
        správnosti a použitelnosti pluginu v daném kontextu."""
        self._plugin_validators.append(plugin_validator)

    def add_all_validators(self, plugin_validators:
                           "Iterable[validator.PluginValidator]"):
        """Funkce přidá všechny dodané identifikátory."""
        for v in plugin_validators:
            self.add_validator(v)

    def violated_identifiers(
            self, abs_path: str) -> "tuple[identifier.PluginIdentifier]":
        """Funkce vrací ntici všech identifikátorů, které prohlašují dodaný
        soubor za neplatný.
        """
        return tuple(filter(
            lambda ident: not ident.is_plugin(abs_path), self.identifiers))
    
    def is_potential_plugin(self, abs_path: str) -> bool:
        """Funkce vrací, zda-li je na dodané cestě potenciální plugin. To je
        zjištěno tak, že se zjistí počet porušených pravidel, tedy je-li počet
        identifikátorů, které soubor na dodané cestě prohlásily za neplatný
        roven nule, pak je dodaný soubor potenciálním pluginem.
        """
        return len(self.violated_identifiers(abs_path)) == 0

    @abstractmethod
    def load(self) -> "tuple[pl.Plugin]":
        """Abstraktní funkce load je odpovědná za načtení všech potenciálních
        pluginů a jejich vrácení. Výstupem funkce je tedy ntice všech pluginů,
        obalujících modul k importování, které dle definovaných pravidel v
        rámci množiny identifikátorů se zdají být platnými pluginy."""


class PluginLoaderError(error.PlatformError):
    """Třída definuje výjimku, která značí vznik chyby v kontextu načítání
    pluginů."""
    def __init__(self, message: str, plugin_loader: PluginLoader):
        error.PlatformError.__init__(self, message)
        self._plugin_loader = plugin_loader
        
    @property
    def plugin_loader(self) -> PluginLoader:
        """Vlastnost vrací PluginLoader, v jehož kontextu došlo k chybě."""
        return self._plugin_loader
