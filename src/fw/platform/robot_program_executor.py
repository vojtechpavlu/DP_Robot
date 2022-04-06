"""Modul obsahuje definici exekutoru programu robota. Pomocí toho je možné
ve vícevláknovém prostředí spustit program při zachování integrity celého
systému."""


# Import lokálních knihoven
import src.fw.robot.robot as robot_module
import src.fw.robot.program as program_module


class RobotProgramExecutor:
    """Instance této třídy umožňují obalit samotný běh programu konkrétního
    robota. Jejich cílem je vytvořit izolované prostředí, které umožňuje
    běh programu i v rámci vícevláknové interakci při odchytávání vzniklých
    výjimek a to bez použití systémových prostředků pro mezivláknovou
    komunikaci."""

    def __init__(self, program: "program_module.AbstractProgram",
                 robot: "robot_module.Robot"):
        """Initor, který přijímá v parametrech program, který má být spuštěn,
        a robota, pro který má tento program běžet.

        Dále iniciuje pole pro výjimku, které slouží k uchování chyby, ke
        které během exekuce programu došlo.
        """
        self._program = program
        self._robot = robot
        self.__exception = None

    @property
    def raised_exception(self) -> "Exception":
        """Vlastnost vrací výjimku, která byla vyhozena při exekuci programu.
        """
        return self.__exception

    @property
    def raised_any(self) -> bool:
        """Vlastnost vrací, zda-li byla doposud evidována nějaká výjimka.
        Pro správné fungování a správný způsob použití této vlastnosti je
        pochopitelně zapotřebí, aby byl předtím spuštěn a zcela dokončen
        program. Pokud tomu tak nebude, vrací defaultně False."""
        return self.__exception is not None

    @property
    def program(self) -> "program_module.AbstractProgram":
        """Vlastnost vrací program, který má být spuštěn."""
        return self._program

    @property
    def robot(self) -> "robot_module.Robot":
        """Vlastnost vrací robota, pro kterého má být robot spuštěn."""
        return self._robot

    def run_program(self):
        """Funkce 'run_program' se stará o samotnou exekuci programu. Její
        tělo se stará o spuštění daného programu v 'bezpečném módu', přesněji
        obalenou v try-except konstrukci.

        Odchycené výjimky (toho nejobecnějšího typu, tedy 'Exception') jsou
        pouze uloženy do vlastní evidence a dále poskytovány v rámci této
        instance pomocí příslušné vlastnosti.
        """

        # Před spuštěním samotného programu je třeba chviličku počkat,
        # aby se systém dokázal zcela připravit na všechny okolnosti běhu
        from time import sleep
        sleep(0.05)

        try:
            # Spuštění dodaného programu s dodaným robotem
            self.program.run(self.robot)

        # Odchycení výjimky, která se může během exekuce vyskytnout
        except Exception as e:
            self.__exception = e
