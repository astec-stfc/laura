"""Writers for Bmad field and short-range wake sidecars."""

from warnings import warn

import numpy as np


def _values(parameter, name: str) -> np.ndarray:
    if parameter.value is None:
        raise ValueError(f"Bmad field export requires {name} data")
    values = np.asarray(parameter.value.val, dtype=float)
    if values.ndim != 1 or len(values) < 2:
        raise ValueError(f"Bmad field export requires at least two 1-D {name} samples")
    return values


def _uniform_step(axis: np.ndarray, name: str) -> float:
    steps = np.diff(axis)
    if np.any(steps <= 0):
        raise ValueError(f"Bmad {name} samples must be strictly increasing")
    if not np.allclose(
        steps,
        steps[0],
        rtol=1e-7,
        atol=max(abs(steps[0]) * 1e-10, 1e-15),
    ):
        raise ValueError(f"Bmad {name} samples must be equally spaced")
    return float(steps[0])


def _format(value) -> str:
    return f"{value:.16g}" if isinstance(value, (float, np.floating)) else str(value)


def _write(self, text: str) -> str:
    filename = self._output_filename(extension=".bmad")
    with open(filename, "w", encoding="utf-8") as output:
        output.write(text)
    return filename


def _write_wake(self, *, verbose: bool) -> str | None:
    if self.Wz.value is None:
        if verbose:
            warn(
                "Bmad has no tabulated transverse short-range wake format; "
                "fit Wx/Wy to Bmad transverse pseudo-modes before export."
            )
        return None

    if self.z.value is not None:
        axis = _values(self.z, "z")
        time_based = "F"
    elif self.t.value is not None:
        axis = _values(self.t, "time")
        time_based = "T"
    else:
        raise ValueError("Bmad wake export requires z or time samples")
    _uniform_step(axis, "wake")
    wake = _values(self.Wz, "Wz")
    if len(axis) != len(wake):
        raise ValueError("Bmad wake coordinate and Wz arrays must have equal lengths")

    if verbose and (self.Wx.value is not None or self.Wy.value is not None):
        warn(
            "Bmad exports the tabulated longitudinal short-range wake Wz; "
            "sampled Wx/Wy require a transverse pseudo-mode fit and were omitted."
        )

    rows = ",\n".join(
        f"      {_format(position)} {_format(value)}"
        for position, value in zip(axis, wake)
    )
    return _write(
        self,
        "{\n"
        "  scale_with_length = F,\n"
        "  z_long = {\n"
        f"    time_based = {time_based},\n"
        "    w = {\n"
        f"{rows}\n"
        "    }\n"
        "  }\n"
        "}\n",
    )


def _write_gen_gradients(
    self, *, field_scale, kind: str, n: int, verbose: bool
) -> str | None:
    if self.field_type != "1DMagnetoStatic":
        if verbose:
            warn(
                f"Bmad magnetic field export does not yet support {self.field_type}; "
                "only 1DMagnetoStatic generalized-gradient profiles are supported."
            )
        return None
    if field_scale is None:
        if verbose:
            warn("Bmad generalized-gradient export requires a physical field scale")
        return None
    if kind not in {"a", "b", "bs"}:
        raise ValueError(f"Unknown Bmad generalized-gradient kind: {kind}")

    z = _values(self.z, "z")
    dz = _uniform_step(z, "generalized-gradient")
    profile = _values(self.Bz, "Bz")
    if len(z) != len(profile):
        raise ValueError(
            "Bmad generalized-gradient z and Bz arrays must have equal lengths"
        )

    centered = np.isclose(z[0], -z[-1], rtol=1e-7, atol=max(abs(dz) * 1e-7, 1e-15))
    anchor = "center" if centered else "beginning"
    rows = ",\n".join(
        f"      {_format(position)}: {_format(value)}"
        for position, value in zip(z, profile)
    )
    return _write(
        self,
        "{\n"
        "  field_type = magnetic,\n"
        f"  field_scale = {_format(field_scale)},\n"
        f"  ele_anchor_pt = {anchor},\n"
        "  r0 = (0, 0, 0),\n"
        f"  dz = {_format(dz)},\n"
        f"  curve = {{ kind = {kind}, n = {n}, derivs = {{\n"
        f"{rows}\n"
        "  } }\n"
        "}\n",
    )


def write_bmad_field_file(
    self,
    *,
    field_scale=None,
    kind: str | None = None,
    n: int | None = None,
    verbose: bool = True,
) -> str | None:
    """
    Generate the field data in a format that is suitable for Bmad, based on the
    :class:`~laura.translator.utils.fields.field` object provided.

    See the `Bmad manual`_ for more details.

    This is then written to a text file.
    The `field_type` parameter determines the format of the file.

    A warning is raised if the field type is not supported (perhaps elevate to a `NotImplementedError`?)

    .. _Bmad manual: https://www.classe.cornell.edu/bmad/manual.html

    Parameters
    ----------
    self: :class:`~laura.translator.utils.fields.field`
        The field object
    field_scale: float | None
        Used for scaling the overall field magnitude
    kind: str | None
        Kind of generalized-gradient field (must be in ``a`` (skew),
        ``b`` (normal), ``bs`` (solenoid))
    n: int | None
        Harmonic index for generalized-gradient

    Returns
    -------
    str | None:
        The name of the field file.
        Will return None if required parameters for certain fields are not provided.

    Raises
    ------
    ValueError:
        If ``kind`` is not in [``a``, ``b``, ``bs``] for ``1DMagnetoStatic`` field map
    ValueError:
        If the field map arrays do not have the same length
    ValueError:
        If a required name for an array is missing
    ValueError:
        If time or position samples are not strictly increasing
    Warning:
        If the ``field_type`` is not supported for export
    Warning:
        If ``field_scale`` is None for a ``1DMagnetoStatic`` field map
    Warning:
        If only transverse wakes are provided
    """
    field_type = (
        self.field_type.decode("utf-8")
        if isinstance(self.field_type, bytes)
        else self.field_type
    )
    if field_type in {"LongitudinalWake", "TransverseWake", "3DWake"}:
        return _write_wake(self, verbose=verbose)
    if "MagnetoStatic" in str(field_type):
        return _write_gen_gradients(
            self,
            field_scale=field_scale,
            kind=kind or "b",
            n=n if n is not None else 1,
            verbose=verbose,
        )
    if verbose:
        warn(f"Field type {field_type} is not supported for Bmad field export")
    return None
