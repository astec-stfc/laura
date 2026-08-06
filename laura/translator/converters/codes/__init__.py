magnetic_orders = {
    "Dipole": 0,
    "Quadrupole": 1,
    "Sextupole": 2,
    "Octupole": 3,
    "Decapole": 4,
    "SBend": 0,
    "RBend": 0,
}

from .astra import astra_unsupported
from .cheetah import cheetah_unsupported
from .csrtrack import csrtrack_unsupported
from .elegant import elegant_unsupported
from .genesis import genesis_unsupported
from .gpt import gpt_unsupported
from .ocelot import ocelot_unsupported
from .opal import opal_unsupported
from .wake_t import wake_t_unsupported
from .xsuite import xsuite_unsupported