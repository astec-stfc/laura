"""How an element looks to a beam traversing it backwards.

This is the *physics* half of path reversal.  The geometry half is
:meth:`MachineLayout.arc_lengths <laura.models.elementList.MachineLayout.arc_lengths>`,
and the two are independent: one moves elements, this one changes what they do.

Neither is :func:`~laura.models.elementList.expand_section_order`'s negative
``repeat``.  That reverses the *order* of a line, leaving every element entered
at its own entrance face, and changes no physics at all.

The transformation
------------------

The reversed frame is a rotation by pi about the horizontal
axis: ``x' = x``, ``y' = -y``, ``s' = -s``.  That is a *proper* rotation
(determinant ``+1``), so ``B`` transforms as an ordinary vector, with no
pseudovector subtlety: ``B_x' = B_x``, ``B_y' = -B_y``, ``B_s' = -B_s``.

For a normal multipole of order ``n``, ``B_y + i B_x = b_n (x + i y)^n``.
Substituting ``x = x'``, ``y = -y'`` and the component signs above gives
``B_y' + i B_x' = -b_n (x' + i y')^n`` --- and for a skew term ``i a_n``, the
same substitution gives ``+i a_n``.  So, at **every** order:

* normal coefficients negate
* skew coefficients are unchanged

What is refused
---------------

Anything whose reversal is not a sign flip is refused rather than
approximated, because a silently half-reversed element is worse than no
reversed element at all:

* **RF cavities.**  Reversal changes the zero-phase convention and the sign of
  the energy gain.  That is a convention decision, not a derivation.
* **Field maps and wakefields.**  A sampled map has to be resampled backwards
  and a wake is causal; neither is a coefficient flip.
* **Symbolic strengths.**  Negating a functional definition means rewriting an
  expression, and a textual ``-(...)`` risks changing what it means.
"""

from __future__ import annotations

import copy
from typing import Any, List
from warnings import warn

_MULTIPOLE_BLOCKS = ("multipoles", "systematic_multipoles", "random_multipoles")
"""Containers of ``{K<n>L: Multipole(normal, skew)}`` on a magnetic block."""

_SOLENOID_BLOCKS = ("fields", "systematic_fields", "random_fields")
"""Containers of ``{S<n>L: float}`` on a solenoid's magnetic block.  The
longitudinal field flips with ``s``, so every term negates."""


class ElementNotReversible(Exception):  # noqa: N818 (reads as a condition, not an Error)
    """Raised when an element's reversal is not a sign flip.

    Carries the element name and every reason found, rather than the first, so
    one attempt reports everything that would have to be decided.
    """

    def __init__(self, name: str, reasons: List[str]):
        self.name = name
        self.reasons = reasons
        super().__init__(
            f"'{name}' cannot be reversed: "
            + "; ".join(reasons)
            + ". Reversal flips the sign of every normal multipole in the beam "
            "frame; these need a decision rather than a sign."
        )


def _is_symbolic(value: Any) -> bool:
    return isinstance(value, str)


_STANDING_WAVE = {"standingwave", "sw", "standing"}
_TRAVELLING_WAVE = {"travellingwave", "travelingwave", "tw", "travelling", "traveling"}


def _cavity_reversal_obstacles(element, cavity) -> List[str]:
    """Why a cavity element cannot be traversed backwards, if it cannot.

    A symmetric standing-wave accelerating cavity can, but other cavities
    are refused due to directionality.
    """
    reasons: List[str] = []

    if getattr(element, "hardware_type", None) != "RFCavity":
        reasons.append(
            f"it is a {getattr(element, 'hardware_type', 'cavity-like')} "
            "rather than a plain accelerating cavity"
        )
        return reasons

    if getattr(cavity, "attenuation_constant", 0):
        reasons.append(
            "its power attenuates along its length (attenuation_constant = "
            f"{cavity.attenuation_constant})"
        )

    structure = str(getattr(cavity, "structure_type", "") or "")
    key = structure.replace("-", "").replace("_", "").replace(" ", "").lower()
    if key in _TRAVELLING_WAVE:
        reasons.append(
            "it is a travelling-wave structure"
        )
    elif key not in _STANDING_WAVE:
        reasons.append(
            f"its structure_type is {structure!r}, which is not recognised"
        )
    return reasons


