import sys
import argparse
import logging
import subprocess

from . import brlogger, cprint, __version__
from .lib import Config
from .utils import Pool
from .constants import *


def run():
    parser = _get_parser()
    # ---
    # version
    if '-v' in sys.argv[1:] or '--version' in sys.argv[1:]:
        print(f'brun version {__version__}\n')
        exit(0)
    # ---
    # parse arguments
    parsed = parser.parse_args()
    # ---
    # configure logger
    if parsed.suppress_warnings:
        brlogger.addFilter(lambda e: e.levelno != logging.WARNING)
    if parsed.debug:
        brlogger.setLevel(logging.DEBUG)
    if parsed.suppress_warnings and parsed.debug:
        brlogger.info('Warnings cannot be suppressed when --debug is active.')
    # turn fields and groups into lists
    parsed.field = [parsed.field] if not isinstance(parsed.field, list) else parsed.field
    parsed.group = [parsed.group] if not isinstance(parsed.group, list) else parsed.group
    # parse brun configuration
    try:
      config = Config(parsed)
    except Exception as e:
      brlogger.error(str(e))
      exit(-1)
    # define number of workers
    num_workers = parsed.parallel if parsed.parallel != -1 else len(config)
    num_workers = min(MAX_PARALLEL_WORKERS, max(1, num_workers))
    is_parallel = num_workers > 1
    # add commands to the pool
    pool = Pool(num_workers)
    for cc in config:
        cmd = cc.apply(parsed.command)
        pool.enqueue(_worker_task, cmd, parsed, is_parallel=is_parallel)
    # start pool and wait
    pool.run()
    pool.join()
    # ---
    brlogger.info('Done!')


def _worker_task(cmd, parsed, is_parallel, print=False):
    stdout = subprocess.PIPE if is_parallel else sys.stdout
    cprint(PARALLEL_TO_START_PROMPT_STRING[is_parallel].format(" ".join(cmd)))
    brlogger.debug(f'Running command: {cmd}')
    if not parsed.dry_run:
        error = None
        try:
            res = subprocess.run(cmd, check=True, stdout=stdout)
            if is_parallel and print:
                cprint(res.stdout.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            error = e
        if error:
            if not parsed.ignore_errors:
                raise error
            brlogger.warning(f'The command "{cmd}" failed with error:\n{error}')
    cprint(PARALLEL_TO_END_PROMPT_STRING[is_parallel].format(" ".join(cmd)))

def _get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--field',
        action='append',
        default=[],
        help="Specify a field (syntax: 'name:type:args')"
    )
    parser.add_argument(
        '-g', '--group',
        action='append',
        default=['cross:*,*'],
        help="Group two or more fields together according to a combination strategy (syntax: 'strategy:field1,field2[,...]')"
    )
    parser.add_argument(
        '-p', '--parallel',
        const=-1,
        default=1,
        action='store',
        nargs='?',
        type=int,
        help="How many commands can run in parallel"
    )
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        default=False,
        help="Whether to run the commands in interactive mode"
    )
    parser.add_argument(
        '-d', '--daemon',
        action='store_true',
        default=False,
        help="Whether to deamonize the commands"
    )
    parser.add_argument(
        '-D', '--dry-run',
        action='store_true',
        default=False,
        help="Performs a dry-run. It shows which commands would run"
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help="Run in debug mode"
    )
    parser.add_argument(
        '--suppress-warnings',
        action='store_true',
        default=False,
        help="Suppress warnings"
    )
    parser.add_argument(
        '-I', '--ignore-errors',
        action='store_true',
        default=False,
        help="Do not stop if one command fails"
    )
    parser.add_argument(
        'command',
        nargs='+'
    )
    return parser
