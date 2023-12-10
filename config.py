import os
from typing import Any

import yaml


_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


with open(_ROOT_DIR+"/config.yaml", "r") as stream:
    try:
        CONFIG: dict = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        raise exc

CONFIG["General"]["root_directory"] = _ROOT_DIR


def get_from_config(keypath: list[str], value_type: object | None = None) -> Any:
    param = CONFIG
    for key in keypath:
        param = param.get(key, None)
        if param is None:
            return None
    if value_type is not None:
        if not isinstance(param, value_type):
            raise ValueError(f"Incorrect value type. Expected {value_type}, got {type(param)}")
    return param