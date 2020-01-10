import os
import glob

aliases = ['g']

type_to_fcn_map = {
    '*': lambda e: True,
    'f': os.path.isfile,
    'd': os.path.isdir,
}


def generate(args):
    args = args[0].split(',')
    if len(args) not in [1, 2, 3]:
        raise ValueError('The field type "glob" takes the following arguments: ' + \
                         'path[,query[,filter-type]]'
        )
    # ---
    path = args[0]
    if not os.path.exists(path):
        raise ValueError('The path "{}" does not exist.'.format(path))
    if not os.path.isdir(path):
        raise ValueError('The path "{}" is not a directory.'.format(path))
    # ---
    query = '*' if len(args) <= 1 else args[1]
    # ---
    type = '*' if len(args) <= 2 else args[2].strip()
    if type not in type_to_fcn_map:
        raise ValueError('Unknown type "{}" for filter-type argument. Allowed {}'.format(
            type, list(type_to_fcn_map.keys())))
    filter_type = type_to_fcn_map[type]
    # ---
    glob_query = os.path.join(path, query)
    return sorted([os.path.basename(p) for p in glob.glob(glob_query) if filter_type(p)])
