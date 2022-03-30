""""""

# Import standardních knihoven
from abc import ABC, abstractmethod
from datetime import datetime

# Import lokálních knihoven
import src.fw.utils.timeworks as timeworks


class Log:
    """Instance třídy Log mají za cíl obalit důležité informace okolo logu.
    Jejich cílem je uchovat především zprávu, stejně jako uchovat časový
    bod, ve kterém zpráva vznikla, stejně jako její kontext."""

    def __init__(self, context: str, message: str):
        """Initor, který přijímá kontext a text zprávy. Kontext není
        case-sensitive; je převáděn na kapitálky.

        Kromě uložení těchto hodnot do proměnných je initor odpovědný za
        označení časového bodu, ve kterém instance vznikla."""

        self._timestamp = datetime.now()
        self._context = context.upper()
        self._message = message

    @property
    def context(self) -> str:
        """Vlastnost vrací kontext, ve kterém log vznikl."""
        return self._context

    @property
    def message(self) -> str:
        """Vlastnost vrací zprávu, která je hlavní náplní samotného logu."""
        return self._message

    @property
    def timestamp(self) -> datetime:
        """Vlastnost vrací instanci typu 'datetime', která reprezentuje časový
        bod, kdy vznikl daný log."""
        return self._timestamp

    @property
    def time(self) -> str:
        """Vlastnost vrací textovou reprezentaci časového bodu (konkrétně jeho
        časové podmnožiny), kdy log vznikl.

        Výsledný řetězec odpovídá plnému formátu, tedy 'HH:MM:SS.ffffff'."""
        return timeworks.time(self.timestamp, True)

    @property
    def date(self) -> str:
        """Vlastnost vrací textovou reprezentaci časového bodu (konkrétně jeho
        datumové podmnožiny), kdy log vznikl.

        Výsledný řetězec odpovídá defaultnímu formátu, tedy 'DD-MM-YY'."""
        return timeworks.date(self.timestamp)


class Logger:
    """"""

    def __init__(self):
        self._outputs = []

    @property
    def outputs(self) -> "tuple":
        return tuple(self._outputs)

    def log(self, context: str, message: str):
        """"""

