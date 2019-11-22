MAX_PARALLEL_WORKERS = 4

PARALLEL_TO_START_PROMPT_STRING = {
    True: ':brun: Starting > {0}',
    False: ':brun:> {0}\n:'
}

PARALLEL_TO_END_PROMPT_STRING = {
    True: ':brun: Finished < {0}',
    False: ':\n:brun:< {0}\n\n\n'
}
