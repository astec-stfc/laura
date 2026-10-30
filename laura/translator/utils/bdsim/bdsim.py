from warnings import warn

BDSIM_APERTURE_TYPES = frozenset(
    {
        "circular",
        "rectangular",
        "elliptical",
        "lhc",
        "lhcdetailed",
        "rectellipse",
        "racetrack",
        "octagonal",
        "circularvacuum",
    }
)


class GmadExpression(float):
    """
    A number that renders as a gmad expression rather than as its value.

    Numbers are stored as-is and written with ``str()``, so a
    ``float`` subclass carrying its own ``__str__`` gets the expression through
    unquoted while still behaving as a real number for any arithmetic pybdsim
    (or LAURA) does with it.

    Parameters
    ----------
    value: float
        The resolved numeric value, used whenever the object is treated as a number.
    expression: str
        The gmad expression to write, e.g. ``"kquad / 0.2"``.
    """

    expression: str

    def __new__(cls, value: float, expression: str) -> "GmadExpression":
        obj = super().__new__(cls, value)
        obj.expression = expression
        return obj

    def __str__(self) -> str:
        return self.expression

    __repr__ = __str__


BDSIM_CHARGE_SIGNED_KEYWORDS = {
    "Quadrupole": frozenset({"k1"}),
    "ThinMultipole": frozenset({"knl", "ksl"}),
}
"""gmad keywords, by pybdsim builder, that BDSIM scales by ``|brho|``: they set the
field for a *positive* particle, so a negative one needs them negated.

Every other strength (bend ``k1``, ``k2``-``k4``, thick ``multipole``, kickers,
solenoid ``ks``) follows the particle's own charge. Measured with
BDSIM 1.7.7 for e-, antiprotons and mu-, in every integrator set.
"""

BDSIM_FIELD_INTEGRATOR_SETS = frozenset({"geant4", "geant4dp"})
"""Integrator sets whose quadrupole is tracked through a field built from the signed
rigidity, so its ``k1`` follows the particle too."""

BDSIM_REVERSED_KEYWORDS = {("Octupole", "bdsimone"): frozenset({"k3"})}
"""gmad keywords, by pybdsim builder and integrator set, that BDSIM 1.7.7 applies
with the wrong sign for every particle: its ``bdsimone`` octupole integrator
reverses both transverse kicks."""


def negate_strength(value):
    """
    Flip the sign of one normalised magnet strength.

    Parameters
    ----------
    value: Any
        The keyword value to negate. Sequences (``knl``/``ksl``) are negated
        element-wise, and non-numeric values are returned untouched.

    Returns
    -------
    Any
        The negated value.
    """
    if isinstance(value, GmadExpression):
        return GmadExpression(-float(value), f"-({value.expression})")
    if isinstance(value, (list, tuple)):
        return type(value)(negate_strength(v) for v in value)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    return -value


def magnet_frame_workaround(obj: type, keywords: dict, integrator_set: str) -> tuple:
    """
    Work around BDSIM 1.7.7's bdsim* integrator sets tracking quadrupoles and
    bends in the reference frame, which ignores ``offsetX``,
    ``offsetY`` and quadrupole ``tilt``. The geant4 sets are fine.

    A quadrupole that is offset or tilted goes out as a thick ``multipole``.
    Warning are emitted for bends.

    Parameters
    ----------
    obj: type
        The pybdsim builder class.
    keywords: dict
        gmad keywords for the element.
    integrator_set: str
        BDSIM ``integratorSet`` option.

    Returns
    -------
    tuple
        The builder class and keywords to use.
    """
    name = obj.__name__
    if (
        name not in ("Quadrupole", "SBend", "RBend")
        or integrator_set in BDSIM_FIELD_INTEGRATOR_SETS
    ):
        return obj, keywords
    keys = (
        ("offsetX", "offsetY", "tilt")
        if name == "Quadrupole"
        else ("offsetX", "offsetY")
    )
    if not any(float(keywords.get(k) or 0.0) for k in keys):
        return obj, keywords
    if name != "Quadrupole":
        warn(
            f"BDSIM's {integrator_set} integrators ignore offsetX/offsetY on bend "
            f"{keywords['name']!r}; track with integrator_set geant4 to misalign it."
        )
        return obj, keywords
    from pybdsim.Builder import Multipole

    k1 = keywords.pop("k1", 0.0)
    return Multipole, dict(keywords, knl=(negate_strength(k1),), ksl=(0.0,))


