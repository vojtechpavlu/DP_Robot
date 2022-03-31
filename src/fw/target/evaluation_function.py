"""Modul 'evaluation_function.py' obsahuje definici obecných evaluačních
funkcí.

Obsahuje tu nejobecnější definici, tedy abstraktní třídu EvaluationFunction,
dále definice spojkových funkcí (potomci třídy EvaluationFunctionJunction),
které se starají dle jejich implementace o vyhodnocování více evaluačních
funkcí zároveň, a konečně negaci - pro snazší použití evaluačních funkcí.
"""

# Import standardních knihoven
from abc import ABC, abstractmethod

# Import lokálních knihoven
from src.fw.utils.error import PlatformError
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named

import src.fw.target.task as task_module
import src.fw.target.event_handling as event_module


class EvaluationFunction(Named, Identifiable, event_module.EventHandler):
    """Evaluační funkce slouží k vyhodnocení splnění daného úkolu.
    Tato abstraktní třída definuje obecný protokol pro takovou funkci.

    Kromě toho, že je tato abstraktní třída potomkem tříd Identifiable
    a Named, je také potomkem třídy EventHandler, která umožňuje této
    evaluační funkci naslouchat událostem ve sledovaných objektech."""

    def __init__(self, name: str):
        """Initor třídy, který přijímá člověku čitelný název evaluační
        funkce. Tento initor je odpovědný za iniciaci předků, tedy tříd
        Identifiable, Named a EventHandler.

        Kromě toho také deklaruje proměnnou pro úkol, kterému bude náležet.
        Ten je ovšem v momentě zpracování initoru neznámý; nastavován je až
        za běhu životního cyklu instance."""

        # Volání předků
        Identifiable.__init__(self)
        Named.__init__(self, name)
        event_module.EventHandler.__init__(self)

        """Úkol, ke kterému evaluační funkce náleží"""
        self._task: "task_module.Task" = None

    @property
    def task(self) -> "task_module.Task":
        """Vlastnost, která vrací referenci na úkol, ke kterému tato
        evaluační funkce náleží."""
        return self._task

    @task.setter
    def task(self, task: "task_module.Task"):
        """Vlastnost se pokusí nastavit dodaný úkol jako vlastníka této
        evaluační funkce.

        Tento dodaný úkol nesmí být None a stejně tak nesmí být již jednou
        jedna instance úkolu být této funkci přiřazena. V opačném případě
        je vyhozena příslušná výjimka.
        """
        if task is None:
            raise EvaluationFunctionError(f"Dodaný úkol nesmí být None", self)
        elif self.task is not None:
            raise EvaluationFunctionError(
                f"Úkol nelze znovu přenastavovat", self)
        self._task = task

    @abstractmethod
    def eval(self) -> bool:
        """Jádrem evaluační funkce je právě tato metoda, která umožňuje
        vyhodnocení splnění stanoveného úkolu."""


class EvaluationFunctionJunction(EvaluationFunction):
    """Spojka evaluačních funkcí slouží jako společný předek všem typům
    evaluačních funkcí, které se sestávají z vyhodnocování více funkcí
    najednou. Zároveň instance této třídy vystupují v roli evaluační funkce
    jako takové, jde totiž o potomka třídy 'EvaluationFunction'."""

    def __init__(self, name: str):
        """Jednoduchý initor spojky evaluačních funkcí"""
        EvaluationFunction.__init__(self, name)
        self._eval_funcs: "list[EvaluationFunction]" = []

    @property
    def evaluation_functions(self) -> "tuple[EvaluationFunction]":
        """Vlastnost vrací ntici evaluačních funkcí, ze kterých se spojka
        skládá."""
        return tuple(self._eval_funcs)

    def add_eval_func(self, fun: "EvaluationFunction"):
        """Metoda umožňující dynamicky přidávat instance evaluačních funkcí
        do této instance."""
        self._eval_funcs.append(fun)


class Conjunction(EvaluationFunctionJunction):
    """Instance třídy 'Conjunction' slouží k zpracovávání více evaluačních
    funkcí najednou, přičemž všechny musí být splněny, aby i tato vracela
    hodnotu o splnění."""

    def __init__(self, name: str):
        """Initor třídy, který pouze postupuje dodaný název svému předkovi."""
        EvaluationFunctionJunction.__init__(self, name)

    def eval(self) -> bool:
        """Jádro spojené evaluační funkce, které prochází všechny spojované.
        Je-li jediná nepravdivá, je vráceno (po vzoru konjunkce) False, jinak
        je vrácena hodnota True."""
        for ef in self.evaluation_functions:
            if not ef.eval():
                return False
        return True


class Disjunction(EvaluationFunctionJunction):
    """Instance třídy 'Disjunction' slouží k zpracovávání více evaluačních
    funkcí najednou, přičemž stačí, aby byla splněna jen jediná, aby i tato
    vracela hodnotu o splnění."""

    def __init__(self, name: str):
        """"""
        EvaluationFunctionJunction.__init__(self, name)

    def eval(self) -> bool:
        """Jádro spojené evaluační funkce, které prochází všechny spojované.
        Je-li jediná pravdivá, je vráceno (po vzoru disjunkce) True, jinak
        je vrácena hodnota False."""
        if len(self.evaluation_functions) == 0:
            return True
        for ef in self.evaluation_functions:
            if ef.eval():
                return True
        return False


class Negation(EvaluationFunction):
    """Instance třídy Negation má za cíl převracet hodnotu vložené evaluační
    funkce."""

    def __init__(self, name: str, ef: "EvaluationFunction"):
        """Initor třídy, který je odpovědná za postoupení názvu evaluační
        funkce svému předkovi, stejně jako je odpovědný za uložení reference
        na vyhodnocovací funkci, jejíž hodnotu bude negovat."""

        # Volání předka
        EvaluationFunction.__init__(self, name)

        """Vyhodnocovací funkce, jejíž hodnotu bude tato instance vracet 
        znegovanou"""
        self._eval_fun = ef

    @property
    def evaluation_function(self) -> "EvaluationFunction":
        """Vlastnost vrací evaluační funkci, jejíž hodnotu tato instance
        obrací."""
        return self._eval_fun

    def eval(self) -> bool:
        """Vrací převrácenou hodnotu vnitřní evaluační funkce."""
        return not self.evaluation_function.eval()


class EvaluationFunctionError(PlatformError):
    """Tato výjimka symbolizuje chyby, které můžou nastat v kontextu
    vyhodnocovacích funkcí. Svého předka rozšiřuje o referenci na evaluační
    funkci, v jejímž kontextu došlo k chybě."""

    def __init__(self, message: str, eval_fun: "EvaluationFunction"):
        """Initor, který postupuje zprávu o chybě svému předkovi a ukládá
        referenci na evaluační funkci, jejímž kontextu došlo k chybě.
        """

        # Volání předka
        PlatformError.__init__(self, message)

        # Evaluační funkce, v jejímž kontextu došlo k chybě
        self._eval_fun = eval_fun

    @property
    def evaluation_function(self) -> "EvaluationFunction":
        """Vlastnost vrací referenci na evaluační funkci, v jejímž kontextu
        došlo k chybě."""
        return self._eval_fun

