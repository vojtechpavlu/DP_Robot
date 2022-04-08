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

    def __str__(self) -> str:
        """Funkce vrací textovou reprezentaci značky, tedy její text."""
        return f"[{self.text}]"


class MarkRule(ABC):
    """Abstraktní funkce MarkRule definuje protokol pro ověřující pravidla,
    která jsou závazná pro tvořené značky."""

    @abstractmethod
    def check(self, mark: "Mark") -> bool:
        """Abstraktní funkce definuje protokol svojí signaturou. Její
        implementace slouží k ověření platnosti značky."""


class MaxLength(MarkRule):
    """Toto pravidlo definuje omezení, že texty značek nesmí být delší, než
    stanovený počet znaků."""

    def __init__(self, max_length: int = 3):
        """Initor, který přijímá stanovený maximální počet znaků. Jeho
        defaultní hodnota jsou 3 znaky."""
        self._max_length = max_length

    @property
    def max_length(self) -> int:
        """Vlastnost vrací maximální délku textu značky."""
        return self._max_length

    def check(self, mark: "Mark") -> bool:
        """Funkce se pokusí ověřit, zda dodaný text značky je kratší nebo
        roven maximální povolené délce."""
        return len(mark.text) <= self.max_length

    def __str__(self) -> str:
        """Textová reprezentace pravidla. Typicky by měla popisovat svoje
        rozhodovací kritérium."""
        return f"Text značky musí být maximálně {self.max_length} znaků dlouhý"


class MinLength(MarkRule):
    """Instance této třídy slouží k omezení minimální délky textu značky."""

    def __init__(self, min_length: int = 1):
        """Initor třídy, který ukládá minimální délku textu značky. Defaultně
        je tato hodnota nastavena na 1; při hodnotě 0 bude tato instance při
        kontrolách vždy vracet True. Pro záporné hodnoty je nastavena 0.
        """
        self._min_length = min_length if min_length > 0 else 0

    @property
    def min_length(self) -> int:
        """Vlastnost vrací minimální stanovenou délku textu značky, aby byl
        považován za validní."""
        return self._min_length

    def check(self, mark: "Mark") -> bool:
        """Funkce ověřuje, zda text značky odpovídá kvótě o minimální délce
        textu."""
        return len(mark.text) >= self.min_length

    def __str__(self) -> str:
        """Textová reprezentace pravidla. Typicky by měla popisovat svoje
        rozhodovací kritérium."""
        return f"Text značky musí být minimálně {self.min_length} znaků dlouhý"


class AllowedCharset(MarkRule):
    """Instance této třídy slouží k ověřování, že texty značek se sestávají
     výhradně jen ze znaků ze stanovené znakové sady."""

    # Výchozí znaková sada
    default_charset = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")

    def __init__(self, charset: "Iterable[str]" = default_charset):
        """Initor třídy, který přijímá v parametru iterovatelnou množinu
        znaků, které omezují použitelné texty značek co do obsahu."""
        self._charset = tuple(charset)

    @property
    def charset(self) -> "tuple[str]":
        """Vlastnost vrací povolenou znakovou sadu v podobě ntice znaků."""
        return self._charset

    def check(self, mark: "Mark") -> bool:
        """Funkce ověřuje, zda-li je značka značky sestaven z pouze povolených
        znaků či zda obsahuje i nějaké nepovolené."""
        for char in tuple(mark.text):
            if char not in self.charset:
                return False
        return True

    def __str__(self) -> str:
        """Textová reprezentace pravidla. Typicky by měla popisovat svoje
        rozhodovací kritérium."""
        return f"Text značky smí obsahovat pouze znaky ze sady {self.charset}"


"""Výchozí sada pravidel, která určuje, jaké texty je možné použít pro 
jednotlivé značky."""
_DEFAULT_MARK_RULES = [MaxLength(), MinLength(), AllowedCharset()]


