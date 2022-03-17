"""V modulu 'error.py' jsou sdružovány všechny obecné třídy, které
představují výjimky, které mohou být při manipulaci se systémem vyhozeny.

Tyto typicky představují chyby, které mohou vzniknout.
"""


class GeneralError(Exception):
    """Tato třída představuje nejobecnější typ chyby, který umí systém
    rozlišovat.

    Oproti standardní implementaci je obohacen přístup ke zprávě, která chybu
    doprovází.
    """

    def __init__(self, message: str):
        """Jednoduchý initor výjimky, který přijímá v parametru textovou
        reprezentaci zprávy."""
        Exception.__init__(self, message)
        self._message = message

    @property
    def message(self) -> str:
        """Vlastnost vrací zprávu, která popisuje okolnosti vzniku výjimky."""
        return self._message


class PlatformError(GeneralError):
    """"""

    def __init__(self, message: str):
        """"""
        GeneralError.__init__(self, message)


class RobotRunError(GeneralError):
    """"""

    def __init__(self, message: str):
        """"""
        GeneralError.__init__(self, message)

