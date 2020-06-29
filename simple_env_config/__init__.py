import inspect
import os


class EnvironmentVariableNotFoundError(KeyError):
    def __init__(self, class_name: str, attribute_name: str, attribute_type: type):
        self.class_name = class_name
        self.attribute_name = attribute_name
        self.attribute_type = attribute_type

        super().__init__(f"class '{self.class_name}' expects a value of type {self.attribute_type} "
                         f"in the environment variable '{self.attribute_name}'")


class CannotConvertEnvironmentVariableError(ValueError):
    def __init__(self, class_name: str, attribute_name: str, attribute_value: str, attribute_type: type, details: str):
        self.class_name = class_name
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.attribute_type = attribute_type
        self.details = details

        super().__init__(f"class '{self.class_name}' expects a value of type {self.attribute_type} "
                         f"in the environment variable '{self.attribute_name}', but the value '{self.attribute_value}' "
                         f"could not be converted: {self.details}")


class CanOnlyDecorateClassesError(ValueError):
    pass


BOOL_VALUES = {
    value: bool_value
    for bool_value, values in {
        True: ("1", "true", "yes", "on"),
        False: ("0", "false", "no", "off")
    }.items()
    for value in values
}


def bool_converter(s):
    try:
        return BOOL_VALUES[s.lower()]
    except KeyError:
        raise ValueError(f"cannot convert to bool: {s}")


def env_config(cls):
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

        if attribute_type == bool:
            converter = bool_converter
        else:
            converter = attribute_type

        try:
            env_value = os.environ[attribute_name]

            try:
                value = converter(env_value)
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
