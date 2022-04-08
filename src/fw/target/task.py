"""Modul obsahuje prostředky pro provádění evaluace vyhodnocovacích funkcí.

Především tento definuje, jak má úkol (reprezentovaný třídou Task) vypadat,
tedy jaký má mít protokol.
"""

# Import standardních knihoven
from collections import Callable
from typing import Iterable


# Import lokálních knihoven
from src.fw.utils.described import Described
from src.fw.utils.error import PlatformError
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named

import src.fw.target.evaluation_function as ef_module
import src.fw.target.target as target_module


class Task(Identifiable, Named, Described):
    """Instance třídy Task umožňují sledovat postup při řešení problému daného
    úlohou."""

    def __init__(self, task_name: str, task_desc: str,
                 eval_fun: "ef_module.EvaluationFunction"):
        """Initor třídy, který přijímá v název úkolu, jeho popis a evaluační
        funkci, která bude vyhodnocovat jeho splnění.

        Zatímco název plní funkci spíše pro člověka identifikační, podstata
        dědění třídy Identifiable je spíše za účelem identifikace strojem.
        Popis plní funkci čistě popisnou. V popisu by měl být uveden (alespoň
        vágně) kýžený stav, jehož splnění je očekáváno a vyhodnocováno
        evaluační funkcí.
        """

        """Volání initorů předků"""
        Identifiable.__init__(self)
        Named.__init__(self, task_name)
        Described.__init__(self, task_desc)

        """Uložení dodané evaluační funkce a vzájemné propojení"""
        self._eval_fun = eval_fun
        self._eval_fun.task = self

        """Úloha, které tato instance úkolu náleží"""
        self._target: "target_module.Target" = None

        """Potrubí loggeru, kterého je použito pro tvorbu standardizovaných
        záznamů v kontextu plnění úkolu."""
        self._logger_pipeline: "Callable" = None

    @property
    def target(self) -> "target_module.Target":
        """Vlastnost vrací úlohu, ke které tento úkol náleží."""
        return self._target

    @target.setter
    def target(self, target: "target_module.Target"):
        """Vlastnost umožňující nastavit úlohu, ke které tento úkol náleží.
        To ovšem umožňuje právě jednou.

        Pokud je dodaná úloha prázdná (None), je vyhozena výjimka. Podobně pak
        v případě, že je již jednou úloha nastavena."""
        if target is None:
            raise TaskError(f"Dodaná úloha je None", self)
        elif self.target is not None:
            raise TaskError(f"Nelze přenastavovat úlohu", self)
        self._target = target
        self.evaluation_function.configure()

    @property
    def log(self) -> "Callable":
        """Vlastnost vrací potrubí loggeru přidělené kontextu úkolu. Pomocí
        této funkce navrácené touto vlastností je možné zaznamenávat pokrok
        v plnění úkolů."""
        return self._logger_pipeline

    @log.setter
    def log(self, logger_pipeline: "Callable"):
        """Vlastnost nastavuje potrubí, kterého má být použito pro potřeby
        logování."""
        self._logger_pipeline = logger_pipeline

    @property
    def evaluation_function(self) -> "ef_module.EvaluationFunction":
        """Vlastnost umožňující získání evaluační funkce."""
        return self._eval_fun

    @evaluation_function.setter
    def evaluation_function(self,
                            new_eval_fun: "ef_module.EvaluationFunction"):
        """Vlastnost umožňující nastavení evaluační funkce mimo initor."""
        self._eval_fun = new_eval_fun

    def eval(self) -> bool:
        """Metoda umožňující vyhodnocení daného úkolu co do jeho splnění pomocí
        instance vyhodnocovací funkce."""
        return self._eval_fun.eval()


class TaskError(PlatformError):
    """Výjimka rozšiřující svého předka o referenci na úkol, v jehož kontextu
    došlo k chybě. Tato výjimka umožňuje svojí symbolizací blíže specifikovat,
    co se stalo."""

    def __init__(self, message: str, task: "Task"):
        """Initor, který postupuje svému předkovi zprávu o chybě, stejně jako
        si ukládá referenci na úkol, v jehož kontextu došlo k chybě."""

        # Volání předka
        PlatformError.__init__(self, message)

        # Uložení úkolu, v jehož kontextu došlo k chybě
        self._task = task

    @property
    def task(self) -> "Task":
        """Vlastnost vrací referenci na úkol, v jehož kontextu došlo k chybě.
        """
        return self._task


