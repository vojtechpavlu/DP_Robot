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

        # Vytvoření prázdného loggeru
        logger = logger_module.Logger()

        # Vytvoření výstupu pro tisknutí na konzoli, přijímá všechny kontexty
        printer = logging_output_module.PrintingOutput(take_all=True)

        # Vytvoření výstupu pro pamatování; přijímá všechny kontexty
        memo_all = logging_output_module.SimpleOutputWithMemo(take_all=True)

        # Vytvoření výstupu pro pamatování; přijímá pouze kontext "OUTPUT"
        memo_out = logging_output_module.SimpleOutputWithMemo(take_all=False)
        memo_out.add_context("OUTPUT")

        # Registrace výstupů u loggeru
        logger.add_output(printer)
        logger.add_output(memo_all)
        logger.add_output(memo_out)

        # Vrácení připraveného defaultního loggeru
        return logger

