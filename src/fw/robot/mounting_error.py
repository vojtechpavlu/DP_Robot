"""V tomto modulu jsou sdružovány třídy výjimek, které mohou být vyhozeny
v případě chyby v kontextu osazování robota."""

# Import standardních knihoven

# Import lokálních knihoven
from src.fw.utils.error import PlatformError


class MountingError(PlatformError):
    """"""

    def __init__(self, message: str):
        """"""
        PlatformError.__init__(self, message)



