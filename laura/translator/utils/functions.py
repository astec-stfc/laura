import re
import os
import numpy as np
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from laura.utils.dict_utils import numpy_scalar_to_python
from laura.models.baseModels import IgnoreExtra
from typing import Any, Dict, Optional, Type, Union, get_args, get_origin


def elegant_functional_definitions(definitions: Dict | None = None) -> str:
    """
    Build the ELEGANT rpn-store header declaring every functional definition for
    the lattice, e.g.::

        % -2 sto quad1_k1l
        % 90 sto cav1_phase

    Element keywords that reference a functional parameter are written as quoted
    rpn variable references (e.g. ``VOLT="V_L02.01"``), which ELEGANT resolves
    against these stored values.

    Parameters
    ----------
    definitions: dict, optional
        The functional definitions to declare. Defaults to the shared registry
        (:attr:`IgnoreExtra.functional_definitions`) when not provided/empty.

    Returns
    -------
    str
        The ``% <value> sto <name>`` block (one line per definition), or an empty
        string if no functional definitions are set.
    """
    if IgnoreExtra.resolve_functional:
        # Resolution mode: values are baked in as numbers, so no rpn store needed.
        return ""
    definitions = definitions or IgnoreExtra.functional_definitions
    return "".join(f"% {value} sto {name}\n" for name, value in definitions.items())


def madx_functional_definitions(definitions: Dict | None = None) -> str:
    """
    Build the MAD-X variable-declaration header assigning every functional
    definition for the lattice, e.g.::

        quad1_k1l = -2;
        cav1_phase = 90;

    Element keywords that reference a functional parameter are written as
    infix expressions (e.g. ``k1 := quad1_k1l / 0.1``), which MAD-X resolves
    against these variable assignments (and keeps updated as deferred
    expressions, ``:=``, wherever a symbolic value is used).

    Parameters
    ----------
    definitions: dict, optional
        The functional definitions to declare. Defaults to the shared registry
        (:attr:`IgnoreExtra.functional_definitions`) when not provided/empty.

    Returns
    -------
    str
        A ``<name> = <value>;`` block (one line per definition), or an empty
        string if no functional definitions are set.
    """
    if IgnoreExtra.resolve_functional:
        # Resolution mode: values are baked in as numbers, so no header needed.
        return ""
    definitions = definitions or IgnoreExtra.functional_definitions
    return "".join(f"{name} = {value};\n" for name, value in definitions.items())


def sanitize_string(string: str) -> str:
    """
    Replaces hyphens in a string with underscores.

    Parameters
    ----------
    string: str
        Any string

    Returns
    -------
    str
        A string with hyphens replaced with underscores
    """
    return string.replace("-", "_")


class Counter(dict):
    def __init__(self, sub={}):
        super().__init__()
        self.sub = sub

    def counter(self, type):
        type = self.sub[type] if type in self.sub else type
        if type not in self:
            return 1
        return self[type] + 1

    def value(self, type):
        type = self.sub[type] if type in self.sub else type
        if type not in self:
            return 1
        return self[type]

    def add(self, type, n=1):
        type = self.sub[type] if type in self.sub else type
        if type not in self:
            self[type] = n
        else:
            self[type] += n
        return self[type]


def convert_numpy_types(v):
    if isinstance(v, dict):
        return {key: convert_numpy_types(item) for key, item in v.items()}
    elif isinstance(v, (np.ndarray, list, tuple)):
        try:
            return [convert_numpy_types(li) for li in v]
        except TypeError:
            return float(v)
    elif isinstance(v, field):
        return convert_numpy_types(v.model_dump())
    return numpy_scalar_to_python(v)


def _rotation_matrix(theta):
    return np.array(
        [
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-1 * np.sin(theta), 0, np.cos(theta)],
        ]
    )


def chop(expr, delta=1e-8):
    """Performs a chop on small numbers"""
    if isinstance(expr, (int, float, complex)):
        return 0 if -delta <= expr <= delta else expr
    else:
        return [chop(x, delta) for x in expr]


def get_field_default(field: FieldInfo) -> Any:
    """Get the default value or instance from a field definition."""
    if callable(field.default_factory):
        try:
            return field.default_factory()
        except Exception:
            return "FACTORY_ERROR"
    if field.default is not None:
        return field.default
    return None


def _unwrap_optional_basemodel(annotation: Any) -> Optional[Type[BaseModel]]:
    """Return ``X`` if ``annotation`` is ``Optional[X]`` for a BaseModel ``X``, else ``None``."""
    if get_origin(annotation) is Union:
        non_none = [a for a in get_args(annotation) if a is not type(None)]
        if len(non_none) == 1 and isinstance(non_none[0], type) and issubclass(non_none[0], BaseModel):
            return non_none[0]
    return None


