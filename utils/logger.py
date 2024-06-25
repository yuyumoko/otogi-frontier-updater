import logging
import colorlog


class Logger:
    def __init__(self, name, level=logging.DEBUG):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._setup_handlers()

    def _setup_handlers(self):
        if not self._logger.hasHandlers():
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self._logger.level)
            formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(levelname)-8s %(blue)s[%(asctime)s](%(name)s) - %(log_color)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            )
            console_handler.setFormatter(formatter)

            self._logger.addHandler(console_handler)

    @property
    def logger(self) -> logging.Logger:
        return self._logger


log = Logger("DEBUG").logger


if __name__ == "__main__":
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")
