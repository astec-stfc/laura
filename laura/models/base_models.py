from typing import Any, ClassVar, Dict, List, Type, TypeVar, Union

import numpy as np
from pydantic import BaseModel, ConfigDict, PrivateAttr, model_serializer
from pydantic_core.core_schema import SerializationInfo

from ..utils.dict_utils import (
    FlowList,
    numpy_scalar_to_python,
)

# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar("T", bound="BaseModel")

_FUNCTIONAL_FIELDS: Dict[type, tuple] = {}
"""Model class -> its fields' ``(name, functional, reserved_contains)``."""


def resolve_functional_parameter(
    value: Any,
    definitions: Union[Dict[str, Union[int, float]], None] = None,
    *,
    force: Union[bool, None] = None,
) -> Any:
    """
    Resolve a (possibly functional) parameter to its numeric value.

    A functional parameter is a string naming an entry in the lattice's
    functional definitions (e.g. ``{"quad1_k1l": -2}``). Whether it is resolved
    depends on ``force``:

    * ``force=True`` — always resolve (used by computations that need a number);
    * ``force=False`` — never resolve (return the string verbatim);
    * ``force=None`` (default) — follow the global resolution mode flag
      :attr:`IgnoreExtra.resolve_functional` (off by default, i.e. leave as a
      string), set from the top level via :func:`set_resolve_functional`.

    Args:
        value (Any): Either a numeric value (returned unchanged) or a string
            naming a functional definition.
        definitions (dict, optional): The functional definitions to resolve
            against. Defaults to the shared registry on
            :class:`IgnoreExtra` (``IgnoreExtra.functional_definitions``).
        force (bool, optional): Override the global resolution mode.

    Returns:
        Any: The numeric value when resolving, otherwise the value unchanged.

    Raises:
        KeyError: If resolving and ``value`` is a string that is not present in
            the available functional definitions.
    """
    if not isinstance(value, str):
        return value
    resolve = IgnoreExtra.resolve_functional if force is None else force
    if not resolve:
        return value
    defs = IgnoreExtra.functional_definitions if definitions is None else definitions
    if value not in defs:
        raise KeyError(
            f"Functional parameter '{value}' is not defined in the available "
            f"functional definitions {sorted(defs.keys())}"
        )
    return defs[value]


def set_resolve_functional(value: bool) -> None:
    """
    Set the session-wide resolution-mode flag, used by elements that belong to
    no machine (a machine has its own ``resolve_functional``): when True,
    functional attributes are
    presented as their resolved numeric values; when False (the default), they
    are rendered as the functional-definition name (a string). Computations that
    require a number always resolve regardless of this flag.
    """
    IgnoreExtra.resolve_functional = bool(value)


#: Schema subset marking a slot whose value may be a functional-definition name.
FUNCTIONAL_SUBSET = "functional_parameters"
#: Schema subset marking a slot that may instead reference the dipole bend angle.
BEND_ANGLE_SUBSET = "bend_angle_reference"


def functional_annotations(field_info: Any) -> Dict[str, Any]:
    """
    Read a field's functional markers, flattened to ``{tag: value}``.

    Schema slots declare these as subset membership (``in_subset:
    [functional_parameters]`` in ``laura_schema.yaml``), which gen-pydantic
    surfaces as ``json_schema_extra["linkml_meta"]["in_subset"]``. Hand-written
    wrapper classes that are not schema-generated may instead set them flat, as
    ``Field(json_schema_extra={"functional": True})``. Both forms are accepted.

    Subsets are used rather than LinkML ``annotations`` because gen-yaml -- which
    the SHACL step in ``laura/schema/generate.sh`` pipes through -- cannot
    serialise ``Annotation`` objects.
    """
    extra = getattr(field_info, "json_schema_extra", None)
    if not isinstance(extra, dict):
        return {}
    if "functional" in extra:
        return extra
    subsets = (extra.get("linkml_meta") or {}).get("in_subset") or ()
    if FUNCTIONAL_SUBSET not in subsets:
        return {}
    meta: Dict[str, Any] = {"functional": True}
    if BEND_ANGLE_SUBSET in subsets:
        meta["reserved_contains"] = "angle"
    return meta


