""""""


# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Iterable

# Import lokálních knihoven
import src.fw.robot.interaction as interaction_module


class InteractionRule(ABC):
    """Abstraktní třída InteractionRule definuje protokol pro všechna
    pravidla, která ověřují formální správnost interakcí; tedy zda-li je je
    možné aplikovat.

    Typickými pravidly je například omezení aplikovatelného počtu interakcí.
    """

    @abstractmethod
    def check(self, interaction: "interaction_module.Interaction") -> bool:
        """Abstraktní funkce definuje způsob ověření, že je interakce z
        formálního hlediska akceptovatelná."""


class LimitedCounter(InteractionRule):
    """Třída LimitedCounter definuje takové pravidlo, které omezuje počet
    všech aplikovaných interakcí. Pokud tento limitní počet je překročen,
    jsou další interakce zamítnuty."""

    def __init__(self, num_of_allowed: int = 100_000):
        """Initor, který přijímá maximální počet aplikovatelných interakcí.

        Tento počet je defaultně nastaven na 100 000. Pokud je však dodán
        záporný počet, je vyhozena výjimka. Nula (0) je validní hodnotou;
        žádná interakce nebude přijata.

        Dále initor deklaruje aktuální stav (který je roven 0).
        """
        self.__num_of_allowed = num_of_allowed
        self.__current_state = 0

        if self.num_of_allowed < 0:
            raise Exception(f"Nelze mít záporný počet povolených "
                            f"interakcí: {self.num_of_allowed}")

    @property
    def num_of_allowed(self) -> int:
        """Vlastnost vrací horní limit povolených interakcí."""
        return self.__num_of_allowed

    @property
    def current_state(self) -> int:
        """Vlastnost vrací aktuální stav, tedy kolik interakcí bylo celkem
        aplikováno."""
        return self.__current_state

    @property
    def have_left(self) -> int:
        """Vlastnost vrací rozdíl mezi limitem a aktuálním stavem, tedy kolik
        interakcí je ještě možné aplikovat.
        """
        return self.num_of_allowed - self.current_state

    def check(self, interaction: "interaction_module.Interaction") -> bool:
        """Funkce ověřující, že je počet doposud aplikovaných interakcí menší,
        než je stanovený limit. Pokud toto pravidlo naplněno není, vrací False.
        """
        self.__current_state += 1
        return self.have_left > 0


class LimitPerInteractionType(InteractionRule):
    """"""

    def __init__(self, num_of_allowed: int = 500):
        """"""
        self._num_of_allowed = 500
        self._registry = {}

    def tick(self, interaction: "interaction_module.Interaction") -> int:
        """"""
        typename = interaction.interaction_type.__name__
        if typename in self._registry:
            self._registry[typename] += 1
        else:
            self._registry[typename] = 1
        return self._registry[typename]

    def check(self, interaction: "interaction_module.Interaction") -> bool:
        return self.tick(interaction) < self._num_of_allowed








