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

    default_values = {
        k: v
        for k, v in inspect.getmembers(cls)
        if not (inspect.isroutine(v) or k.startswith("__"))
    }

    annotations = cls.__annotations__

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
