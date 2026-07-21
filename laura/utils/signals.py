from dataclasses import dataclass, is_dataclass
import inspect
from laura.utils.resolution import object_path, resolve_callable_dataclass
import numpy as np

@dataclass
class RandomWalk:
    noise: float

    def __call__(self, value: float = 0.0):
        return value + np.random.normal(scale=self.noise)

@dataclass
class Sinusoid:
    period: float
    amplitude: float
    noise: float = 0.0
    phase: float = 0.0

    def __call__(self, t):
        y = self.amplitude * np.sin(
            2*np.pi*t/self.period + self.phase
        )

        if self.noise:
            y += np.random.normal(scale=self.noise)

        return y


SIGNALS = {
    name: obj
    for name, obj in list(globals().items())
    if isinstance(obj, type) and is_dataclass(obj)
}
"""Built-in signal classes, keyed by bare name."""


def signal_path(signal_cls: type) -> str:
    """Fully qualified import path of a signal class, e.g.
    ``laura.utils.signals.Sinusoid``."""
    return object_path(signal_cls)


def resolve_signal(name: str) -> type:
    """Resolve a signal class from a bare name in `SIGNALS` or a fully qualified
    import path; see `resolve_callable_dataclass`."""
    return resolve_callable_dataclass(name, SIGNALS, "signal")


def call_signal(signal, **context):
    """Call `signal` with whichever of the `context` values it accepts.

    Signals need different inputs -- `Sinusoid` is a function of time `t`, while
    `RandomWalk` steps on from the current `value` -- so a caller that drives
    signals generically cannot know what to pass. It supplies everything it
    knows about (typically ``t``, ``value`` and ``dt``) and this passes on the
    subset that `signal` declares::

        call_signal(signal, t=elapsed, value=current, dt=timestep)
    """
    parameters = inspect.signature(signal).parameters
    if any(p.kind is p.VAR_KEYWORD for p in parameters.values()):
        return signal(**context)
    return signal(**{k: v for k, v in context.items() if k in parameters})
