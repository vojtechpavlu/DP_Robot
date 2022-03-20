"""Modul sdružuje jednoduché nástroje pro získávání názvů robotů. Cílem není
a priori unikátnost, nýbrž spíše popisná a rozlišovací přidaná hodnota."""

# Import standardních knihoven
from abc import ABC, abstractmethod
from random import choice


class RobotNameGenerator(ABC):
    """Abstraktní třída odpovědná za stanovení obecného protokolu společného
    pro množinu typů reprezentovaných potomky této třídy.

    Obecným cílem generátorů jmen robotů je přiřadit robotům názvy, které
    nemusí být unikátní, ale mají spíše rozlišovací charakter pro člověka.
    """

    @abstractmethod
    def get(self) -> str:
        """Abstraktní funkce odpovědná za vygenerování názvu pro robota."""


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



