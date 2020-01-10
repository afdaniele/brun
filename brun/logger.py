import os
import sys
import time
import logging
import threading

from queue import Queue


def get_logger(console):
    # create logger
    logging.basicConfig()
    logger = BrLogger(console, 'brun', logging.INFO)
    return logger


class BrLogger(logging.Logger):
    def __init__(self, console, name, level=logging.NOTSET):
        super(BrLogger, self).__init__(name, level)
        self.console = console

    def _log(self, lvl, msg, *args, **kwargs):
        pre = ''
        if 'step' in kwargs:
            pre = '[{}] '.format(kwargs['step'])
        # build message
        if not msg.endswith('\n'):
            msg += '\n'
        if 'clear' in kwargs and kwargs['clear']:
            out = msg
        else:
            out = '{}:{}{}'.format(logging._levelToName[lvl], pre, msg)
        # add message to buffer
        self.console.write(out)
        # force flush
        self.console.flush()
