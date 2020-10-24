import typing

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


def optional_type(t):
    """If t is Optional[T] for some type T, returns T. Otherwise, returns None."""
    try:
        origin = t.__origin__
        args = t.__args__
    except AttributeError:
        return None

    if origin != typing.Union:
        return None

    if len(args) != 2 or type(None) not in args:
        return None

    args_not_none = tuple(arg for arg in args if not arg == type(None))
    if not args_not_none:
        return None

    return args_not_none[0]


def convert(value: str, attribute_type: type):
    type_inside_optional = optional_type(attribute_type)
    if type_inside_optional is not None:
        return convert(value, type_inside_optional)

    if attribute_type == bool:
        converter = bool_converter
    else:
        converter = attribute_type

    return converter(value)
