"""Global placement of a Bmad lattice: the datum, the run-up and the patches."""

import numpy as np

from .angles import bmad_floor_angles_from_matrix, is_flat_roll

__all__ = [
    "bmad_beginning_datum",
    "bmad_leading_drift",
    "bmad_patch",
    "bmad_survey_frame",
]

_BMAD_DATUM_TOLERANCE = 1e-12


def bmad_beginning_datum(first_element, lead: float = 0.0) -> str:
    """Emit ``beginning[..._position]`` lines placing a lattice in the world.

    The datum is the point where the *line* starts, which is ``lead`` metres
    upstream of the first element's entrance along its incoming direction --
    ``lead`` being the run-up that :func:`bmad_leading_drift` re-emits as a
    drift.
    """
    physical = getattr(first_element, "physical", None)
    if physical is None or physical.middle is None:
        return ""
    try:
        start = np.array(physical.start.array, dtype=float)
        matrix = physical.rotation_matrix
        angles = bmad_floor_angles_from_matrix(matrix)
    except Exception:  # unresolved geometry is not an export failure
        return ""
    if lead:
        start = start - lead * (matrix @ np.array([0.0, 0.0, 1.0]))
    values = [
        ("x_position", start[0]),
        ("y_position", start[1]),
        ("z_position", start[2]),
        ("theta_position", angles["theta"]),
        ("phi_position", angles["phi"]),
        ("psi_position", angles["psi"]),
    ]
    if all(abs(value) <= _BMAD_DATUM_TOLERANCE for _, value in values):
        return ""
    return "".join(
        f"beginning[{name}] = {value:.16g}\n"
        for name, value in values
        if abs(value) > _BMAD_DATUM_TOLERANCE
    )


_BMAD_LEAD_TOLERANCE = 1e-9


def bmad_leading_drift(name: str, lead: float) -> tuple:
    """Re-emit the run-up between a section's start and its first element.

    ``createDrifts()`` only fills the gaps *between* elements, so a section
    whose first element does not sit at s=0 used to export a lattice physically
    shorter than the one it came from.

    Returns the definition line and the line-member name, or ``("", None)`` when
    there is no meaningful gap to fill.
    """
    if lead is None or lead <= _BMAD_LEAD_TOLERANCE:
        return "", None
    drift = f"{name}_lead_drift"
    return f"{drift}: drift, l = {lead:.16g}\n", drift


_BMAD_PATCH_TOLERANCE = 1e-9


def bmad_survey_frame(element, face: str) -> np.ndarray:
    """The orientation Bmad's own survey would report at one face of an element.

    For everything but a rolled bend this is just LAURA's frame. A bend whose
    plane is rolled out of the horizontal is the exception, and it has to be
    undone here rather than left to the caller.
    """
    physical = element.physical
    matrix = (
        physical.rotation_matrix if face == "start" else physical.end_rotation_matrix
    )
    roll = getattr(getattr(element, "magnetic", None), "tilt", None) or 0.0
    if not roll or is_flat_roll(roll) or abs(physical._physical_angle) < 1e-9:
        return matrix
    cosine, sine = np.cos(-roll), np.sin(-roll)
    return matrix @ np.array(
        [[cosine, -sine, 0.0], [sine, cosine, 0.0], [0.0, 0.0, 1.0]]
    )


def bmad_patch(name: str, previous, following) -> tuple:
    """Describe the frame change between two neighbours as a Bmad ``patch``.

    ``createDrifts()`` fills every gap with a drift whose length is the straight
    line between the two faces, which keeps the distance and throws the
    orientation away.

    Returns the definition line and the name, or ``("", None)`` when a drift
    already says everything there is to say.
    """
    try:
        origin = np.array(previous.physical.end.array, dtype=float)
        frame = bmad_survey_frame(previous, "end")
        target = np.array(following.physical.start.array, dtype=float)
        rotation = bmad_survey_frame(following, "start")
    except Exception:  # unresolved geometry is not an export failure
        return "", None
    offset = frame.T @ (target - origin)
    relative = frame.T @ rotation
    turned = float(np.abs(relative - np.eye(3)).max()) > _BMAD_PATCH_TOLERANCE
    slipped = max(abs(offset[0]), abs(offset[1])) > _BMAD_PATCH_TOLERANCE
    if not turned and not slipped and offset[2] >= -_BMAD_PATCH_TOLERANCE:
        return "", None
    angles = bmad_floor_angles_from_matrix(relative)
    values = (
        ("x_offset", offset[0]),
        ("y_offset", offset[1]),
        ("z_offset", offset[2]),
        ("x_pitch", angles["theta"]),
        ("y_pitch", angles["phi"]),
        ("tilt", angles["psi"]),
    )
    written = ", ".join(
        f"{key} = {value:.16g}"
        for key, value in values
        if abs(value) > _BMAD_PATCH_TOLERANCE
    )
    if not written:
        return "", None
    return f"{name}: patch, {written}\n", name
