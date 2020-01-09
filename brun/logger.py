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
        # build message
        if not msg.endswith('\n'):
            msg += '\n'
        msg = '{}:{}'.format(logging._levelToName[lvl], msg)
        # add message to buffer
        self.console.write(msg)
        # force flush
        self.console.flush()
