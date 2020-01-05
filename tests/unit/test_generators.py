import unittest
import brun
from utils import stringify, get_sandbox, get_sandbox_object
from datetime import datetime

from brun.generators.json import JSONInputError
from json.decoder import JSONDecodeError



class TestGenerators(unittest.TestCase):

    def _get_generator(self, generator_name):
        return brun.generators._get_generator(generator_name)

    # Generator: List

    def test_gen_list_alias(self):
        gen1 = self._get_generator('l')
        gen2 = self._get_generator('list')
        self.assertEqual(gen1, gen2)

    def test_gen_list_no_args(self):
        gen = self._get_generator('list')
        self.assertEqual(gen(['']), [])

    def test_gen_list_one_element(self):
        gen = self._get_generator('list')
        self.assertEqual(gen(['1']), ['1'])

    def test_gen_list_generic(self):
        gen = self._get_generator('list')
        self.assertEqual(gen(['1,2,3,4,5']), ['1','2','3','4','5'])


    # Generator: Range

    def test_gen_range_alias(self):
        gen1 = self._get_generator('r')
        gen2 = self._get_generator('range')
        self.assertEqual(gen1, gen2)

    def _test_gen_range(self, *args):
        gen = self._get_generator('range')
        range1 = gen([','.join(stringify(args))])
        range2 = stringify(range(*args))
        return range1, range2

    def test_gen_range_start_only(self):
        self.assertEqual(*self._test_gen_range(9))

    def test_gen_range_start_end_only(self):
        self.assertEqual(*self._test_gen_range(9, 20))

    def test_gen_range_full(self):
        self.assertEqual(*self._test_gen_range(9, 1, 20))
        self.assertEqual(*self._test_gen_range(9, 2, 20))
        self.assertEqual(*self._test_gen_range(9, 3, 20))


    # Generator: File

    def test_gen_file_alias(self):
        gen1 = self._get_generator('f')
        gen2 = self._get_generator('file')
        self.assertEqual(gen1, gen2)

    def test_gen_file_empty_file(self):
        gen = self._get_generator('file')
        filepath = get_sandbox_object(1, 'f0.ini')
        self.assertEqual([], gen([filepath]))

    def test_gen_file_oneline_file(self):
        gen = self._get_generator('file')
        filepath = get_sandbox_object(1, 'f1.txt')
        self.assertEqual(['line1'], gen([filepath]))

    def test_gen_file_twoline_file(self):
        gen = self._get_generator('file')
        filepath = get_sandbox_object(1, 'f2.txt')
        self.assertEqual(['line1', 'line2'], gen([filepath]))

    def test_gen_file_full(self):
        gen = self._get_generator('file')
        filepath = get_sandbox_object(1, 'f3.dat')
        self.assertEqual(['line1', 'line2', 'line3'], gen([filepath]))


    # Generator: Glob

    def test_gen_glob_alias(self):
        gen1 = self._get_generator('g')
        gen2 = self._get_generator('glob')
        self.assertEqual(gen1, gen2)

    def test_gen_glob_pathonly_emptydir(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox_object(1, 'd0')
        self.assertEqual([], gen([dirpath]))

    def test_gen_glob_pathonly_onefiledir(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox_object(1, 'd1')
        self.assertEqual(['f1'], gen([dirpath]))

    def test_gen_glob_pathonly_twofiledir(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox_object(1, 'd2')
        self.assertEqual(['f1', 'f2'], gen([dirpath]))

    def test_gen_glob_pathonly_fulldir(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox(1)
        expected_output = ['d0', 'd1', 'd2', 'f0.ini', 'f1.txt', 'f2.txt', 'f3.dat']
        self.assertEqual(expected_output, gen([dirpath]))

    def test_gen_glob_path_and_query_1(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox(1)
        expected_output = ['d0', 'd1', 'd2']
        args = '{},{}'.format(dirpath, 'd*')
        self.assertEqual(expected_output, gen([args]))

    def test_gen_glob_path_and_query_2(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox(1)
        expected_output = ['f1.txt', 'f2.txt']
        args = '{},{}'.format(dirpath, 'f*.txt')
        self.assertEqual(expected_output, gen([args]))

    def test_gen_glob_path_and_query_3(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox(1)
        expected_output = ['f0.ini', 'f1.txt', 'f2.txt', 'f3.dat']
        args = '{},{}'.format(dirpath, 'f*')
        self.assertEqual(expected_output, gen([args]))

    def test_gen_glob_allargs_test_defaults_1(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox(1)
        expected_output = ['d0', 'd1', 'd2', 'f0.ini', 'f1.txt', 'f2.txt', 'f3.dat']
        args = '{},{}'.format(dirpath, '*')
        self.assertEqual(expected_output, gen([args]))

    def test_gen_glob_allargs_test_defaults_2(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox(1)
        expected_output = ['d0', 'd1', 'd2', 'f0.ini', 'f1.txt', 'f2.txt', 'f3.dat']
        args = '{},{},{}'.format(dirpath, '*', '*')
        self.assertEqual(expected_output, gen([args]))

    def test_gen_glob_allargs_files_only(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox(1)
        expected_output = ['f0.ini', 'f1.txt', 'f2.txt', 'f3.dat']
        args = '{},{},{}'.format(dirpath, '*', 'f')
        self.assertEqual(expected_output, gen([args]))

    def test_gen_glob_allargs_dirs_only(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox(1)
        expected_output = ['d0', 'd1', 'd2']
        args = '{},{},{}'.format(dirpath, '*', 'd')
        self.assertEqual(expected_output, gen([args]))

    def test_gen_glob_allargs_files_regex(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox(1)
        expected_output = ['f1.txt', 'f2.txt']
        args = '{},{},{}'.format(dirpath, '*.txt', 'f')
        self.assertEqual(expected_output, gen([args]))

    def test_gen_glob_allargs_dirs_regex(self):
        gen = self._get_generator('glob')
        dirpath = get_sandbox(1)
        expected_output = ['d0', 'd1']
        args = '{},{},{}'.format(dirpath, 'd[0-1]', 'd')
        self.assertEqual(expected_output, gen([args]))


    # Generator: Json

    def test_gen_json_alias(self):
        gen1 = self._get_generator('j')
        gen2 = self._get_generator('json')
        self.assertEqual(gen1, gen2)

    def test_gen_json_missing_file(self):
        gen = self._get_generator('json')
        dirpath = get_sandbox_object(2, 'j99.json')
        self.assertRaises(FileNotFoundError, gen, [dirpath])

    def test_gen_json_empty_file(self):
        gen = self._get_generator('json')
        dirpath = get_sandbox_object(2, 'j0.json')
        self.assertEqual({}, gen([dirpath]))

    def test_gen_json_invalidjson_file(self):
        gen = self._get_generator('json')
        dirpath = get_sandbox_object(2, 'j1.json')
        self.assertRaises(JSONDecodeError, gen, [dirpath])

    def test_gen_json_invalidinput_file_1(self):
        gen = self._get_generator('json')
        dirpath = get_sandbox_object(2, 'j2.json')
        self.assertRaises(JSONInputError, gen, [dirpath])

    def test_gen_json_invalidinput_file_2(self):
        gen = self._get_generator('json')
        dirpath = get_sandbox_object(2, 'j3.json')
        self.assertRaises(JSONInputError, gen, [dirpath])

    def test_gen_json_invalidinput_file_3(self):
        gen = self._get_generator('json')
        dirpath = get_sandbox_object(2, 'j4.json')
        self.assertRaises(JSONInputError, gen, [dirpath])

    def test_gen_json_invalidinput_file_4(self):
        gen = self._get_generator('json')
        dirpath = get_sandbox_object(2, 'j5.json')
        self.assertRaises(JSONInputError, gen, [dirpath])

    def test_gen_json_emptyinput_file(self):
        gen = self._get_generator('json')
        dirpath = get_sandbox_object(2, 'j6.json')
        self.assertEqual({}, gen([dirpath]))

    def test_gen_json_singlekeyinput_file(self):
        gen = self._get_generator('json')
        dirpath = get_sandbox_object(2, 'j7.json')
        expected_output = {'key': [1, 2]}
        self.assertEqual(expected_output, gen([dirpath]))

    def test_gen_json_multikeyinput_file(self):
        gen = self._get_generator('json')
        dirpath = get_sandbox_object(2, 'j8.json')
        expected_output = {'key1': [1, 11, 21], 'key2': [2, 12, 22], 'key3': [3, 13, 23]}
        self.assertEqual(expected_output, gen([dirpath]))



if __name__ == '__main__':
    unittest.main()