def functional_references(model: Any) -> set:
    """
    Recursively collect the functional-definition names referenced by a model
    and its nested models (string values of functional-enabled fields).

    Args:
        model (Any): A pydantic model (typically an element); non-models yield
            an empty set.

    Returns:
        set: The set of referenced functional-definition names.
    """
    refs: set = set()
    if not isinstance(model, BaseModel):
        return refs
    for name, functional, reserved in _functional_fields(type(model)):
        try:
            value = getattr(model, name)
        except Exception:
            continue
        if functional and isinstance(value, str):
            if not (reserved and reserved in value):
                refs.add(value)
        if isinstance(value, BaseModel):
            refs |= functional_references(value)
    return refs


def _functional_fields(cls: type) -> tuple:
    if cls not in _FUNCTIONAL_FIELDS:
        fields = []
        for name, field_info in cls.model_fields.items():
            meta = functional_annotations(field_info)
            fields.append(
                (name, bool(meta.get("functional")), meta.get("reserved_contains"))
            )
        _FUNCTIONAL_FIELDS[cls] = tuple(fields)
    return _FUNCTIONAL_FIELDS[cls]


def validate_functional_references(
    elements: Any,
    definitions: Union[Dict[str, Union[int, float]], None],
    source: Union[str, None] = None,
) -> None:
    """
    Raise if any element references a functional definition that is not present
    in ``definitions``, naming the missing reference(s), the element(s) that use
    them, and where the definitions were provided.

    Args:
        elements: Iterable of element models to check.
        definitions: The available functional definitions.
        source (str, optional): Where the definitions came from (e.g. a YAML file
            path), surfaced in the error message.

    Raises:
        ValueError: If one or more referenced functional definitions are missing.
    """
    available = set(definitions or {})
    missing: Dict[str, set] = {}
    for elem in elements:
        for ref in functional_references(elem):
            if ref not in available:
                missing.setdefault(ref, set()).add(getattr(elem, "name", "?"))
    if missing:
        where = f" provided in {source}" if source else " provided to the lattice"
        details = "; ".join(
            f"'{ref}' (used by {', '.join(sorted(names))})"
            for ref, names in sorted(missing.items())
        )
        raise ValueError(
            f"Undefined functional parameter(s): {details}. "
            f"Available functional_definitions{where}: {sorted(available)}. "
            f"Add the missing definition(s) to the functional_definitions{where}."
        )


def set_functional_definitions(
    definitions: Union[Dict[str, Union[int, float]], None], merge: bool = True
) -> None:
    """
    Populate the session-wide functional definitions, used by elements that
    belong to no machine. A machine, section or layout keeps its own (see
    :class:`FunctionalScope`) and does not touch these.

    Args:
        definitions (dict | None): Mapping of functional-parameter names to
            their numeric values, e.g. ``{"quad1_k1l": -2, "cav1_phase": 90}``.
        merge (bool, optional): If True (default), merge into the existing
            registry; if False, replace it entirely.
    """
    registry = IgnoreExtra.functional_definitions
    if not merge:
        registry.clear()
    registry.update(definitions or {})


def convert_numpy_types(v: Any) -> Any:
    """
    Recursively convert numpy types in a data structure to native Python types.

    Args:
        v (Any): The input data structure which may contain numpy types.

    Returns:
        Any: The data structure with numpy types converted to native Python types.
    """
    if isinstance(v, (dict)):
        return {k: convert_numpy_types(l) for k, l in v.items()}
    if isinstance(v, np.ndarray) and v.ndim == 0:
        return numpy_scalar_to_python(v.item())
    if isinstance(v, (np.ndarray, list, tuple)):
        return FlowList([convert_numpy_types(arr) for arr in v])
    return numpy_scalar_to_python(v)


class ModelBase(BaseModel):
    """Base model with numpy-tolerant equality and dumps."""

    def __eq__(self, other):
        """Equality that gracefully handles numpy arrays in private attributes."""
        try:
            return super().__eq__(other)
        except (ValueError, TypeError):
            if not isinstance(other, BaseModel):
                return NotImplemented
            return self.model_dump() == other.model_dump()

    def __hash__(self):
        return id(self)

    def base_model_dump(self, exclude_defaults: bool = False) -> dict:
        return convert_numpy_types(_dump(self, exclude_defaults))


