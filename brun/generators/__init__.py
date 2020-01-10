# generator: list
from .list import \
    generate as generator_list, \
    aliases as aliases_list

# generator: range
from .range import \
    generate as generator_range, \
    aliases as aliases_range

# generator: file
from .file import \
    generate as generator_file, \
    aliases as aliases_file

# generator: stdin
from .stdin import \
    generate as generator_stdin, \
    aliases as aliases_stdin

# generator: glob
from .glob import \
    generate as generator_glob, \
    aliases as aliases_glob

# generator: json
from .json import \
    generate as generator_json, \
    aliases as aliases_json

_generators_map = {
    'list': generator_list,
    'range': generator_range,
    'file': generator_file,
    'stdin': generator_stdin,
    'glob': generator_glob,
    'json': generator_json,
}

_generators_map.update({alias: generator_list for alias in aliases_list})
_generators_map.update({alias: generator_range for alias in aliases_range})
_generators_map.update({alias: generator_file for alias in aliases_file})
_generators_map.update({alias: generator_stdin for alias in aliases_stdin})
_generators_map.update({alias: generator_glob for alias in aliases_glob})
_generators_map.update({alias: generator_json for alias in aliases_json})


def _get_generator(gen_name):
    if not gen_name in _generators_map:
        msg = 'Field type "{}" not found!'.format(gen_name)
        raise ValueError(msg)
    # ---
    return _generators_map[gen_name]
