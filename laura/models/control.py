import builtins
from pydantic import (
    ValidationError,
    field_validator,
    model_serializer,
    ConfigDict, Field,
)
from pydantic import ValidationInfo
from typing import Any, Callable, Dict, Type
import operator
from dataclasses import fields, is_dataclass
from laura.utils.dynamics import resolve_response, response_path
from laura.utils.signals import resolve_signal, signal_path
from warnings import warn

from ._generated import (
    _ControlVariableBase,
    _ControlsInformationBase,
)

OPS = {
    "add": operator.add,
    "sub": operator.sub,
    "mul": operator.mul,
    "truediv": operator.truediv,
    "pow": operator.pow,
}


def resolve_path(context, path: str):
    head, *rest = path.split(".")
    if head not in context:
        raise KeyError(f"Unknown symbol '{head}' in expression")

    obj = context[head]
    for attr in rest:
        obj = getattr(obj, attr)
    return obj


def eval_expr(expr, context):
    if isinstance(expr, (int, float)):
        return expr

    if isinstance(expr, str):
        return resolve_path(context, expr)

    op = OPS[expr["op"]]
    args = [eval_expr(a, context) for a in expr["args"]]
    return op(*args)


def set_attr_by_path(obj, path: str, value):
    *parents, attr = path.split(".")
    for part in parents:
        obj = getattr(obj, part)
    setattr(obj, attr, value)


def validate_callable_spec(
    v: Any,
    field: str,
    key: str,
    resolve: Callable[[str], type],
    path: Callable[[type], str],
    label: str,
    who: str,
) -> Dict | None:
    """Normalise and check a callable-dataclass definition, as used by the `update`
    and `dynamics` fields of `ControlVariable`.

    Accepts a class, an instance, or a dict of the form ``{key: <name>, **kwargs}``;
    all are normalised to the dict form, with the name rewritten to a fully
    qualified import path so that a serialised definition can be resolved without
    LAURA. Anything invalid warns and returns None, leaving the field unset.
    """
    if v is None:
        return None

    # An instance, e.g. Sinusoid(period=1.0, amplitude=2.0)
    if is_dataclass(v) and not isinstance(v, type):
        v = {
            key: path(type(v)),
            **{f.name: getattr(v, f.name) for f in fields(v) if f.init},
        }

    # A class, e.g. RandomWalk
    elif isinstance(v, type):
        v = {key: path(v)}

    if not isinstance(v, dict):
        warn(f"`{field}` for {who} must be a {label} class, instance or dict, got {type(v).__name__}")
        return None

    if key not in v:
        warn(f"`{field}` for {who} requires a '{key}' key")
        return None

    name = v[key]
    try:
        obj_cls = resolve(name)
    except LookupError as exc:
        warn(f"Cannot resolve `{field}` for {who}: {exc}")
        return None

    # Construct the class to validate the supplied arguments: a kw_only dataclass
    # rejects unknown keys, missing required ones, and -- for the built-ins,
    # which are `type_checked` -- wrong types. Reproducing those checks here
    # would only duplicate what the constructor already enforces. Fields with
    # init=False (runtime state) are likewise rejected, since they are not
    # constructor arguments.
    kwargs = {k: val for k, val in v.items() if k != key}
    try:
        obj_cls(**kwargs)
    except (TypeError, ValueError) as exc:
        warn(f"Invalid {label} '{name}' for {who}: {exc}")
        return None

    # Store the fully qualified path, so a short name is upgraded on the way in.
    return {**v, key: path(obj_cls)}


