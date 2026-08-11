# Legacy import paths (laura.Exporters, laura.models.RF, ...) are served by a
# meta-path finder rather than shim files -- see laura/_legacy.py for why.
# Installed first so it is in place before any submodule import can resolve.
from . import _legacy

_legacy.install()

from .laura import LAURA  # noqa: E402
from . import models  # noqa: E402
from . import translator  # noqa: E402
from . import exporters  # noqa: E402
from . import utils  # noqa: E402
from .debug_wrapper import set_log_level  # noqa: E402

__all__ = ["LAURA", "models", "utils", "exporters", "set_log_level"]
