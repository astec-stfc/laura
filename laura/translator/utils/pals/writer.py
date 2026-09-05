"""Write LAURA elements, sections and layouts as a PALS document.

This is the inverse of ``translator/converters/codes/pals.py``
Two things the standard offers are deliberately not used:

``placement`` / ``superimpose``
    A PALS line item can be positioned by an offset from another item rather
    than by the running sum of the lengths ahead of it, which would let a
    lattice be written without drifts at all. Here, gaps are written as
    explicit ``Drift`` elements, from ``SectionLattice.createDrifts()``.

``BeamLine`` nesting
    LAURA has no sub-line concept to nest with, so each section is written flat.

The document shape is one ``BeamLine`` per LAURA section, one ``Lattice``
naming them as branches, and a ``use``.
"""

from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Sequence
from warnings import warn

import numpy as np
import yaml

from .kinds import LAURA_TYPE_EXTENSION, laura_type_to_pals_kind, pals_kind_round_trips

__all__ = [
    "PALS_RESERVED_NAMES",
    "PALS_TWISS_COMPONENTS",
    "PalsBeamLine",
    "pals_document",
    "pals_element_body",
    "pals_safe_names",
]

PALS_RESERVED_NAMES = frozenset(
    {"expand_lattice", "include", "load", "set", "superimpose", "use"}
)
"""Facility keys a PALS parser reads as a command rather than as a name.
"""

PALS_RENAME_SUFFIX = "_element"
"""Appended to a reserved name; a further ``_2``, ``_3`` ... breaks a tie."""

_KIND_GROUPS = {
    "ACKicker": {"ApertureP", "BodyShiftP", "MagneticMultipoleP"},
    "BeamBeam": {"ApertureP", "BodyShiftP"},
    "BeginningEle": {"ApertureP", "BodyShiftP", "ReferenceP"},
    "Bend": {"ApertureP", "BendP", "BodyShiftP", "MagneticMultipoleP"},
    "CrabCavity": {"ApertureP", "BodyShiftP", "MagneticMultipoleP", "RFP"},
    "Drift": {"ApertureP", "BodyShiftP"},
    "Instrument": {"ApertureP", "BodyShiftP", "MagneticMultipoleP"},
    "Kicker": {"ApertureP", "BodyShiftP", "MagneticMultipoleP"},
    "Marker": {"ApertureP", "BodyShiftP"},
    "Mask": {"ApertureP", "BodyShiftP", "MagneticMultipoleP"},
    "Match": {"ApertureP", "BodyShiftP"},
    "Multipole": {"ApertureP", "BodyShiftP", "MagneticMultipoleP"},
    "Octupole": {"ApertureP", "BodyShiftP", "MagneticMultipoleP"},
    "Quadrupole": {"ApertureP", "BodyShiftP", "MagneticMultipoleP"},
    "RFCavity": {
        "ApertureP",
        "BodyShiftP",
        "MagneticMultipoleP",
        "RFP",
        "SolenoidP",
    },
    "Sextupole": {"ApertureP", "BodyShiftP", "MagneticMultipoleP"},
    "Solenoid": {"ApertureP", "BodyShiftP", "MagneticMultipoleP", "SolenoidP"},
    "Taylor": {"ApertureP", "BodyShiftP"},
    "Wiggler": {"ApertureP", "BodyShiftP", "MagneticMultipoleP"},
}

_APERTURE_SHAPES = {
    "circular": "ELLIPTICAL",
    "elliptical": "ELLIPTICAL",
    "rectangular": "RECTANGULAR",
    "scraper": "RECTANGULAR",
}

_CAVITY_TYPES = {
    "standingwave": "STANDING_WAVE",
    "travellingwave": "TRAVELING_WAVE",
    "travelingwave": "TRAVELING_WAVE",
}


