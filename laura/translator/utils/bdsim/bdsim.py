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
    radius = getattr(aperture, "radius", None)
    horizontal = getattr(aperture, "horizontal_size", None)
    vertical = getattr(aperture, "vertical_size", None)
    sizes = [s for s in (horizontal, vertical) if s]
    size = radius if radius else (sizes if len(sizes) > 1 else (sizes[0] if sizes else None))
    if shape not in BDSIM_APERTURE_TYPES and size is None:
        return {}
    return aperture_params(
        {
            "type": shape,
            "size": size,
            "material": getattr(aperture, "material", None),
        }
    )
