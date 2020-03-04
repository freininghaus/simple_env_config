from unittest import TestCase
from unittest.mock import patch

from simple_env_config import env_config, CanOnlyDecorateClasses


class TestEnvConfig(TestCase):

    def test_env_config(self):
        with patch("os.environ", {"INT_42": 42, "INT_99": 99}):

            @env_config
            class A:
                INT_42: int
                INT_77: int = 77
                INT_99: int = 100  # value is overwritten by env var

        self.assertEqual(42, A.INT_42)
        self.assertEqual(77, A.INT_77)
        self.assertEqual(99, A.INT_99)

    def test_invalid_type(self):
        with self.assertRaises(CanOnlyDecorateClasses):
            @env_config
            def f():
                pass
