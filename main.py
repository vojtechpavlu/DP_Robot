# Import lokálních knihoven
from src.fw.platform.platform import Platform
from src.conf.configuration import *
from src.fw.gui.visualization import *


def build_platform():
    """Funkce je odpovědná za vybudování platformy s nastavenou konfigurací.
    Instance této platformy je dále vrácena k dalšímu použití."""

    return Platform(
        assignment_name=assignment(),
        unit_fact_loaders=unit_factory_loaders(),
        program_loaders=program_loaders(),
        runtime_loader=runtime_factory_loaders(),
        runtime_change_notification=update_runtime,)


def run_platform(platform: Platform, intro_sleep: float = 0):
    """Funkce je odpovědná za spuštění platformy. V první řadě se provede
    volitelné čekání na uvedení všech vláken do požadovaného stavu. Následně
    se spustí načítání všech potřebných zdrojů, na které navazuje samotné
    spuštění platformy."""

    # Lokální import pro zpřehlednění celého modulu
    import time

    # Mikročekání na připravení všech vláken do provozuschopného stavu
    time.sleep(intro_sleep)

    # Načtení všech potřebných zdrojů
    platform.load()

    # Spuštění platformy
    platform.run()

    # Po ukončení běhu platformy vypni okno
    window_close()


def start():
    """Funkce odpovědná za spuštění celého systému. Pokud má být spuštěn bez
    grafického rozhraní, bude platforma spuštěna v hlavním vlákně, jinak bude
    v hlavním vlákně spuštěno okno grafického rozhraní a platforma bude běžet
    v nově vytvořeném strašidlu."""

    """Vybudovaná platforma, která bude spuštěna"""
    platform = build_platform()

    """Pokud má být spuštěno grafické rozhraní, musí být platforma spuštěna
    v samostatném vlákně."""
    if start_gui():

        """Vlákno platformy je prohlášeno za strašidlo, aby bylo možné
        přerušit běh vypnutím okna GUI."""
        import threading

        p_thread = threading.Thread(target=run_platform, args=(platform, 0.5))
        p_thread.setDaemon(True)
        p_thread.start()

        """Spuštění grafického rozhraní"""
        build_graphical_interface(platform)

    else:
        """Spuštění platformy v hlavním vlákně"""
        run_platform(platform)

    """V obou případech vytvoř výstup"""
    build_outputs(platform)


if __name__ == "__main__":
    start()
