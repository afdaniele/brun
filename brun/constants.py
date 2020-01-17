import multiprocessing

_RED = b'\x1b[31m'
_GREY = b'\x1b[30m'
_BOLD = b'\x1b[1m'
_RESET = b'\x1b[0m'

NUMBER_OF_CORES = multiprocessing.cpu_count()

DEFAULT_COMBINATOR = 'cross'

PARALLEL_TO_START_PROMPT_STRING = {True: ':brun: Starting > {0}', False: ':brun:> {0}'}

PARALLEL_TO_FAILURE_PROMPT_STRING = {True: ':brun: Failed < {0}', False: ':brun:< {0}\n\n\n'}

PARALLEL_TO_END_PROMPT_STRING = {True: ':brun: Finished < {0}', False: ':brun:< {0}\n\n\n'}

TASK_OUTPUT_TEMPLATE = (b"""
%s-- Output: ({cmd}) -------------------------------------------------------------
{content}
-- Output: ({cmd}) -------------------------------------------------------------%s\n
""" % (_BOLD + _GREY, _RESET)).decode('utf-8')

TASK_ERROR_TEMPLATE = (b"""
%s-- Error: ({cmd}) -------------------------------------------------------------
{content}
-- Error: ({cmd}) -------------------------------------------------------------%s\n
""" % (_RED, _RESET)).decode('utf-8')

DEFAULT_FIELD = ('_builtin_field', 'json', '.brun')

ESCALATE_TO_KILL_AFTER_SECS = 10

APP_HEARTBEAT_HZ = 10
