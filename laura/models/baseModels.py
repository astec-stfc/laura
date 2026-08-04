from pydantic import BaseModel, model_serializer, ConfigDict
from typing import TypeVar, Any, Type, List, Union, Dict, ClassVar
import numpy as np
from pydantic_core.core_schema import SerializationInfo

from ..utils.dict_utils import (
    FlowList as flow_list,
    numpy_scalar_to_python,
)

# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar("T", bound="BaseModel")


def resolve_functional_parameter(
    value: Any,
    definitions: Union[Dict[str, Union[int, float]], None] = None,
    *,
    force: Union[bool, None] = None,
) -> Any:
    """
    Resolve a (possibly functional) parameter to its numeric value.

    Many element attributes (e.g. multipole strengths, cavity phases) may be
    defined either directly as a number or symbolically as a string that names
    an entry in the lattice's functional definitions (for example
    ``{"quad1_k1l": -2, "cav1_phase": 90}``). The string is stored verbatim on
    the element; whether it is resolved to a number here depends on ``force``:

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
    Set the global resolution-mode flag: when True, functional attributes are
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
    Recursively collect the names of functional definitions referenced by a
    model — i.e. the string values stored in fields flagged as functional-enabled
    (``annotations: {functional: true}`` on the schema slot). Nested models are
    walked so that, for example, a magnet's multipole strengths are discovered.

    Args:
        model (Any): A pydantic model (typically an element); non-models yield
            an empty set.

    Returns:
        set: The set of referenced functional-definition names.
    """
    refs: set = set()
    if not isinstance(model, BaseModel):
        return refs
    for name, field_info in type(model).model_fields.items():
        try:
            value = getattr(model, name)
        except Exception:
            continue
        meta = functional_annotations(field_info)
        if meta.get("functional") and isinstance(value, str):
            # A field may reserve some literal string values that are not
            # functional-definition names (e.g. edge angles use "angle"/"angle/2"
            # to reference the bend angle); those are skipped.
            reserved = meta.get("reserved_contains")
            if not (reserved and reserved in value):
                refs.add(value)
        if isinstance(value, BaseModel):
            refs |= functional_references(value)
    return refs


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
    Populate the shared registry of functional definitions for the lattice.

    Args:
        definitions (dict | None): Mapping of functional-parameter names to
            their numeric values, e.g. ``{"quad1_k1l": -2, "cav1_phase": 90}``.
        merge (bool, optional): If True (default), merge into the existing
            registry; if False, replace it entirely.
    """
    if not merge:
        IgnoreExtra.functional_definitions.clear()
    IgnoreExtra.functional_definitions.update(definitions or {})


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
    if isinstance(v, (np.ndarray, list, tuple)):
        return flow_list([convert_numpy_types(arr) for arr in v])
    return numpy_scalar_to_python(v)


class ModelBase(BaseModel):
    """Base Model that ignores extra fields."""

    def __eq__(self, other):
        """Equality that gracefully handles numpy arrays in private attributes."""
        try:
            return super().__eq__(other)
        except (ValueError, TypeError):
            # Fallback: compare serialised forms when private-attribute
            # comparison fails (e.g. numpy arrays).
            if not isinstance(other, BaseModel):
                return NotImplemented
            return self.model_dump() == other.model_dump()

    def __hash__(self):
        return id(self)

    def base_model_dump(self, exclude_defaults: bool = False) -> dict:
        return convert_numpy_types(
            self.model_dump(exclude_none=True, exclude_defaults=exclude_defaults)
        )


class FunctionalMixin:
    """
    Provides :meth:`resolve` / :meth:`resolved` to any model holding functional
    parameters.

    This is a plain mixin rather than methods on :class:`IgnoreExtra` because the
    schema-generated element bases in ``laura/models/_generated.py`` descend from
    their own ``ConfiguredBaseModel`` root, not from ``IgnoreExtra``. That file is
    regenerated from ``laura_schema.yaml`` and must not be hand-edited, so wrapper
    classes that declare functional fields mix this in alongside their generated
    base instead.
    """

    def resolve(self, value: Any) -> Any:
        """
        Resolve a single (possibly functional) value to its number, regardless of
        the global resolution mode (this is an explicit request to resolve).

        See :func:`resolve_functional_parameter`.
        """
        return resolve_functional_parameter(
            value, IgnoreExtra.functional_definitions, force=True
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


class IgnoreExtra(ModelBase, FunctionalMixin):
    """Base Model that ignores extra fields."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="ignore",
        populate_by_name=True,
    )

    # Shared registry of functional definitions for the accelerator lattice,
    # e.g. ``{"quad1_k1l": -2, "cav1_phase": 90}``. This is a class variable so
    # that a single set of definitions, provided to a high-level container such
    # as ``SectionLattice``/``MachineModel``/``LAURA``, is visible to every
    # (deeply nested) element model when it needs to resolve a string-valued
    # functional parameter to a number. Populate it via
    # :func:`set_functional_definitions`.
    functional_definitions: ClassVar[Dict[str, Union[int, float]]] = {}

    # Global resolution mode (see :func:`set_resolve_functional`). When False
    # (default), functional attributes render as their definition name (string);
    # when True, the "configured value" accessors and the codes that support
    # functional parameters present resolved numbers instead.
    resolve_functional: ClassVar[bool] = False

    def _create_field_class(
        self, fields: dict, fieldname: str, fieldclass: List[str]
    ) -> None:
        fields[fieldname] = fieldclass.from_CATAP(fields)

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


class objectList(IgnoreExtra):

    def __iter__(self) -> iter:
        cls = self.__class__
        return iter(getattr(self, list(cls.model_fields.keys())[0]))

    def __str__(self) -> str:
        cls = self.__class__
        return str(list(getattr(self, list(cls.model_fields.keys())[0])))

    def __repr__(self) -> repr:
        cls = self.__class__
        return repr(list(getattr(self, list(cls.model_fields.keys())[0])))


class DeviceList(objectList):
    devices: list = []


class Aliases(objectList):
    aliases: list = []