def apply_charge_sign(
    keywords: dict,
    charge_sign: int | float = 1,
    builder: str = "",
    integrator_set: str = "bdsimmatrix",
) -> dict:
    """
    Negate the strengths in a gmad keyword dictionary that BDSIM reads as a field
    (see :data:`BDSIM_CHARGE_SIGNED_KEYWORDS`) when the beam particle is negatively
    charged. Strengths BDSIM gets backwards for every particle
    (:data:`BDSIM_REVERSED_KEYWORDS`) are negated too.

    Parameters
    ----------
    keywords: dict
        gmad keywords for one element. Modified in place.
    charge_sign: int or float
        Sign of the beam particle's charge.
    builder: str
        Name of the pybdsim builder class the keywords are for, e.g. ``"Quadrupole"``.
    integrator_set: str
        BDSIM ``integratorSet`` option; see :data:`BDSIM_FIELD_INTEGRATOR_SETS`.

    Returns
    -------
    dict
        The same dictionary, for chaining.
    """
    for key in (
        BDSIM_REVERSED_KEYWORDS.get((builder, integrator_set), frozenset())
        & keywords.keys()
    ):
        keywords[key] = negate_strength(keywords[key])
    if charge_sign >= 0:
        return keywords
    if builder == "Quadrupole" and integrator_set in BDSIM_FIELD_INTEGRATOR_SETS:
        return keywords
    for key in BDSIM_CHARGE_SIGNED_KEYWORDS.get(builder, frozenset()) & keywords.keys():
        keywords[key] = negate_strength(keywords[key])
    return keywords


def aperture_params(dic: dict | None):
    conv = {}
    if dic is None:
        return conv
    if len(list(dic.keys())) == 0:
        return conv
    if dic.get("type") in BDSIM_APERTURE_TYPES:
        conv.update({"apertureType": dic["type"]})
    size = dic.get("size")
    if isinstance(size, (list, tuple)):
        for i, value in enumerate(size[:4], start=1):
            conv.update({f"aper{i}": (value, "m")})
    elif isinstance(size, (int, float)):
        conv.update({"aper1": (size, "m")})
    if dic.get("material") is not None:
        conv.update({"beampipeMaterial": dic["material"]})
    return conv


def element_aperture_params(aperture) -> dict:
    """
    Build the gmad aperture keywords from an element's own
    :class:`~laura.models.simulation.ApertureElement`.

    An element's aperture describes the beam pipe *through that element*, so it
    takes precedence over the section-wide beam pipe wherever both are set.

    Parameters
    ----------
    aperture: ApertureElement | None
        The element's aperture, if it has one.

    Returns
    -------
    dict
        gmad aperture keywords, empty when the element has no usable aperture.
    """
    if aperture is None:
        return {}
    shape = getattr(aperture, "shape", None)
    # gmad has no planar type; LAURA treats it as rectangular everywhere else
    shape = "rectangular" if shape == "planar" else shape
    radius = getattr(aperture, "radius", None)
    horizontal = getattr(aperture, "horizontal_size", None)
    vertical = getattr(aperture, "vertical_size", None)
    sizes = [s for s in (horizontal, vertical) if s]
    size = (
        radius
        if radius
        else (sizes if len(sizes) > 1 else (sizes[0] if sizes else None))
    )
    if shape not in BDSIM_APERTURE_TYPES and size is None:
        return {}
    return aperture_params(
        {
            "type": shape,
            "size": size,
            "material": getattr(aperture, "material", None),
        }
    )
