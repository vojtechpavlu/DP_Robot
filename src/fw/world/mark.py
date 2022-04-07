"""V tomto modulu jsou obsaženy definice značkování políček."""

# Import standardních knihoven
from abc import ABC, abstractmethod
from typing import Iterable

# Import lokálních knihoven
from src.fw.utils.error import PlatformError


class Mark:
    """Instance této třídy slouží k uchování značky. Jejich smysl spočívá
    k uchování textu, kterým je daný označený objekt označen.

    Hlavním významem těchto instancí je vytvoření možnosti značkovat políčka
    světa a opatřit je patřičným textem."""

    def __init__(self, text: str):
        """Initor třídy, který slouží k zadání neměnného textu reprezentujícího
        danou značku. Ten je nastaven do privátní proměnné.
        """
        self.__text = text

    @property
    def text(self) -> str:
        """Vlastnost vrací nastavený text značky."""
        return self.__text


class MarkRule(ABC):
    """Abstraktní funkce MarkRule definuje protokol pro ověřující pravidla,
    která jsou závazná pro tvořené značky."""

    @abstractmethod
    def check(self, mark: "Mark") -> bool:
        """Abstraktní funkce definuje protokol svojí signaturou. Její
        implementace slouží k ověření platnosti značky."""


class Markable:
    """"""

    def __init__(self, rules: "Iterable[MarkRule]"):
        """"""
        self._rules = list(rules)
        self._mark: "Mark" = None

    @property
    def mark(self) -> "Mark":
        """"""
        return self._mark

    @property
    def has_mark(self) -> bool:
        """"""
        return self.mark is not None

    @property
    def mark_rules(self) -> "tuple[MarkRule]":
        """"""
        return tuple(self._rules)

    def add_mark_rule(self, rule: "MarkRule"):
        """"""
        self._rules.append(rule)

    def check(self, mark: "Mark") -> bool:
        """"""
        return self.violated_mark_rules(mark) == 0

    def violated_mark_rules(self, mark: "Mark") -> "tuple[MarkRule]":
        """"""
        return tuple(filter(lambda r: not r.check(mark), self.mark_rules))

    def mark_yourself(self, text: str) -> "Mark":
        """"""

        # Vytvoření nové značky
        new_mark = Mark(text)

        # Pokud již jedna značka v této instanci evidována je
        if self.has_mark:
            raise MarkError(
                f"Jedna značka je již přítomná: '{self.mark=}'", self.mark)

        # Pokud daná značka neodpovídá pravidlům
        elif not self.check(new_mark):
            raise MarkError(
                f"Značka s textem '{new_mark.text}' není přípustná: "
                f"{self.violated_mark_rules(new_mark)}", new_mark)

        # Pokud je vše v pořádku
        else:
            self._mark = new_mark
            return self.mark


class MaxLength(MarkRule):
    """"""

    def __init__(self, max_length: int = 3):
        """"""
        self._max_length = max_length

    @property
    def max_length(self) -> int:
        """"""
        return self._max_length

    def check(self, mark: "Mark") -> bool:
        """"""
        return len(mark.text) <= self.max_length

    def __str__(self) -> str:
        """Textová reprezentace pravidla. Typicky by měla popisovat svoje
        rozhodovací kritérium."""
        return f"Text značky musí být maximálně {self.max_length} znaků dlouhý"


class MinLength(MarkRule):
    """"""

    def __init__(self, min_length: int = 1):
        """"""
        self._min_length = min_length

    @property
    def min_length(self) -> int:
        """"""
        return self._min_length

    def check(self, mark: "Mark") -> bool:
        """"""
        return len(mark.text) >= self.min_length

    def __str__(self) -> str:
        """Textová reprezentace pravidla. Typicky by měla popisovat svoje
        rozhodovací kritérium."""
        return f"Text značky musí být minimálně {self.min_length} znaků dlouhý"


class AllowedCharset(MarkRule):
    """"""

    default_charset = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890".split(""))

    def __init__(self, charset: "Iterable[str]" = default_charset):
        """"""
        self._charset = tuple(charset)

    @property
    def charset(self) -> "tuple[str]":
        """"""
        return self._charset

    def check(self, mark: "Mark") -> bool:
        """"""
        for char in mark.text.split(""):
            if not char in self.charset:
                return False
        return True

    def __str__(self) -> str:
        """Textová reprezentace pravidla. Typicky by měla popisovat svoje
        rozhodovací kritérium."""
        return f"Text značky smí obsahovat pouze znaky ze sady {self.charset}"


"""Výchozí sada pravidel, která určuje, jaké texty je možné použít pro 
jednotlivé značky."""
_DEFAULT_MARK_RULES = [MaxLength(), MinLength(), AllowedCharset()]


class MarkError(PlatformError):
    """"""

    def __init__(self, message: str, mark: "Mark"):
        """"""
        PlatformError.__init__(self, message)
        self._mark = mark

    @property
    def mark(self) -> Mark:
        """"""
        return self._mark




