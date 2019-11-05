aliases = ['l']

def generate(args):
    if len(args) != 1:
        msg = 'The field type "list" takes a single argument. i.e., a comma-separated list'
        raise ValueError(msg)
    # ---
    return args[0].split(',')
