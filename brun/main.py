import sys
import argparse
import logging
import subprocess

from . import brlogger
from .lib import Config


def run():
  parser = _get_parser()
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
  config = Config(parsed)
  # execute command
  for cc in config:
      cmd = cc.apply(parsed.command)
      print(f':brun:> {" ".join(cmd)}\n:')
      brlogger.debug(f'Running command: {cmd}')
      if not parsed.dry_run:
          subprocess.check_call(cmd)
      print(f':\n:brun:< {" ".join(cmd)}\n\n\n')
  # ---
  brlogger.info('Done!')


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
    type=int,
    default=1,
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
    'command',
    nargs='+'
  )
  return parser