class PalsBeamLine(NamedTuple):
    """One branch of the document: a ``BeamLine`` and its reference state."""

    name: str
    """Beamline name."""

    definitions: Dict[str, Dict[str, Any]]
    """Element name -> body, one entry per element the line names."""

    line: List[str]
    """Element names in traversal order."""

    periodic: bool = False
    """Flag to indicate whether the beamline is periodic."""

    particle: Optional[str] = None
    """Particle type for this beamline."""

    energy: Optional[float] = None
    """Reference total energy [eV], written onto the line's ``BeginningEle``."""

    twiss: Optional[Any] = None
    """A ``TwissMatchSimulationElement``, if the branch declares design optics."""

    begin_name: Optional[str] = None
    """What to call the ``BeginningEle``, if not ``<branch>_begin``."""

    s_position: Optional[float] = None
    """Arc length the branch starts at."""


def pals_safe_names(names: Iterable[str]) -> Dict[str, str]:
    """
    Map each name PALS would read as something other than a name to a safe one.

    Parameters
    ----------
    names: Iterable[str]
        Every name that will be written into the document.

    Returns
    -------
    dict
        Original name -> replacement, for the reserved names only.
    """
    names = list(names)
    seen = {name.lower() for name in names}
    renames: Dict[str, str] = {}
    reserved = list(
        dict.fromkeys(name for name in names if name.lower() in PALS_RESERVED_NAMES)
    )
    for name in reserved:
        candidate = name + PALS_RENAME_SUFFIX
        count = 1
        while candidate.lower() in seen or candidate.lower() in PALS_RESERVED_NAMES:
            count += 1
            candidate = f"{name}{PALS_RENAME_SUFFIX}_{count}"
        seen.add(candidate.lower())
        renames[name] = candidate
    if renames:
        listed = ", ".join(f"{old} -> {new}" for old, new in sorted(renames.items()))
        warn(
            "PALS reads these names as facility commands, so they are written "
            f"out under different ones: {listed}. Anything matching the exported "
            "lattice back to this one by name has to follow the same mapping."
        )
    return renames


def _scalar(value: Any) -> Any:
    """A number the YAML emitter will accept, or ``None`` if it is not one."""
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number:  # NaN
        return None
    return number + 0.0  # normalises -0.0


def _resolve(element: Any, value: Any) -> Any:
    """Resolve a possibly-functional parameter to a number.

    PALS has an expression language of its own, but LAURA's functional
    definitions are a lattice-level construct with no PALS counterpart to hang
    them on, so they are baked in.
    """
    resolver = getattr(element, "resolve", None)
    if resolver is not None and isinstance(value, str):
        value = resolver(value)
    return _scalar(value)


def _edge_angle(element: Any, which: str) -> Optional[float]:
    """A bend's entrance or exit edge angle, as a number.
    LAURA legacy behaviour allows `"angle"` to be defined as a parameter, so
    this is retained here.

    All other functional definitions go through ``_resolve``.
    """
    magnetic = element.magnetic
    value = getattr(magnetic, which)
    if isinstance(value, str):
        stripped = value.replace(" ", "")
        if stripped == "angle":
            return _scalar(magnetic.KnL(0))
        if stripped in ("angle/2", "angle/2.0"):
            return _scalar(magnetic.KnL(0) / 2.0)
    return _resolve(element, value)


def _multipole_group(
    element: Any, skip_orders: Sequence[int] = (), tilt: bool = True
) -> Dict[str, Any]:
    """``MagneticMultipoleP`` for an ordinary magnet."""
    magnetic = getattr(element, "magnetic", None)
    multipoles = getattr(magnetic, "multipoles", None)
    if multipoles is None:
        return {}
    group: Dict[str, Any] = {}
    for order in range(5):
        if order in skip_orders:
            continue
        for component, prefix in (("normal", "Kn"), ("skew", "Ks")):
            value = _resolve(element, getattr(multipoles, component)(order))
            if value:
                group[f"{prefix}{order}L"] = value
    angle = _resolve(element, getattr(magnetic, "tilt", None)) if tilt else None
    if angle:
        group[f"tilt{int(getattr(magnetic, 'order', 0) or 0)}"] = angle
    return group


