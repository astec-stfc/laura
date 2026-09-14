import importlib

_EXPORTS = {
    "BmadLatticeImporter": ".converters.codes",
    "ElegantLatticeImporter": ".converters.codes",
    "MadxLatticeImporter": ".converters.codes",
    "OcelotLatticeImporter": ".converters.codes",
    "XsuiteLatticeImporter": ".converters.codes",
    "SectionLatticeTranslator": ".converters.section",
    "MachineLayoutTranslator": ".converters.layout",
    "MachineModelTranslator": ".converters.model",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return getattr(importlib.import_module(_EXPORTS[name], __name__), name)
