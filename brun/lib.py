import os
import re
import itertools
import networkx as nx

from . import brlogger
from .exceptions import CLISyntaxError, InvalidConfigurationError
from .generators import _get_generator
from .combinators import _get_combinator
from .constants import *


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
            msg = 'The command contains a field {} that was not declared'.format(e)
        raise CLISyntaxError(msg)

    def __str__(self):
        return self._data.__str__()


class Config(object):
    def __init__(self, parsed):
        self._data = []
        self._fields = dict()
        # use default field if none were given
        if 'field' not in parsed:
            default_json_input_file = os.path.join(os.getcwd(), DEFAULT_FIELD[2])
            if os.path.exists(default_json_input_file):
                parsed.field = [':'.join(DEFAULT_FIELD)]
            else:
                raise CLISyntaxError(
                    "Argument --field/-f is required when the file '.brun' does not exist.")
        # parse fields and create their data points
        for field_str in parsed.field:
            # parse field
            name, type, generator_args = _parse_field(field_str)
            # make sure the fields are unique
            if name in self._fields:
                msg = 'Collision between fields. ' + \
                      'The field {} was declared more than once.'.format(name)
                raise ValueError(msg)
            # generate data
            generator = _get_generator(type)
            values = generator(generator_args)
            if isinstance(values, dict):
                self._fields.update(values)
                # fields that are generated together are naturally grouped using zip
                keys = list(values.keys())
                for k0, k1 in zip(keys, keys[1:]):
                    parsed.group.append('zip:{},{}'.format(k0, k1))
            else:
                self._fields[name] = values
        self._fields_keys = sorted(list(self._fields.keys()))
        # create fields graph
        G = nx.Graph()
        # add nodes
        G.add_nodes_from(self._fields_keys)
        brlogger.debug('Add nodes {}'.format(self._fields_keys))
        # parse groups
        for group_str in parsed.group:
            # parse group
            type, fields, combinator_args = _parse_group(group_str, self._fields_keys)
            # add edges
            for f0, f1 in zip(fields, fields[1:]):
                brlogger.debug('Add edge. Type {} between fields ({}, {})'.format(type, f0, f1))
                G.add_edge(f0, f1, type=type, args=combinator_args)
        # make sure the graph is consistent
        head, tail = _complete_graph(G)
        if not head:
            return
        # get path from head to tail
        paths = list(nx.all_simple_paths(G, source=head, target=tail)) or [[head]]
        if len(paths) > 1:
            raise InvalidConfigurationError('The induced graph has more than one path')
        self._fields_keys = paths[0]
        # combine fields
        data = [(v, ) for v in self._fields[self._fields_keys[0]]] if self._fields_keys else []
        field_to_blob = {f: self._fields[f] for f in self._fields_keys}
        for u, v in zip(self._fields_keys, self._fields_keys[1:]):
            combinator_data = G.get_edge_data(u, v)
            combinator_args = combinator_data['args']
            combinator = _get_combinator(combinator_data['type'])
            blob0, blob1 = field_to_blob[u], field_to_blob[v]
            data = field_to_blob[v] = _flatten_data(combinator(blob0, blob1, combinator_args))
        # turn data into CommandConfigs
        for d in data:
            assert len(self._fields_keys) == len(d)
            cc_dict = {k: v for k, v in zip(self._fields_keys, d)}
            cc = CommandConfig(cc_dict)
            self._data.append(cc)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


def _parse_field(field_str):
    parts = tuple(field_str.split(':'))
    if len(parts) <= 1:
        raise CLISyntaxError('Syntax error in field descriptor "{}"'.format(field_str))
    # ---
    name, type, *generator_args = parts
    # validate field name
    if not re.search('\w+', name):
        raise CLISyntaxError(
            'Field name {} not valid. Only letters and numbers are allowed'.format(name))
    # ---
    return name, type, generator_args


def _parse_group(group_str, declared_fields):
    parts = tuple(group_str.split(':'))
    if len(parts) <= 1:
        raise CLISyntaxError('Syntax error in group descriptor "{}"'.format(group_str))
    # ---
    type, fields, *combinator_args = parts
    # verify fields
    fields = fields.split(',')
    if len(fields) <= 1:
        msg = 'Group descriptor "{}" should have at least two fields, {} given'.format(
            group_str, len(fields))
        raise CLISyntaxError(msg)
    for field in fields:
        if field not in declared_fields + ['*']:
            msg = 'Field "{}" used in group argument "{}" was not declared'.format(
                field, group_str)
            raise CLISyntaxError(msg)
    # ---
    return type, fields, combinator_args


def _flatten_data(blob):
    nblob = []
    for e in blob:
        if isinstance(e, (tuple, list)) and isinstance(e[0], (tuple, list)):
            nblob.append(e[0] + (e[1], ))
        else:
            nblob.append(e)
    return nblob


def _complete_graph(G, default_comb=DEFAULT_COMBINATOR):
    """
    The given groups have added edges to the graph to form several connected components.
    A graph is valid iff all connected components are valid.
    A connected component is valid iff:
        - it has n vertices and exactly n-1 edges
        - the degree of each node is either 1 or 2
    """
    cc = [G.subgraph(c).copy() for c in nx.connected_components(G)]
    cc_degree = [G1.degree() for G1 in cc]
    unitary_nodes = []
    for G1, degree in zip(cc, cc_degree):
        msg = 'Invalid grouping. No loops of forks are allowed. ' + \
              'Invalid grouping found between the fields: {}'.format(G1.nodes)
        e = InvalidConfigurationError(msg, data=set(G1.nodes))
        # check if this connected component is valid
        if G1.number_of_edges() != G1.number_of_nodes() - 1:
            raise e
        for _, d in degree:
            if d not in [0, 1, 2]:
                raise e
        ends = [n for n, d in degree if d in [0, 1]]
        unitary_nodes += ends if len(ends) > 1 else 2 * [ends[0]]
    # all the connected components are valid, add missing edges
    for n0, n1 in zip(unitary_nodes[1:-2], unitary_nodes[2:-1]):
        G.add_edge(n0, n1, type=default_comb, args=None)
    # return head, tail
    return (unitary_nodes[0], unitary_nodes[-1]) if len(unitary_nodes) else (None, None)
