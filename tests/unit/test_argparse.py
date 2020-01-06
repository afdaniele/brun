import unittest
import brun

COMMAND = ['--', 'echo']


class TestArgparse(unittest.TestCase):
    def setUp(self):
        self.parser = brun.cli.get_parser()

    def test_field_empty(self):
        parsed = self.parser.parse_args([] + COMMAND)
        self.assertTrue('field' not in parsed)

    def test_field_single(self):
        field = ['x:list:1,2']
        parsed = self.parser.parse_args(['-f', field[0]] + COMMAND)
        self.assertEqual(parsed.field, field)

    def test_field_multi(self):
        fields = ['x:list:1,2', 'y:list:3,4,5']
        parsed = self.parser.parse_args(['-f', fields[0], '-f', fields[1]] + COMMAND)
        self.assertEqual(parsed.field, fields)


if __name__ == '__main__':
    unittest.main()
