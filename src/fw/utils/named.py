"""V tomto modulu jsou uloženy všechny základní prostředky pro pojmenovávání
instancí textovými reprezentacemi.

Samotný institut pojmenování je v tomto kontextu chápán především pro potřeby
lidského zpracování. Pojmenování není unikátní; mnoho instancí může mít
identický název a to i napříč různými datovými typy či kontexty použití.
"""

from abc import ABC


class Named(ABC):
    """Abstraktní třída Named slouží ke stanovení společného protokolu pro
    všechny instance tříd, které vyžadují ze svého způsobu použití a kontextu
    pojmenování. Třída je prohlášena za abstraktní, neboť z důvodu její
    přílišné obecnosti je zbytečné tuto samu o sobě instanciovat.

    Samotný institut pojmenování chápejme jako schopnost udržovat a poskytovat
    textový řetězec, který umožňuje tyto instance ČÁSTEČNĚ identifikovat
    nebo zastoupit.

    Důvodem je typicky pro člověka čitelný způsob popisu elementárního popisu
    instance.
    """

    def __init__(self, name: str = "«no_name»"):
        """Jednoduchý initor odpovědný za přijetí názvu instance. Tento název
        nemusí být unikátní; dokonce může být nastaven automaticky. Defaultní
        hodnotou pak je textový řetězec '«no_name»'.
        """
        self._name = name

    @property
    def name(self) -> str:
        """Vlastnost vrací název, který instance nese."""
        return self._name



