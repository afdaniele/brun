import sys

aliases = []

def generate(args):
    if len(args) > 1:
        msg = 'The field type "stdin" takes one optional argument. i.e., a string delimiter (default=\\n)'
        raise ValueError(msg)
    # ---
    sep = '\n'
    if len(args) > 0:
        sep = args[0].strip()
    values = [l.strip().replace('\n', ';') for l in sys.stdin.read().split(sep)]
    # ---
    return list(filter(lambda l: len(l) > 0, values))
