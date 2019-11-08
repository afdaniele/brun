import logging

__version__ = '0.1.4'

logging.basicConfig()
brlogger = logging.getLogger('brun')
brlogger.setLevel(logging.INFO)

from .main import run
