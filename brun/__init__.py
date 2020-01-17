import sys
from .logger import get_logger
from .console import Console

__version__ = '0.2.4'

# create console
brconsole = Console()

# get logger
brlogger = get_logger(brconsole)

# import CLI entrypoint
from .cli import run