def reversal_obstacles(element) -> List[str]:
    """Every reason ``element`` cannot be reversed by a sign flip, in order.

    Empty for an element :func:`reverse_element` can handle.  Exposed so a
    caller can test a whole line before committing to reversing any of it.
    """
    reasons: List[str] = []

    cavity = getattr(element, "cavity", None)
    if cavity is not None:
        reasons.extend(_cavity_reversal_obstacles(element, cavity))

    simulation = getattr(element, "simulation", None)
    if simulation is not None:
        if getattr(simulation, "field_definition", None):
            reasons.append(
                "it carries a field map"
            )
        if getattr(simulation, "wakefield_definition", None):
            reasons.append(
                "it carries wakefield data"
            )

    magnetic = getattr(element, "magnetic", None)
    if magnetic is not None:
        symbolic = sorted(
            f"{block}.{name}.{component}"
            for block in _MULTIPOLE_BLOCKS
            for name, pole in _iter_multipoles(magnetic, block)
            for component in ("normal", "skew")
            if _is_symbolic(getattr(pole, component, None))
        )
        symbolic += sorted(
            f"{block}.{name}"
            for block in _SOLENOID_BLOCKS
            for name, value in _iter_solenoid_fields(magnetic, block)
            if _is_symbolic(value)
        )
        if symbolic:
            reasons.append(
                "these strengths are symbolic and negating them would mean "
                f"rewriting an expression: {', '.join(symbolic)}"
            )
        for edge in ("entrance_edge_angle", "exit_edge_angle"):
            if _is_symbolic(getattr(magnetic, edge, None)):
                reasons.append(
                    f"'{edge}' is symbolic, so the entrance/exit swap cannot be "
                    "checked against the bend angle it references"
                )

    return reasons


def _is_misaligned(error) -> bool:
    """True only if a measured misalignment is actually non-zero.

    ``physical.error`` is always present as a zero-valued model, so its mere
    existence says nothing; ``exclude_defaults`` is what distinguishes an
    element someone has surveyed from one nobody has.
    """
    if error is None:
        return False
    return bool(error.model_dump(exclude_defaults=True))


def _iter_multipoles(magnetic, block: str):
    container = getattr(magnetic, block, None)
    if container is None:
        return
    for name in type(container).model_fields:
        pole = getattr(container, name, None)
        if pole is not None:
            yield name, pole


def _iter_solenoid_fields(magnetic, block: str):
    container = getattr(magnetic, block, None)
    if container is None:
        return
    for name in type(container).model_fields:
        yield name, getattr(container, name, None)


def reverse_element(element, *, strict: bool = True):
    """A deep copy of ``element`` as a beam traversing it backwards sees it.

    The original is never touched: reversal belongs to a beam path, not to the
    installed hardware, so it must not be persisted.

    Parameters
    ----------
    element
        Any element carrying a ``magnetic`` block; anything else (a drift, a
        marker, a screen) is returned as a plain copy, which is correct --- it
        has nothing that depends on direction.
    strict
        ``True`` (default) raises :class:`ElementNotReversible` for anything
        listed by :func:`reversal_obstacles`.  ``False`` warns and reverses
        what it can, leaving the rest alone --- only for a caller that has
        decided a partial reversal is acceptable.

    Returns
    -------
    The reversed copy.  ``reverse_element(reverse_element(x))`` restores the
    original values.
    """
    obstacles = reversal_obstacles(element)
    if obstacles:
        if strict:
            raise ElementNotReversible(element.name, obstacles)
        warn(
            f"'{element.name}' is only partly reversible and strict=False, so "
            "it is reversed where it can be and left alone elsewhere: "
            + "; ".join(obstacles)
        )

    reversed_element = copy.deepcopy(element)

    physical = getattr(reversed_element, "physical", None)
    if physical is not None and _is_misaligned(getattr(physical, "error", None)):
        warn(
            f"'{element.name}' carries a measured misalignment, which is not "
            "transformed: its offsets and angles are still expressed in the "
            "forward frame."
        )

    magnetic = getattr(reversed_element, "magnetic", None)
    if magnetic is None:
        return reversed_element

    for block in _MULTIPOLE_BLOCKS:
        for _, pole in _iter_multipoles(magnetic, block):
            # Normal coefficients negate at every order; skew are unchanged.
            if isinstance(getattr(pole, "normal", None), (int, float)):
                pole.normal = -pole.normal

    for block in _SOLENOID_BLOCKS:
        container = getattr(magnetic, block, None)
        if container is None:
            continue
        for name, value in _iter_solenoid_fields(magnetic, block):
            if isinstance(value, (int, float)):
                setattr(container, name, -value)

    if "horizontal_kick" in type(magnetic).model_fields and isinstance(
        magnetic.horizontal_kick, (int, float)
    ):
        magnetic.horizontal_kick = -magnetic.horizontal_kick

    entrance = getattr(magnetic, "entrance_edge_angle", None)
    exit_ = getattr(magnetic, "exit_edge_angle", None)
    if entrance is not None or exit_ is not None:
        magnetic.entrance_edge_angle, magnetic.exit_edge_angle = exit_, entrance

    tilt = getattr(magnetic, "tilt", None)
    if isinstance(tilt, (int, float)):
        # A roll about the beam axis, and the beam axis has flipped.
        magnetic.tilt = -tilt

    return reversed_element