class ControlVariable(_ControlVariableBase):
    """
    Model representing a control variable in a system.

    Example on updating element attributes based on control variables:

    .. code-block:: python

        from laura.models.element import Element
        from laura.models.control import ControlVariable, ControlsInformation
        # Define control variables
        cv1 = ControlVariable(
            identifier="k1l_control",
            dtype=float,
            protocol="some_protocol",
            units="1/m",
            description="Control for k1l",
            read_only=False,
            value=0.1,
            target="magnetic.k1l",
            expression={"op": "mul", "args": ["k1l_control", "magnetic.length"]},
        )
        controls_info = ControlsInformation(variables={"k1l_control": cv1})
        # Create an element with magnetic attributes
        element = Element(
            name="Quad1",
            magnetic={"k1l": 0.0, "k2l": 0.0},
            controls=controls_info,
        )
        # Apply control variables to the element
        controls_info.apply(element)
        print(element.magnetic.k1l)  # Should reflect the updated value based on the control variable
    """

    # Slots below override `_ControlVariableBase` where the Python type is
    # richer than the LinkML range can express, or where the schema's
    # cardinality is looser than this model wants. Everything else --
    # `units`, `description`, `read_only`, `control_type`, `target`,
    # `readback`, `setpoint` -- is inherited from the generated base,
    # including the `type` alias on `control_type`.

    identifier: str
    """Unique identifier for the control variable."""

    dtype: type = float
    """Data type of the control variable (e.g., int, float, str).

    Held as a Python type; the schema range is ``string`` because it is
    serialised by name (see `serialize`).
    """

    protocol: str
    """Protocol or method used to interact with the control variable."""

    value: float | int | str | list | None = None
    """Current value of the control variable.

    Widened from the schema's scalar ``any_of`` to also accept a list, for
    ``waveform`` variables.
    """

    expression: dict | None = None  # expression graph
    """Expression defining how to compute the value to set at the target."""

    states: Dict | None = None
    """Possible state mapping enums."""

    update: Dict | None = None
    """
    Defines the update function for the variable; see `laura.utils.signals` for examples.

    Accepts a dict with a "function" key naming a signal class plus its keyword
    arguments (``{"function": "Sinusoid", "period": 1.0, "amplitude": 2.0}``), a
    signal class (only if it has no required arguments), or a signal instance
    (``Sinusoid(period=1.0, amplitude=2.0)``).

    It is always normalised to the dict form, with "function" stored as a fully
    qualified import path (``laura.utils.signals.Sinusoid``) so a serialised
    definition can be resolved without LAURA. Signals defined outside LAURA are
    allowed, provided they are callable dataclasses named by import path. Use
    `build_update` to get a callable back.
    """

    dynamics: Dict | None = None
    """
    Response model describing how this variable's readback follows its setpoint;
    see `laura.utils.dynamics` for examples. Only meaningful alongside `readback`
    or `setpoint`, and intended for simulated control systems, where a readback
    should lag its setpoint rather than track it instantly.

    Defined as for `update`, except that the naming key is "model" rather than
    "function" (``{"model": "first_order", "tau": 0.5}``). Use `build_dynamics`
    to get a callable back; response models are stateful, so each readback needs
    its own instance.
    """

    # The generated base ignores unknown keys; control variables carry
    # protocol-specific extras (auto_buffer, buffer_size, ...) that must
    # survive a load/export round-trip, so keep them.
    model_config = ConfigDict(
        arbitrary_types_allowed=False,
        extra="allow",
        # frozen=True,
    )

    def __init__(self, **data):
        super().__init__(**data)

    @field_validator("update", mode="before")
    @classmethod
    def validate_update(cls, v: Any, info: ValidationInfo) -> Dict | None:
        """Checks that the `update` function resolves to a signal dataclass and that the
        keyword arguments supplied for it match that class' fields.

        Accepts a signal class, a signal instance, or a dict of the form
        ``{"function": <name>, **kwargs}``; all are normalised to the dict form,
        with "function" rewritten to a fully qualified import path
        (``laura.utils.signals.Sinusoid``) so that a serialised definition can be
        resolved without LAURA. Anything invalid warns and returns None, leaving
        the variable without an update function.
        """
        # `identifier` is declared before `update`, so it is already validated here.
        return validate_callable_spec(
            v,
            field="update",
            key="function",
            resolve=resolve_signal,
            path=signal_path,
            label="signal",
            who=info.data.get("identifier", "<unknown>"),
        )

    @field_validator("dynamics", mode="before")
    @classmethod
    def validate_dynamics(cls, v: Any, info: ValidationInfo) -> Dict | None:
        """As `validate_update`, for the response model relating a readback to its
        setpoint; the naming key is "model" rather than "function"."""
        return validate_callable_spec(
            v,
            field="dynamics",
            key="model",
            resolve=resolve_response,
            path=response_path,
            label="response model",
            who=info.data.get("identifier", "<unknown>"),
        )

    def build_update(self):
        """Instantiate the signal described by `update`, or None if unset."""
        if self.update is None:
            return None
        kwargs = {k: val for k, val in self.update.items() if k != "function"}
        return resolve_signal(self.update["function"])(**kwargs)

    def build_dynamics(self):
        """Instantiate the response model described by `dynamics`, or None if unset.

        Response models are stateful, so the returned object should be kept for
        the lifetime of the readback rather than rebuilt on each update.
        """
        if self.dynamics is None:
            return None
        kwargs = {k: val for k, val in self.dynamics.items() if k != "model"}
        return resolve_response(self.dynamics["model"])(**kwargs)

    @field_validator("dtype", mode="before")
    def validate_dtype(cls, v) -> Type:
        """Convert from string to type if necessary."""
        if isinstance(v, str):
            try:
                return getattr(builtins, v)
            except AttributeError:
                raise ValueError(f"Unknown dtype string: {v}")
        if isinstance(v, type):
            return v
        raise TypeError(f"dtype must be a type or string, got {type(v)}")

    # Default values that should be omitted from serialised output to keep
    # YAML exports clean.  Only exact matches are suppressed.
    _SERIALIZE_DEFAULTS: dict = {
        "units": "Arb. Units",
        "read_only": True,
        "type": "statistical",
        "description": "Default Description",
    }

    @model_serializer
    def serialize(self):
        # Collect declared fields + extra fields (e.g. auto_buffer, buffer_size)
        data = {k: getattr(self, k) for k in self.__class__.model_fields}
        if self.model_extra:
            data.update(self.model_extra)
        # Convert dtype to its string name
        if isinstance(data.get("dtype"), type):
            data["dtype"] = data["dtype"].__name__
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        # Remove known defaults
        for key, default_val in self._SERIALIZE_DEFAULTS.items():
            if data.get(key) == default_val:
                del data[key]
        return data

    def apply(self, element, context):
        if self.target is None or self.expression is None:
            return

        value = eval_expr(self.expression, context)
        set_attr_by_path(element, self.target, value)

    def __str__(self) -> str:
        return self.identifier


