"""Šablona pluginu definující program. Její význam je v zjednodušení přístupu
k vytváření pluginů tohoto typu.

K tomu nejjednoduššímu použití je třeba vyplnit de facto jen jméno autora
a proceduru, která má být v rámci běhu programu spuštěna (tedy metoda
'run(Robot)').

Dále je třeba, aby v tomto modulu byla definována přístupová tovární funkce,
která na zavolání bude vracet instanci tohoto programu. V defaultním pojetí
je tato pojmenována 'get_program' a její název je takto důsledně vyžadován.

Kromě toho je ve výchozím nastavení definováno, že dokumentační komentář
tohoto modulu musí být neprázdný; tedy obsahovat alespoň jeden znak, který
není mezerou či jemu podobný. Podobným pravidlem je, že tento soubor, který
reprezentuje modul v jazyce Python musí mít jen omezenou velikost (v bytech).

V neposlední řadě podléhá celý tento modul striktním pravidlům co do názvu.
V defaultním pojetí musí modul nést název počínající řetězcem 'program_' a
dále končící koncovkou '.py'. Příkladně tedy 'program_franta_voprsalek.py'
je validní název, ale třeba 'franta_voprsalek.py' již považován jako validní
plugin nebude a tedy nebude ani načten.
"""

# Import potřebných zdrojů a nástrojů
from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import Robot

# Import zdrojů, které jsou vyžadovány jen v případě vlastní definice osazení
# from src.fw.robot.unit import AbstractUnit
# from typing import Iterable

# Jméno autora, který je odpovědný za daný program
_AUTHOR_NAME = ""


class Program(AbstractProgram):
    """Šablonová třída implementující svého předka ('AbstractProgram'),
    co do jeho abstraktní funkce 'run(Robot)'.

    Kromě této metody je však možné upravit implementaci procedury pro
    osazování robota. To je vhodné, když je třeba změnit strategii osazení.
    Například jsou-li poskytnuty jednotky, které nejsou třeba. V defaultním
    nastavení totiž je tato procedura nastavena na osazení robota všemi
    dostupnými jednotkami.

    Tuto proceduru lze upravit přidáním následujícího kusu kódu jako metodu
    tohoto programu; automaticky bude zavolána v přípravné fázi robota:

    def mount(self, robot: "robot_module.Robot",
              available_units: "Iterable[unit_module.AbstractUnit]"):
        # kód pro osazení robota jednotkami

    K tomu je důležité taky odstranit křížky ('#', komentáře) před importem
    potřebných knihoven (v horní části tohoto modulu).
    """

    def run(self, robot: "Robot"):
        """Šablona metody, která se stará o definici sekvence akcí, které
        má robot provést.

        K tomu, aby robot mohl interagovat se světem, používá svých jednotek,
        které můžeme řadit na aktuátory (instance třídy 'Actuator') a senzory
        (instance třídy 'Sensor').

        Zatímco aktuátory mají za cíl provést nějakou akci ve světě (pomocí
        své metody 'execute'), senzory mají zase za cíl vrátit nějakou
        použitelnou informaci o prostředí robota (pomocí své metody 'scan').

        Řetězením těchto interakcí se pak robot snaží vyřešit zadanou úlohu
        a splnit tak své poslání."""


def get_program():
    """Tovární (přístupová) funkce, která vrací zcela novou instanci programu.

    Tato funkce má pevně stanovený název, čehož se využívá v rámci dynamického
    importování pluginů; v tomto případě pluginu programu. Pokud by se název
    této přístupové funkce neshodoval s předepsaným a vyhledávaným názvem,
    nebude tento modul považovaný za validní a použitelný plugin programu a
    z titulu loaderu programů bude tento vyhodnocen jako potenciálně rizikový.
    """
    return Program(_AUTHOR_NAME)



