import inspect
import os

from . import converters
from simple_env_config.errors import CanOnlyDecorateClassesError, CannotConvertEnvironmentVariableError, \
    EnvironmentVariableNotFoundError


def env_config(cls=None, *, upper_case_variable_names=True):
    if cls is None:
        return lambda cls_: env_config_impl(cls_, upper_case_variable_names)
    return env_config_impl(cls, upper_case_variable_names)


def env_config_impl(cls, upper_case_variable_names: bool):
    if type(cls) != type:
        raise CanOnlyDecorateClassesError(f"env_config can only decorate classes, not '{cls}'")

    annotations = cls.__annotations__

    default_values = {
        **{
            # Attributes with type hint Optional[T] for some T get the implicit default value None.
            # If such an attribute has an explicit default value, it will appear in inspect.getmembers(cls) (see below),
            # such that the implicit default value None will be overwritten.
            attribute_name: None
            for attribute_name, attribute_type in annotations.items()
            if converters.optional_type(attribute_type) is not None
        },
        **{
            # Handle attributes which have a default value set with '=' in the class definition
            attribute_name: value
            for attribute_name, value in inspect.getmembers(cls)
            if not (inspect.isroutine(value) or attribute_name.startswith("__"))
        }
    }

    all_attributes = {*default_values, *annotations}

    for attribute_name in all_attributes:
        attribute_type = annotations.get(attribute_name, str)

        try:
            env_value = os.environ[attribute_name.upper() if upper_case_variable_names else attribute_name]

            try:
                value = converters.convert(env_value, attribute_type)
            except ValueError as e:
                raise CannotConvertEnvironmentVariableError(cls.__name__, attribute_name, env_value, attribute_type,
                                                            " ".join(e.args))
        except KeyError:
            try:
                value = default_values[attribute_name]
            except KeyError:
                raise EnvironmentVariableNotFoundError(cls.__name__, attribute_name, attribute_type)

        setattr(cls, attribute_name, value)

    return cls
