"""Modul obsahuje prostředky pro provádění evaluace vyhodnocovacích funkcí.

Především tento definuje, jak má úkol (reprezentovaný třídou Task) vypadat,
tedy jaký má mít protokol.
"""

# Import standardních knihoven


# Import lokálních knihoven
from src.fw.utils.described import Described
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named

import src.fw.target.evaluation_function as ef_module


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

        """Uložení dodané evaluační funkce"""
        self._eval_fun = eval_fun

    def eval(self) -> bool:
        """Metoda umožňující vyhodnocení daného úkolu co do jeho splnění pomocí
        instance vyhodnocovací funkce."""
        return self._eval_fun.eval()

    @property
    def evaluation_function(self) -> "ef_module.EvaluationFunction":
        """Vlastnost umožňující získání evaluační funkce."""
        return self._eval_fun

    @evaluation_function.setter
    def evaluation_function(self,
                            new_eval_fun: "ef_module.EvaluationFunction"):
        """Vlastnost umožňující nastavení evaluační funkce mimo initor."""
        self._eval_fun = new_eval_fun