class Markable(ABC):
    """Instance této třídy slouží k uchovávání značek, stejně jako k
    jejich ověřování.

    Samotné ověřování probíhá na základě pravidel, kterými jsou značky,
    resp. jejich texty, ověřovány."""

    def __init__(
            self, rules: "Iterable[MarkRule]" = tuple(_DEFAULT_MARK_RULES)):
        """Initor třídy, který slouží k uložení potřebných hodnot a iniciaci
        požadovaných polí. V parametru přijímá iterovatelnou množinu pravidel,
        kterými budou dané značky ověřovány.
        """
        # Seznam ověřovacích pravidel pro nové potenciální značky
        self._rules = list(rules)

        # Připravení pole pro značku
        self._mark: "Mark" = None

    @property
    def mark(self) -> "Mark":
        """Vlastnost vrací značku, která je v instanci uložena."""
        return self._mark

    @property
    def has_mark(self) -> bool:
        """Vlastnost vrací, zda-li je již v této instanci značka uložena."""
        return self.mark is not None

    @property
    def pop_mark(self) -> "Mark":
        """Vlastnost vymaže značku z evidence a vrátí ji."""
        mark = self.mark
        self._mark = None
        return mark

    @property
    def mark_rules(self) -> "tuple[MarkRule]":
        """Vlastnost vrací ntici pravidel pro potenciální značky."""
        return tuple(self._rules)

    def add_mark_rule(self, rule: "MarkRule"):
        """Funkce přidává pravidlo pro potenciální značky."""
        self._rules.append(rule)

    def check_mark(self, mark: "Mark") -> bool:
        """Funkce se stará o kontrolu potenciální značky, zda-li neporušuje
        některé pravidlo."""
        return len(self.violated_mark_rules(mark)) == 0

    def violated_mark_rules(self, mark: "Mark") -> "tuple[MarkRule]":
        """Funkce vrací pro dodanou značku sadu pravidel, která byla porušena.
        """
        return tuple(filter(lambda r: not r.check(mark), self.mark_rules))

    def mark_yourself(self, text: str) -> "Mark":
        """Funkce se pokusí z dodaného textu vytvořit značku a tuto v sobě
        uložit.

        Typicky může vyhodit výjimku, a to v případě, když již jedna značka
        v této instanci je uložena, nebo když je dodaný text pro značku
        nevyhovující (není v souladu s některým z pravidel)."""

        # Vytvoření nové značky
        new_mark = Mark(text)

        # Pokud nemůže být tato instance označkována
        if not self.can_be_marked:
            raise MarkError(
                f"Tato instance nemůže být označkována: {self}", new_mark)

        # Pokud již jedna značka v této instanci evidována je
        elif self.has_mark:
            raise MarkError(
                f"Jedna značka je již přítomná: '{self.mark=}'", self.mark)

        # Pokud daná značka neodpovídá pravidlům
        elif not self.check_mark(new_mark):
            raise MarkError(
                f"Značka s textem '{new_mark.text}' není přípustná: "
                f"{self.violated_mark_rules(new_mark)}", new_mark)

        # Pokud je vše v pořádku
        else:
            self._mark = new_mark
            return self.mark

    @property
    @abstractmethod
    def can_be_marked(self) -> bool:
        """Abstraktní vlastnost vrací, zda-li může být tato instance
        označitelná či nikoliv."""


class MarkError(PlatformError):
    """Instance této třídy výjimek slouží k symbolizaci chyby, ke které může
    dojít v kontextu značek."""

    def __init__(self, message: str, mark: "Mark"):
        """Initor třídy, který přijímá zprávu o chybě a postupuje ji předkovi,
        a značku, v jejímž kontextu došlo k chybě."""
        PlatformError.__init__(self, message)
        self._mark = mark

    @property
    def mark(self) -> Mark:
        """Vlastnost vrací značku, v jejímž kontextu došlo k chybě."""
        return self._mark




