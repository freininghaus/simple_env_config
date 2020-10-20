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