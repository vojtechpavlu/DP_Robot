"""Modul 'logger_factory' je odpovědný za definici schopnosti dynamického
poskytování instancí loggeru.

Především je zde definován protokol továrny loggeru, který má za cíl stanovit
obecné signatury pro vybudování řčených instancí."""


# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
import src.fw.utils.logging.logger as logger_module
import src.fw.utils.logging.logging_output as logging_output_module


class LoggerFactory(ABC):
    """Abstraktní třída LoggerFactory stanovuje obecný protokol pro tvorbu
    instancí třídy 'Logger'. Její účel tkví v dynamicky řízeném poskytování
    těchto instancí dle procedury definované implementací zde uvedené
    abstraktní metody 'build()'."""

    @abstractmethod
    def build(self) -> "logger_module.Logger":
        """Abstraktní metoda 'build()' je odpovědná za stanovení protokolu
        obecnou signaturou, přičemž garantuje, že jednotlivé implementace
        abstraktní třídy 'LoggerFactory' jsou schopny tvořit instance třídy
        'Logger'."""


class DefaultLoggerFactory(LoggerFactory):
    """Výchozí definice továrny loggeru, která má za cíl tvořit instanci
    loggeru s defaultním nastavením."""

    def build(self) -> "logger_module.Logger":
        """Funkce tvoří logger s defaultním nastavením."""
        logger = logger_module.Logger()
        output = logging_output_module.PrintingOutput(take_all=True)
        output.add_context("output")
        logger.add_output(output)
        return logger

