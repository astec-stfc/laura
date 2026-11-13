"""
LAURA data models. Lattice containers and every element class defined in
:mod:`laura.models.element` are importable from here, e.g.
``from laura.models import MachineModel, Quadrupole``.
"""

import importlib

_EXPORTS = {
    "ElementList": ".element_list",
    "SectionLattice": ".element_list",
    "MachineLayout": ".element_list",
    "MachineModel": ".element_list",
    "ELEMENT_REGISTRY": ".element",
    "LatticeError": ".exceptions",
}

__all__ = list(_EXPORTS)


def _element_classes() -> dict:
    element = importlib.import_module(".element", __name__)
    return {
        name: obj
        for name, obj in vars(element).items()
        if isinstance(obj, type)
        and obj.__module__ == element.__name__
        and not name.startswith("_")
    }


def __getattr__(name: str):
    if name in _EXPORTS:
        return getattr(importlib.import_module(_EXPORTS[name], __name__), name)
    if not name.startswith("_"):
        cls = _element_classes().get(name)
        if cls is not None:
            return cls
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(_EXPORTS) | set(_element_classes()))
