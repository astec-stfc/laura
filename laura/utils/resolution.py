"""Shared machinery for naming and resolving the callable dataclasses used by
:py:class:`ControlVariable <laura.models.control.ControlVariable>`, i.e. the
signals in `laura.utils.signals` and the response models in
`laura.utils.dynamics`."""

from dataclasses import is_dataclass
from importlib import import_module
from typing import Dict


def object_path(obj_cls: type) -> str:
    """Fully qualified import path of a class, e.g.
    ``laura.utils.signals.Sinusoid``."""
    return f"{obj_cls.__module__}.{obj_cls.__qualname__}"


def resolve_callable_dataclass(name: str, registry: Dict[str, type], label: str) -> type:
    """Resolve a callable dataclass from a fully qualified import path.

    A bare name (``"Sinusoid"``, ``"first_order"``) is looked up in `registry`,
    which keeps short names and aliases working; a dotted path is imported,
    which allows classes defined outside LAURA. `label` names the kind of object
    being resolved, and is only used in error messages. Raises `LookupError` if
    the name cannot be resolved to a callable dataclass.

    Note that a dotted path imports the named module, so only resolve paths from
    definitions you trust.
    """
    if "." not in name:
        if name in registry:
            return registry[name]
        raise LookupError(
            f"Unknown {label} '{name}'; expected one of {sorted(registry)} "
            f"or a fully qualified import path."
        )

    module_name, _, attr = name.rpartition(".")
    try:
        module = import_module(module_name)
    except ImportError as exc:
        raise LookupError(f"Cannot import module '{module_name}' for {label} '{name}': {exc}")

    obj_cls = getattr(module, attr, None)
    if obj_cls is None:
        raise LookupError(f"Module '{module_name}' has no attribute '{attr}'")
    if not isinstance(obj_cls, type) or not is_dataclass(obj_cls):
        raise LookupError(
            f"{label.capitalize()} '{name}' must be a dataclass, got {type(obj_cls).__name__}"
        )
    if not any("__call__" in vars(klass) for klass in obj_cls.__mro__):
        raise LookupError(f"{label.capitalize()} '{name}' does not define __call__")

    return obj_cls
