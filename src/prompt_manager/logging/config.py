import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from prompt_manager.config.models import AppConfig
from prompt_manager.logging.filters import ConsoleDependencyFilter, FileDependencyFilter
from prompt_manager.logging.formatters import ConsoleFormatter, JSONFormatter
from prompt_manager.logging.handlers import RichConsoleHandler
from prompt_manager.paths import LOG_DIR, LOG_FILE


def get_log_file_path() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_FILE


def configure_logging(config: AppConfig):
    file_config = config.logging.file
    console_config = config.logging.console

    # get root logger
    logger = logging.getLogger()

    # remove existing handlers
    # if logger.hasHandlers():
    #    logger.handlers.clear()
    for hander in logger.handlers[:]:
        hander.close()
        logger.removeHandler(hander)
    # logger.propagate = False

    # define the logger, once with a console handler and once with a file handler
    console_handler = RichConsoleHandler()

    file_handler = TimedRotatingFileHandler(
        filename=str(get_log_file_path()),
        when=file_config.rotation,
        interval=1,
        backupCount=file_config.retain_days,
        utc=file_config.utc_time,
    )

    # get filter instances
    console_dependeny_filter: ConsoleDependencyFilter = ConsoleDependencyFilter(
        console_config=console_config
    )
    file_dependency_filter: FileDependencyFilter = FileDependencyFilter(
        file_config=file_config
    )

    # console handler config
    console_handler.setFormatter(ConsoleFormatter())
    console_handler.addFilter(console_dependeny_filter)
    console_handler.setLevel(logging.DEBUG)

    # file handler config
    file_handler.setFormatter(JSONFormatter())
    file_handler.addFilter(file_dependency_filter)
    file_handler.setLevel(logging.DEBUG)

    # add handler and level to root logger
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
