"""Tento modul obsahuje základní proměnné prostředí. Jejich význam spočívá
v poskytnutí možnosti nastavení některých klíčových parametrů."""


# *************************************************************************** #
# --------------------- Stanovení proměnného prostředí ---------------------- #
# --------------------------------------------------------------------------- #

"""Proměnná stanovující právě spouštěné zadání. To je definováno názvem
adresáře, který má být prohledán co do definice zadání a jednotlivých 
definic programů pro roboty, které mají být v rámci tohoto zadání otestovány.

Podoba tohoto zadání odpovídá relativní cestě (od kořene projektu):

/src/plugins/assignments/[název_adresáře]

přičemž se zde stanovuje pouze název adresáře.
"""
_ASSIGNMENT: str = "playground"


"""Proměnná stanovující dobu, po kterou má trvat krok jedné interakce.
Pomocí tohoto drobného čekání je možné zajistit simulaci pohybu robota.
Tato doba je v sekundách, jejichž počet je stanoven hodnotou typu float."""
_SLEEP_TIME: float = 0.1


"""Proměnná stanovuje, zda-li má či nemá být vybudován HTML výstup."""
_BUILD_HTML_OUTPUT: bool = True


"""Proměnná stanovuje, zda-li má či nemá být vybudován výstup do konzole."""
_BUILD_CONSOLE_OUTPUT: bool = False

"""Proměnná stanovuje, zda-li má či nemá být při testování spuštěno grafické
rozhraní."""
_OPEN_UI: bool = True


# *************************************************************************** #
# ---------------------------- Přístupové funkce ---------------------------- #
# --------------------------------------------------------------------------- #

def assignment() -> str:
    """Funkce vrací název zadání, které má být otestováno co do splnění."""
    return _ASSIGNMENT


def sleep_time() -> float:
    """Funkce vracející dobu, po kterou má trvat jedna interakce robota
    se světem."""
    return _SLEEP_TIME


def unit_factory_loaders() -> tuple:
    """Funkce vrací všechny loadery továren jednotek, které mají být použity
    pro získávání jednotek robotů. Tyto jsou vráceny v podobě ntice."""

    # Lokální import pro zpřehlednění celého modulu
    from src.fw.utils.loading.unit_factory_loader import (
        DefaultUnitFactoryLoader)

    # Funkce vrací ntici všech loaderů továren jednotek
    return (

        # Výchozí loader továren jednotek
        DefaultUnitFactoryLoader(),
    )


def program_loaders() -> tuple:
    """Funkce vrací všechny loadery programů, které mají být použity pro
    dynamické načítání programů, tedy studentských řešení."""

    # Lokální import pro zpřehlednění celého modulu
    from src.fw.utils.loading.program_loader import (
        DefaultFunBasedProgramLoader)

    # Funkce vrací ntici všech loaderů programů
    return (

        # Výchozí loader programů definovaných funkcí 'run'
        DefaultFunBasedProgramLoader(assignment()),
    )


def runtime_factory_loaders():
    """Funkce vrací všechny loadery továren běhových prostředí, které mají
    být použity pro budování izolovaných běhových prostředí pro testování
    studentských úloh."""

    # Lokální import pro zpřehlednění celého modulu
    from src.fw.utils.loading.runtime_factory_loader import (
        DefaultRuntimeFactoryLoader)

    # Funkce vrací výchozí loader továren běhových prostředí
    return DefaultRuntimeFactoryLoader(assignment())


def start_gui() -> bool:
    """Funkce vrací informaci o tom, zda-li má být spuštěno grafické rozhraní
    či nikoliv."""
    return _OPEN_UI


# *************************************************************************** #
# ------------------------- Pomocné řídící funkce --------------------------- #
# --------------------------------------------------------------------------- #


def build_outputs(platform):
    """Funkce odpovědná za vybudování výstupů dle dodané konfigurace."""
    _build_console_output(platform)
    _build_html_output(platform)


def _build_console_output(platform):
    """Funkce odpovědná za vybudování výstupu do konzole."""

    # Lokální import pro zpřehlednění celého modulu
    from src.fw.target.results.console_results import (
        RuntimeResultPrinter, PlatformResultPrinter)

    if _BUILD_CONSOLE_OUTPUT:
        PlatformResultPrinter(platform).build()
        for runtime in platform.all_runtimes:
            RuntimeResultPrinter(runtime).build()


def _build_html_output(platform):
    """Funkce odpovědná za vybudování HTML výstupu."""

    # Lokální import pro zpřehlednění celého modulu
    from src.fw.target.results.html_results import PlatformHTMLBuilder

    if _BUILD_HTML_OUTPUT:
        PlatformHTMLBuilder(platform).build()


