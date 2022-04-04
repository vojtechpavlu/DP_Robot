"""Šablona pluginu definující program. Její význam je v zjednodušení přístupu
k vytváření pluginů tohoto typu.

K tomu nejjednoduššímu použití je třeba vyplnit de facto jen jméno autora
a proceduru, která má být v rámci běhu programu spuštěna (tedy metoda
'run(Robot)').

Dále je třeba, aby v tomto modulu byla definována přístupová tovární funkce,
která na zavolání bude vracet instanci tohoto programu. V defaultním pojetí
je tato pojmenována 'get_program' a její název je takto důsledně vyžadován.
"""

# Import potřebných zdrojů a nástrojů
from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import Robot

# Jméno autora, který je odpovědný za daný program
_AUTHOR_NAME = ""


class Program(AbstractProgram):
    """Šablonová třída implementující svého předka ('AbstractProgram'),
    co do jeho abstraktní funkce 'run(Robot)'."""

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