def introspect_model_defaults(
    model_cls: Type[BaseModel],
    flatten: bool = False,
    parent_key: str = "",
    separator: str = "_",
    resolve_optional: bool = False,
) -> Dict[str, Any]:
    """Recursively introspect a Pydantic model class, extracting default values (including nested).

    Parameters
    ----------
    resolve_optional: bool
        A field typed ``Optional[SomeModel]`` with no ``default_factory`` (e.g.
        ``physical: Optional[PhysicalElement] = None``) has a class-level
        default of ``None`` -- there is no instance to recurse into. When
        ``False`` (the default, preserving prior behaviour) such a field's
        entry is just ``None``. When ``True``, its declared type is unwrapped
        and introspected directly (using ``SomeModel``'s own field defaults)
        instead of stopping at ``None``.
    """
    result = {}

    for field_name, field in model_cls.model_fields.items():
        default_value = get_field_default(field)

        # If the default value is a BaseModel (e.g., from default_factory), recurse
        if isinstance(default_value, BaseModel):
            nested = introspect_model_defaults(
                default_value.__class__,
                flatten=flatten,
                parent_key=(
                    f"{parent_key}{separator}{field_name}" if parent_key else field_name
                ),
                separator=separator,
                resolve_optional=resolve_optional,
            )
            if flatten:
                result.update(nested)
            else:
                result[field_name] = nested
            continue

        if default_value is None and resolve_optional:
            inner_cls = _unwrap_optional_basemodel(field.annotation)
            if inner_cls is not None:
                nested = introspect_model_defaults(
                    inner_cls,
                    flatten=flatten,
                    parent_key=(
                        f"{parent_key}{separator}{field_name}" if parent_key else field_name
                    ),
                    separator=separator,
                    resolve_optional=resolve_optional,
                )
                if flatten:
                    result.update(nested)
                else:
                    result[field_name] = nested
                continue

        key = (
            f"{parent_key}{separator}{field_name}"
            if (flatten and parent_key)
            else field_name
        )
        result[key] = default_value

    return result


def isevaluable(self, s):
    try:
        eval(s)
        return True
    except Exception:
        return False


def path_function(a):
    if a:
        return os.path.abspath(a)
    return "./"

def expand_substitution(self, param, master_lattice="./", subs=None, elements=None, absolute=False):
    subs = subs or {}
    elements = elements or {}
    if isinstance(param, str):
        subs["master_lattice"] = path_function(master_lattice) + "/"
        regex = re.compile(r"\$(.*?)\$")
        s = re.search(regex, param)
        if s:
            if isevaluable(self, s.group(1)) is True:
                replaced_str = str(eval(re.sub(regex, str(eval(s.group(1))), param)))
            else:
                replaced_str = re.sub(regex, s.group(1), param)
            for key in subs:
                replaced_str = replaced_str.replace(key, subs[key])
            if os.path.exists(replaced_str):
                replaced_str = path_function(replaced_str).replace("\\", "/")
                # print('\tpath exists', replaced_str)
            for e in elements.keys():
                if e in replaced_str:
                    print("Element is in string!", e, replaced_str)
            return replaced_str
        else:
            return param
    else:
        return param


def checkValue(self, d, default=None):
    if isinstance(d, dict):
        if "type" in d and d["type"] == "list":
            if "default" in d:
                return [
                    a if a is not None else b for a, b in zip(d["value"], d["default"])
                ]
            else:
                if isinstance(d["value"], list):
                    return [val if val is not None else default for val in d["value"]]
                else:
                    return None
        else:
            d["value"] = expand_substitution(self, d["value"])
            return (
                d["value"]
                if d["value"] is not None
                else d["default"] if "default" in d else default
            )
    elif isinstance(d, str):
        return (
            getattr(self, d)
            if hasattr(self, d) and getattr(self, d) is not None
            else default
        )


def tw_cavity_energy_gain(cavity):
    """
    Estimate energy gain in a travelling-wave RF cavity.

    Parameters:
        cavity (laura.models.element.RFCavity): RFCavity element

    Returns:
        float: Estimated energy gain [eV]
    """

    # Approximate effective accelerating gradient
    E_acc = cavity.field_amplitude * np.sin(
        np.pi * cavity.mode_numerator * 2 / cavity.mode_denominator / 2
    )

    # Total cavity length
    L_total = cavity.n_cells * cavity.cell_length

    # Energy gain in MeV (since 1 MV/m * 1 m = 1 MeV for charge = e)
    delta_W = E_acc * L_total * np.cos(np.pi * cavity.phase / 180)

    return delta_W
