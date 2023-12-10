import importlib
import os
from typing import List, Type
from config import get_from_config


def load_modules() -> List[Type]:
    result = []
    root_dir = get_from_config(["General", "root_directory"], str)
    all_modules = get_from_config(["Modules"], dict).keys()
    modules_dir = get_from_config(["General", "modules_directory"], str)
    modules_enabled = [module_name for module_name in all_modules if _is_module_enabled(module_name)]
    for module in modules_enabled:
        module_path = os.path.join(root_dir, modules_dir, module, f"{module}.py")
        if os.path.exists(module_path):
            module_path = f"Modules.{module}.{module}"
            new_class = getattr(importlib.import_module(module_path), module)
            result.append(new_class)
    return result

def _is_module_enabled(module_name: str) -> bool:
    module_settings = get_from_config(["Modules", module_name], dict)
    if not module_settings:
        return False
    return module_settings.get("enabled", False)