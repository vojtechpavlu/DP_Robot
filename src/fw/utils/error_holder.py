"""Modul obsahuje definici kontejneru pro výjimky. Této služby je použito
pro zachování chyby, ke které může dojít, stejně jako pro potřeby stopování
její cesty, kudy se šířila dál."""

# Import standardních knihoven
from typing import Type


class ErrorHolder:
    """Instance této třídy slouží k uchování výjimek a jejich stopy.

    Použití instancí této třídy je k zaznamenání, že došlo k chybě,
    zaznamenání trasy této chyby a její zpracování za účelem pozdější
    analýzy."""

    def __init__(self, exception: Exception, traceback: str):
        """Initor, který přijímá výjimku, která byla vyhozena, a trasu
        od bodu, kde byla vyhozena až k jejímu odchytu.
        """
        self._exception = exception
        self._traceback = traceback

    @property
    def exception(self) -> Exception:
        """Vlastnost vrací výjimku, která byla do této instance umístěna k
        jejímu držení."""
        return self._exception

    @property
    def traceback(self) -> str:
        """Vlastnost vrací cestu (stopu) chyby, která byla vyhozena,
        odchycena a této instanci postoupena."""
        return self._traceback

    @property
    def exception_type(self) -> Type:
        """Vlastnost vrací typ výjimky, která byla vyhozena."""
        return self.exception.__class__

    @property
    def exception_type_name(self) -> str:
        """Vlastnost vrací název typu výjimky, která byla vyhozena."""
        return self.exception_type.__name__

    @property
    def exception_message(self) -> str:
        """Vlastnost vrací zprávu, která výjimce náleží."""
        return str(self.exception)


