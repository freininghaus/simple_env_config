import contextlib
import unittest
import unittest.mock

from simple_env_config import env_config, CanOnlyDecorateClasses


@contextlib.contextmanager
def patch_env(env):
    with unittest.mock.patch("os.environ", env):
        yield


class TestEnvConfig(unittest.TestCase):

    def test_env_config_str(self):
        env = {
            "VALUE1": "ABC",
            "VALUE3": "XYZ"
        }

        with patch_env(env):
            @env_config
            class A:
                VALUE1: str
                VALUE2 = "default"  # type 'str' is optional
                VALUE3 = "overwrite"  # value is overwritten by env var

            self.assertEqual("ABC", A.VALUE1)
            self.assertEqual("default", A.VALUE2)
            self.assertEqual("XYZ", A.VALUE3)

    def test_env_config_int(self):
        env = {
            "INT_42": "42",
            "INT_99": "99"
        }

        with patch_env(env):
            @env_config
            class A:
                INT_42: int
                INT_77: int = 77
                INT_99: int = 100  # value is overwritten by env var

        self.assertEqual(42, A.INT_42)
        self.assertEqual(77, A.INT_77)
        self.assertEqual(99, A.INT_99)

    def test_env_config_float(self):
        env = {
            "TEN": "10",
            "ANSWER": "42",
            "HALF": "0.5",
            "MILLION": "1e6"
        }

        with patch_env(env):
            @env_config
            class A:
                TEN: float
                ANSWER: float = 9.9  # value is overwritten by env var
                HALF: float
                MILLION: float
                BILLION: float = 1e9

            self.assertEqual(10.0, A.TEN)
            self.assertEqual(42.0, A.ANSWER)
            self.assertEqual(0.5, A.HALF)
            self.assertEqual(1_000_000.0, A.MILLION)
            self.assertEqual(1_000_000_000.0, A.BILLION)

    def test_env_config_bool(self):
        truth_values = {
            True: ("1", "TRUE", "True", "true", "YES", "Yes", "yes", "ON", "On", "on"),
            False: ("0", "FALSE", "False", "false", "NO", "No", "no", "OFF", "Off", "off")
        }

        for expected_bool, string_values in truth_values.items():
            for string_value in string_values:
                env = {
                    key: string_value
                    for key in ("VALUE1", "VALUE2", "VALUE3")
                }

                with self.subTest(f"{expected_bool=} {string_value=}"), patch_env(env):
                    @env_config
                    class A:
                        VALUE1: bool
                        VALUE2: bool = True
                        VALUE3: bool = False
                        VALUE_TRUE: bool = True  # not overwritten by env var
                        VALUE_FALSE: bool = False  # not overwritten by env var

                    self.assertEqual(expected_bool, A.VALUE1)
                    self.assertEqual(expected_bool, A.VALUE2)
                    self.assertEqual(expected_bool, A.VALUE3)

                    self.assertTrue(A.VALUE_TRUE)
                    self.assertFalse(A.VALUE_FALSE)

    def test_invalid_type(self):
        with self.assertRaises(CanOnlyDecorateClasses):
            @env_config
            def f():
                pass


if __name__ == '__main__':
    unittest.main()