class VisitAllTask(Task):
    """Třída definuje samostatnou tvorbu úkolu, který ověřuje navštívení
    všech navštivitelných políček, které v daném světě jsou. Typicky tedy
    všechny cesty.

    Za tímto účelem si vytváří instanci třídy 'VisitAllEvaluationFunction',
    což je v podstatě konjunkční obal evaluačních funkcí reagujících na
    navštívení políčka. Pro každou cestu je pak vytvořena jedna."""

    def __init__(self):
        Task.__init__(
            self, "VisitAllTask",
            "Úkol, který očekává navštívení všech cest světa.",
            ef_module.VisitAllEvaluationFunction())


class VisitSpecificFieldsTask(Task):
    """Třída definuje úkol, který je plněn navštívením konkrétních políček.
    Tato políčka jsou předem známá a musí v daném světě existovat."""

    def __init__(self, to_visit: "Iterable[Iterable[int, int]]"):
        """Initor, který přijímá iterovatelnou množinu iterovatelných
        souřadnic, na kterých se nachází políčko, které má být sledováno
        co do navštívení.

        Doporučená podoba těchto souřadnic je například taková:
            >>> [(1, 1), (2, 2), (3, 3)]
        """
        Task.__init__(
            self, "VisitSpecificFields",
            "Úkol, který očekává navštívění specifických políček ve světě.",
            ef_module.VisitSpecificFieldEvaluationFunction(to_visit))


class ApplyAllInteractions(Task):
    """Třída, která obaluje evaluační funkce z kontextu ověřování aplikace
    požadovaných interakcí.

    Tento úkol slouží k ověření, že bylo použito všech minimálních prostředků.
    """

    def __init__(self, interaction_names: "Iterable[str]"):
        Task.__init__(
            self, "ApplyAllInteractions",
            "Úkol, který kontroluje, že byly použity všechny stanovené"
            "interakce.", ef_module.UsedAllInteractions(interaction_names))


class IsMountedWithAllTask(Task):
    """Tento úkol umožňuje kontrolu robotů co do jejich osazení, zda-li jsou
    osazeni všemi požadovanými jednotkami."""

    def __init__(self, unit_names: "Iterable[str]"):
        """"""
        Task.__init__(
            self, "IsMountedWithAllTask",
            "Úkol, kontrolující robota, zda je osazen všemi požadovanými "
            "jednotkami", ef_module.IsRobotMountedWithAll(unit_names))


class AddedMarkAtTask(Task):
    """Tento úkol umožňuje kontrolu splnění požadavku na označení stanoveného
    políčka na specifických souřadnicích. Samotný text značky zde není
    nijak rozhodující."""

    def __init__(self, x: int, y: int):
        """Initor, který přijímá souřadnice sledovaného políčka."""
        Task.__init__(
            self, f"AddedMark @ [{x}, {y}]", "Úkol, který kontroluje, "
            f"že bylo políčko na souřadnicích [{x}, {y}] robotem označeno",
            ef_module.AddedAnyMarkEvalFun(x, y))


class RemovedMarkAtTask(Task):
    """Tento úkol umožňuje kontrolu splnění požadavku na odstranění značky
    ze stanoveného políčka na specifických souřadnicích.

    Tato značka předtím na políčku musí být, resp. musí dojít k explicitnímu
    odstranění značky robotem."""

    def __init__(self, x: int, y: int):
        """Initor, který přijímá souřadnice sledovaného políčka."""
        Task.__init__(
            self, f"RemovedMark @ [{x}, {y}]", "Úkol, který kontroluje, "
            f"že byla odstraněna značka z políčka na souřadnicích [{x}, {y}]",
            ef_module.RemovedMarkEvalFun(x, y))


class LoggedAnythingInContext(Task):
    """Tento úkol slouží ke kontrole splnění požadavku na zalogování libovolné
    zprávy v předem stanoveném kontextu."""

    def __init__(self, context: str = "OUTPUT"):
        """"""
        Task.__init__(
            self, f"LoggedAnythingInContext '{context}'", "Úkol, který "
            f"kontroluje, že bylo zalogováno v kontextu '{context}'",
            ef_module.LoggedAnything(context))


def always_true_task() -> "Task":
    """Funkce vrací instanci úkolu, který je vykonstruován tak, že je vždy
    za všech okolností pravdivý, tedy splněný."""
    return Task(
        "Always True task", "Úkol, který je vždy zcela splněn.",
        ef_module.AlwaysTrueEvaluationFunction())


def always_false_task() -> "Task":
    """Funkce vrací instanci úkolu, který je vykonstruován tak, že je vždy
    za všech okolností nepravdivý, tedy nesplněný."""
    return Task(
        "Always False task", "Úkol, který není nikdy splněn.",
        ef_module.AlwaysFalseEvaluationFunction())



