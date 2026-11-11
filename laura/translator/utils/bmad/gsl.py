"""Load Bmad's own GSL before libtao, so it is not bound to an older one already in the process."""

import ctypes
import os
from pathlib import Path
from typing import Optional


def preload_bmad_gsl(libtao: Optional[str] = None) -> None:
    """
    Load the GSL beside libtao globally before pytao opens libtao.

    The ``soliday.sdds`` wheel bundles its own ``libgsl.so.27`` built from
    GSL < 2.6, which ``import laura`` maps first; libtao's libfgsl would then
    bind to it by soname and miss ``gsl_linalg_ldlt_band_solve``.

    Parameters
    ----------
    libtao : str, optional
        libtao.so path; defaults to ``$ACC_ROOT_DIR/production/lib``, where pytao looks
    """
    if libtao:
        lib = Path(libtao).expanduser().parent
    elif os.environ.get("ACC_ROOT_DIR"):
        lib = Path(os.environ["ACC_ROOT_DIR"]) / "production" / "lib"
    else:
        return
    for name in ("libgslcblas.so.0", "libgsl.so.27"):
        if (lib / name).exists():
            ctypes.CDLL(str(lib / name), mode=ctypes.RTLD_GLOBAL)
