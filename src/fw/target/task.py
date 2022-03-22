""""""

# Import standardních knihoven


# Import lokálních knihoven
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named

import src.fw.target.evaluation_function as ef_module


class Task(Identifiable, Named):
    """Instance třídy Task umožňují sledovat postup při řešení problému daného
    úlohou."""

    def __init__(self, name: str, eval_fun: "ef_module.EvaluationFunction"):
        """"""
        Identifiable.__init__(self)
        Named.__init__(self, name)

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


