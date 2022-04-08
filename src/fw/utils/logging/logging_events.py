"""Modul obsahuje definici událostí, které mohou vzniknout v kontextu logování.
Především obsahuje definici datové třídy LogEvent, která obsahuje ten záznam,
který byl zaznamenán. Z toho lze zjistit kontext i samotnou zprávu, která byla
poslána."""


# Import standardních knihoven
from dataclasses import dataclass

# Import lokálních knihoven
import src.fw.target.event_handling as event_module
import src.fw.utils.logging.logger as logger_module


@dataclass(frozen=True)
class LogEvent(event_module.Event):
    """Datová třída reprezentující událost zaznamenání logu. Tato obsahuje
    jen referenci na log, který vznikl.

    Příklad použití:

        >>> LogEvent(log)
    """

    # Log, který má být ověřen co do jeho "úkolusplnění". Lze z něj zjistit
    # kontext, v jakém vznikl, stejně jako samotnou zprávu
    log: "logger_module.Log"



