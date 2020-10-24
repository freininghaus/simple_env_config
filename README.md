# simple-env-config

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
    port: int = 8080
    k8s_namespace: str
    debug_mode: bool = False

run_app(Config.port, Config.k8s_namespace, Config.debug_mode)
```
Note that this example uses lower case variable names in `class Config`. These
will be converted to upper case for the environment variable lookup, i.e., the
values will be read from the environment variables `PORT`, `K8S_NAMESPACE`, and
`DEBUG_MODE`, respectively.

This behavior can be changed: decorating the class with 

    @env_config(upper_case_variable_names=False)

will cause a case-sensitive variable lookup in the environment.

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

Thus, very little code is needed, and everything works nicely with static type
checkers.

This design requires Python 3.6 or later. Earlier versions do not support
[annotating the types of class variables](https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep526).

## Installation
```bash
pip install simple-env-config
```
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
    var1: str = "A"
    var2 = "B"

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
    required: str
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
    port: int = 8080
    tolerance: float = 1e-3
    debug_mode: bool = False
```
In most cases, a variable whose type hint is `T` will be initialized with the
expression `T(value)`, where `value` is the string content of the environment
variable.

For some types, there are special conversion rules.

#### `bool` 
Boolean values are initialized by comparing the string content of the
environment variable case-insensitively with the values in these two groups:
  * `"1"`, `"true"`, `"yes"`, `"on"`,
  * `"0"`, `"false"`, `"no"`, `"off"`,

and assigning the value `True` or `False`, respectively.

#### `Optional[T]`
A variable with the type hint `Optional[T]` will be initialized just like a
variable with type hint `T`. However, it gets the implicit default value `None`:

```python
@env_config
class ConfigWithOptionals:
    A: Optional[int]
    B: Optional[bool]
```
If neither `A` nor `B` are valid environment variables, both `A` and `B` will
be assigned the value `None` in this class.

Otherwise, the value of the environment variable `A` will be parsed as an `int`,
and the value of `B` will be compared case-insensitively with "true", "yes",
etc., to determine a Boolean value.

#### Conversion errors
If a conversion fails, either because the expression `T(value)` raises a
`ValueError`, or applying the rule for types like `bool` and `Optional[T]`
fails, a `simple_env_config.CannotConvertEnvironmentVariableError` is thrown.

### Configuration
`env_config` can be called as a function and accepts a keyword argument
`upper_case_variable_names`. This argument controls whether the variable names
will be converted to upper case before looking up variables in the environment:
```python
@env_config(upper_case_variable_names=False)
class CaseSensitiveConfig:
    key: str  # reads from env var 'key'
    Key: str  # reads from env var 'Key'
    KEY: str  # reads from env var 'KEY'
```
The default behavior is to consider only upper case environment variables:
```python
@env_config
class DefaultConfig:
    # all these variables read from the env var 'KEY'
    key: str
    Key: str
    KEY: str
```

## Notes on similar libraries
[env-var-config](https://pypi.org/project/env-var-config/) also makes use of
type hints for loading environment variable values into a config object. Notable
differences are:
* With simple_env_config, only a class decorator is needed to initialize the
  config object. With env_var_config, a base class and a function call are
   required.
* Since simple_env_config stores the loaded values in the class that contains
  the type hints, and not in an instance of the class, it works better with
  static type checkers.
* simple_env_config only accepts pre-defined input strings for `bool` values.
  For other inputs, it raises an exception, rather than converting them `False`.
 