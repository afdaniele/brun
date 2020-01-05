import os
import brun
import unittest
from itertools import product
from functools import reduce

from utils import IterableNamespace, get_sandbox


class TestConfig(unittest.TestCase):

    def _get_config(self, field, group=[]):
        args = lambda a: ','.join([str(e) for e in a])
        field = [':'.join([f[0], f[1], args(f[2])]) for f in field]
        parsed = IterableNamespace(
            field=field,
            group=group
        )
        return brun.lib.Config(parsed)

    def test_default_field(self):
        sbox = get_sandbox(2)
        p = os.getcwd()
        os.chdir(sbox)
        command = "echo {key}"
        try:
            cfg = brun.lib.Config(IterableNamespace(group=[]))
            commands1 = ['echo 1', 'echo 2']
            commands2 = [' '.join(c.apply(command.split(' '))) for c in cfg]
            self.assertEqual(commands1, commands2)
        finally:
            os.chdir(p)

    def test_no_group(self):
        fields = [('x', 'list', [1,2])]
        cfg = self._get_config(fields)
        self.assertEqual(len(fields[0][2]), len(cfg))

    def test_default_group(self):
        fields = [('x', 'list', [1,2]), ('y', 'list', [3,4,5])]
        cfg = self._get_config(fields)
        prod = reduce(lambda p, n: p*n, [len(f[2]) for f in fields])
        self.assertEqual(prod, len(cfg))

    def test_command_single_field(self):
        fields = [('x', 'list', [1,2])]
        command = 'echo {x}'
        commands1, commands2 = _get_commands(self, fields, command)
        self.assertEqual(commands1, commands2)

    def test_command_multi_field(self):
        fields = [('x', 'list', [1,2]), ('y', 'list', [3,4,5])]
        command = 'echo {x}:{y}'
        commands1, commands2 = _get_commands(self, fields, command)
        self.assertEqual(commands1, commands2)


def _get_commands(test, fields, command):
    cfg = test._get_config(fields)
    values = product(*[f[2] for f in fields])
    command_pos = command.format(**{f[0]: '{}' for f in fields})
    commands1 = set([command_pos.format(*v) for v in values])
    commands2 = set([' '.join(c.apply(command.split(' '))) for c in cfg])
    return commands1, commands2


if __name__ == '__main__':
    unittest.main()
