# simple-env-config release history

## Next version (not released yet!)
* Classes derived from `enum.Enum` can be used as a type hint.
* Missing variables without default value now causes an exception only when
  trying to access that variable. To get the old behavior (check for missing
  variables while parsing the class), decorate with
  `@env_config(lazy_missing_variables_check=False)`.

## Version 0.2, released 2020-10-24
* Environment variable names are converted to upper case by default. Decorating
  with `@env_config(upper_case_variable_names=False)` enforces that class
  members and environment variable names are compared case-sensitively.
* `Optional[T]` can be used as a type hint. Attributes with an `Optional[T]`
  type hint get the implicit default value `None`.

## Version 0.1, released 2020-10-06
* Initial release on PyPI
