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
from src.fw.utils.filesystem import assignment

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

    @property
    def not_valid_plugins(self) -> "tuple[ClassBasedProgramPlugin]":
        """Vlastnost implementuje protokol předka. Tato funkce vrací ntici
        všech pluginů, které sice prošly identifikací, ale nebyly validní.

        Této vlastnosti lze využít ke zpětnému odhalování, co s nebylo s
        těmito pluginy v pořádku."""
        invalid_plugins = []
        for path in self.potential_plugins:
            plugin = ClassBasedProgramPlugin(path, self, _ACCESS_FUN)
            if not plugin.is_valid_plugin:
                invalid_plugins.append(plugin)
        return tuple(invalid_plugins)

    def load(self) -> "tuple[ClassBasedProgramPlugin]":
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
            plugin = ClassBasedProgramPlugin(
                potential_plg_path, self, _ACCESS_FUN)
            if plugin.is_valid_plugin:
                valid_plugins.append(plugin)
        return tuple(valid_plugins)


class ClassBasedProgramPlugin(plugin_module.Plugin):
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


class FunctionBasedProgramPlugin(plugin_module.Plugin):
    """Instance třídy FunctionBasedProgramPlugin sdružují funkcionalitu pro
    získávání referencí na programy získané z dynamického načítání pluginů.
    """

    def __init__(self, abs_path: str, plugin_loader: "ProgramLoader",
                 run_fun_name: str, mount_fun_name: str, author_id_attr: str,
                 author_name_attr: str):
        """Initor třídy, který je odpovědný za přípravu celé instance.

        Konkrétně přijímá absolutní cestu k souboru modulu, kterým je de facto
        definován plugin, dále referenci na loader (konkrétně instanci třídy
        ProgramLoader), který je odpovědný za vytvoření této instance, a
        název přístupové funkce, která má být zavolána pro získání instance
        programu.
        """
        # Volání předka
        plugin_module.Plugin.__init__(self, abs_path, plugin_loader)

        # Uložení názvů sledovaných funkcí a atributů
        self._run_fun_name = run_fun_name
        self._mount_fun_name = mount_fun_name
        self._author_id_attr = author_id_attr
        self._author_name_attr = author_name_attr

    @property
    def program(self) -> "program_module.ProgramPrototype":
        """"""
        if not self.has_function(self._run_fun_name):
            raise plugin_module.PluginError(
                f"Plugin nemá požadovanou funkci definice programu "
                f"'{self._run_fun_name}'", self)

        run_fun = self.get_function(self._run_fun_name)
        mount_fun = None
        if self.has_function(self._mount_fun_name):
            mount_fun = self.get_function(self._mount_fun_name)
        author_id = str(self.get_attribute(self._author_id_attr))
        author_name = str(self.get_attribute(self._author_name_attr))

        return program_module.ProgramPrototype(
            author_id, author_name, self.absolute_path, run_fun, mount_fun)


class DefaultClassBasedProgramLoader(ProgramLoader):
    """Třída rozšiřuje svého předka nastavením defaultních hodnot. Tyto jsou
    specifikovány v horní části tohoto modulu.

    Konkrétně jsou instance vybaveny výchozí sadou doporučených identifikátorů
    a validátorů pluginů.

    Předpokladem je, že programy jsou uloženy v adresáři všech zadání.
    Výchozí cesta je tedy (relativně vůči kořeni projektu) následující:

    'src/plugins/assignments/[název zadání]'
    """

    """Výchozí identifikátory pluginů, které jsou používány pro vytipování
    pluginů v kontextu programů."""
    _DEFAULT_IDENTIFIERS = [

        # Zdrojové soubory musí mít koncovku '.py'
        pl_identifier.ExtensionPluginIdentifier(".py"),

        # Zdrojové soubory musí začínat řetězcem 'unit_'
        pl_identifier.PrefixPluginIdentifier("program_")
    ]

    """Výchozí validátory pluginů, které jsou používány pro ověření platnosti
    a správnosti pluginů v kontextu programů."""
    _DEFAULT_VALIDATORS = [

        # Modul musí být syntakticky validní
        pl_validator.SyntaxValidator(),

        # Modul musí být opatřen neprázdným dokumentačním komentářem
        pl_validator.ModuleDocstringExistenceValidator(),

        # Modul musí obsahovat funkci s definovaným názvem
        pl_validator.FunctionExistenceValidator(_ACCESS_FUN),

        # Modul musí obsahovat funkci vracející hodnotu konkrétního typu
        pl_validator.FunctionReturnValueTypeValidator(
            _ACCESS_FUN, program_module.AbstractProgram)
    ]

    def __init__(self, assignment_name: str):
        """Initor třídy, který přijímá název zadání, které je reprezentováno
        adresářem v rámci adresáře všech zadání.

        Předpokladem je, že všechny programy k otestování jsou v rámci tohoto
        adresáře."""
        ProgramLoader.__init__(
            self, assignment(assignment_name),
            DefaultClassBasedProgramLoader._DEFAULT_IDENTIFIERS,
            DefaultClassBasedProgramLoader._DEFAULT_VALIDATORS)


