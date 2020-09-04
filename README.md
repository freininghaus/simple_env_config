# simple_env_config

[![Build Status](https://travis-ci.com/freininghaus/simple_env_config.svg?branch=master)](https://travis-ci.com/freininghaus/simple_env_config)

This Python library, which works with Python 3.6 and above, tries to make
reading configuration values from the environment easy, such that you can
replace code like

```python
import os

PORT = int(os.getenv("PORT", 8080))
K8S_NAMESPACE = os.environ["K8S_NAMESPACE"]  # required, no default value
DEBUG_MODE = os.getenv("DEBUG_MODE", "0").lower() in ("1", "true", "yes", "on")

run_app(PORT, K8S_NAMESPACE, DEBUG_MODE)
```

by

```python
from simple_env_config import env_config

@env_config
class Config:
    PORT: int = 8080
    K8S_NAMESPACE: str
    DEBUG_MODE: bool = False

run_app(Config.PORT, Config.K8S_NAMESPACE, Config.DEBUG_MODE)
```

## Motivation
As shown in the example above, parsing many environment variables without
helper functions or libraries requires quite a bit code that is not only
repetitive, but sometimes even confusing and error prone.

This library makes this task easier. In contrast to alternatives like
[environs](https://pypi.org/project/environs/) and
[environ-config](https://pypi.org/project/environ-config/), which are very
useful and offer more features, the goal is maximal simplicity:
* A single decorator indicates that a class contains parsed environment
 variables.
* The parsed variable and the environment variable share the same name.
* Python's type hints are used to request type conversions.
* Assignment with `=` specifies default values.

Thus, very little code is needed, and everything work nicely with static type
checkers.

This design requires Python 3.6 or later. Earlier versions do not support
[annotating the types of class variables](https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep526).

## Usage

The library is imported with
```python
import simple_env_config
```
or
```python
from simple_env_config import env_config
```
The following examples use the latter.

### String values
For string values, adding the `str` type hint is optional:
```python
@env_config
class Strings:
    VAR1: str = "A"
    VAR2 = "B"

print(Strings.VAR1, Strings.VAR2)
```
The code above ill print the values of the environment variables VAR1 and VAR2.
If any of these are undefined, the default values will be "A" and "B",
respectively.

### Values without defaults
If no default value is given for a variable in a class decorated with
`@env_config`, and the environment variable does not exist, an exception is
thrown:
```python
@env_config
class Strings:
    REQUIRED: str
```
results in
```
simple_env_config.EnvironmentVariableNotFoundError: "class 'Strings' expects a value of type <class 'str'> in the environment variable 'REQUIRED'"
```
if there is no environment variable named REQUIRED.

### Converting to other data types
A type hint indicates the type that the parsed environment variable value should
be converted to:
```python
@env_config
class DataTypes:
    PORT: int = 8080
    TOLERANCE: float = 1e-3
    DEBUG_MODE: bool = False
```
Note:
* In most cases, a variable whose type hint is `T` will be initialized with the
  expression `T(value)`, where `value` is the string content of the environment
  variable.
* The exception is `bool`. Boolean values are initialized by comparing the
  string content of the environment variable case-insensitively with the values
  in these two groups:
  * "1", "true", "yes", "on",
  * "0", "false", "no", "off",
  
  and assigning the value `True` or `False`, respectively.
* If the initialization of a `bool` fails because the value does not match any
  of those shown above, or the expression `T(value)` fails for any other type
  `T`, a `simple_env_config.CannotConvertEnvironmentVariableError` is thrown.
   