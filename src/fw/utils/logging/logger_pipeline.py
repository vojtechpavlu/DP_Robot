""""""

# Import lokálních knihoven
import src.fw.utils.logging.logger as logger_module

class LoggerPipeline:
    """"""

    def __init__(self, logger: "logger_module.Logger", context: str):
        """"""
        self._logger = logger
        self._context = context.upper()

    @property
    def logger(self) -> "logger_module.Logger":
        """"""
        return self._logger

    @property
    def context(self) -> str:
        """"""
        return self._context

    def log(self, message: str):
        """"""
        self._logger.log(self._context, message)