class DefaultFunBasedProgramLoader(ProgramLoader):
    """Výchozí loader programů, který je odpovědný za zpracování pluginů
    reprezentovaných modulem, ve kterém je samotný program definován jako
    funkce."""

    """Název funkce, která obsahuje definici samotného programu robota.
    Pokud tato funkce není v modulu obsažena, nemůže být toto řešení za 
    žádných okolností přijato."""
    _PROGRAM_FUNCTION_NAME = "run"

    """Název funkce, která obsahuje definici osazovací procedury. Tato
    funkce je volitelná."""
    _MOUNTING_FUNCTION_NAME = "mount"

    """Specifikace požadovaných personálií, které musí být studentem
    vyplněny pro jeho identifikaci. Pokud modul tyto neobsahuje, nesmí
    být připuštěn k testování."""
    _AUTHOR_ID = "AUTHOR_ID"
    _AUTHOR_NAME = "AUTHOR_NAME"

    """Výchozí identifikátory pluginů, které jsou používány pro vytipování
    pluginů v kontextu programů."""
    _DEFAULT_IDENTIFIERS = [

        # Zdrojové soubory musí mít koncovku '.py'
        pl_identifier.ExtensionPluginIdentifier(".py"),

        # Zdrojové soubory musí začínat řetězcem 'unit_'
        pl_identifier.PrefixPluginIdentifier("program_"),

        # Zdrojové soubory musí mít maximálně 100 kB
        pl_identifier.MaxFilesizePluginIdentifier(102400)
    ]

    """Výchozí validátory pluginů, které jsou používány pro ověření platnosti
    a správnosti pluginů v kontextu programů."""
    _DEFAULT_VALIDATORS = [

        # Modul musí být syntakticky validní
        pl_validator.SyntaxValidator(),

        # Modul musí být opatřen neprázdným dokumentačním komentářem
        pl_validator.ModuleDocstringExistenceValidator(),

        # Modul musí obsahovat funkci s definovaným názvem
        pl_validator.FunctionExistenceValidator(_PROGRAM_FUNCTION_NAME),

        # Modul musí obsahovat atribut reprezentující ID autora
        pl_validator.HasAttributePluginValidator(_AUTHOR_ID),

        # Modul musí obsahovat atribut reprezentující jméno autora
        pl_validator.HasAttributePluginValidator(_AUTHOR_NAME),

        # Modul musí obsahovat atribut s ID o délce alespoň 3 znaků
        pl_validator.CustomAttributePluginValidator(
            _AUTHOR_ID, lambda v: type(v) == str and len(v) > 3,
            "Author ID Validator",
            f"Kontrola, že má modul definováno ID autora pod atributem "
            f"'{_AUTHOR_ID}' v podobě textového řetězce a o délce alespoň "
            f"3 znaků."),

        # Modul musí obsahovat atribut se jménem autora
        pl_validator.CustomAttributePluginValidator(
            _AUTHOR_NAME, lambda v: type(v) == str and len(v) > 4,
            "Author Name Validator",
            f"Kontrola, že má modul definováno jméno autora v atributu "
            f"'{_AUTHOR_NAME}' o délce alespoň 4 znaků.")
    ]

    def __init__(self, assignment_name: str):
        """Initor, který přijímá název zadání a připravuje loader vybavený
        identifikátory a validátory pro zpracování pluginu programu s definicí
        programu ve funkci modulu."""

        ProgramLoader.__init__(
            self, assignment(assignment_name),
            DefaultFunBasedProgramLoader._DEFAULT_IDENTIFIERS,
            DefaultFunBasedProgramLoader._DEFAULT_VALIDATORS)

    @property
    def not_valid_plugins(self) -> "tuple[FunctionBasedProgramPlugin]":
        """Vlastnost implementuje protokol předka. Tato funkce vrací ntici
        všech pluginů, které sice prošly identifikací, ale nebyly validní.

        Této vlastnosti lze využít ke zpětnému odhalování, co s nebylo s
        těmito pluginy v pořádku.
        """
        invalid_plugins = []

        # Napříč všemi potenciálně validními pluginy
        for path in self.potential_plugins:

            # Vytvořit plugin
            plugin = FunctionBasedProgramPlugin(
                path, self, self._PROGRAM_FUNCTION_NAME,
                self._MOUNTING_FUNCTION_NAME, self._AUTHOR_ID,
                self._AUTHOR_NAME)

            # Pokud není validní
            if not plugin.is_valid_plugin:
                invalid_plugins.append(plugin)

        # Vrátit všechny nevalidní pluginy
        return tuple(invalid_plugins)

    def load(self) -> "tuple[FunctionBasedProgramPlugin]":
        """Implementace abstraktní funkce předka, která načte všechny validní
        pluginy a vrátí je v sdružené do ntice.

        V první řadě si vytipuje pomocí identifikátorů všechny potenciální
        pluginy (vlastnost 'potential_plugins' implementovaná v předkovi) a
        pro každý vybuduje instanci třídy 'ProgramPlugin'. Pokud je tento
        stanoven podle všech validátorů za validní, je zařazen do výstupní
        množiny validních pluginů.
        """
        valid_plugins = []

        # Napříč všemi identifikovanými pluginy
        for potential_plg_path in self.potential_plugins:

            # Vytvoření potenciálně validního pluginu
            plugin = FunctionBasedProgramPlugin(
                potential_plg_path, self, self._PROGRAM_FUNCTION_NAME,
                self._MOUNTING_FUNCTION_NAME, self._AUTHOR_ID,
                self._AUTHOR_NAME)

            # Ověření, že je plugin validní
            if plugin.is_valid_plugin:
                valid_plugins.append(plugin)

        # Vrácení validních pluginů
        return tuple(valid_plugins)




