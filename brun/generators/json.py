import os
import json

aliases = ['j']


def generate(args):
    if len(args) != 1:
        msg = 'The field type "json" takes exactly one argument. i.e., a path to a json file'
        raise ValueError(msg)
    # ---
    # get file path
    filepath = os.path.join(os.getcwd(), args[0])
    # make sure the file exists
    if not os.path.exists(filepath):
        msg = f'The file "{filepath}" does not exist.'
        raise FileNotFoundError(msg)
    # load file from disk
    try:
        with open(filepath, 'r') as fin:
            data = json.load(fin)
    except json.decoder.JSONDecodeError as e:
        msg = f'The file "{filepath}" must contain a valid JSON. Error: {str(e)}'
        raise json.decoder.JSONDecodeError(msg, e.doc, e.pos)
    # simple case: empty json
    if len(data) == 0:
        return {}
    _, lst = next(iter(data.items()))
    # check if the file contains a signle key
    if not (len(data) == 1 and isinstance(lst, list)):
        msg = f'The file "{filepath}" must contain a single key with a list of objects as value'
        raise JSONInputError(msg)
    # simple case: empty list
    if len(lst) == 0:
        return {}
    # check if the list contains dictionaries only
    if sum([int(isinstance(e, dict)) for e in lst]) != len(lst):
        msg = f'The file "{filepath}" must contain a single key with a list of objects as value'
        raise JSONInputError(msg)
    # get the prototype of the objects from the first one
    _proto = lambda d: [(k, type(v)) for k, v in d.items()]
    proto = _proto(lst[0])
    # allowed types are [int, float, string]
    for _, t in proto:
        if t not in [int, float, str]:
            msg = f'All the objects in the file "{filepath}" must contain only values of types [int, float, str]'
            raise JSONInputError(msg)
    # check if all the dictionaries contain the same keys => types
    for d in lst:
        if _proto(d) != proto:
            msg = f'All the objects in the file "{filepath}" must share the same prototype'
            raise JSONInputError(msg)
    # get values
    keys = [k for k, _ in proto]
    values = {k: [] for k in keys}
    for d in lst:
        for k, v in d.items():
            values[k].append(v)
    # ---
    return values


class JSONInputError(RuntimeError):
    def __init__(self, msg):
        super(RuntimeError, self).__init__(msg)
