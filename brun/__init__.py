import logging

__version__ = '0.1'

logging.basicConfig()
brlogger = logging.getLogger('brun')
brlogger.setLevel(logging.INFO)

from .main import run