_PLACEMENT_FIELDS = ("s", "reference_placement", "datum")
"""Position fields that lattice assembly writes onto a resolved element."""

_ORIENTATION_FIELDS = ("rotation", "global_rotation")
"""Orientation fields assembly *derives* — see :func:`_forget_placement`."""


def _forget_placement(phys, keep_s: bool = False) -> None:
    """Return a resolved physical block to its pre-placement state.

    Placement derives an element's orientation only when the author did not
    supply one, and it decides that with ``"rotation" not in
    phys.model_fields_set``.  A resolved orientation must be forgotten
    rather than overwritten.

    """
    cleared = _PLACEMENT_FIELDS[1:] if keep_s else _PLACEMENT_FIELDS
    for name in ("middle",) + cleared:
        setattr(phys, name, None)
    for name in ("middle",) + cleared + _ORIENTATION_FIELDS:
        phys.model_fields_set.discard(name)
    phys.physical_angle = 0.0
    phys._trajectory = None
    object.__setattr__(phys, "_position_stated", keep_s)


def reverse_section(section, element_registry, *, strict: bool = True, name=None):
    """A :class:`SectionLattice` as a beam traversing *section* backwards sees it.

    The order is reversed, every element is passed through
    :func:`reverse_element`, and the result is re-placed from its own lengths
    by ordinary sequential placement.

    Bend angles are negated by :func:`reverse_element`, so accumulating lengths
    along the reversed order retraces the original path backwards.

    The source section and its elements are not touched.
    """
    from .elementList import SectionLattice

    order = list(reversed(section.order))

    extent = 0.0
    for element_name in section.order:
        phys = getattr(element_registry.get(element_name), "physical", None)
        if phys is not None and phys.s is not None:
            extent = max(extent, phys.s + (phys.length or 0.0) / 2.0)

    elements = {}
    for element_name in order:
        source = element_registry.get(element_name)
        if source is None:
            raise KeyError(
                f"Section '{section.name}' lists '{element_name}', which is not "
                "in the element registry, so it cannot be reversed."
            )
        element = reverse_element(source, strict=strict)
        phys = element.physical
        forward_middle = phys.s
        _forget_placement(phys, keep_s=forward_middle is not None)
        if forward_middle is not None:
            phys.s = extent - forward_middle
            phys.s_point = "middle"
        elements[element_name] = element

    reversed_section = SectionLattice(
        name=name or f"{section.name}_reversed",
        elements=list(elements.values()),
        order=order,
        section_type=section.section_type,
        master_lattice=section.master_lattice,
        functional_definitions=section.functional_definitions,
        resolve_functional=section.resolve_functional,
    )
    registry = reversed_section.elements.elements
    reversed_section._resolve_sequential_placement(registry)
    reversed_section.resolve_positions(registry)
    return reversed_section
