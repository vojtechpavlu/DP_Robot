""""""

# Import standardních knihoven
from abc import ABC, abstractmethod
from datetime import datetime

# Import lokálních knihoven
import src.fw.utils.timeworks as timeworks
import src.fw.utils.logging.logging_output as output_module


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
    """Třída Logger je odpovědná za definici loggeru, který bude schopen
    přijímat zprávy z různých kontextů a s řídit jejich výstupní zpracování.

    K tomu, aby tyto zprávy mohl zpracovat pro výstup, je definována třída
    jako kontejner evidovaných výstupních loggovacích zpracovatelů."""

    def __init__(self):
        """Initor třídy, který je odpovědný za iniciaci evidence výstupních
        loggovacích zpracovatelů. Tato evidence je v úvodu prázdná."""
        self._outputs: "list[output_module.LoggingOutput]" = []

    @property
    def outputs(self) -> "tuple[output_module.LoggingOutput]":
        """Vlastnost vrací množinu všech výstupních logovacích zpracovatelů
        v podobě ntice."""
        return tuple(self._outputs)

    def add_output(self, output: "output_module.LoggingOutput"):
        """Funkce přidá nového výstupního logovacího zpracovatele do evidence.
        """
        self._outputs.append(output)

    def remove_output(self, output: "output_module.LoggingOutput"):
        """Funkce odstraňuje dodaného výstupního logovacího zpracovatele z
        evidence."""
        self._outputs.remove(output)

    def clear(self) -> "tuple[output_module.LoggingOutput]":
        """Funkce odstraňuje všechny logovací výstupní zpracovatele z
        evidence. Množinu (konkrétně ntici) doposud evidovaných však vrací.
        """
        outputs = self.outputs
        self._outputs: "list[output_module.LoggingOutput]" = []
        return outputs

    def log(self, context: str, message: str):
        """Funkce se postará o zalogování dodané zprávy v daném kontextu.
        Funkce vytvoří instanci logu z dodaných vstupů a tuto pak předá všem
        výstupním zpracovatelům k vytvoření výstupu."""

        # Tvorba instance třídy Log
        log_instance = Log(context, message)

        # Pro každý výstup: je-li odpovědný za tento typ logu, zaloguj ho
        for output in self.outputs:
            if output.is_responsible_for(log_instance):
                output.log(log_instance)

