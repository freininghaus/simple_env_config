import contextlib
import unittest
import unittest.mock

from simple_env_config import env_config, CanOnlyDecorateClassesError, EnvironmentVariableNotFoundError, \
    CannotConvertEnvironmentVariableError


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

                with self.subTest(f"'{string_value}' -> {expected_bool}"), patch_env(env):
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

    def test_env_config_function(self):
        """Test that a function is not overwritten if there is an environment variable with the same name."""

        env = {
            "WIDTH": "3",
            "HEIGHT": "4",
            "AREA": "this value should not overwrite a function",
            "CIRCUMFERENCE": "this value should not overwrite a function"
        }

        with patch_env(env):
            @env_config
            class Rectangle:
                WIDTH: int
                HEIGHT: int

                # staticmethods can access WIDTH and HEIGHT
                @staticmethod
                def AREA():
                    return Rectangle.WIDTH * Rectangle.HEIGHT

                # classmethods can access them too
                @classmethod
                def CIRCUMFERENCE(cls):
                    return 2 * (cls.WIDTH + cls.HEIGHT)

            self.assertEqual(3, Rectangle.WIDTH)
            self.assertEqual(4, Rectangle.HEIGHT)
            self.assertEqual(12, Rectangle.AREA())
            self.assertEqual(14, Rectangle.CIRCUMFERENCE())

    def test_invalid_type(self):
        with self.assertRaises(CanOnlyDecorateClassesError):
            @env_config
            def f():
                pass

        with self.assertRaises(CanOnlyDecorateClassesError):
            @env_config(upper_case_variable_names=False)
            def f():
                pass

    def test_variable_not_found(self):
        env = {}

        with self.assertRaises(EnvironmentVariableNotFoundError) as cm:
            with patch_env(env):
                @env_config
                class ClassWithMissingVariable:
                    MISSING: int

        exception = cm.exception

        self.assertEqual("ClassWithMissingVariable", exception.class_name)
        self.assertEqual("MISSING", exception.attribute_name)
        self.assertEqual(int, exception.attribute_type)

    def test_cannot_convert_variable(self):

        test_cases = (
            (int, ""),
            (int, "1.5"),
            (int, "43x"),
            (float, ""),
            (float, "1.4x"),
            (bool, ""),
            (bool, "a"),
            (bool, "11"),
            (bool, "00"),
        )

        for attribute_type, attribute_value in test_cases:
            env = {f"VALUE_{attribute_type.__name__.upper()}": attribute_value}

            with self.subTest(f"{attribute_type.__name__}('{attribute_value}')"), patch_env(env):
                with self.assertRaises(CannotConvertEnvironmentVariableError) as cm:
                    @env_config
                    class ClassWithVariableWithIncompatibleType:
                        VALUE_INT: int = 42
                        VALUE_FLOAT: float = 1.5
                        VALUE_BOOL: bool = True

                exception = cm.exception

                self.assertEqual("ClassWithVariableWithIncompatibleType", exception.class_name)
                self.assertEqual(attribute_type, exception.attribute_type)
                self.assertEqual(attribute_value, exception.attribute_value)

    def test_decorator_function(self):
        env = {
            "KEY": "value"
        }

        with patch_env(env):
            @env_config
            class A:
                KEY: str

            self.assertEqual("value", A.KEY)

            @env_config()
            class B:
                KEY: str

            self.assertEqual("value", B.KEY)

    def test_case_sensitivity(self):
        env = {
            "UPPER": "value1",
            "lower": "value2"
        }

        with patch_env(env):
            @env_config(upper_case_variable_names=False)
            class NoUpperCase:
                upper: str = "default1"  # will not be overwritten because there is no env var 'upper'
                lower: str = "default2"  # will be overwritten by env var 'lower'

            self.assertEqual("default1", NoUpperCase.upper)
            self.assertEqual("value2", NoUpperCase.lower)

            @env_config(upper_case_variable_names=True)
            class UpperCase:
                upper: str = "default1"  # will be overwritten by env var 'UPPER'
                lower: str = "default2"  # will not be overwritten because there is no env var 'LOWER'

            self.assertEqual("value1", UpperCase.upper)
            self.assertEqual("default2", UpperCase.lower)

            # default: convert variable names to upper case
            @env_config
            class Default:
                upper: str = "default1"  # will be overwritten by env var 'UPPER'
                lower: str = "default2"  # will not be overwritten because there is no env var 'LOWER'

            self.assertEqual("value1", Default.upper)
            self.assertEqual("default2", Default.lower)


if __name__ == '__main__':
    unittest.main()
