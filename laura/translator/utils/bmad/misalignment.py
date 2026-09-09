"""How ``physical.error`` is written into a Bmad element definition."""

from typing import Any, Dict

__all__ = [
    "BMAD_MISALIGNMENT",
    "BMAD_NO_MISALIGNMENT",
    "bmad_misalignment",
]

BMAD_MISALIGNMENT = {
    "dx": ("x_offset", 1.0),
    "dy": ("y_offset", 1.0),
    "dz": ("z_offset", 1.0),
    "dx_rot": ("x_pitch", -1.0),
    "dy_rot": ("y_pitch", -1.0),
}
"""
``physical.error`` -> (Bmad misalignment attribute, sign).
"""

BMAD_NO_MISALIGNMENT = frozenset({"match"})
"""
Bmad types that reject misalignment attributes (measured, not assumed).
"""


def bmad_misalignment(
    element, etype: str, parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Return the Bmad misalignment attributes carried by ``physical.error``.

    Only non-zero errors are emitted, so an element that is not misaligned
    is written exactly as it was before.

    Parameters
    ----------
    element: BaseElementTranslator
        The element being written, read for its ``physical.error`` components
        and for the functional-expression settings that decide whether a
        folded ``tilt`` is resolved or left as an expression.
    etype: str
        Bmad element type, which decides where the roll goes.
    parameters: Dict[str, Any]
        Attributes already gathered for this element, read for the design
        ``tilt`` the roll has to be folded into.

    Returns
    -------
    dict
        Attributes to merge into the element definition.
    """
    if etype in BMAD_NO_MISALIGNMENT:
        return {}
    misalignment = {
        attribute: sign * value
        for source, (attribute, sign) in BMAD_MISALIGNMENT.items()
        if (value := getattr(element, source))
    }
    roll = element.dz_rot
    if roll:
        if etype in ("sbend", "rbend"):
            misalignment["roll"] = roll
        else:
            tilt = parameters.get("tilt", 0.0)
            misalignment["tilt"] = (
                f"({tilt}) + {roll}"
                if not element._resolve_functional and element.is_functional(tilt)
                else element.resolve(tilt) + roll
            )
    return misalignment
