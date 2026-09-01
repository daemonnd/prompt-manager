import logging

from promp_manager.logging.formatters import get_style
from rich.console import Console


class RichConsoleHandler(logging.Handler):
    """
    Class for logging colorful in the console
    """

    def __init__(self):
        super().__init__()
        self.console = Console()

    def emit(self, record):
        message = self.format(record)
        style: str = get_style(levelname=record.levelname)
        self.console.print(message, style=style)
