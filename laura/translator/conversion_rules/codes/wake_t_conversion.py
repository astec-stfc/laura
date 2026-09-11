try:
    from wake_t import (
        PlasmaStage,
        ActivePlasmaLens,
        Dipole,
        Quadrupole,
        Sextupole,
        GaussianPulse,
    )

    _WAKE_T_AVAILABLE = True
except ImportError as _err:
    raise ImportError(
        'wake_t is not installed. Install with: pip install "laura-accelerator[wake_t]"'
    ) from _err

wake_t_conversion_rules = {
    "Dipole": Dipole,
    "Quadrupole": Quadrupole,
    "Sextupole": Sextupole,
    "Laser": GaussianPulse,
    "Plasma": PlasmaStage,
    "Plasma_Lens": ActivePlasmaLens,
}
