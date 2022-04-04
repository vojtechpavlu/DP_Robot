"""Šablona pluginu definující program. Její význam je v zjednodušení přístupu
k vytváření pluginů tohoto typu.

K tomu nejjednoduššímu použití je třeba vyplnit de facto jen jméno autora
a proceduru, která má být v rámci běhu programu spuštěna (tedy metoda
'run(Robot)').

Dále je třeba, aby v tomto modulu byla definována přístupová tovární funkce,
která na zavolání bude vracet instanci tohoto programu. V defaultním pojetí
je tato pojmenována 'get_program' a její název je takto důsledně vyžadován."""


from src.fw.robot.program import AbstractProgram
from src.fw.robot.robot import Robot

# Jméno autora
_AUTHOR_NAME = ""


class Program(AbstractProgram):
    """Šablonová třída implementující svého předka ('AbstractProgram'),
    co do jeho abstraktní funkce 'run(Robot)'."""

    def run(self, robot: "Robot"):
        """"""


def get_program():
    """"""
    return Program(_AUTHOR_NAME)



