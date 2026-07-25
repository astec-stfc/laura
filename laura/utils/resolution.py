"""Shared machinery for naming and resolving the callable dataclasses used by
:py:class:`ControlVariable <laura.models.control.ControlVariable>`, i.e. the
signals in `laura.utils.signals` and the response models in
`laura.utils.dynamics`."""

from dataclasses import fields, is_dataclass
from importlib import import_module
from typing import Dict


def check_field_types(instance) -> None:
    """Raise `TypeError` for any init field whose value does not match its annotation.

    Only plain class annotations are enforced; anything more elaborate (``Union``,
    ``Optional``, parameterised generics) is left unchecked rather than risk a
    false rejection, as is a field whose annotation is a string (from
    ``from __future__ import annotations``). `int` is accepted where `float` is
    annotated, following the usual numeric convention.

    Meant to be applied through `type_checked`, which calls it from a dataclass'
    ``__post_init__`` so that construction validates its own arguments.
    """
    for f in fields(instance):
        if not f.init:
            continue
        annotation = f.type
        if not isinstance(annotation, type):
            continue
        value = getattr(instance, f.name)
        if annotation is float and isinstance(value, int) and not isinstance(value, bool):
            continue
        if not isinstance(value, annotation):
            raise TypeError(
                f"{type(instance).__name__}.{f.name} must be "
                f"{annotation.__name__}, got {type(value).__name__}"
            )


def type_checked(cls):
    """Class decorator adding argument type-checking to a dataclass.

    Apply it *below* ``@dataclass`` so that the ``__post_init__`` it installs
    exists when the dataclass generates its ``__init__``::

        @dataclass(kw_only=True)
        @type_checked
        class Sinusoid:
            period: float
            ...

    Any ``__post_init__`` already defined on the class still runs, after the type
    check, so a class can add its own validation on top.
    """
    original = cls.__dict__.get("__post_init__")

    def __post_init__(self, *args, **kwargs):
        check_field_types(self)
        if original is not None:
            original(self, *args, **kwargs)

    cls.__post_init__ = __post_init__
    return cls


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
