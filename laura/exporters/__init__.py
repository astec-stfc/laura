import importlib

# name -> (module, attribute); the SQL ``export_machine`` is renamed here to
# avoid clashing with the YAML one.
_EXPORTS = {
    "export_machine": (".yaml_exporter", "export_machine"),
    "export_elements": (".yaml_exporter", "export_elements"),
    "export_as_yaml": (".yaml_exporter", "export_as_yaml"),
    "export_machine_sections": (".yaml_exporter", "export_machine_sections"),
    "export_machine_combined_file": (".yaml_exporter", "export_machine_combined_file"),
    "export_machine_rdf": (".rdf_exporter", "export_machine_rdf"),
    "export_machine_sql": (".sql_exporter", "export_machine"),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module, attr = _EXPORTS[name]
    return getattr(importlib.import_module(module, __name__), attr)


def __dir__():
    return sorted(set(globals()) | set(_EXPORTS))
