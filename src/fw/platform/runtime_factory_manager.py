"""Modul je odpovědný za správu načítání a poskytování továren běhových
prostředí.

Především zde definuje třídu RuntimeFactoryManager, která je odpovědná za
řízení načtení instancí továrních tříd běhových prostředí a jejich
poskytování."""


# Import standardních knihoven
from typing import Iterable

# Import lokálních knihoven
import src.fw.platform.runtime as runtime_module
import src.fw.utils.loading.runtime_factory_loader as loader_module
from src.fw.utils.error import PlatformError


class RuntimeFactoryManager:
    """Instance této třídy se starají o obalení funkcionality loaderu
    továrních tříd běhových prostředí (RuntimeFactoryLoader) a její zařazení
    do kontextu."""

    def __init__(self, rf_loader: "loader_module.RuntimeFactoryLoader"):
        """Initor funkce, který přijímá loader, který bude použit pro
        dynamické načítání instancí továrních tříd běhových prostředí.

        Vedle toho si připravuje seznam pro registraci takových továren,
        který je v úvodní fázi pochopitelně prázdný."""

        # Loader, který bude použit pro dynamické načítání
        self._loader = rf_loader

        # Evidence registrovaných továren běhových prostředí, v úvodu
        # pochopitelně prázdná
        self._registered: "list[runtime_module.AbstractRuntimeFactory]" = []

    @property
    def loader(self) -> "loader_module.RuntimeFactoryLoader":
        """Vlastnost vrací loader, který je použit pro dynamické načítání
        instancí továrních tříd běhových prostředí."""
        return self._loader

    @property
    def registered_factories(
            self) -> "tuple[runtime_module.AbstractRuntimeFactory]":
        """Vlastnost vrací ntici všech registrovaných instancí továren
        běhových prostředí.
        """
        return tuple(self._registered)

    @property
    def num_of_registered(self) -> int:
        """Vlastnost vrací počet registrovaných továren běhových prostředí v
        evidenci.
        """
        return len(self.registered_factories)

    def register(self, rt_factory: "runtime_module.AbstractRuntimeFactory"):
        """Funkce se pokusí zaregistrovat dodanou továrnu běhových prostředí.
        Pokud již jednou v evidenci tato instance vedena je, není přidána
        znovu.
        """
        if rt_factory not in self.registered_factories:
            self._registered.append(rt_factory)
        # TODO - LOG již evidované továrny běhových prostředí

    def load(self):
        """Funkce se pokusí zaregistrovat všechny továrny běhových prostředí.

        V prvním kroku tato funkce čistí svoji evidenci továren. Poté se
        pokusí přidat všechny továrny načtené z loaderu.

        Pokud nebyla načtena jediná továrna běhových prostředí, je vyhozena
        výjimka.
        """
        self._registered: "list[runtime_module.AbstractRuntimeFactory]" = []

        for runtime_factory in self.loader.runtime_factories:
            self.register(runtime_factory)

        if self.num_of_registered == 0:
            # TODO - specifikace výjimky
            raise Exception(
                "Nebyla načtena jediná továrna běhových prostředí.")


class RuntimeFactoryManagerError(PlatformError):
    """Výjimky tohoto typu rozšiřují svého předka o referenci na správce
    továren běhových prostředí. Cílem této třídy je symbolizace chyby, která
    vznikla, a její reprezentace v systému."""

    def __init__(self, message: str, rfm: "RuntimeFactoryManager"):
        """Initor třídy, který postupuje textovou zprávu o chybě svému
        předkovi a ukládá referenci na instanci správce, v jehož kontextu
        došlo k chybě.
        """

        # Volání předka
        PlatformError.__init__(self, message)

        # Uložení správce, v jehož kontextu došlo k chybě
        self._rfm = rfm

    @property
    def runtime_factory_manager(self) -> "RuntimeFactoryManager":
        """Vlastnost vrací správce továren běhových prostředí, v jehož
        kontextu došlo k chybě."""
        return self._rfm

