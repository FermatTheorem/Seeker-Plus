import importlib
import os
from typing import List, Type


def load_modules(modules_path: str) -> List[Type]:
    result = []
    for root, dirs, files in os.walk(modules_path):
        for directory in dirs:
            module_name = os.path.splitext(directory)[0]
            module_path = os.path.join(root, directory, f"{module_name}.py")
            if os.path.exists(module_path):
                module_path = f"Modules.{directory}.{module_name}"
                new_class = getattr(importlib.import_module(module_path), module_name)
                result.append(new_class)
    return result
