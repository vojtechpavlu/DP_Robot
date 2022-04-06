"""Modul obsahuje definici událostí, které vznikají za životního cyklu
běhových prostředí. Tyto jsou typicky dále postupovány jednotlivým evaluačním
funkcím s cílem ověřit splnění nějakého předdefinovaného úkolu."""


# Import standardních knihoven
from dataclasses import dataclass

# Import lokálních knihoven
import src.fw.target.event_handling as event_module
import src.fw.platform.runtime as runtime_module


@dataclass(frozen=True)
class RuntimeStarted(event_module.Event):
    """Tato datová třída reprezentuje událost započetí běhového prostředí."""
    runtime: "runtime_module.AbstractRuntime"



