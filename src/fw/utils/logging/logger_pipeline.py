"""Modul umožňuje definovat přístupovou funkci pro poskytování logování bez
nutnosti předat instanci samotného loggeru dodanému objektu, který logování
přímo potřebuje."""

# Import lokálních knihoven
import src.fw.utils.logging.logger as logger_module


class LoggerPipeline:
    """Instance této třídy jsou odpovědné za zpřístupnění funkcionality
    logování bez nutnosti poskytnout nutně i instanci loggeru.

    Zároveň tato funkce umožňuje poskytnutí pouze funkce jako hodnoty,
    kterou lze volat v případě potřeby stanovit kontext logování některým
    objektům.

    Typicky je to použito v programu, kde je třeba, aby robot měl ze svého
    programu možnost provádět logování (např. pro potřeby výstupu), ale
    zároveň mu neodkrývat implementaci loggeru a tu mu nechat ukrytu.

    Realizace je podle návrhového vzoru Prostředník, kdy instance této
    třídy poskytují služby prostředníka mezi loggerem a objektem, který
    obdrží pouze funkci 'log(str)'.
    """

    def __init__(self, logger: "logger_module.Logger", context: str):
        """Initor, který přijímá instanci loggeru, do kterého bude logováno,
        a textový řetězec, který značí stanovený kontext, v jakém bude
        logováno.

        Dodaný název kontextu je převeden na kapitálky, nerozlišuje tedy
        malá a velká písmena.
        """

        # 'Privátní' logger; totální soukromí nelze zcela zajistit
        self.__logger = logger

        # Uložení kontextu v kapitálkách
        self._context = context.upper()

    @property
    def context(self) -> str:
        """Kontext, ve kterém je logováno. Defaultně je v kapitálkách."""
        return self._context

    def log(self, *message: str):
        """Samotná funkce, která se postará o zalogování dodané textové zprávy
        do privátního loggeru."""
        self.__logger.log(self._context, " ".join(map(str, message)))

