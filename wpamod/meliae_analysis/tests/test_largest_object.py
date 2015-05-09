import tempfile

from unittest import TestCase
from meliae import scanner
from wpamod.meliae_analysis.load_meliae import load_meliae
from wpamod.meliae_analysis.largest_object import largest_object


class TestLargestObject(TestCase):
    def get_temp_file(self):
        return tempfile.NamedTemporaryFile(delete=False, prefix='meliae').name

    def test_largest_object_simple(self):
        output_file = self.get_temp_file()
        test_object = [1, 2, ['foo', 'spam']]
        scanner.dump_all_referenced(output_file, test_object)

        om = load_meliae(output_file)
        result = largest_object(om)

        largest_obj = result[0]

        self.assertEqual(largest_obj.get_type(), 'list')
        self.assertEqual(largest_obj.get_child_types(), ['int', 'list'])
        self.assertEqual(largest_obj.get_child_len(), 3)
