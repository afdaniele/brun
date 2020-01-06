import sys
from .logger import get_logger

__version__ = '0.1.7'


# get logger
brlogger = get_logger()

# import CLI entrypoint
from .cli import run
