""""""

# Import standardních knihoven


# Import lokálních knihoven
from src.fw.utils.identifiable import Identifiable
from src.fw.utils.named import Named


class Task(Identifiable, Named):
    """Instance třídy Task umožňují sledovat postup při řešení problému daného
    úlohou. Úkolu je přiděleno v první řadě ID, dále název a také člověku
    čitelný popis, čeho se má dosáhnout a jakými prostředky, resp. jak je
    dosažení testováno.
    """

    def __init__(self, name: str, eval_fun: "EvaluationFunction"):
        Identifiable.__init__(self)
        Named.__init__(self, name)
        self._eval_fun = eval_fun

    def eval(self) -> bool:
        """Metoda umožňující vyhodnocení daného úkolu co do jeho splnění pomocí
        instance vyhodnocovací funkce."""
        return self._eval_fun.eval()

    @property
    def evaluation_function(self) -> "EvaluationFunction":
        """Vlastnost umožňující získání evaluační funkce."""
        return self._eval_fun

    @evaluation_function.setter
    def evaluation_function(self, new_eval_fun: "EvaluationFunction"):
        """Vlastnost umožňující nastavení evaluační funkce mimo initor."""
        self._eval_fun = new_eval_fun


