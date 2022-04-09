"""Tento modul sdružuje všechny prostředky pro výstupní logování. Především
definuje obecný protokol pro všechny výstupní loggery, konkrétně třídu
'LoggingOutput'.
"""


# Import standardních knihoven
from abc import ABC, abstractmethod
from textwrap import fill
import sys

# Import lokálních knihoven
import src.fw.utils.logging.logger as logger_module


class LoggingOutput(ABC):
    """Abstraktní třída LoggingOutput stanovuje obecný a závazný protokol pro
    všechny své potomky, tedy výstupy loggerů. Především stanovuje nakládání
    se správou kontextů logů, stejně jako funkci pro zalogování; tedy pověření
    k výstupu."""

    def __init__(self, take_all: bool = False):
        """Initor třídy, který je odpovědný za připravení evidence kontextů
        logů. Ta je v úvodní fázi pochopitelně prázdná a doplňuje se až během
        životního cyklu instance.

        Initor dále přijímá boolean značku 'take_all', která značí, zda-li
        má tato instance přijímat všechny kontexty, nehledě na obsah. Pokud
        bude tato defaultní hodnota překlopena na True, bude tento výstupní
        zpracovatel přijímat všechny kontexty.
        """
        self._contexts: "list[str]" = []
        self._takes_all = take_all

    @property
    def contexts(self) -> "tuple[str]":
        """Vlastnost vrací všechny evidované kontexty."""
        return tuple(self._contexts)

    @property
    def takes_all(self) -> bool:
        """Vlastnost vrací, zda-li tento výstupní zpracovatel logů přijímá
        všechny kontexty."""
        return self._takes_all

    def has_context(self, context_name: str) -> bool:
        """Funkce vrací, zda-li má tento výstupní logger daný kontext evidován.
        Pokud ano, vrací True, pokud ne, vrací False.

        Funkce není case-sensitive, tedy vstupní názvy kontextů jsou převedeny
        na kapitálky a prověřovány co do incidence v evidenci kontextů.

        Pokud je tato instance nastavena jako 'takes_all' (byl-li jí v initoru
        nastaven tento flag na hodnotu True), přijímá pak všechny kontexty
        a tedy vždy vrací hodnotu True."""
        return self.takes_all or (context_name.upper() in self.contexts)

    def is_responsible_for(self, log: "logger_module.Log") -> bool:
        """Funkce vrací, zda-li je tato instance odpovědná za zpracování
        daného logu. Pokud je jeho kontext v evidenci kontextů této instance,
        pak je vrácena hodnota True, jinak False.

        Pokud je tato instance nastavena jako 'takes_all' (byl-li jí v initoru
        nastaven tento flag na hodnotu True), přijímá pak všechny kontexty
        a tedy vždy vrací hodnotu True.
        """
        return self.takes_all or self.has_context(log.context)

    def add_context(self, context_name: str):
        """Funkce je odpovědná za přidání nového kontextu do evidence.
        Pokud již jednou evidován je, již znovu přidáván není.

        Kontext je definován jako textový řetězec, tedy název. Tento název
        je převáděn na kapitálky.
        """
        if context_name.upper() not in self.contexts:
            self._contexts.append(context_name.upper())

    @abstractmethod
    def log(self, log: "logger_module.Log"):
        """Abstraktní funkce definující protokol pomocí předepsání signatury
        funkce. Implementace této funkce jsou odpovědné za vytvoření
        příslušného výstupu dle pravidel dané třídy.

        Funkce přijímá referenci na log, který by měl být zpracován."""


class OutputWithMemo(LoggingOutput):
    """Abstraktní třída OutputWithMemo má za cíl definovat obecný protokol
    pro všechny své potomky, tedy výstupní zpracovatelé logů, které jsou si
    schopny zapamatovat (a udržet v paměti) dodané logy."""

    def __init__(self, take_all: bool = False):
        """Initor třídy, který postupuje dodanou informaci o univerzálním
        kontextu svému předkovi.

        Dále si připravuje evidenční seznam všech záznamů, které jsou této
        instanci postoupeny k zaznamenání. V úvodní fázi je tento seznam
        prázdný."""

        # Volání předka
        LoggingOutput.__init__(self, take_all)

        # Evidenční seznam pro uchování logů
        self._logs: "list[logger_module.Log]" = []

    @property
    def remember(self) -> "tuple[logger_module.Log]":
        """Vlastnost vrací všechny logy, které byly zapamatovány. Tyto vrací
        v podobě ntice."""
        return tuple(self._logs)

    def save_log(self, log: "logger_module.Log"):
        """Funkce odpovědná za uložení logu do evidence. Je přitom ověřována
        příslušnost. Pokud tato instance není odpovědná za zpracovávání logů
        tohoto kontextu, log přidán není."""
        if self.is_responsible_for(log):
            self._logs.append(log)

    def filter_by_context(self, context: str) -> "tuple[logger_module.Log]":
        """Funkce, která poskytuje funkcionalitu filtrování podle dodaného
        kontextu. Název tohoto kontextu není case-sensitive; převádí se
        defaultně na kapitálky."""
        return tuple(filter(lambda log: log.context == context.upper(),
                            self.remember))

    def flush(self) -> "tuple[logger_module.Log]":
        """Funkce, která se postará o vyčištění evidence logů. Všechny doposud
        zapamatované jsou však vráceny v podobě ntice."""
        logs = self.remember
        self._logs: "list[logger_module.Log]" = []
        return logs


class PrintingOutput(LoggingOutput):
    """Třída PrintingOutput je odpovědná za vypisování logů na konzoli."""

    def __init__(self, take_all: bool = True):
        """Initor, který přijímá informaci o tom, zda-li přijímat všechny
        kontexty či nikoliv.

        Pokud je nastavena tato defaultní hodnota na False, je třeba všechny
        výstupní kontexty přidat do evidence posteriorně."""
        LoggingOutput.__init__(self, take_all)

    def log(self, log: "logger_module.Log"):
        """Funkce implementující protokol definovaný v předkovi. Funkce se
        pouze stará o výpis v daném formátu."""

        prefix = f"[{log.time}][{log.context.ljust(8)}]: "
        message = fill(log.message, width=100, initial_indent=prefix,
                       subsequent_indent=len(prefix)*" ")

        sys.stdout.write(f"{message}\n")


class SimpleOutputWithMemo(OutputWithMemo):
    """Elementární funkce umožňující zaznamenávat jednotlivé logy ve své
    evidenci. Kromě jejich ukládání se nestará o nic jiného."""

    def __init__(self, take_all: bool = False):
        """Initor, který pouze postupuje informaci o univerzálním přijímání
        záznamů do evidence."""
        OutputWithMemo.__init__(self, take_all)

    def log(self, log: "logger_module.Log"):
        """Funkce, která implementuje protokol prapředka (LoggingOutput) a
        stará se pouze o zaznamenání daného logu do evidence."""
        self.save_log(log)




