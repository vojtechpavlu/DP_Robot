"""Modul obsahuje definici událostí, které vznikají za životního cyklu
běhových prostředí. Tyto jsou typicky dále postupovány jednotlivým evaluačním
funkcím s cílem ověřit splnění nějakého předdefinovaného úkolu."""


# Import standardních knihoven
from dataclasses import dataclass

# Import lokálních knihoven
import src.fw.target.event_handling as event_module
import src.fw.platform.runtime as runtime_module


@dataclass(frozen=True)
class RuntimeEvent(event_module.Event):
    """Tato datová třída reprezentuje událost v souvislosti s běhovým
    prostředím.

    Slouží jako společný předek. Sama stanovuje protokol pro své potomky,
    kde se očekává běhové prostředí."""
    runtime: "runtime_module.AbstractRuntime"


@dataclass(frozen=True)
class RuntimePreparedEvent(RuntimeEvent):
    """Tato datová třída reprezentuje událost úspěšného připravení běhového
    prostředí."""
    runtime: "runtime_module.AbstractRuntime"


@dataclass(frozen=True)
class RuntimeStartedEvent(RuntimeEvent):
    """Tato datová třída reprezentuje událost započetí běhového prostředí."""
    runtime: "runtime_module.AbstractRuntime"



