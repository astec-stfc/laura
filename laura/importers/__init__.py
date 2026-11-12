import importlib

_EXPORTS = {
    "read_yaml_element_file": ".yaml_loader",
    "read_yaml_element_files": ".yaml_loader",
    "read_yaml_combined_file": ".yaml_loader",
    "interpret_yaml_element": ".yaml_loader",
    "ElementLoadError": ".yaml_loader",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(importlib.import_module(_EXPORTS[name], __name__), name)


def __dir__():
    return sorted(set(globals()) | set(_EXPORTS))
