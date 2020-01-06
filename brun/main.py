import sys
import time
import signal
import logging
import subprocess

from enum import Enum
from threading import Timer

from . import brlogger, cprint
from .lib import Config, CLISyntaxError
from .utils import Pool
from .constants import *



class AppStatus(Enum):
    INITIALIZING = 1
    RUNNING = 2
    ABORTING = 3
    KILLING = 4
    DONE = 10


class Brun():

    _status = AppStatus.INITIALIZING
    _sigint_counter = 0
    _sigint_received_time = None


    def __init__(self, args):
        self.status(AppStatus.INITIALIZING)
        self._setup_signal_handler()
        self.args = args
        # ---
        # configure logger
        if self.args.suppress_warnings:
            brlogger.addFilter(lambda e: e.levelno != logging.WARNING)
        if self.args.debug:
            brlogger.setLevel(logging.DEBUG)
        if self.args.suppress_warnings and self.args.debug:
            brlogger.info('Warnings cannot be suppressed when --debug is active.')
        # turn fields and groups into lists
        if 'field' in self.args:
            self.args.field = [self.args.field] if not isinstance(self.args.field, list) else self.args.field
        self.args.group = [self.args.group] if not isinstance(self.args.group, list) else self.args.group
        # parse brun configuration
        try:
            self.config = Config(self.args)
        except CLISyntaxError as e:
            brlogger.error(str(e))
            parser.print_help()
            exit(-1)
        except Exception as e:
            brlogger.error(str(e))
            exit(-2)
        # define number of workers
        num_workers = self.args.parallel if self.args.parallel != -1 else len(self.config)
        self.num_workers = min(MAX_PARALLEL_WORKERS, max(1, num_workers))
        self.is_parallel = num_workers > 1


    def start(self):
        self.status(AppStatus.RUNNING)
        # add commands to the pool
        pool = Pool(self.num_workers)
        for cc in self.config:
            cmd = cc.apply(self.args.command)
            pool.enqueue(self._worker_task, cmd)
        # start pool
        pool.run()
        # monitor the status of the app
        while (pool.alive() and not pool.idle()) or (not pool.done()):
            self._update_status()
            # Status: ABORTING
            if self.status() == AppStatus.ABORTING:
                pool.abort()
            # Status: KILLING
            if self.status() == AppStatus.KILLING:
                brlogger.warning('Escalating to KILL...')
                sys.exit(1)
            # breath
            time.sleep(1.0 / APP_HEARTBEAT_HZ)
        # ---
        brlogger.info('Done!')


    def status(self, status=None):
        if status and not isinstance(status, AppStatus):
            raise ValueError(f'Invalid status {status}')
        if status:
            self._status = status
        return self._status


    def abort(self):
        self.status(AppStatus.ABORTING)


    def kill(self):
        self.status(AppStatus.KILLING)


    def _update_status(self):
        # escalate SIGINT -> SIGKILL ater some time
        s = self._sigint_received_time
        if s and time.time() - s > ESCALATE_TO_KILL_AFTER_SECS:
            self.status(AppStatus.KILLING)


    def _worker_task(self, cmd, print=False):
        stdout = subprocess.PIPE if self.is_parallel else sys.stdout
        cprint(PARALLEL_TO_START_PROMPT_STRING[self.is_parallel].format(" ".join(cmd)))
        brlogger.debug(f'Running command: {cmd}')
        if not self.args.dry_run:
            error = None
            try:
                no_sigint = lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
                res = subprocess.run(' '.join(cmd), check=True, shell=True, stdout=stdout, preexec_fn=no_sigint)
                if self.is_parallel and print:
                    cprint(res.stdout.decode('utf-8'))
            except subprocess.CalledProcessError as e:
                error = e
            if error:
                if not self.args.ignore_errors:
                    raise error
                brlogger.warning(f'The command "{cmd}" failed with error:\n{error}')
        cprint(PARALLEL_TO_END_PROMPT_STRING[self.is_parallel].format(" ".join(cmd)))


    def _setup_signal_handler(self):
        # create signal handler function
        def signal_handler(sig, frame):
            self._sigint_counter += 1
            if self.status() == AppStatus.INITIALIZING:
                # just exit if still initializing
                sys.exit(0)
            if self.status() == AppStatus.RUNNING:
                # shutdown app (if running)
                brlogger.warning(' Request of interruption received. Waiting for tasks to finish...')
                brlogger.warning(' (Press Ctrl+C three times to force kill)')
                self.abort()
            elif self.status() == AppStatus.ABORTING and self._sigint_counter == 3:
                # kill app if already aborting
                self.kill()
        # register signal handler
        signal.signal(signal.SIGINT, signal_handler)