def _corrector_group(element: Any) -> Dict[str, Any]:
    """``MagneticMultipoleP`` for a corrector, from its two kick angles.

    The sign convention is the importer's, read backwards
    """
    magnetic = element.magnetic
    group: Dict[str, Any] = {}
    horizontal = _resolve(element, getattr(magnetic, "horizontal_kick", 0.0))
    vertical = _resolve(element, getattr(magnetic, "vertical_kick", 0.0))
    if horizontal:
        group["Kn0L"] = -horizontal
    if vertical:
        group["Ks0L"] = vertical
    return group


def _bend_group(element: Any) -> Dict[str, Any]:
    """``BendP`` for a dipole."""
    magnetic = element.magnetic
    group: Dict[str, Any] = {}
    angle = _scalar(magnetic.KnL(0))
    length = _scalar(element.length)
    if angle is not None:
        if length:
            group["g_ref"] = angle / length
        else:
            group["angle_ref"] = angle
    for pals_key, laura_key in (
        ("e1", "entrance_edge_angle"),
        ("e2", "exit_edge_angle"),
    ):
        value = _edge_angle(element, laura_key)
        if value:
            group[pals_key] = value
    integrals = element._fringe_integrals()
    for pals_key, fint, half_gap in (
        ("edge1_int", integrals[0], magnetic.half_gap),
        ("edge2_int", integrals[1], magnetic.exit_half_gap),
    ):
        fint, half_gap = _resolve(element, fint), _scalar(half_gap)
        if fint and half_gap:
            group[pals_key] = fint * half_gap
    tilt = _resolve(element, getattr(magnetic, "tilt", None))
    if tilt:
        group["tilt_ref"] = tilt
    return group


def _solenoid_group(element: Any) -> Dict[str, Any]:
    """``SolenoidP`` for a solenoid."""
    fields = getattr(element.magnetic, "fields", None)
    strength = _resolve(element, getattr(fields, "S0L", None))
    length = _scalar(element.length)
    if not strength:
        return {}
    if not length:
        warn(
            f"LAURA solenoid {element.name!r} has a strength but no length; "
            "PALS states the strength per metre, so it could not be written."
        )
        return {}
    return {"Ksol": strength / length}


def _rf_group(element: Any) -> Dict[str, Any]:
    """``RFP`` for a cavity."""
    cavity = element.cavity
    group: Dict[str, Any] = {}
    frequency = _resolve(element, cavity.frequency)
    if frequency:
        group["frequency"] = frequency
    structure = str(cavity.structure_type or "").replace("_", "").lower()
    amplitude = _resolve(element, getattr(element.simulation, "field_amplitude", None))
    factor = getattr(element, "travelling_wave_voltage_factor", None)
    if amplitude and structure.startswith("travel") and factor is not None:
        group["gradient"] = amplitude
        active_length = _scalar(factor())
        if active_length:
            group["L_active"] = active_length
    elif amplitude:
        group["voltage"] = amplitude
    phase = _resolve(element, cavity.phase)
    if phase is not None:
        group["phase"] = -phase / 360.0
    cells = _scalar(cavity.n_cells)
    if cells:
        group["num_cells"] = int(cells)
    cavity_type = _CAVITY_TYPES.get(
        str(cavity.structure_type or "").replace("_", "").lower()
    )
    if cavity_type:
        group["cavity_type"] = cavity_type
    return group


def _aperture_group(element: Any) -> Dict[str, Any]:
    """``ApertureP`` from LAURA's full widths.

    LAURA has no aperture offset, so they are symmetric.
    """
    aperture = getattr(element, "aperture", None)
    horizontal = _scalar(getattr(aperture, "horizontal_size", None)) or 0.0
    vertical = _scalar(getattr(aperture, "vertical_size", None)) or 0.0
    if not horizontal and not vertical:
        return {}
    group: Dict[str, Any] = {}
    for axis, size in (("x", horizontal), ("y", vertical)):
        if size:
            group[f"{axis}_min"] = -size / 2.0
            group[f"{axis}_max"] = size / 2.0
    shape = _APERTURE_SHAPES.get(str(getattr(aperture, "shape", "") or "").lower())
    if shape:
        group["shape"] = shape
    group["location"] = "EVERYWHERE"
    return group


