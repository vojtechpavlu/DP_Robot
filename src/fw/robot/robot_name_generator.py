"""Modul sdružuje jednoduché nástroje pro získávání názvů robotů. Cílem není
a priori unikátnost, nýbrž spíše popisná a rozlišovací přidaná hodnota."""

# Import standardních knihoven
from abc import ABC, abstractmethod
from random import choice
from typing import Iterable


class RobotNameGenerator(ABC):
    """Abstraktní třída odpovědná za stanovení obecného protokolu společného
    pro množinu typů reprezentovaných potomky této třídy.

    Obecným cílem generátorů jmen robotů je přiřadit robotům názvy, které
    nemusí být unikátní, ale mají spíše rozlišovací charakter pro člověka.
    """

    @abstractmethod
    def get(self) -> str:
        """Abstraktní funkce odpovědná za vygenerování názvu pro robota."""


class ConstantRobotNameGenerator(RobotNameGenerator):
    """Instance této třídy slouží k pojmenovávání robotů jedním konstantním
    jménem."""

    def __init__(self, constant_name: str):
        """Initor, který přijímá jméno, kterým bude každý robot na požádání
        pojmenován."""
        self._name = constant_name

    @property
    def constant_name(self) -> str:
        """Vlastnost vrací jméno, kterým je každý robot na požádání pojmenován.
        """
        return self._name

    def get(self) -> str:
        """Funkce vrací pokaždé to samé jméno, tedy to konstantní, které
        bylo postoupeno této instanci v initoru."""
        return self.constant_name


class FamousSystems(RobotNameGenerator):
    """Instance této třídy poskytují názvy slavných robotů, androidů a jiných
    systémů z oblasti výzkumu robotiky, umělé inteligence a z oblasti science
    fiction."""

    _NAMES = [
        "Optimus-Prime", "R2D2", "C-3PO", "B-9", "Robby the Robot",
        "Karel", "T-800", "WALL-E", "Marvin-the-Paranoid-Android",
        "Parry", "ELIZA", "Ultron", "Johnny 5", "S1M0NE", "Kismet",
        "Sophia", "Aibo", "E2-DR", "Perceptron", "Deep-blue", "Tay",
        "Shakey-the-robot", "Roomba", "Siri", "Watson", "Eugene", "Alexa",
        "AlphaGo", "Cortana", "STRIPS", "GPS", "logic-theorist", "mycin"
    ]

    def get(self) -> str:
        """Funkce vrací náhodný název z výchozího seznamu slavných systémů."""
        return choice(FamousSystems._NAMES).lower()


class FamousScientists(RobotNameGenerator):
    """Instance této třídy vrací náhodně vybrané jméno z výběru slavných
    vědců."""

    _NAMES = [
        "Einstein", "Newton", "Kepler", "Dalton", "Sklodowska", "Galilei",
        "Darwin", "Edison", "Archimedes", "Tesla", "Faraday", "Hawking",
        "Copernicus", "Pasteur", "Lovelace", "Boyle", "Lavoisier", "Mendel",
        "Feynman", "Aristotle", "Celsius", "Rutherford", "Nobel", "Bohr",
        "Planck", "Pythagoras", "Thompson", "Mendeleev", "Pavlov", "Hertz",
        "Fleming", "Heisenberg", "Riemann", "Godel", "Neumann", "Kant",
        "Hilbert", "Turing", "Newell", "Simon", "Searle", "Leibniz",
        "Babbage", "Knuth", "Liskov", "Minsky", "Norvig", "Gosling",
        "Stroustrup", "Rossum", "Matsumoto", "Röntgen", "Marconi",
        "Schrödinger", "Fermi", "Higgs", "Pauling"
    ]

    def get(self) -> str:
        """Funkce vrací náhodný název z výchozího seznamu slavných vědců."""
        return choice(FamousScientists._NAMES).lower()


class FamousExplorers(RobotNameGenerator):
    """Instance této třídy mají za cíl poskytovat náhodná jména slavných
    postav na poli kolonizace, objevitelství, válečnictví a mořeplavectví."""

    _NAMES = [
        "Genghis", "Alexander", "Atilla", "Thutmose", "Napoleon",
        "Eriksson", "Barbarossa", "Vespucci", "Columbus", "Pizzaro",
        "Holub", "Livingstone", "Achilles", "Leonidas", "Spartacus",
        "Hannibal", "Caesar", "Saladin", "Lionheart", "Hector", "Mars",
        "Ares", "Bloodaxe", "Ragnar", "Ironside", "Churchill", "Žižka",
        "Blackbeard", "Cook"
    ]

    def get(self) -> str:
        """Funkce vrací náhodný název z výchozího seznamu slavných mořeplavců,
        objevitelů, dobyvatelů a kolonizátorů."""
        return choice(FamousExplorers._NAMES).lower()


class RandomRobotName(RobotNameGenerator):
    """Instance této třídy jsou odpovědné za generování náhodných řetězců
    o stanovené délce a ze stanovené abecedy."""

    """Výchozí abeceda použitá pro generování názvů robotů."""
    _DEF_ALPHABET = tuple("abcdefghijklmnopqrstuvwxyz0123456789")

    def __init__(self, name_length: int = 8,
                 alphabet: Iterable[str] = _DEF_ALPHABET):
        """Initor, který přijímá délku vytvářených řetězců (názvů) a abecedu,
        která má být k tomuto účelu použita. Oba parametry jsou nastaveny na
        defaultní hodnoty a není tedy nutné je poskytovat.
        """
        self._length = name_length
        self._alphabet = tuple(alphabet)

        if len(self._alphabet) <= 1:
            raise Exception(
                f"Použitá abeceda musí být delší než 1 znak: {self.alphabet}")
        elif name_length <= 0:
            raise Exception(
                f"Minimální délka názvu robota je 1 znak: {name_length}")

    @property
    def alphabet(self) -> "tuple[str]":
        """Vlastnost vrací ntici znaků, které jsou použity pro generování
        názvů robotů."""
        return tuple(self._alphabet)

    @property
    def name_length(self) -> int:
        """Vlastnost vrací délku, kterou mají mít generované řetězce (názvy
        robotů) co do počtu znaků."""
        return self._length

    def get(self) -> str:
        """Funkce odpovědná za vygenerování příslušného řetězce.

        Generování probíhá pomocí rekurzivního volání, dokud nemá řetězec
        požadovanou délku. Pokud této dosáhne, je navrácen."""
        gen_name = self.get()
        return (gen_name if len(gen_name) == self.name_length
                else f"{choice(self.alphabet)}{gen_name}")


class NameGeneratorContainer(RobotNameGenerator):
    """Kontejner, který umožňuje kombinaci více generátorů pro získávání
    názvů robotů."""

    def __init__(self, generators: "Iterable[RobotNameGenerator]"):
        """Initor třídy, který přijímá množinu generátorů názvů, kterých dále
        používá pro získávání názvů pro roboty.
        """
        self._generators = list(generators)

    @property
    def generators(self) -> "tuple[RobotNameGenerator]":
        """Vlastnost vrací ntici všech generátorů, které instance eviduje."""
        return tuple(self._generators)

    def get(self) -> str:
        """Funkce vybere náhodný řetězec tak, že náhodně vybere evidovaný
        generátor názvů a ten požádá o nějaký název. Ten typicky pojmenovává
        také na základě náhody.

        Tento náhodný řetězec je pak vrácen coby budoucí název pro robota."""
        return choice(self.generators).get()



