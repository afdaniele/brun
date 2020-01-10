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
        msg = 'The file "{}" does not exist.'.format(filepath)
        raise FileNotFoundError(msg)
    # load file from disk
    try:
        with open(filepath, 'r') as fin:
            data = json.load(fin)
    except json.decoder.JSONDecodeError as e:
        msg = 'The file "{}" must contain a valid JSON. Error: {}'.format(filepath, str(e))
        raise json.decoder.JSONDecodeError(msg, e.doc, e.pos)
    # simple case: empty json
    if len(data) == 0:
        return {}
    _, lst = next(iter(data.items()))
    # check if the file contains a signle key
    if not (len(data) == 1 and isinstance(lst, list)):
        msg = 'The file "{}" must contain a single key with a list of objects as value'.format(
            filepath)
        raise JSONInputError(msg)
    # simple case: empty list
    if len(lst) == 0:
        return {}
    # check if the list contains dictionaries only
    if sum([int(isinstance(e, dict)) for e in lst]) != len(lst):
        msg = 'The file "{}" must contain a single key with a list of objects as value'.format(
            filepath)
        raise JSONInputError(msg)
    # get the prototype of the objects from the first one
    _proto = lambda d: [(k, type(v)) for k, v in d.items()]
    proto = _proto(lst[0])
    # allowed types are [int, float, string]
    for _, t in proto:
        if t not in [int, float, str]:
            msg = 'All the objects in the file "{}" must contain only values of types [int, float, str]'.format(
                filepath)
            raise JSONInputError(msg)
    # check if all the dictionaries contain the same keys => types
    for d in lst:
        if _proto(d) != proto:
            msg = 'All the objects in the file "{}" must share the same prototype'.format(filepath)
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
