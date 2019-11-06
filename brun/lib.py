import re
import sys
import argparse
import itertools

from . import brlogger
from .exceptions import CLISyntaxError
from .generators import _get_generator
from .combinators import _get_combinator


class CommandConfig(object):

    def __init__(self, dp_dict=None):
        self._data = dp_dict if dp_dict else dict()

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        return self._data[key]

    def apply(self, command):
        try:
            return [c.format(**self._data) for c in command]
        except KeyError as e:
            msg = f'The command contains a field {e} that was not declared'
        raise CLISyntaxError(msg)

    def __str__(self):
        return self._data.__str__()


class Config(object):

    def __init__(self, parsed):
        self._data = []
        self._fields = dict()
        # parse fields and create their data points
        for field_str in parsed.field:
            # parse field
            name, type, generator_args = _parse_field(field_str)
            # make sure the fields are unique
            if name in self._fields:
                msg = f'Collision between fields. The field {name} was declared more than once.'
                raise ValueError(msg)
            # generate data
            generator = _get_generator(type)
            self._fields[name] = generator(generator_args)
        self._fields_keys = sorted(list(self._fields.keys()))
        # default combination strategy is 'cross'
        combination_map = {k: ('default', None) for k in itertools.product(self._fields_keys, self._fields_keys)}
        # parse groups
        for group_str in parsed.group:
            # parse group
            type, fields, combinator_args = _parse_group(group_str, self._fields_keys)
            # fill in the combination map
            for f1, f2 in itertools.product(fields, fields):
                combination_map[(f1, f2)] = (type, combinator_args)
        # combine fields
        # 1. create one blob for each field
        field_to_blob = {f: i for f,i in zip(self._fields_keys, range(len(self._fields_keys)))}
        blobs = [[(v,) for v in self._fields[f]] for f in self._fields_keys]
        # 2. combine blobs
        for f0, f1 in zip(self._fields_keys, self._fields_keys[1:]):
            next_blob_id = len(blobs)
            type, combinator_args = _get_blob_combinator(self._fields_keys, combination_map, f1)
            combinator = _get_combinator(type)
            blob0, blob1 = blobs[field_to_blob[f0]], blobs[field_to_blob[f1]]
            blobs.append(_flatten_data(combinator(blob0, blob1, combinator_args)))
            field_to_blob[f0] = next_blob_id
            field_to_blob[f1] = next_blob_id
        data = blobs[-1] if blobs else []
        # turn data into CommandConfigs
        for d in data:
            assert len(self._fields_keys) == len(d)
            cc_dict = {k:v for k, v in zip(self._fields_keys, d)}
            cc = CommandConfig(cc_dict)
            self._data.append(cc)

    def __iter__(self):
        return iter(self._data)



def _parse_field(field_str):
    parts = tuple(field_str.split(':'))
    if len(parts) <= 1:
        raise CLISyntaxError(f'Syntax error in field descriptor "{field_str}"')
    # ---
    name, type, *generator_args = parts
    # validate field name
    if not re.search('\w+', name):
        raise CLISyntaxError(f'Field name {name} not valid. Only letters and numbers are allowed')
    # ---
    return name, type, generator_args


def _parse_group(group_str, declared_fields):
    parts = tuple(group_str.split(':'))
    if len(parts) <= 1:
        raise CLISyntaxError(f'Syntax error in group descriptor "{group_str}"')
    # ---
    type, fields, *combinator_args = parts
    # verify fields
    fields = fields.split(',')
    if len(fields) <= 1:
        msg = f'Group descriptor "{group_str}" should have at least two fields, {len(fields)} given'
        raise CLISyntaxError(msg)
    for field in fields:
        if field not in declared_fields + ['*']:
            msg = f'Field "{field}" used in group argument "{group_str}" was not declared'
            raise CLISyntaxError(msg)
    # ---
    return type, fields, combinator_args


def _flatten_data(blob):
    nblob = []
    for e in blob:
        if isinstance(e, (tuple, list)) and isinstance(e[0], (tuple, list)):
            nblob.append(e[0] + e[1])
        else:
            nblob.append(e)
    return nblob


def _get_blob_combinator(fields, combination_map, f1):
    processed_fields = fields[:fields.index(f1)]
    combs_w_f1 = [
        combination_map[(f0, f1)] for f0 in processed_fields if combination_map[(f0, f1)][0] != 'default'
    ]
    if len(combs_w_f1) > 1:
        msg = f'Field "{f1}" is grouped with more than one field. Not supported'
        raise CLISyntaxError(msg)
    # ---
    if len(combs_w_f1) == 0:
        return 'default', None
    return combs_w_f1.pop()
