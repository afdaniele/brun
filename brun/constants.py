import multiprocessing

MAX_PARALLEL_WORKERS = multiprocessing.cpu_count()

PARALLEL_TO_START_PROMPT_STRING = {
    True: ':brun: Starting > {0}',
    False: ':brun:> {0}'
}

PARALLEL_TO_FAILURE_PROMPT_STRING = {
    True: ':brun: Failed < {0}',
    False: ':brun:< {0}\n\n\n'
}

PARALLEL_TO_END_PROMPT_STRING = {
    True: ':brun: Finished < {0}',
    False: ':brun:< {0}\n\n\n'
}

DEFAULT_FIELD = ('_builtin_field', 'json', '.brun')

ESCALATE_TO_KILL_AFTER_SECS = 10

APP_HEARTBEAT_HZ = 20
