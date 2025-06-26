import logging
from rich.logging import RichHandler

log = logging
log.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler()])
