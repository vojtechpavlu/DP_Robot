"""Modul sdružuje funkcionalitu ve vztahu k práci s časovou veličinou.

Základem je sdružení funkcí pro formátování času."""


# Import standardních knihoven
import datetime


"""Stanovení výchozích formátů datumů"""

# ISO formát datumů, tedy 'YYYY-MM-DD'
ISO_DATE_FORMAT = "%Y-%m-%d"

# Výchozí zkrácený formát datumu, odpovídající formátu 'DD.MM.YY'
DEFAULT_DATE_FORMAT_SHORT = "%d.%m.%y"

# Výchozí zkrácený formát datumu, odpovídající formátu 'DD-MM-YY'
DEFAULT_DATE_FORMAT_SHORT_DASHED = "%d-%m-%y"

# Výchozí formát datumu, odpovídající formátu 'DD.MM.YYYY'
DEFAULT_DATE_FORMAT = "%d.%m.%Y"

# Výchozí formát datumu, odpovídající formátu 'DD-MM-YYYY'
DEFAULT_DATE_FORMAT_DASHED = "%d-%m-%Y"


def time(timestamp: "datetime.datetime", include_ms: bool = True) -> str:
    """Funkce vrací textovou reprezentaci času z dodané instance časového
    bodu. Dále přijímá výchozí boolean hodnotu, která značí zařazení
    mikrosekund nebo ne. Defaultně jsou v řetězci zařazeny.

    Výsledek je typu str (textový řetězec) a odpovídá formátu:
    'HH:MM:SS.ffffff', resp. 'HH:MM:SS'.
    """
    return timestamp.strftime("%H:%M:%S.%f" if include_ms else "%H:%M:%S")


def date(timestamp: "datetime.datetime",
         date_format: str = DEFAULT_DATE_FORMAT_SHORT_DASHED) -> str:
    """Funkce starající se především o formátování datumů. Funkce přijímá
    instanci časového bodu, který převede dle stanoveného formátu do textové
    reprezentace.

    Datumový formát je defaultně nastaven; a to na podobu 'DD-MM-YY'.
    """
    return timestamp.strftime(date_format)

