# simple_env_config

[![Build Status](https://travis-ci.com/freininghaus/simple_env_config.svg?branch=master)](https://travis-ci.com/freininghaus/simple_env_config)

This library tries to make reading configuration values from the environment
easy, such that you can replace code like

```
import os

PORT = int(os.getenv("PORT", 8080))
K8S_NAMESPACE = os.env["K8S_NAMESPACE"]  # required, no default value
DEBUG_MODE = os.getenv("DEBUG_MODE", "0").lower() in ("1", "true", "yes", "on")

run_app(PORT, K8S_NAMESPACE, DEBUG_MODE)
```

by

```
from simple_env_config import env_config

@env_config
class Config:
    PORT: int = 8080
    K8S_NAMESPACE: str
    DEBUG_MODE: bool = False
    

run_app(Config.PORT, Config.K8S_NAMESPACE, Config.DEBUG_MODE)
```
