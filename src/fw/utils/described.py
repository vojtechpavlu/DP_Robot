"""Modul 'description' definuje obecnou abstraktní třídu coby protokol pro
všechny instance, které mají vlastní popis v přirozeném jazyce."""


# Import standardních knihoven
from abc import ABC, abstractmethod


class Described(ABC):
    """Abstraktní třída 'Described' slouží k definici společného protokolu
    všech instancí, které vyžadují popis v člověku čitelném jazyce.

    Instance tříd, které implementují tuto třídu, mají v sobě uložen popis
    v podobě textového řetězce a jsou schopny tento nabídnout i svému okolí.
    """

    def __init__(self, description: str = ""):
        """Initor třídy, který přijímá v parametru popis, jenž bude dále
        reprezentovat člověku čitelnou reprezentaci instance.

        Významem je například zdůvodnit způsob použití, specifikovat
        konkrétní specifické vlastnosti instance nebo popsat význam.
        """
        self._desc = description

    @property
    def description(self) -> str:
        """Vlastnost, která vrací textový řetězec reprezentující popis
        této instance, resp. instance implementující tuto abstraktní třídu.
        """
        return self._desc