def _same(value, default) -> bool:
    try:
        return bool(value == default)
    except ValueError:
        return np.array_equal(value, default)


def _dump(model: BaseModel, exclude_defaults: bool) -> dict:
    """``model_dump(exclude_none=True)``, without defaults if asked.

    Pydantic compares a value with its default using ``==``, so a numpy-array
    field makes a whole ``exclude_defaults`` dump raise. Fall back to comparing
    field by field.
    """
    try:
        return model.model_dump(exclude_none=True, exclude_defaults=exclude_defaults)
    except ValueError:
        if not exclude_defaults:
            raise
    out = {}
    for name, field in type(model).model_fields.items():
        value = getattr(model, name)
        if value is None or _same(value, field.get_default(call_default_factory=True)):
            continue
        if isinstance(value, BaseModel):
            out[name] = _dump(value, True)
        else:
            out[name] = model.model_dump(include={name}, exclude_none=True)[name]
    for name in type(model).model_computed_fields:
        value = model.model_dump(include={name}, exclude_none=True).get(name)
        if value is not None:
            out[name] = value
    return out


class FunctionalScope:
    """
    The functional definitions and resolution mode that a machine's elements
    resolve against. Each machine, section and layout holds its own, so names
    and values do not carry over from one machine to another. An element that
    belongs to no machine uses the session-wide ones (see
    :func:`set_functional_definitions` and :func:`set_resolve_functional`).
    """

    def __init__(
        self,
        definitions: Union[Dict[str, Union[int, float]], None] = None,
        resolve: bool = False,
    ):
        self.definitions = {} if definitions is None else definitions
        self.resolve = bool(resolve)

    # Which machine an element belongs to is not part of its value: elements
    # compare equal across machines, and a copy stays with its machine.
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, FunctionalScope)

    __hash__ = object.__hash__

    def __deepcopy__(self, memo: dict) -> "FunctionalScope":
        return self


class _SessionScope(FunctionalScope):
    """The session-wide definitions and mode, for elements in no machine."""

    def __init__(self):
        pass

    definitions = property(lambda self: IgnoreExtra.functional_definitions)
    resolve = property(lambda self: IgnoreExtra.resolve_functional)


_SESSION_SCOPE = _SessionScope()


def attach_functional_scope(model: Any, scope: FunctionalScope) -> None:
    """Point ``model`` (an element, or a list of them), and every model nested
    in it, at ``scope``."""
    if isinstance(model, (list, tuple)):
        for item in model:
            attach_functional_scope(item, scope)
        return
    if not isinstance(model, BaseModel):
        return
    if isinstance(model, FunctionalMixin):
        if model.functional_scope is scope:
            return
        model._functional_scope = scope
    for name in type(model).model_fields:
        value = model.__dict__.get(name)
        if isinstance(value, (BaseModel, list, tuple)):
            attach_functional_scope(value, scope)


class FunctionalMixin(BaseModel):
    """
    Provides :meth:`resolve` / :meth:`resolved` to any model holding functional
    parameters, resolved against the model's :attr:`functional_scope`.

    A mixin rather than methods on :class:`IgnoreExtra` because the generated
    bases in ``laura/models/_generated.py`` do not descend from ``IgnoreExtra``.

    It also checks a name set on a functional field against the functional
    definitions, when there are any; list it before the generated base so that
    its ``__setattr__`` runs.
    """

    _functional_scope: Any = PrivateAttr(default_factory=lambda: _SESSION_SCOPE)

    @property
    def functional_scope(self) -> FunctionalScope:
        """The definitions and resolution mode of the machine this model belongs
        to, or the session-wide ones."""
        private = getattr(self, "__pydantic_private__", None) or {}
        return private.get("_functional_scope") or _SESSION_SCOPE

    def __setattr__(self, name: str, value: Any) -> None:
        scope = self.functional_scope
        defs = scope.definitions
        if isinstance(value, str) and defs and value not in defs:
            for field, functional, reserved in _functional_fields(type(self)):
                if field == name and functional and not (reserved and reserved in value):
                    raise ValueError(
                        f"'{value}' is not a functional definition; "
                        f"{type(self).__name__}.{name} takes a number or one of "
                        f"{sorted(defs)}"
                    )
        super().__setattr__(name, value)
        if name in type(self).model_fields:  # a new sub-model joins this machine
            attach_functional_scope(self.__dict__.get(name), scope)

    def resolve(self, value: Any, force: Union[bool, None] = True) -> Any:
        """
        Resolve a single (possibly functional) value against this model's
        functional definitions: always by default, or with ``force=None`` only
        when its machine's resolution mode says so.

        See :func:`resolve_functional_parameter`.
        """
        scope = self.functional_scope
        return resolve_functional_parameter(
            value, scope.definitions, force=scope.resolve if force is None else force
        )

    def resolved(self, field_name: str) -> Any:
        """
        Return the numeric value of a field, resolving it against the functional
        definitions if it is stored symbolically as a string.

        Args:
            field_name (str): Name of the attribute to resolve.

        Returns:
            Any: The resolved numeric value.
        """
        return self.resolve(getattr(self, field_name))


