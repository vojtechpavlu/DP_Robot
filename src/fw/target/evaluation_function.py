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
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named

import src.fw.target.task as task_module


class EvaluationFunction(ABC, Named, Identifiable):
    """Evaluační funkce slouží k vyhodnocení splnění daného úkolu.
    Tato abstraktní třída definuje obecný protokol pro takovou funkci."""

    def __init__(self, name: str):
        Identifiable.__init__(self)
        Named.__init__(self, name)

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
            raise Exception(f"Dodaný úkol nesmí být None")
        elif self.task is not None:
            raise Exception(f"Úkol nelze znovu přenastavovat")
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

    @abstractmethod
    def eval(self) -> bool:
        """Jádrem evaluační funkce je právě tato metoda, která umožňuje
        vyhodnocení splnění stanoveného úkolu."""


class Conjunction(EvaluationFunctionJunction):
    """Instance třídy 'Conjunction' slouží k zpracovávání více evaluačních
    funkcí najednou, přičemž všechny musí být splněny, aby i tato vracela
    hodnotu o splnění."""

    def __init__(self, name: str):
        """"""
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
        EvaluationFunction.__init__(self, name)
        self._eval_fun = ef

    @property
    def evaluation_function(self) -> "EvaluationFunction":
        """"""
        return self._eval_fun

    def eval(self) -> bool:
        """Vrací převrácenou hodnotu vnitřní evaluační funkce."""
        return not self.evaluation_function.eval()