class ControlsInformation(_ControlsInformationBase):
    """
    Model representing a collection of control variables.
    """

    # Narrowed from the generated base's `_ControlVariableBase` values so the
    # validators and helpers on `ControlVariable` are available.
    variables: Dict[str, ControlVariable]
    """Dictionary mapping variable names to `~laura.models.control.ControlVariable` instances."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
        frozen=True,
    )

    def __getattr__(self, name: str) -> ControlVariable:
        try:
            variables = self.__dict__["variables"]
        except KeyError:
            raise AttributeError(name)
        if name in variables:
            return variables[name]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    @field_validator("variables", mode="before")
    def validate_variables(cls, v) -> Dict[str, ControlVariable]:
        """Ensure all values are ControlVariable instances."""
        if isinstance(v, dict):
            validated_dict = {}
            for key, value in v.items():
                if isinstance(value, ControlVariable):
                    validated_dict[key] = value
                elif isinstance(value, dict):
                    try:
                        validated_dict[key] = ControlVariable(**value)
                    except ValidationError as e:
                        raise ValueError(
                            (
                                "Invalid ControlVariable definition for key "
                                + f"'{key}': "
                                + f"{e}"
                            )
                        ) from e
                else:
                    raise TypeError(
                        (
                            f"Value for key '{key}'"
                            + "must be a ControlVariable or dict, "
                            + f"got {type(value)}"
                        )
                    )
            return validated_dict
        raise TypeError(f"variables must be a dict, got {type(v)}")

    @staticmethod
    def build_context(element):
        ctx = {k: v.value for k, v in element.controls.variables.items()}
        for param in ["magnetic", "physical", "cavity", "simulation"]:
            if hasattr(element, param):
                ctx.update({param: getattr(element, param)})
        return ctx

    # @staticmethod
    # def build_context(element):
    #     return {
    #         **{k: v.value for k, v in element.controls.variables.items()},
    #         "magnetic": element.magnetic,
    #         "physical": element.physical,
    #     }

    def apply(self, element):
        ctx = self.build_context(element)

        for cv in element.controls.variables.values():
            cv.apply(element, ctx)


class ScreenControlsInformation(ControlsInformation):
    """
    Model representing a collection of control variables pertaining to screens.
    """

    movement_type: str = Field(default="Unknown")
    """Screen motion type"""

    devices: dict = Field(default={})
    """List of screen device enums"""

    horizontal_devices: dict | None = None
    """List of horizontal screen device enums"""

    vertical_devices: dict | None = None
    """List of vertical screen device enums"""


class MirrorControlsInformation(ControlsInformation):
    """
    Model representing a collection of control variables pertaining to mirrors.
    """

    step_max: float = 0.05
    """Maximum step size for mirror movement"""

    default_step: float = 0.005
    """Default step size for mirror movement"""

    right_sense: int = -1
    """Right sense for mirror movement"""

    up_sense: int = -1
    """Up sense for mirror movement"""

    left_sense: int = 1
    """Left sense for mirror movement"""

    down_sense: int = 1
    """Down sense for mirror movement"""


class ShutterControlsInformation(ControlsInformation):
    """
    Model representing a collection of control variables pertaining to shutters.
    """

    shutter_type: str = Field(default="Unknown")
    """Type of shutter, i.e. 'LASER', 'BEAM'"""
