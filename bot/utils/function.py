import inspect
from types import ModuleType


def has_and_is_coroutine_function(module: ModuleType, attr_name: str):
    if hasattr(module, attr_name):
        func = getattr(module, attr_name)
        if inspect.isfunction(func) and inspect.iscoroutinefunction(func):
            return func
    return None


def has_and_is_function(module: ModuleType, attr_name: str):
    if hasattr(module, attr_name):
        func = getattr(module, attr_name)
        if inspect.isfunction(func):
            return func
    return None
