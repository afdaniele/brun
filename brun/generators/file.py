import os

aliases = ['f']

def generate(args):
    if len(args) != 1:
        msg = 'The field type "file" takes a single argument. i.e., the path to a file'
        raise ValueError(msg)
    # ---
    filepath = args[0]
    if not os.path.exists(filepath):
        msg = f'The file "{filepath}" does not exist.'
        raise ValueError(msg)
    # ---
    with open(filepath, 'rt') as fin:
        lines = fin.readlines()
        return [line.strip() for line in lines]
