import builtins
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
    model_serializer,
    ConfigDict,
)
from typing import Dict, Type, Literal
import operator

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


class ControlVariable(BaseModel):
    """
    Model representing a control variable in a system.

    Example on updating element attributes based on control variables:
    ```python
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
    ```
    """

    identifier: str
    """Unique identifier for the control variable."""

    dtype: type = float
    """Data type of the control variable (e.g., int, float, str)."""

    protocol: str
    """Protocol or method used to interact with the control variable."""

    units: str = "Arb. Units"
    """Units of measurement for the control variable."""

    description: str = "Default Description"
    """Description of the control variable."""

    read_only: bool = True
    """Indicates if the variable is read-only."""

    value: float | int | str | list | None = None
    """Current value of the control variable."""

    target: str | None = None  # "magnetic.k1l"
    """Target attribute path in the system to apply the control variable."""

    expression: dict | None = None  # expression graph
    """Expression defining how to compute the value to set at the target."""

    type: Literal["scalar", "binary", "state", "string", "waveform", "statistical"] = (
        "statistical"
    )
    """Type of control variable."""

    states: Dict | None = None
    """Possible state mapping enums."""

    model_config = ConfigDict(
        arbitrary_types_allowed=False,
        extra="allow",
        # frozen=True,
    )

    def __init__(self, **data):
        super().__init__(**data)

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


class ControlsInformation(BaseModel):
    """
    Model representing a collection of control variables.
    """

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

    movement_type: str
    """Screen motion type"""

    devices: dict
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

    shutter_type: str
    """Type of shutter, i.e. 'LASER', 'BEAM'"""
