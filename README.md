# simple_env_config

[![Build Status](https://travis-ci.com/freininghaus/simple_env_config.svg?branch=master)](https://travis-ci.com/freininghaus/simple_env_config)

This Python library, which works with Python 3.6 and above, tries to make
reading configuration values from the environment easy, such that you can
replace code like

```python
import os

PORT = int(os.getenv("PORT", 8080))
K8S_NAMESPACE = os.env["K8S_NAMESPACE"]  # required, no default value
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