class IgnoreExtra(FunctionalMixin, ModelBase):
    """Base Model that ignores extra fields."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="ignore",
        populate_by_name=True,
    )

    functional_definitions: ClassVar[Dict[str, Union[int, float]]] = {}
    """
    Session-wide functional definitions, e.g. ``{"quad1_k1l": -2, "cav1_phase":
    90}``, for elements that belong to no machine. Populate it via
    :func:`set_functional_definitions`; a machine keeps its own (see
    :class:`FunctionalScope`).
    """

    resolve_functional: ClassVar[bool] = False
    """
    Session-wide resolution mode (see :func:`set_resolve_functional`), for
    elements that belong to no machine. When False (default), functional
    attributes render as their definition name (string); when True, the
    "configured value" accessors and the codes that support functional
    parameters present resolved numbers instead.
    """

    def _create_field(
        self, fields: dict, fieldname: str, fieldinputs: List[str]
    ) -> None:
        fields[fieldname] = [fields[x] for x in fieldinputs]

    def update(self, **kwargs):
        cls = self.__class__
        [
            v.annotation.update(k)
            for k, v in cls.model_fields.items()
            if hasattr(v.annotation, "update")
        ]
        self.__dict__.update(kwargs)


class NumpyModel(ModelBase):
    """Model using numpy arrays."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_serializer(mode="wrap")
    def ser_model(self, handler, info: SerializationInfo):
        if info.mode == "json":
            return self.array.tolist()  # vector for JSON
        return handler(self)  # default dict for python

    @property
    def array(self) -> np.ndarray:
        cls = self.__class__
        return np.array([getattr(self, a) for a in cls.model_fields.keys()])

    @classmethod
    def from_list(cls: Type[T], vec: List[Union[float, int]]) -> T:
        assert len(vec) == len(cls.model_fields.keys())
        return cls(**dict(zip(list(cls.model_fields.keys()), vec)))

    @classmethod
    def from_values(cls: Type[T], *values: Union[float, int]) -> T:
        assert len(values) == len(cls.model_fields.keys())
        return cls(**dict(zip(list(cls.model_fields.keys()), values)))

    def update(self, **kwargs):
        cls = self.__class__
        [
            v.annotation.update(v)
            for v in cls.model_fields.values()
            if hasattr(v.annotation, "update")
        ]
        self.__dict__.update(kwargs)


class NumpyVectorModel(NumpyModel):
    """vector model using numpy arrays."""

    def __iter__(self) -> iter:
        cls = self.__class__
        return iter([getattr(self, k) for k in cls.model_fields.keys()])

    def __eq__(self, other: Any) -> bool:
        cls = self.__class__
        if other == 0 or other == 0.0 or other is None:
            if all([getattr(self, k) == 0 for k in cls.model_fields.keys()]):
                return True
            return False
        return list(self) == list(other)


class ObjectList(IgnoreExtra):
    def __iter__(self) -> iter:
        cls = self.__class__
        return iter(getattr(self, list(cls.model_fields.keys())[0]))

    def __str__(self) -> str:
        cls = self.__class__
        return str(list(getattr(self, list(cls.model_fields.keys())[0])))

    def __repr__(self) -> repr:
        cls = self.__class__
        return repr(list(getattr(self, list(cls.model_fields.keys())[0])))


class DeviceList(ObjectList):
    devices: list = []


class Aliases(ObjectList):
    aliases: list = []


from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "objectList": "ObjectList",
    },
)
