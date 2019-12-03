import sys
import logging
import threading

__version__ = '0.1.7'

# define logger
logging.basicConfig()
brlogger = logging.getLogger('brun')
brlogger.setLevel(logging.INFO)

# define concurrent printer function
_print_sem = threading.Semaphore(1)
def cprint(msg, pipe=sys.stdout):
    _print_sem.acquire()
    pipe.write(msg + '\n')
    pipe.flush()
    _print_sem.release()

from .main import run
