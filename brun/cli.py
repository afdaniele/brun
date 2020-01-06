import sys
import argparse

from .main import Brun
from . import __version__


def run():
    parser = get_parser()
    # ---
    # version
    if '-v' in sys.argv[1:] or '--version' in sys.argv[1:]:
        print(f'brun version {__version__}\n')
        exit(0)
    # ---
    # parse arguments
    parsed = parser.parse_args()
    # create app and spin it
    app = Brun(parsed)
    app.start()


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--field',
        action='append',
        default=argparse.SUPPRESS,
        help="Specify a field (syntax: 'name:type[:args]')"
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
