"""
Import a PALS (Particle Accelerator Language Standard) document into LAURA.

PALS is a code-agnostic, YAML-based lattice interchange standard
(https://github.com/campa-consortium/pals). Expansion — ``include``/``load``
merging, ``inherit``, ``repeat``/``direction``/``placement``, ``set``,
superposition, forks, controllers and the expression language — is done by the
reference parser and reaches this module as the plain dataclasses in
``translator/utils/pals``; see there for why that seam exists and how to
install the parser.

Structure maps as: PALS branch -> :class:`SectionLattice`, PALS ``Lattice`` ->
:class:`MachineLayout`, several lattices -> :class:`MachineModel`. That mirrors
the Bmad importer, where a branch is likewise a section and a universe a
layout.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from warnings import warn

from pydantic import BaseModel, ConfigDict, PrivateAttr
from scipy.constants import speed_of_light

import laura.models.element as LAURA_elements
from laura.models.elementList import (
    ElementList,
    MachineLayout,
    MachineModel,
    SectionLattice,
)

from ....Exporters.YAML import PositionMode, export_machine_combined_file
from ...utils.functions import merge_layout_elements, number_repeated_names
from ...utils.pals import (
    LAURA_TYPE_EXTENSION,
    PalsBranch,
    PalsDocument,
    PALS_TWISS_COMPONENTS,
    PalsElement,
    laura_type_to_pals_kind,
    pals_kind_to_laura_type,
    parse_pals_file,
)

#: Parsed but never turned into a LAURA element. Drifts are regenerated from
#: resolved arc-length gaps by ``SectionLattice.createDrifts()``; ``Placeholder``
#: is the ``branch_end`` sentinel every expanded branch carries. ``BeginningEle``
#: is a branch's reference state, read into the section rather than placed as an
#: element, and is handled by :meth:`PalsLatticeImporter._beginning_twiss` --
#: it is the one kind that can still yield an element, from its ``TwissP``.
_SILENTLY_SKIPPED_KINDS = ("Drift", "Placeholder")

#: PALS kinds LAURA has no representation for at all.
_UNSUPPORTED_KINDS = ("Converter", "Feedback", "Girder", "UnionEle")

#: Kinds that survive import in a reduced form, and what is lost. A kind
#: resolved by :func:`pals_kind_to_laura_type` to something other than its
#: natural type belongs here or the loss goes unannounced.
_LOSSY_CONVERSIONS = {
    "Fork": "the branch it forks to; the fork point is kept as a Marker",
    "Patch": "its coordinate transform; LAURA has no patch element",
    "FloorShift": "its floor-frame shift; LAURA has no patch element",
    "ReferenceChange": "its reference-energy/species change",
    "Fiducial": "its fiducial constraint",
    "Foil": "its material and thickness; kept as a Collimator",
    "EGun": "its cathode model; kept as an RFCavity",
    "Taylor": "nothing yet -- the map itself is not imported",
    "ACKicker": "its time dependence; kept as a horizontal AC dipole",
}

#: ``BmadP.Bmad_key`` refinements. PALS collapses a plane-specific corrector
#: onto one ``Kicker`` kind and every diagnostic onto ``Instrument``; a document
#: written out of Bmad carries the original key in its extension group, which
#: recovers the distinction without guessing. Only consulted for the two kinds
#: that are genuinely ambiguous, so a stray ``Bmad_key`` cannot retype an
#: element wholesale.
_BMAD_KEY_REFINEMENT = {
    "Kicker": {
        "hkicker": "Horizontal_Corrector",
        "vkicker": "Vertical_Corrector",
        "kicker": "Combined_Corrector",
    },
    "Instrument": {
        "monitor": "Beam_Position_Monitor",
        "instrument": "Diagnostic",
        "marker": "Marker",
    },
}

_ORDER_TYPES = {0: "Dipole", 1: "Quadrupole", 2: "Sextupole", 3: "Octupole"}

#: The LAURA types whose magnetic model is a kick angle rather than multipoles.
_CORRECTOR_TYPES = (
    "Horizontal_Corrector",
    "Vertical_Corrector",
    "Combined_Corrector",
)

#: ``RFP.cavity_type`` -> LAURA ``cavity.structure_type``.
_CAVITY_TYPES = {
    "STANDING_WAVE": "StandingWave",
    "TRAVELING_WAVE": "TravellingWave",
}

pals_unsupported = [
    "ChargeDiagnostic",
    "CombinedSolenoidQuadrupole",
    "Decapole",
    "ElectrostaticSeparator",
    "Laser",
    "LaserAttenuator",
    "LaserEnergyMeter",
    "LaserHalfWavePlate",
    "LaserMirror",
    "Lighting",
    "Low_Level_RF",
    "NonLinearLens",
    "PID",
    "Plasma",
    "PowerSupply",
    "RFHeartbeat",
    "RFModulator",
    "RFMultipole",
    "RFProtection",
    "Shutter",
    "Stage",
    "VacuumGauge",
    "Valve",
    "Wakefield",
    "Wire",
]


def _number(value: Any) -> Optional[float]:
    """Coerce a PALS scalar to a float, or ``None`` if it is not one.

    Values come back from the expanded tree as YAML scalars, and YAML 1.1 reads
    an exponent written without a decimal point (``1e+09``, which is how the
    parser re-emits ``1.0e9``) as a *string*. Everything numeric therefore has
    to go through here rather than being trusted to arrive as a float.
    """
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _charge_number(species: str) -> Optional[int]:
    """Charge of a PALS species, in units of the elementary charge.

    Species names follow the openPMD convention: a name for the fundamental
    particles, and an ion written with its charge state appended (``Au+79``,
    ``#3He+2``). Only the sign and magnitude of the charge are needed here, to
    normalise a field, so the isotope prefix is ignored.
    """
    name = str(species or "").strip().lower()
    if not name:
        return None
    known = {
        "electron": -1,
        "positron": 1,
        "anti-electron": 1,
        "proton": 1,
        "anti-proton": -1,
        "muon": -1,
        "anti-muon": 1,
        "neutron": 0,
        "anti-neutron": 0,
        "photon": 0,
    }
    if name in known:
        return known[name]
    match = re.search(r"([+-])(\d*)$", name)
    if match:
        magnitude = int(match.group(2)) if match.group(2) else 1
        return magnitude if match.group(1) == "+" else -magnitude
    return None


def _normalisation(element: PalsElement) -> Optional[float]:
    """Factor turning a PALS field into its normalised strength, or ``None``.

    PALS relates the two by ``K = (q / P_0) B``. With the reference momentum
    given as ``pc_ref`` in eV and the charge as a multiple of ``e``, the
    magnetic rigidity is ``pc_ref / (c * charge)``, so the factor is
    ``charge * c / pc_ref``. Both are propagated onto every element by
    expansion, so the conversion is exact and local — checked against
    ``iota.pals.yaml``, whose quadrupoles carry ``Kn1`` and ``Bn1`` together
    and agree to every digit under this factor.

    Returns ``None`` when the branch has no reference (a document may leave it
    out) or the species is neither a name this knows nor a charge-suffixed ion.
    """
    reference = element.group("ReferenceP")
    momentum = _number(reference.get("pc_ref"))
    charge = _charge_number(reference.get("species_ref", ""))
    if not momentum or not charge:
        return None
    return charge * speed_of_light / momentum


def _multipole_orders(
    group: Dict[str, Any], length: float, factor: Optional[float]
) -> tuple:
    """Read ``MagneticMultipoleP`` into ``{order: {normal, skew}}``.

    Values come back integrated and normalised, which is what LAURA stores.
    PALS offers four spellings of the same pole: normalised or not (``KnN`` /
    ``BnN``) and per metre or integrated (a trailing ``L``). Expansion fills in
    whichever the document did not write, so all four usually arrive and agree;
    the normalised pair is read first and the field pair only fills a gap,
    which keeps the ``factor`` out of the common path.

    Returns the orders alongside the field keys that could not be normalised
    because :func:`_normalisation` had nothing to work with.
    """
    orders: Dict[int, Dict[str, float]] = {}
    unconvertible: Dict[str, tuple] = {}
    for prefix in ("K", "B"):
        for key, value in group.items():
            if len(key) < 3 or key[0] != prefix or key[1] not in ("n", "s"):
                continue
            integrated = key.endswith("L")
            digits = key[2:-1] if integrated else key[2:]
            # Excludes the `_taper` companions, which LAURA cannot hold and
            # which the caller reports separately.
            if not digits.isdigit():
                continue
            number = _number(value)
            if number is None:
                continue
            component = "normal" if key[1] == "n" else "skew"
            if prefix == "B":
                if factor is None:
                    unconvertible[key] = (int(digits), component)
                    continue
                number *= factor
            entry = orders.setdefault(int(digits), {})
            entry.setdefault(component, number if integrated else number * length)
    # A field left unconverted only matters where nothing else filled its slot.
    lost = [
        key
        for key, (order, component) in unconvertible.items()
        if component not in orders.get(order, {})
    ]
    return orders, sorted(lost)


def _multipoles(
    element: PalsElement, skip_orders: tuple = ()
) -> Dict[str, Dict[str, Any]]:
    """Build LAURA ``magnetic.multipoles`` from an element's magnetic group."""
    group = element.group("MagneticMultipoleP")
    if not group:
        return {}
    orders, unconvertible = _multipole_orders(
        group, element.length, _normalisation(element)
    )
    multipoles: Dict[str, Dict[str, Any]] = {}
    unconvertible = [
        key
        for key in unconvertible
        if int(key[2:].rstrip("L")) not in skip_orders
    ]
    for order, components in sorted(orders.items()):
        if order in skip_orders:
            continue
        pole: Dict[str, Any] = {"order": order, **components}
        if len(pole) > 1:
            multipoles[f"K{order}L"] = pole

    converted: Dict[str, Any] = {"multipoles": multipoles} if multipoles else {}

    # PALS tilts each order of the field separately and LAURA holds one tilt for
    # the whole magnet, so a single tilt -- which is what a rotated magnet has,
    # and all a magnet written out of LAURA can have -- comes across as that
    # one. Several different ones do not.
    tilted = sorted(
        key for key in group if key.startswith("tilt") and _number(group[key])
    )
    angles = {_number(group[key]) for key in tilted}
    if len(angles) == 1:
        converted["tilt"] = angles.pop()
    elif tilted:
        warn(
            f"PALS element {element.name!r} tilts its multipole orders by "
            f"different amounts ({', '.join(tilted)}); LAURA holds a single "
            "magnet tilt, so none of them were imported."
        )
    tapered = sorted(
        key for key in group if key.endswith("_taper") and _number(group[key])
    )
    if tapered:
        warn(
            f"PALS element {element.name!r} sets tapering fields "
            f"({', '.join(tapered)}); LAURA has no tapering model, so only the "
            "untapered strength was imported."
        )
    if unconvertible:
        warn(
            f"PALS element {element.name!r} gives unnormalised fields "
            f"({', '.join(unconvertible)}) that no normalised value accompanies; "
            "converting them needs the branch reference momentum and species, "
            "which this branch does not set, so those poles were dropped."
        )
    return converted


def _corrector(magnetic: Dict[str, Any], hardware_type: str) -> tuple:
    """Move a kicker's order-0 multipole into LAURA's per-plane kick angles.

    PALS gives a kicker its deflection as a multipole; LAURA's
    ``Corrector_Magnet`` holds an angle per plane and no multipoles at all, so
    the pole has to be carried across rather than stored. A deflection is
    measured the opposite way round from a bend's -- a positive ``Kn0L`` bends
    towards negative ``x``, a positive horizontal kick towards positive ``x`` --
    so the normal component changes sign and the skew one does not. That is the
    same convention LAURA already reads Xsuite's ``knl[0]``/``ksl[0]`` with, and
    the one the PALS reference translators use for MAD-X's ``hkick``/``vkick``.

    A single-plane corrector that turns out to carry the other plane's pole is
    widened to a combined one, which is the only way to keep both. Returns the
    rewritten magnetic block, the hardware type and any higher-order poles the
    corrector model cannot hold.
    """
    poles = magnetic.get("multipoles", {})
    pole = poles.pop("K0L", None) or {}
    horizontal = -pole["normal"] if pole.get("normal") else 0.0
    vertical = pole["skew"] if pole.get("skew") else 0.0
    if horizontal and hardware_type == "Vertical_Corrector":
        hardware_type = "Combined_Corrector"
    if vertical and hardware_type == "Horizontal_Corrector":
        hardware_type = "Combined_Corrector"

    kicks = {"horizontal_kick": horizontal, "vertical_kick": vertical}
    if hardware_type == "Horizontal_Corrector":
        del kicks["vertical_kick"]
    elif hardware_type == "Vertical_Corrector":
        del kicks["horizontal_kick"]
    rewritten = {key: value for key, value in magnetic.items() if key != "multipoles"}
    rewritten.update(kicks)
    return rewritten, hardware_type, sorted(poles)


def _bend(element: PalsElement) -> Dict[str, Any]:
    """Convert ``BendP`` (plus the bend's own multipoles) to LAURA ``magnetic``.

    The bending strength is taken once: from ``angle_ref`` where the parser
    computed it, else ``length * g_ref``. ``MagneticMultipoleP.Kn0``/``Kn0L``
    mirror the same field whenever ``Kn0_from_g_ref`` is set, so order 0 is
    skipped in the multipole pass to avoid counting the dipole field twice.
    """
    bend = element.group("BendP")
    length = element.length
    angle = _number(bend.get("angle_ref"))
    if angle is None:
        g_ref = _number(bend.get("g_ref"))
        angle = None if g_ref is None else g_ref * length
    if angle is None:
        multipole = element.group("MagneticMultipoleP")
        angle = _number(multipole.get("Kn0L"))
        if angle is None:
            per_metre = _number(multipole.get("Kn0"))
            angle = None if per_metre is None else per_metre * length

    magnetic: Dict[str, Any] = _multipoles(element, skip_orders=(0,))
    multipoles = magnetic.setdefault("multipoles", {})
    if angle is not None:
        multipoles["K0L"] = {"normal": angle, "order": 0}

    # e1/e2 are radians in PALS, and every LAURA importer hands a native
    # radian edge angle to these fields unconverted, so do the same here
    # rather than being the one code that disagrees.
    geometry = str(bend.get("ref_geometry", "ARC")).upper()
    for pals_key, laura_key in (
        ("e1", "entrance_edge_angle"),
        ("e2", "exit_edge_angle"),
    ):
        value = _number(bend.get(pals_key))
        if value is None:
            # Expansion normally fills e1/e2 in from the rectangular pair, but
            # the sector angle is recoverable if it did not. The offset between
            # the two depends on which end the reference frame is fixed to:
            # half the bend angle under ARC/CHORD, the whole angle at the free
            # end under ENTRANCE_COORDS/EXIT_COORDS, and nothing at the fixed
            # one (BendP docs, e1/e2).
            rectangular = _number(bend.get(f"{pals_key}_rect"))
            if rectangular is not None and angle is not None:
                if geometry in ("ARC", "CHORD"):
                    offset = angle / 2.0
                elif geometry == "ENTRANCE_COORDS":
                    offset = 0.0 if pals_key == "e1" else angle
                elif geometry == "EXIT_COORDS":
                    offset = angle if pals_key == "e1" else 0.0
                else:
                    offset = angle / 2.0
                value = rectangular + offset
        if value:
            magnetic[laura_key] = value

    curvatures = sorted(key for key in ("h1", "h2") if _number(bend.get(key)))
    if curvatures:
        warn(
            f"PALS bend {element.name!r} has curved pole faces "
            f"({', '.join(curvatures)}); LAURA has no pole-face curvature, so "
            "the faces were imported flat."
        )

    for pals_key, fint_key, gap_key in (
        ("edge1_int", "edge_field_integral", "gap"),
        ("edge2_int", "exit_edge_field_integral", "exit_gap"),
    ):
        product = _number(bend.get(pals_key))
        if not product:
            continue
        # PALS states one number where LAURA holds two: `edgeN_int` *is* the
        # `fint * hgap` product (BendP docs), and nothing in the document says
        # how it divides. Only the product enters the edge kick, so it is
        # preserved exactly by pinning the half gap to 1 m.
        magnetic[fint_key] = product
        magnetic[gap_key] = 2.0
        warn(
            f"PALS bend {element.name!r} gives {pals_key} = {product}, which is "
            "the fint*hgap product; LAURA stores the two separately, so the gap "
            "was pinned to 2 m and the integral set to the product. The edge "
            "kick is right, the individual values are not physical."
        )
    for exit_key, entrance_key in (
        ("exit_edge_field_integral", "edge_field_integral"),
        ("exit_gap", "gap"),
    ):
        if exit_key in magnetic and magnetic.get(exit_key) == magnetic.get(
            entrance_key
        ):
            magnetic.pop(exit_key)

    tilt = _number(bend.get("tilt_ref"))
    if tilt:
        magnetic["tilt"] = tilt
    if not multipoles:
        magnetic.pop("multipoles", None)
    return magnetic


def _body_shift(element: PalsElement) -> Dict[str, Any]:
    """Convert ``BodyShiftP`` to a LAURA ``physical.error``.

    The three rotations are named for the axis they turn about, and LAURA's are
    not, so the mapping is composed from two measured conversions rather than
    read off the names: PALSParserPy's ``to_bmad`` writes ``x_rot`` as Bmad
    ``y_pitch`` *negated*, ``y_rot`` as ``x_pitch``, and ``z_rot`` as ``tilt``;
    LAURA's Bmad importer then takes ``phi = -y_pitch``, ``theta = -x_pitch``
    and ``psi = roll``. Composing gives ``phi = x_rot``, ``theta = -y_rot``,
    ``psi = z_rot``.
    """
    shift = element.group("BodyShiftP")
    if not shift:
        return {}
    position = {
        axis: _number(shift.get(f"{axis}_offset")) or 0.0 for axis in ("x", "y", "z")
    }
    rotation = {
        "phi": _number(shift.get("x_rot")) or 0.0,
        "theta": -(_number(shift.get("y_rot")) or 0.0),
        "psi": _number(shift.get("z_rot")) or 0.0,
    }
    if not any(position.values()) and not any(rotation.values()):
        return {}
    return {"error": {"position": position, "rotation": rotation}}


def _aperture(element: PalsElement) -> Dict[str, Any]:
    """Convert ``ApertureP`` limits to a LAURA ``aperture`` dict.

    PALS states signed edges (``x_min``/``x_max``) or a full ``x_width`` about
    an ``x_center``; LAURA's ``horizontal_size``/``vertical_size`` are full
    widths, so the width form is used directly and the edge form is differenced.
    An ``ApertureP`` carrying only a shape and a location — which is what a
    Bmad-derived document puts on every element — describes no aperture at all
    and must not become a zero-size one.
    """
    group = element.group("ApertureP")
    if not group or group.get("aperture_active") is False:
        return {}
    sizes: Dict[str, Any] = {}
    one_sided = []
    for axis, laura_key in (("x", "horizontal_size"), ("y", "vertical_size")):
        width = _number(group.get(f"{axis}_width"))
        if width is None:
            low, high = (
                _number(group.get(f"{axis}_min")),
                _number(group.get(f"{axis}_max")),
            )
            if low is not None and high is not None:
                width = high - low
            elif low is not None or high is not None:
                # A limit on one side only, which PALS allows and LAURA's single
                # full width cannot express. Mirroring the limit keeps the stated
                # side right and is the least surprising of the wrong answers.
                one_sided.append(axis)
                width = 2.0 * abs(low if low is not None else high)
        if width:
            sizes[laura_key] = abs(width)
    if not sizes:
        return {}
    if one_sided:
        warn(
            f"PALS element {element.name!r} has a one-sided "
            f"{'/'.join(one_sided)} aperture; LAURA holds a full width, so it "
            "was imported symmetric about the axis."
        )
    offsets = sorted(
        axis for axis in ("x", "y") if _number(group.get(f"{axis}_center"))
    )
    if offsets:
        warn(
            f"PALS element {element.name!r} has an off-axis aperture "
            f"({', '.join(f'{axis}_center' for axis in offsets)}); LAURA has no "
            "aperture offset, so it was centred on the axis."
        )
    shape = str(group.get("shape", "ELLIPTICAL")).lower()
    if shape in ("vertices", "custom_shape"):
        warn(
            f"PALS element {element.name!r} has a {shape} aperture; LAURA has no "
            "polygon aperture, so only its bounding size was imported."
        )
        shape = "rectangular"
    sizes["shape"] = shape if shape in ("rectangular", "elliptical") else "rectangular"

    location = str(group.get("location", "")).upper()
    if location and location not in ("EVERYWHERE", "BOTH_ENDS"):
        warn(
            f"PALS element {element.name!r} applies its aperture at {location}; "
            "LAURA has no aperture location, so it will act along the whole element."
        )
    return {"aperture": sizes}


def _cell_length(frequency: float, cavity: Dict[str, Any]) -> float:
    """The length of one cell, from the cavity's frequency and its mode.

    PALS states a cavity's frequency but never its mode, so this is an
    assumption about the mode and nothing more: a travelling-wave structure is
    read as 2*pi/3 (`lambda/3`, the S-band linac standard) and everything else
    as pi (`lambda/2`). The `structure_type` discriminator is the same one the
    field amplitude needs just below. Taking `lambda/2` for *every* cavity,
    which is what this did before, makes a travelling-wave cell half as long
    again as it should be.

    The tempting alternative -- `L_active/num_cells`, which would be geometry
    rather than a guess -- is not available. The parser's bookkeeper derives
    `L_active` as the element length whenever the document omits it, exactly as
    it derives `voltage` from `gradient`, so a stated active length cannot be
    told from a defaulted one; and `length/num_cells` under-reads a real cavity,
    whose physical length also holds couplers and end cells.
    """
    order = 3.0 if cavity.get("structure_type") == "TravellingWave" else 2.0
    return speed_of_light / (order * frequency)


def _cavity(element: PalsElement) -> Dict[str, Dict[str, Any]]:
    """Convert ``RFP`` to LAURA ``cavity`` and ``simulation`` dicts."""
    rf = element.group("RFP")
    if not rf:
        return {}
    length = element.length
    frequency = _number(rf.get("frequency"))
    if frequency is None and rf.get("harmon") is not None:
        warn(
            f"PALS cavity {element.name!r} sets harmon rather than frequency; "
            "converting it needs the ring circumference, so no frequency was set."
        )
    n_cells = int(_number(rf.get("num_cells")) or 1)
    active_length = _number(rf.get("L_active")) or length

    cavity: Dict[str, Any] = {}
    cavity_type = str(rf.get("cavity_type", "") or "").upper()
    if cavity_type:
        # LAURA spells the travelling-wave case with two Ls throughout.
        cavity["structure_type"] = _CAVITY_TYPES.get(cavity_type, "StandingWave")

    if frequency:
        cavity["frequency"] = frequency
        cavity["cell_length"] = _cell_length(frequency, cavity)
    cavity["n_cells"] = n_cells
    phase = _number(rf.get("phase"))
    if phase is not None:
        # PALS states phase in rad/2pi (turns) and the reference translator
        # copies it straight to Bmad's phi0; LAURA's Bmad importer reads a
        # phi0 as -360*phi0 degrees, so the same negation applies here.
        cavity["phase"] = -360.0 * phase

    # A LAURA field amplitude is a voltage for a standing-wave cavity but a
    # gradient for a travelling-wave one, which is the same split PALS makes.
    # Which of the pair to read is decided by the structure type and not by
    # which one the document states: the parser's bookkeeper derives the other
    # (`voltage = gradient * L_active`), so both are nearly always present, and
    # reading the voltage of a travelling-wave cavity scales the amplitude by
    # the active length every time the lattice is read.
    voltage = _number(rf.get("voltage"))
    gradient = _number(rf.get("gradient"))
    if cavity.get("structure_type") == "TravellingWave":
        amplitude = gradient
        if amplitude is None and voltage is not None:
            amplitude = voltage / active_length if active_length else voltage
    else:
        amplitude = voltage
        if amplitude is None and gradient is not None:
            amplitude = gradient * active_length

    zero_phase = str(rf.get("zero_phase", "ACCELERATING") or "ACCELERATING").upper()
    if zero_phase != "ACCELERATING":
        warn(
            f"PALS cavity {element.name!r} measures its phase from {zero_phase}; "
            "LAURA's phase is always measured from the accelerating crest, so "
            "the imported phase is offset by a quarter period."
        )
    for key, message in (
        ("multipass_phase", "a per-pass phase offset"),
        ("dE_ref", "a reference-energy change"),
    ):
        if _number(rf.get(key)):
            warn(
                f"PALS cavity {element.name!r} sets {key}; LAURA cannot hold "
                f"{message}, so it was dropped."
            )

    converted: Dict[str, Dict[str, Any]] = {"cavity": cavity}
    if amplitude is not None:
        converted["simulation"] = {"field_amplitude": amplitude}
    return converted


class PalsLatticeImporter(BaseModel):
    """Read a ``*.pals.yaml`` document into LAURA elements, sections and layouts."""

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    source_file: Optional[str] = None
    """Path to the PALS document to import."""

    document: Optional[Any] = None
    """A pre-parsed :class:`~laura.translator.utils.pals.PalsDocument`, used in
    place of ``source_file`` when the caller already has one."""

    name: str = "Lattice"

    machine_area: str = "Lattice"

    lattice: Optional[str] = None
    """Which PALS ``Lattice`` to import. Defaults to the only one present —
    ``use`` has already selected it during expansion."""

    laura_elements: Dict = {}
    """Converted elements, keyed by numbered name, for the selected branch."""

    _by_branch: Dict[str, Dict[str, Any]] = PrivateAttr(default_factory=dict)
    _native: Dict[str, Dict[str, PalsElement]] = PrivateAttr(default_factory=dict)
    _reference: Dict[str, Dict[str, Any]] = PrivateAttr(default_factory=dict)
    _warned_kinds: set = PrivateAttr(default_factory=set)

    def _default_name(self) -> str:
        if self.name != "Lattice":
            return self.name
        if self.source_file:
            return Path(self.source_file).name.split(".")[0]
        return self.name

    def _document(self) -> PalsDocument:
        if self.document is None:
            if not self.source_file:
                raise ValueError(
                    "PalsLatticeImporter needs either source_file or document."
                )
            self.document = parse_pals_file(self.source_file)
            for problem in self.document.errors:
                # Expansion reports an ERROR without necessarily giving up on
                # the document -- bta.pals.yaml raises 21 and still expands --
                # so these are surfaced, not raised.
                warn(f"PALS expansion problem: {problem}")
        return self.document

    def _lattice(self):
        document = self._document()
        if not document.lattices:
            # Only the lattice named by `use` is expanded, so a document with
            # none is either a fragment meant to be loaded by another file or a
            # complete one that forgot to say which lattice to use.
            raise ValueError(
                f"No expanded lattice in {document.source}. A PALS document only "
                "expands the lattice its `use` names; import the file that "
                "declares `use` rather than a fragment it loads."
            )
        if self.lattice is None:
            return document.lattices[0]
        for lattice in document.lattices:
            if lattice.name == self.lattice:
                return lattice
        available = ", ".join(lat.name for lat in document.lattices)
        raise KeyError(f"No lattice named {self.lattice!r}; found: {available}")

    def branch_names(self) -> List[str]:
        """Names of the branches in the selected lattice, in document order."""
        return [branch.name for branch in self._lattice().branches]

    def create_element_dictionary(
        self, branch: Optional[str] = None
    ) -> Dict[str, PalsElement]:
        """Return the branch's expanded PALS elements, keyed by numbered name."""
        target = self._branch(branch)
        numbered = number_repeated_names([element.name for element in target.elements])
        native = dict(zip(numbered, target.elements))
        self._native[target.name] = native
        self._reference[target.name] = self._branch_reference(target)
        return native

    def _branch(self, branch: Optional[str] = None) -> PalsBranch:
        lattice = self._lattice()
        if branch is None:
            return lattice.branches[0]
        for candidate in lattice.branches:
            if candidate.name == branch:
                return candidate
        available = ", ".join(b.name for b in lattice.branches)
        raise KeyError(f"No branch named {branch!r}; found: {available}")

    @staticmethod
    def _branch_reference(branch: PalsBranch) -> Dict[str, Any]:
        """Species, energy and geometry for a branch, from its first element.

        ``ReferenceP`` is an input parameter only on the ``BeginningEle``; every
        other element carries the propagated output value, so the first element
        of the branch is the one to read.
        """
        reference: Dict[str, Any] = {}
        if branch.elements:
            group = branch.elements[0].group("ReferenceP")
            species = group.get("species_ref")
            if species:
                reference["particle"] = str(species)
            energy = _number(group.get("E_tot_ref"))
            if energy is None:
                energy = _number(group.get("pc_ref"))
            if energy is not None:
                reference["reference_energy"] = energy
        # `periodic` asks whether periodic optics are appropriate, which is the
        # same linac-vs-ring distinction LAURA's geometry enum draws, though
        # PALS is explicit that it does not assert the ends join. PALS documents
        # its default as false, so a branch that is silent is an open one.
        reference["geometry"] = "closed" if branch.attributes.get("periodic") else "open"
        return reference

    def create_laura_element_dictionary(
        self, branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert one branch's PALS elements into LAURA elements."""
        target = self._branch(branch)
        native = self.create_element_dictionary(target.name)
        switch = pals_kind_to_laura_type()

        elements: Dict[str, Any] = {}
        for numbered_name, element in native.items():
            converted = self._convert(numbered_name, element, switch)
            if converted is not None:
                elements[numbered_name] = converted
        self._by_branch[target.name] = elements
        self.laura_elements = elements
        return elements

    def _convert(
        self, numbered_name: str, element: PalsElement, switch: Dict[str, str]
    ) -> Optional[Any]:
        kind = element.kind
        if kind == "BeginningEle":
            return self._beginning_twiss(numbered_name, element)
        if kind in _SILENTLY_SKIPPED_KINDS:
            return None
        if kind in _UNSUPPORTED_KINDS:
            self._warn_once(
                kind,
                f"PALS {kind} elements have no LAURA equivalent; "
                f"{numbered_name!r} was skipped.",
            )
            return None

        hardware_type = switch.get(kind.lower())
        if kind == "Multipole":
            hardware_type = self._multipole_type(element)
        hardware_type = self._refine(kind, element, hardware_type)
        if not hardware_type:
            warn(f"Unrecognised PALS element kind {kind!r} for {numbered_name!r}; skipping.")
            return None
        if kind in _LOSSY_CONVERSIONS:
            self._warn_once(
                kind,
                f"PALS {kind} {numbered_name!r} loses {_LOSSY_CONVERSIONS[kind]}.",
            )
        if element.parameters.get("direction") == -1:
            warn(
                f"PALS element {numbered_name!r} is traversed in reverse "
                "(direction: -1); LAURA has no element reversal, so it was "
                "imported facing forwards."
            )
        if element.parameters.get("is_on") is False:
            warn(
                f"PALS element {numbered_name!r} has is_on: false; LAURA has no "
                "field-off switch, so it was imported with its fields on."
            )

        length = element.length
        if length < 0.0:
            # PALS does not forbid a negative length (an expression can produce
            # one), LAURA's physical model does. Keeping the exit face and
            # zeroing the length leaves everything downstream where PALS put it.
            warn(
                f"PALS element {numbered_name!r} has a negative length "
                f"({length}); LAURA cannot hold one, so it was imported as a "
                "zero-length element at its exit position."
            )
            length = 0.0
        data: Dict[str, Any] = {
            "name": numbered_name,
            "hardware_type": hardware_type,
            "machine_area": self.machine_area,
            # PALS `s_position` is the element's upstream face; LAURA's
            # importers all hand `physical.s` the exit position.
            "physical": {
                "s": element.s_end,
                "s_point": "end",
                "length": length,
            },
        }
        data["physical"].update(_body_shift(element))
        data.update(_aperture(element))
        data.update(_cavity(element))

        magnetic: Dict[str, Any] = {}
        if kind == "Bend":
            magnetic = _bend(element)
        elif kind == "Solenoid":
            # S0L holds the normalised strength here, as it does coming from
            # MAD-X (`ks`), Xsuite (`ks`) and Ocelot (`k`), which is also what
            # keeps a solenoid consistent with the normalised multipoles above.
            solenoid = element.group("SolenoidP")
            strength = _number(solenoid.get("Ksol"))
            if strength is None:
                field = _number(solenoid.get("Bsol"))
                factor = _normalisation(element)
                if field is not None and factor is None:
                    self._warn_once(
                        "Solenoid",
                        f"PALS solenoid {numbered_name!r} gives only the "
                        "unnormalised Bsol; normalising it needs the branch "
                        "reference momentum and species, which this branch does "
                        "not set, so no strength was imported.",
                    )
                elif field is not None:
                    strength = field * factor
            if strength is not None:
                magnetic = {"length": length, "fields": {"S0L": strength * length}}
        else:
            magnetic = _multipoles(element)
        if magnetic and hardware_type in _CORRECTOR_TYPES:
            magnetic, hardware_type, leftover = _corrector(magnetic, hardware_type)
            data["hardware_type"] = hardware_type
            if leftover:
                self._warn_once(
                    "Kicker",
                    f"PALS kicker {numbered_name!r} carries higher-order "
                    f"multipoles ({', '.join(leftover)}) alongside its "
                    "deflection; a LAURA corrector holds only a kick angle per "
                    "plane, so those poles were dropped.",
                )
        if magnetic:
            if "length" not in magnetic:
                magnetic["length"] = length
            data["magnetic"] = magnetic
        if element.group("ElectricMultipoleP"):
            self._warn_once(
                "ElectricMultipoleP",
                f"PALS element {numbered_name!r} has electric multipoles, which "
                "LAURA cannot represent; they were dropped.",
            )
        if element.parameters.get("multipass_index") not in (None, 1):
            self._warn_once(
                "multipass",
                f"PALS element {numbered_name!r} is a multipass element; LAURA "
                "has no multipass concept, so each pass is a separate element.",
            )

        try:
            element_class = getattr(LAURA_elements, hardware_type)
        except AttributeError:
            warn(
                f"LAURA has no element class {hardware_type!r} for PALS "
                f"{kind} {numbered_name!r}; skipping."
            )
            return None
        return element_class(**data)

    def _beginning_twiss(
        self, numbered_name: str, element: PalsElement
    ) -> Optional[Any]:
        """A branch's ``BeginningEle`` as a LAURA element, if it holds anything.

        The element is the branch's reference state, which
        :meth:`_branch_reference` reads into the section rather than into the
        lattice, so ordinarily nothing comes back from it. Its ``TwissP`` is the
        exception: design optics have nowhere else to live, and LAURA states
        them as a zero-length ``TwissMatch`` at the head of the section, which
        is what the Bmad importer makes of a ``beginning_ele`` too.
        """
        twiss = element.group("TwissP")
        if not twiss:
            return None
        values = {
            laura_key: _number(twiss.get(pals_key))
            for pals_key, laura_key in PALS_TWISS_COMPONENTS.items()
        }
        if not values.get("beta_x") or not values.get("beta_y"):
            warn(
                f"PALS branch element {numbered_name!r} gives Twiss parameters "
                "without a beta in both planes; LAURA's TwissMatch needs both, "
                "so the design optics were dropped."
            )
            return None
        return LAURA_elements.TwissMatch(
            name=numbered_name,
            hardware_type="TwissMatch",
            machine_area=self.machine_area,
            physical={"s": element.s_end, "s_point": "end", "length": 0.0},
            simulation={
                **{key: value for key, value in values.items() if value is not None},
                "from_beam": False,
            },
        )

    def _multipole_type(self, element: PalsElement) -> Optional[str]:
        """Pick a LAURA type for a thin ``Multipole`` from its highest order.

        LAURA has no general thin-multipole element, so the element is typed by
        the strongest pole it carries — the same fallback the Bmad importer
        uses for Bmad's own multipole types.
        """
        orders, _ = _multipole_orders(
            element.group("MagneticMultipoleP"),
            element.length,
            _normalisation(element),
        )
        if not orders:
            return "Marker"
        highest = max(orders)
        chosen = _ORDER_TYPES.get(highest)
        if chosen is None:
            self._warn_once(
                "Multipole",
                f"PALS Multipole {element.name!r} has order {highest}, above the "
                "highest LAURA magnet type; imported as an Octupole with its "
                "higher poles kept as multipoles.",
            )
            chosen = "Octupole"
        return chosen

    @staticmethod
    def _refine(
        kind: str, element: PalsElement, hardware_type: Optional[str]
    ) -> Optional[str]:
        """Recover a subtype the kind cannot express, from an extension group.

        A document LAURA wrote states the type outright in its own extension
        group, which is exact; one that came out of Bmad carries the original
        Bmad key, which distinguishes the two families PALS collapses. The
        LAURA hint wins where both are present.

        It is honoured only when LAURA still has the type named and the type
        agrees with the kind it is written on -- either because that is the
        kind LAURA exports it as, or because the type has no kind of its own
        and was written out as the ``Marker`` or ``Drift`` that stood in for it.
        """
        stated = str(element.group(LAURA_TYPE_EXTENSION).get("hardware_type", ""))
        if stated and laura_type_to_pals_kind(stated) in (kind, None):
            if hasattr(LAURA_elements, stated):
                return stated
            warn(
                f"PALS element {element.name!r} states a LAURA hardware type "
                f"{stated!r} that this version of LAURA does not have; the type "
                "was taken from the element kind instead."
            )
        refinements = _BMAD_KEY_REFINEMENT.get(kind)
        if not refinements:
            return hardware_type
        bmad_key = str(element.group("BmadP").get("Bmad_key", "")).lower()
        return refinements.get(bmad_key, hardware_type)

    def _warn_once(self, key: str, message: str) -> None:
        if key in self._warned_kinds:
            return
        self._warned_kinds.add(key)
        warn(message)

    def create_section(
        self, branch: Optional[str] = None
    ) -> Dict[str, SectionLattice]:
        """Build one :class:`SectionLattice` from a PALS branch.

        Returns nothing for a branch that holds only drifts and reference
        elements — legal in PALS, and a section LAURA has no use for — so that
        one such branch does not take a lattice's real branches down with it.
        """
        target = self._branch(branch)
        elements = self._by_branch.get(target.name)
        if elements is None:
            elements = self.create_laura_element_dictionary(target.name)
        if not elements:
            warn(
                f"PALS branch {target.name!r} holds no element LAURA keeps "
                "(drifts are regenerated from the gaps between elements), so no "
                "section was made for it."
            )
            return {}
        reference = self._reference.get(target.name, {})
        section = SectionLattice(
            order=[
                name
                for name, element in elements.items()
                if not element.is_subelement()
            ],
            elements=ElementList(elements=elements),
            name=target.name,
            geometry=reference.get("geometry"),
            reference_energy=reference.get("reference_energy"),
        )
        section.resolve_positions(elements)
        return {target.name: section}

    def create_layout(
        self, name: Optional[str] = None, branches: Optional[List[str]] = None
    ) -> MachineLayout:
        """Build a layout from the lattice's branches, one section per branch."""
        lattice = self._lattice()
        wanted = branches or [branch.name for branch in lattice.branches]
        sections: Dict[str, SectionLattice] = {}
        for branch_name in wanted:
            sections.update(self.create_section(branch_name))
        if not sections:
            raise ValueError(
                f"No branch of PALS lattice {lattice.name!r} produced a LAURA "
                "section."
            )
        particles = {
            self._reference.get(branch_name, {}).get("particle")
            for branch_name in wanted
        }
        particles.discard(None)
        return MachineLayout(
            name=name or lattice.name or self._default_name(),
            sections=sections,
            particle=particles.pop() if len(particles) == 1 else None,
        )

    def create_machine_model(self, min_section_length: int = 5) -> MachineModel:
        """Build a model with one layout per PALS ``Lattice``.

        Only the lattice named by ``use`` survives expansion, so this is usually
        a single layout; the shape allows more, as ``create_layout`` does.
        """
        if min_section_length < 1:
            raise ValueError("min_section_length must be at least 1.")
        document = self._document()

        elements: Dict[str, Any] = {}
        section_definitions: Dict[str, List[str]] = {}
        layout_definitions: Dict[str, List[str]] = {}
        section_metadata: Dict[str, tuple] = {}
        layout_particles: Dict[str, Optional[str]] = {}
        skipped: List[str] = []

        for pals_lattice in document.lattices:
            layout = PalsLatticeImporter(
                document=document,
                lattice=pals_lattice.name,
                machine_area=self.machine_area,
            ).create_layout()
            layout_sections = []
            for source_name, section in layout.sections.items():
                if len(section.order) < min_section_length:
                    skipped.append(f"{layout.name}/{source_name}")
                    continue
                section_name = source_name
                if section_name in section_definitions:
                    section_name = f"{layout.name}_{section_name}"
                merge_layout_elements(
                    elements,
                    section_definitions,
                    section_name,
                    section.elements.elements.items(),
                    section.order,
                    layout.name,
                )
                section_metadata[section_name] = (
                    section.geometry,
                    section.reference_energy,
                )
                layout_sections.append(section_name)
            if layout_sections:
                layout_definitions[layout.name] = layout_sections
                layout_particles[layout.name] = layout.particle

        if skipped:
            warn(
                "Skipped PALS branches shorter than min_section_length="
                f"{min_section_length}: {', '.join(skipped)}"
            )
        if not layout_definitions:
            raise ValueError(
                f"No PALS layouts meet min_section_length={min_section_length}."
            )

        particles = {particle for particle in layout_particles.values() if particle}
        model = MachineModel(
            elements=elements,
            section={"sections": section_definitions},
            layout={
                "layouts": layout_definitions,
                "default_layout": next(iter(layout_definitions)),
            },
            master_lattice=str(Path(document.source).parent),
            particle=particles.pop() if len(particles) == 1 else None,
        )
        for section_name, (geometry, reference_energy) in section_metadata.items():
            section = model.sections.get(section_name)
            if section is None:
                continue
            section.geometry = geometry
            section.reference_energy = reference_energy
        for layout_name, particle in layout_particles.items():
            layout = model.lattices.get(layout_name)
            if layout is not None:
                layout.particle = particle
        return model

    def export_yaml(
        self,
        path: str,
        source: Union[SectionLattice, MachineLayout, MachineModel],
        position_mode: PositionMode = "s",
    ) -> None:
        export_machine_combined_file(path, source, position_mode=position_mode)
