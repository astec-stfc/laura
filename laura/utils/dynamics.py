"""Response models describing how a readback follows its setpoint.

A response model is a callable dataclass taking a target value and a timestep,
and returning the value the readback should now report::

    response = FirstOrderResponse(tau=0.5)
    response(target=1.0, dt=0.1)

Unlike the signals in `laura.utils.signals`, response models are stateful: each
call advances an internal value towards the target. One instance is therefore
needed per readback, and it must be kept between calls rather than rebuilt.
"""

from dataclasses import dataclass, field
from laura.utils.resolution import object_path, resolve_callable_dataclass, type_checked
from typing import Dict


@dataclass(kw_only=True)
@type_checked
class ImmediateResponse:
    """A readback that follows its setpoint with no lag."""

    value: float = field(default=0.0, init=False)

    def __call__(self, target: float, dt: float) -> float:
        self.value = target
        return self.value


@dataclass(kw_only=True)
@type_checked
class FirstOrderResponse:
    """Exponential approach to the setpoint with time constant `tau`.

    `tau` is the time (in the same units as `dt`) taken to cover roughly 63% of
    the remaining distance to the target.
    """

    tau: float
    initial: float = 0.0
    value: float = field(default=0.0, init=False)

    def __post_init__(self):
        if self.tau <= 0:
            raise ValueError(f"tau must be positive, got {self.tau}")
        self.value = self.initial

    def __call__(self, target: float, dt: float) -> float:
        # Clamped so that a timestep longer than tau settles at the target
        # rather than overshooting it.
        self.value += (target - self.value) * min(dt / self.tau, 1.0)
        return self.value


@dataclass(kw_only=True)
@type_checked
class DelayedResponse:
    """A readback that jumps to the setpoint after a fixed dead time."""

    delay: float
    initial: float = 0.0
    value: float = field(default=0.0, init=False)
    elapsed: float = field(default=0.0, init=False)

    def __post_init__(self):
        if self.delay < 0:
            raise ValueError(f"delay must not be negative, got {self.delay}")
        self.value = self.initial

    def __call__(self, target: float, dt: float) -> float:
        if target == self.value:
            self.elapsed = 0.0
            return self.value
        self.elapsed += dt
        if self.elapsed >= self.delay:
            self.value = target
            self.elapsed = 0.0
        return self.value


RESPONSE_MODELS: Dict[str, type] = {
    "ImmediateResponse": ImmediateResponse,
    "FirstOrderResponse": FirstOrderResponse,
    "DelayedResponse": DelayedResponse,
    # Short names, as used in lattice definitions.
    "immediate": ImmediateResponse,
    "first_order": FirstOrderResponse,
    "delayed": DelayedResponse,
}
"""Built-in response models, keyed by class name and by short name."""


def response_path(response_cls: type) -> str:
    """Fully qualified import path of a response model, e.g.
    ``laura.utils.dynamics.FirstOrderResponse``."""
    return object_path(response_cls)


def resolve_response(name: str) -> type:
    """Resolve a response model from a short name in `RESPONSE_MODELS` or a fully
    qualified import path; see `resolve_callable_dataclass`."""
    return resolve_callable_dataclass(name, RESPONSE_MODELS, "response model")
