"""Modul obsahuje definici obecných protokolů nástrojů pro přenos informace o
vzniku událostí a jejich zpracování.

Především jsou zde definovány třídy EventHandler a EventEmitter, které jsou
odpovědné za naslouchání a druhá za vytváření událostí a následnou notifikaci.

Realizace je podle návrhového vzoru Observer."""


# Import standardních knihoven
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


class EventHandler(ABC):
    """Abstraktní třída EventHandler je odpovědná za definici základního
    společného protokolu pro všechny své potomky, tedy posluchače událostí.

    Kromě abstraktní funkce 'update(EventEmitter)' tato definuje i funkci
    'unsubscribe(EventEmitter)', která slouží k odhlášení se, není-li již
    třeba naslouchat dalším událostem. Typicky je tato volána v návaznosti
    na reakci na událost v podobě zpracovávání kódu metody 'update'.
    """

    def unsubscribe(self, emitter: "EventEmitter"):
        """Funkce se pokusí odregistrovat tuto instanci z dodaného emitoru
        událostí.
        Pokud je u něj evidována, je z evidence emitoru odstraněna."""
        emitter.unregister_event_handler(self)

    @abstractmethod
    def update(self, emitter: "EventEmitter", event: "Event"):
        """Abstraktní funkce stanovující protokol pro zpracování událostí.
        Funkce přijímá referenci na emitor událostí, který je původcem,
        například pro potřeby odregistrování se u něj, nebude-li naslouchání
        dalším událostem již třeba.

        Dále funkce přijímá událost, která nastala a která je potenciálním
        nositelem důležité informace v souvislosti s touto událostí."""


class EventEmitter(ABC):
    """EventEmitter je abstraktní třída odpovědná za definici protokolu pro
    všechny třídy, které vytváří generují svým působením v nějakém smyslu
    zajímavé a odposlouchávatelné události.

    Instance této třídy jsou vybaveny funkcionalitou pro registraci posluchačů
    do evidence, o jejich mazání z evidence a především jejich upozorňování.
    """

    def __init__(self):
        """Initor třídy, který je odpovědný za připravení evidence posluchačů
        událostí, kteří budou v případě vzniku důležité události informováni.
        """
        self._event_handlers: "list[EventHandler]" = []

    @property
    def event_handlers(self) -> "tuple[EventHandler]":
        """Vlastnost, která vrací množinu všech registrovaných posluchačů
        událostí tohoto emitoru."""
        return tuple(self._event_handlers)

    def has_event_handler(self, handler: "EventHandler") -> bool:
        """Funkce vrací, zda-li má v evidenci uvedeného tohoto posluchače."""
        return handler in self.event_handlers

    def register_event_handler(self, handler: "EventHandler"):
        """Funkce odpovědná za registraci nových posluchačů událostí, kteří
        na tyto jsou odpovědni reagovat."""
        self._event_handlers.append(handler)

    def unregister_event_handler(self, handler: "EventHandler"):
        """Funkce je odpovědná za odregistrování dodaného posluchače ze
        své evidence."""
        if self.has_event_handler(handler):
            self._event_handlers.remove(handler)

    def notify_all_event_handlers(self, event: "Event"):
        """Funkce, která obvolá všechny své posluchače a upozorní je na vznik
        situace."""
        for handler in self._event_handlers:
            handler.update(self, event)


@dataclass(frozen=True)
class Event:
    """Instance této Dataclass jsou odpovědné za stanovení základního
    společného předka pro všechny události.

    Základem je pojmenování takového objektu. To umožňuje člověku v případě
    potřeby rozpoznat, co se v rámci systému dělo."""
    event_name: str = "«event_not_named»"




