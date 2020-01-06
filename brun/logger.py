import os
import sys
import time
import logging
import threading

from queue import Queue



def get_logger():
    # create logger
    logging.basicConfig()
    logger = BrLogger('brun', logging.INFO)
    return logger


class BrLogger(logging.Logger):

    def __init__(self, name, level=logging.NOTSET, debug=None):
        super(BrLogger, self).__init__(name, level)
        # redirect stdout to buffer
        self.stdout = sys.stdout
        self.buffer = Queue()
        self.lock = threading.Semaphore(1)
        self.delete_last = False
        self.stime = time.time()
        self.set_debug(debug)

    def set_debug(self, debug):
        if isinstance(debug, bool) and not debug:
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
        self.is_debug = debug

    def _log(self, lvl, msg, *args, **kwargs):
        # build message
        msg = '{}:{}'.format(logging._levelToName[lvl], msg)
        # add message to buffer
        self.buffer.put(msg)
        # continue with the logger business
        super(BrLogger, self)._log(lvl, msg, *args, **kwargs)

    def status_bar(self, progress):
        return "[brun {:.1f} s] [{:d}/{:d} complete] [{:d}/{:d} jobs] [{:d} queued] [{:d} aborted] [{:d} failed]".format(
            time.time() - self.stime,
            progress['tasks_completed'],
            progress['tasks_total'],
            progress['jobs_max']-progress['jobs_idle'],
            progress['jobs_max'],
            progress['tasks_queued'],
            progress['tasks_aborted'],
            progress['tasks_failed'],
        )

    def step(self, progress):
        # get the lock
        self.lock.acquire()
        # clear last line
        if self.delete_last:
            # clear 2 lines
            self.stdout.write("\033[F\033[K" + "\033[F\033[K")
        # dump buffer content on the console
        while not self.buffer.empty():
            line = self.buffer.get()
            self.stdout.write(line + "\033[K" + "\n")
        # print separator then status bar
        self.stdout.write(("-" * 80) + "\n")
        self.stdout.write(self.status_bar(progress) + "\n")
        # flush stdout
        self.stdout.flush()
        self.delete_last = True
        # release the lock
        self.lock.release()
