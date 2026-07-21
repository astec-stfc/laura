from dataclasses import dataclass, is_dataclass
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
"""Registry of signal classes available to `ControlVariable.update`."""
