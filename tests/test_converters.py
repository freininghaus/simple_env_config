from typing import Union, Optional
from unittest import TestCase

from simple_env_config.converters import optional_type


class Test(TestCase):
    def test_optional_type(self):
        self.assertIsNone(optional_type(int))
        self.assertIsNone(optional_type(str))
        self.assertIsNone(optional_type(Union[int, str]))
        self.assertIsNone(optional_type(Optional[Union[str, int]]))

        self.assertEqual(str, optional_type(Optional[str]))
        self.assertEqual(int, optional_type(Optional[int]))