def _body_shift_group(element: Any) -> Dict[str, Any]:
    """``BodyShiftP`` from a LAURA position/rotation error.

    The rotations are the importer's mapping read backwards: ``x_rot = phi``,
    ``y_rot = -theta``, ``z_rot = psi``.
    """
    error = getattr(getattr(element, "physical", None), "error", None)
    if error is None:
        return {}
    group: Dict[str, Any] = {}
    position = getattr(error, "position", None)
    for axis in ("x", "y", "z"):
        offset = _scalar(getattr(position, axis, None))
        if offset:
            group[f"{axis}_offset"] = offset
    rotation = getattr(error, "rotation", None)
    for pals_key, laura_key, sign in (
        ("x_rot", "phi", 1.0),
        ("y_rot", "theta", -1.0),
        ("z_rot", "psi", 1.0),
    ):
        angle = _scalar(getattr(rotation, laura_key, None))
        if angle:
            group[pals_key] = sign * angle
    return group


def pals_element_body(element: Any) -> Dict[str, Any]:
    """
    Build the PALS facility entry for one LAURA element.

    Parameters
    ----------
    element: BaseElementTranslator
        The element to convert.

    Returns
    -------
    dict
        The body of the entry -- its ``kind``, ``length`` and parameter groups.
        The caller keys it by the element's name.
    """
    hardware_type = element.hardware_type
    kind = laura_type_to_pals_kind(hardware_type)
    length = _scalar(element.length) or 0.0
    if kind is None:
        kind = "Drift" if length else "Marker"
    body: Dict[str, Any] = {"kind": kind}
    if length:
        body["length"] = length

    groups = _KIND_GROUPS.get(kind, set())
    magnetic = getattr(element, "magnetic", None)
    if magnetic is not None and "MagneticMultipoleP" in groups:
        if hasattr(magnetic, "horizontal_kick"):
            multipoles = _corrector_group(element)
        elif kind == "Bend":
            multipoles = _multipole_group(element, skip_orders=(0,), tilt=False)
        else:
            multipoles = _multipole_group(element)
        if multipoles:
            body["MagneticMultipoleP"] = multipoles
    if magnetic is not None and "BendP" in groups:
        bend = _bend_group(element)
        if bend:
            body["BendP"] = bend
    if magnetic is not None and "SolenoidP" in groups:
        solenoid = _solenoid_group(element)
        if solenoid:
            body["SolenoidP"] = solenoid
    if getattr(element, "cavity", None) is not None and "RFP" in groups:
        rf = _rf_group(element)
        if rf:
            body["RFP"] = rf
    if "ApertureP" in groups:
        aperture = _aperture_group(element)
        if aperture:
            body["ApertureP"] = aperture
    if "BodyShiftP" in groups:
        shift = _body_shift_group(element)
        if shift:
            body["BodyShiftP"] = shift
    if not pals_kind_round_trips(hardware_type):
        body[LAURA_TYPE_EXTENSION] = {"hardware_type": hardware_type}
    return body


PALS_TWISS_COMPONENTS = {
    "beta_a": "beta_x",
    "beta_b": "beta_y",
    "alpha_a": "alpha_x",
    "alpha_b": "alpha_y",
    "eta_x": "eta_x",
    "eta_y": "eta_y",
    "etap_x": "eta_xp",
    "etap_y": "eta_yp",
}


