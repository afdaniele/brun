import sys
import argparse
import logging

from . import brlogger


def run():
  parser = _get_parser()
  parsed = parser.parse_args()
  # ---
  data = _prepare_data(parsed)
  print(parsed.command)


  brlogger.info('Done!')
  return


def _get_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '-f', '--field',
    default=[],
    help="Specify a field (syntax: 'name:type:args')"
  )
  parser.add_argument(
    '-g', '--group',
    default='cross:*',
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
    'command',
    nargs='+'
  )
  return parser


def _prepare_data(parsed):
  data = []
  return data
