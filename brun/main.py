import sys
import time
import types
import signal
import logging
import subprocess

from enum import Enum
from threading import Timer

from . import brlogger, brconsole
from .lib import Config, CLISyntaxError
from .utils import Pool
from .constants import *
from .console import restrict_console_access
from .exceptions import TaskFailureError


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
        # configure console
        if not self.args.debug:
            restrict_console_access(brlogger)
        brconsole.set_show_status(not self.args.no_status)
        brconsole.set_plain_console(self.args.debug)
        # turn fields and groups into lists
        if 'field' in self.args:
            self.args.field = [self.args.field] \
                if not isinstance(self.args.field, list) else self.args.field
        self.args.group = [self.args.group] \
            if not isinstance(self.args.group, list) else self.args.group
        # parse brun configuration
        try:
            self.config = Config(self.args)
        except CLISyntaxError as e:
            brlogger.error(str(e))
            exit(-1)
        except Exception as e:
            brlogger.error(str(e))
            exit(-2)
        # define number of workers
        num_workers = self.args.parallel if self.args.parallel != -1 else len(self.config)
        num_workers = min(MAX_PARALLEL_WORKERS, max(1, num_workers))
        self.is_parallel = num_workers > 1
        # create workers pool
        self.pool = Pool(num_workers, self._exception_handler)

    def start(self):
        self.status(AppStatus.RUNNING)
        # add commands to the pool
        for cc in self.config:
            cmd = cc.apply(self.args.command)
            self.pool.enqueue(self._worker_task, cmd)
        # start pool
        self.pool.run()
        # monitor the status of the app
        while (self.pool.alive() and not self.pool.idle()) or (not self.pool.done()):
            self._update_status()
            brconsole.set_progress(self._get_progress())
            # Status: ABORTING
            if self.status() == AppStatus.ABORTING:
                self.pool.abort()
            # Status: KILLING
            if self.status() == AppStatus.KILLING:
                brlogger.warning('Escalating to KILL...')
                sys.exit(1)
            # breath
            time.sleep(1.0 / APP_HEARTBEAT_HZ)
        # update status bar one more time and then stop it
        brconsole.set_progress(self._get_progress())
        brconsole.set_show_status(False)
        # show collected errors
        self._process_tasks_output(stderr_only=(not self.args.verbose))
        # ---
        brlogger.info('Done!')
        brconsole.flush()

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

    def _process_tasks_output(self, stderr_only=False):
        cmds = []
        stdouts = []
        stderrs = []
        # get cmd, stdout, and stderr
        for res in self.pool.results():
            cmd = ' '.join(res.cmd)
            cmds.append(cmd)
            stdouts.append(res.stdout)
            stderrs.append(res.stderr)
        # dump stdout to console
        if not stderr_only:
            for cmd, std in zip(cmds, stdouts):
                if len(std):
                    brconsole.write(TASK_OUTPUT_TEMPLATE.format(cmd=cmd, content=std.rstrip()))
        # dump stderr to console
        for cmd, std in zip(cmds, stderrs):
            if len(std):
                brconsole.write(TASK_ERROR_TEMPLATE.format(cmd=cmd, content=std.rstrip()))

    def _get_progress(self):
        stats = self.pool.get_stats()
        stats['app_status'] = {
            AppStatus.INITIALIZING: 'init',
            AppStatus.RUNNING: 'healthy',
            AppStatus.ABORTING: 'aborting',
            AppStatus.KILLING: 'killing'
        }[self.status()]
        return stats

    def _worker_task(self, cmd):
        cmd_str = ' '.join(cmd)
        stdout = subprocess.PIPE if self.is_parallel else sys.stdout
        result = types.SimpleNamespace(cmd=cmd, stdout="", stderr="")
        # -->
        brlogger.info(PARALLEL_TO_START_PROMPT_STRING[self.is_parallel].format(cmd_str))
        if not self.args.dry_run:
            no_sigint = lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
            # launch task
            task = subprocess.Popen(cmd_str,
                                    shell=True,
                                    stdout=stdout,
                                    stderr=subprocess.PIPE,
                                    preexec_fn=no_sigint)
            # wait for the task to end
            task.wait()
            if self.is_parallel:
                result.stdout = task.stdout.read().decode('utf-8')
            result.stderr = task.stderr.read().decode('utf-8')
            # on failure
            if task.returncode != 0:
                brlogger.info(PARALLEL_TO_FAILURE_PROMPT_STRING[self.is_parallel].format(cmd_str))
                # raise error
                msg = 'The command {} failed with exit code {}.'
                raise TaskFailureError(msg.format(cmd, task.returncode), result)
        # <--
        brlogger.info(PARALLEL_TO_END_PROMPT_STRING[self.is_parallel].format(cmd_str))
        return result

    def _exception_handler(self, name, exception_type, exception, tback, *args, **kwargs):
        # abort remaining tasks
        if not self.args.ignore_errors:
            self.abort()

    def _setup_signal_handler(self):
        # create signal handler function
        def signal_handler(sig, frame):
            self._sigint_counter += 1
            if self.status() == AppStatus.INITIALIZING:
                # just exit if still initializing
                sys.exit(0)
            if self.status() == AppStatus.RUNNING:
                # shutdown app (if running)
                brlogger.warning(
                    ' Request of interruption received. Waiting for tasks to finish...')
                brlogger.warning(' (Press Ctrl+C three times to force kill)')
                self.abort()
            elif self.status() == AppStatus.ABORTING and self._sigint_counter == 3:
                # kill app if already aborting
                self.kill()

        # register signal handler
        signal.signal(signal.SIGINT, signal_handler)
