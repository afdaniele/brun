import os
import io
import sys
import time
import logging
import threading

from collections import defaultdict

from queue import Queue


def restrict_console_access(logger):
    sys.stdout = ProxyStream(logger, logging.INFO)
    sys.stderr = ProxyStream(logger, logging.ERROR)


class ProxyStream(io.TextIOWrapper):
    def __init__(self, logger, level, *args, **kwargs):
        self._logger = logger
        self._level = level
        self._buffer = ""
        self._lock = threading.Semaphore(1)
        self._disabled = False
        super(ProxyStream, self).__init__(open(os.devnull, 'w'), *args, **kwargs)

    def write(self, s, *args, **kwargs):
        if self._disabled:
            return
        self._lock.acquire()
        self._buffer += s
        lines = self._buffer.split('\n')
        for line in lines[:-1]:
            self._logger._log(self._level, line, None)
        self._buffer = lines[-1]
        self._lock.release()


class Console():
    def __init__(self):
        # redirect stdout to buffer
        self.start_time = time.time()
        self.stdout = sys.stdout
        self.buffer = Queue()
        self.lock = threading.Semaphore(1)
        self.progress = defaultdict(lambda: 0)
        self.has_progress = False
        self.delete_last = False
        self.show_status = None
        self.plain_console = False

    def set_progress(self, progress):
        self.progress.update(progress)
        self.has_progress = True
        self.flush()

    def uptime(self):
        return time.time() - self.start_time

    def set_show_status(self, val):
        self.show_status = val

    def set_plain_console(self, val):
        self.plain_console = val

    def write(self, msg):
        # get the lock
        self.lock.acquire()
        # write to buffer
        self.buffer.put(msg)
        # release the lock
        self.lock.release()

    def flush(self):
        # get the lock
        self.lock.acquire()
        # clear last line
        self._clear_status_bar()
        # dump buffer content on the console
        while not self.buffer.empty():
            line = self.buffer.get()
            self.stdout.write(line + "\033[K")
        # print separator then status bar
        self._print_status_bar()
        # flush stdout
        self.stdout.flush()
        # release the lock
        self.lock.release()

    def close(self):
        self.set_show_status(False)
        # clear status (if any)
        self._clear_status_bar()

    def _clear_status_bar(self):
        if self.delete_last and (not self.plain_console):
            # clear 2 lines
            self.stdout.write("\033[F\033[K" * 2)
            self.delete_last = False
            # flush stdout
            self.stdout.flush()

    def _print_status_bar(self):
        if self.show_status and self.has_progress:
            self.stdout.write(("-" * 80) + "\n")
            self.stdout.write(self._get_status_bar() + "\n")
            self.delete_last = True
            # flush stdout
            self.stdout.flush()

    def _get_status_bar(self):
        return "[brun {:.1f} s] [{:s}] [{:d}/{:d} complete] [{:d}/{:d} jobs] [{:d} queued] [{:d} aborted] [{:d} failed]".format(
            self.uptime(),
            str(self.progress['app_status']),
            self.progress['tasks_completed'],
            self.progress['tasks_total'],
            self.progress['jobs_max'] - self.progress['jobs_idle'],
            self.progress['jobs_max'],
            self.progress['tasks_queued'],
            self.progress['tasks_aborted'],
            self.progress['tasks_failed'],
        )