def _twiss_group(twiss: Any) -> Dict[str, Any]:
    """``TwissP`` for a branch's design optics.

    Only meaningful on a ``BeginningEle``, where PALS reads it as an input.
    """
    group: Dict[str, Any] = {}
    for pals_key, laura_key in PALS_TWISS_COMPONENTS.items():
        value = _scalar(getattr(twiss, laura_key, None))
        if value is not None and (value or pals_key.startswith(("beta", "alpha"))):
            group[pals_key] = value
    return group


def _beginning_element(beamline: PalsBeamLine) -> Dict[str, Any]:
    """The ``BeginningEle`` that opens a branch and sets its reference state."""
    reference: Dict[str, Any] = {}
    if beamline.particle:
        reference["species_ref"] = str(beamline.particle)
    energy = _scalar(beamline.energy)
    if energy:
        reference["E_tot_ref"] = energy
    body: Dict[str, Any] = {"kind": "BeginningEle"}
    start = _scalar(beamline.s_position)
    if start:
        body["s_position"] = start
    if reference:
        body["ReferenceP"] = reference
    if beamline.twiss is not None:
        twiss = _twiss_group(beamline.twiss)
        if twiss:
            body["TwissP"] = twiss
    if not reference:
        warn(
            f"LAURA section {beamline.name!r} has no reference species or "
            "energy, so the exported branch cannot state one. A PALS parser "
            "will report that the reference parameters are not computable, and "
            "any unnormalised field in the document cannot be converted."
        )
    return body


def pals_document(
    beamlines: Sequence[PalsBeamLine],
    lattice_name: str,
    *,
    notes: Sequence[str] = (),
) -> str:
    """
    Assemble a complete PALS document from one or more beamlines.

    Parameters
    ----------
    beamlines: Sequence[PalsBeamLine]
        One per LAURA section; each becomes a ``BeamLine`` and a branch.
    lattice_name: str
        Name for the ``Lattice`` the branches belong to.
    notes: Sequence[str]
        Optional notes recorded in the document's ``notes`` list.

    Returns
    -------
    str
        The document, ready to be written to a ``*.pals.yaml`` file.
    """
    if not beamlines:
        raise ValueError("A PALS document needs at least one beamline")

    facility: List[Dict[str, Any]] = []
    defined: Dict[str, Dict[str, Any]] = {}
    uses_extension = False
    for beamline in beamlines:
        for name, body in beamline.definitions.items():
            existing = defined.get(name)
            if existing is not None and existing != body:
                raise ValueError(
                    f"Two different elements are both named {name!r}; PALS "
                    "allows a name to be reused only for the same definition."
                )
            if existing is None:
                defined[name] = body
                facility.append({name: body})
            uses_extension = uses_extension or LAURA_TYPE_EXTENSION in body

    for beamline in beamlines:
        begin = beamline.begin_name or f"{beamline.name}_begin"
        line: List[Any] = [{begin: _beginning_element(beamline)}]
        line.extend(beamline.line)
        entry: Dict[str, Any] = {"kind": "BeamLine"}
        if beamline.periodic:
            entry["periodic"] = True
        entry["line"] = line
        facility.append({beamline.name: entry})

    facility.append(
        {
            lattice_name: {
                "kind": "Lattice",
                "branches": [beamline.name for beamline in beamlines],
            }
        }
    )
    facility.append({"use": lattice_name})

    document: Dict[str, Any] = {"version": None}
    if notes:
        document["notes"] = list(notes)
    if uses_extension:
        document["extension_labels"] = {
            "names": {
                LAURA_TYPE_EXTENSION: (
                    "LAURA hardware type, where the PALS kind covers a family "
                    "of them. See the LAURA documentation."
                )
            }
        }
    document["facility"] = facility

    header = (
        "# Written by LAURA.\n"
        "#\n"
        "# Gaps between elements are explicit Drift elements: the reference\n"
        "# parser does not yet implement `placement` or `superimpose`.\n"
    )
    return header + yaml.safe_dump(
        {"PALS": _plain(document)}, sort_keys=False, default_flow_style=False, width=100
    )


def _plain(value: Any) -> Any:
    """The document with every numpy scalar reduced to a Python one."""
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value
