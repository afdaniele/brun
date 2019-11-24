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
        msg = 'The field type "glob" takes the following arguments: ' + \
              'path[,query[,filter-type]]'
        raise ValueError(msg)
    # ---
    path = args[0]
    if not os.path.exists(path):
        msg = f'The path "{path}" does not exist.'
        raise ValueError(msg)
    if not os.path.isdir(path):
        msg = f'The path "{path}" is not a directory.'
        raise ValueError(msg)
    # ---
    query = '*' if len(args) <= 1 else args[1]
    # ---
    type = '*' if len(args) <= 2 else args[2].strip()
    if type not in type_to_fcn_map:
      msg = f'Unknown type "{type}" for filter-type argument. Allowed {list(type_to_fcn_map.keys())}'
      raise ValueError(msg)
    filter_type = type_to_fcn_map[type]
    # ---
    glob_query = os.path.join(path, query)
    return [
      os.path.basename(p)
      for p in glob.glob(glob_query)
      if filter_type(p)
    ]
