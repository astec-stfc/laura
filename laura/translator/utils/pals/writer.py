"""Write LAURA elements, sections and layouts as a PALS document.

This is the inverse of ``translator/converters/codes/pals.py``
Two things the standard offers are deliberately not used:

``placement`` / ``superimpose``
    A PALS line item can be positioned by an offset from another item rather
    than by the running sum of the lengths ahead of it, which would let a
    lattice be written without drifts at all. Here, gaps are written as
    explicit ``Drift`` elements, from ``SectionLattice.createDrifts()``.

The document shape is one ``BeamLine`` per LAURA section, one ``Lattice``
naming them as branches, and a ``use``. A section that repeats a cell nests a
further ``BeamLine`` inside its own; see :func:`fold_repeated_cells`.
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
    "fold_repeated_cells",
    "pals_document",
    "pals_element_body",
    "pals_keyword_map",
    "pals_safe_names",
]

PALS_RESERVED_NAMES = frozenset(
    {"expand_lattice", "include", "load", "set", "superimpose", "use"}
)
"""Facility keys a PALS parser reads as a command rather than as a name.
"""

PALS_RENAME_SUFFIX = "_element"
"""Appended to a reserved name; a further ``_2``, ``_3`` ... breaks a tie."""


class _FlowList(list):
    """A list written on one line, so a 6x6 matrix is six rows and not 36."""


yaml.SafeDumper.add_representer(
    _FlowList,
    lambda dumper, value: dumper.represent_sequence(
        "tag:yaml.org,2002:seq", value, flow_style=True
    ),
)

PALS_DEFAULT_AREA = "Lattice"

_KIND_GROUPS = {
    "ACKicker": {"ApertureP", "BodyShiftP", "MagneticMultipoleP"},
    "BeamBeam": {"ApertureP", "BeamBeamP", "BodyShiftP"},
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

#: What a kind loses on the way out, where PALS has nowhere to put it. The
#: mirror of ``_LOSSY_CONVERSIONS`` in ``converters/codes/pals.py``.
_LOSSY_KINDS = {
    "Wiggler": "its period, peak field and number of periods",
    "BeamBeam": "its offsets and width; BeamBeamP has no component for either",
}


class PalsBeamLine(NamedTuple):
    """One branch of the document: a ``BeamLine`` and its reference state."""

    name: str
    """Beamline name."""

    definitions: Dict[str, Dict[str, Any]]
    """Element name -> body, one entry per element the line names."""

    line: List[Any]
    """Traversal order: an element or sub-line name, or a single-key mapping of
    one to its line-item options (``repeat``)."""

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

    sublines: Dict[str, Dict[str, Any]] = {}
    """Nested ``BeamLine`` bodies the entries of ``line`` name, written into the
    facility ahead of it. Not branches of their own."""


def _reads_as_something_else(name: str) -> bool:
    """True for a name PALS would not read as a name."""
    return name.lower() in PALS_RESERVED_NAMES or (
        len(name) > 1
        and name.isascii()
        and name.isalpha()
        and name[0].isupper()
        and name.endswith("P")
    )


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
        Original name -> replacement, for the unusable names only.
    """
    names = list(names)
    seen = {name.lower() for name in names}
    renames: Dict[str, str] = {}
    reserved = list(
        dict.fromkeys(name for name in names if _reads_as_something_else(name))
    )
    for name in reserved:
        candidate = name + PALS_RENAME_SUFFIX
        count = 1
        while candidate.lower() in seen or _reads_as_something_else(candidate):
            count += 1
            candidate = f"{name}{PALS_RENAME_SUFFIX}_{count}"
        seen.add(candidate.lower())
        renames[name] = candidate
    if renames:
        listed = ", ".join(f"{old} -> {new}" for old, new in sorted(renames.items()))
        warn(
            "PALS reads these names as a command or a parameter group rather "
            f"than as a name, so they are written out under different ones: "
            f"{listed}. Anything matching the exported lattice back to this one "
            "by name has to follow the same mapping."
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


def pals_keyword_map(rules: Dict[str, str], group: str) -> Dict[str, str]:
    """The ``LAURA keyword -> PALS parameter`` entries of a keyword table that
    belong to one parameter group, with the group stripped off."""
    prefix = f"{group}."
    return {
        laura_key: pals_key.removeprefix(prefix)
        for laura_key, pals_key in rules.items()
        if pals_key.startswith(prefix)
    }


def _table_groups(element: Any, groups: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    """The parameters the PALS keyword table renames, split into their groups.

    Everything that is not a plain rename is left to the ``_*_group`` helpers
    below, as is any group the element's kind cannot carry.
    """
    rules = element.conversion_rules["pals"]
    parameters: Dict[str, Dict[str, Any]] = {}
    for keyword, value in element.full_dump().items():
        target = element._convert_keyword(keyword, rules)
        if "." not in target:
            continue
        group, pals_key = target.split(".")
        number = _resolve(element, value)
        if group in groups and number:
            parameters.setdefault(group, {})[pals_key] = number
    return parameters


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
    """``BendP`` for a dipole: what the keyword table cannot state as a rename."""
    magnetic = element.magnetic
    group: Dict[str, Any] = {}
    angle = _scalar(magnetic.KnL(0))
    length = _scalar(element.length)
    if angle is not None:
        if length:
            group["g_ref"] = angle / length
        else:
            group["angle_ref"] = angle
    integrals = element._fringe_integrals()
    for pals_key, fint, half_gap in (
        ("edge1_int", integrals[0], magnetic.half_gap),
        ("edge2_int", integrals[1], magnetic.exit_half_gap),
    ):
        fint, half_gap = _resolve(element, fint), _scalar(half_gap)
        if fint and half_gap:
            group[pals_key] = fint * half_gap
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
    """``RFP`` for a cavity: what the keyword table cannot state as a rename."""
    cavity = element.cavity
    group: Dict[str, Any] = {}
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
    """``ApertureP`` from LAURA's full widths about their centres.

    None of this can ride the keyword table: it renames numbers only, and
    ``location``, ``material`` and the two flags are strings and booleans.
    """
    aperture = getattr(element, "aperture", None)
    horizontal = _scalar(getattr(aperture, "horizontal_size", None)) or 0.0
    vertical = _scalar(getattr(aperture, "vertical_size", None)) or 0.0
    if not horizontal and not vertical:
        return {}
    group: Dict[str, Any] = {}
    for axis, size, centre in (
        ("x", horizontal, _scalar(getattr(aperture, "horizontal_center", None)) or 0.0),
        ("y", vertical, _scalar(getattr(aperture, "vertical_center", None)) or 0.0),
    ):
        if not size:
            continue
        group[f"{axis}_min"] = centre - size / 2.0
        group[f"{axis}_max"] = centre + size / 2.0
        if centre:
            group[f"{axis}_center"] = centre
    shape = _APERTURE_SHAPES.get(str(getattr(aperture, "shape", "") or "").lower())
    if shape:
        group["shape"] = shape
    location = getattr(aperture, "location", None)
    location = getattr(location, "value", location) or "everywhere"
    group["location"] = str(location).upper()
    material = getattr(aperture, "material", None)
    if material:
        group["material"] = str(material)
    thickness = _scalar(getattr(aperture, "thickness", None))
    if thickness:
        group["thickness"] = thickness
    for laura_key, pals_key in (
        ("active", "aperture_active"),
        ("shifts_with_body", "aperture_shifts_with_body"),
    ):
        flag = getattr(aperture, laura_key, None)
        if flag is False:  # the PALS default is true; only state a departure
            group[pals_key] = False
    return group


def _meta_group(element: Any) -> Dict[str, Any]:
    """``MetaP``: the identity LAURA carries and no other group has room for.
    Only what somebody actually set goes in.
    """
    group: Dict[str, Any] = {}
    aliases = [str(alias) for alias in getattr(element, "alias", None) or []]
    if aliases:
        group["alias"] = aliases[0] if len(aliases) == 1 else aliases
    serial = getattr(getattr(element, "manufacturer", None), "serial_number", None)
    if serial:
        group["ID"] = str(serial)
    area = getattr(element, "machine_area", None)
    if area and area != PALS_DEFAULT_AREA:
        group["location"] = str(area)
    return group


def _sparse_matrix(array: Any, order: int) -> Dict[str, float]:
    """A Taylor coefficient array as ``"1,2,2" -> coefficient``, 1-based."""
    if array is None:
        return {}
    array = np.asarray(array, dtype=float)
    if array.ndim != order:
        return {}
    return {
        ",".join(str(index + 1) for index in position): float(array[position])
        for position in zip(*np.nonzero(array))
    }


def _matrix_extension(element: Any) -> Dict[str, Any]:
    """The transfer map, for the ``LauraP`` extension group.

    PALS has a ``TaylorP``, but neither the standard nor the reference parser
    states the format of a term. So the map goes in LAURA's own extension group,
    which round-trips exactly and invents no wire format.
    """
    simulation = getattr(element, "simulation", None)
    r_matrix = getattr(simulation, "r_matrix", None)
    if r_matrix is None:
        return {}
    matrix: Dict[str, Any] = {}
    if not np.allclose(r_matrix, np.eye(6)):
        matrix["r"] = [_FlowList(float(value) for value in row) for row in r_matrix]
    for key, order in (("c", 1), ("t", 3), ("u", 4)):
        terms = _sparse_matrix(getattr(simulation, f"{key}_matrix", None), order)
        if terms:
            matrix[key] = terms
    spin = getattr(simulation, "spin_taylor", None)
    if spin:
        matrix["spin_taylor"] = list(spin)
    return {"matrix": matrix} if matrix else {}


def _body_shift_group(element: Any) -> Dict[str, Any]:
    """The one ``BodyShiftP`` rotation LAURA states with the opposite sign; the
    offsets and the other two are renames, in the keyword table."""
    error = getattr(getattr(element, "physical", None), "error", None)
    theta = _scalar(getattr(getattr(error, "rotation", None), "theta", None))
    return {"y_rot": -theta} if theta else {}


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
    derived: Dict[str, Dict[str, Any]] = {}
    if magnetic is not None and "MagneticMultipoleP" in groups:
        if hasattr(magnetic, "horizontal_kick"):
            derived["MagneticMultipoleP"] = _corrector_group(element)
        elif kind == "Bend":
            derived["MagneticMultipoleP"] = _multipole_group(
                element, skip_orders=(0,), tilt=False
            )
        else:
            derived["MagneticMultipoleP"] = _multipole_group(element)
    if magnetic is not None and "BendP" in groups:
        derived["BendP"] = _bend_group(element)
    if magnetic is not None and "SolenoidP" in groups:
        derived["SolenoidP"] = _solenoid_group(element)
    if getattr(element, "cavity", None) is not None and "RFP" in groups:
        derived["RFP"] = _rf_group(element)
    if "ApertureP" in groups:
        derived["ApertureP"] = _aperture_group(element)
    if "BodyShiftP" in groups:
        derived["BodyShiftP"] = _body_shift_group(element)
    derived["MetaP"] = _meta_group(element)

    parameters = _table_groups(element, groups)
    for group, values in derived.items():
        if values:
            parameters.setdefault(group, {}).update(values)
    body.update(parameters)

    extension: Dict[str, Any] = {}
    if not pals_kind_round_trips(hardware_type):
        extension["hardware_type"] = hardware_type
    if kind == "Taylor":
        extension.update(_matrix_extension(element))
        warn(
            "Neither the PALS standard nor its parser states how a TaylorP "
            "term is written, so the transfer map of a LAURA "
            f"{hardware_type} is in the {LAURA_TYPE_EXTENSION} extension "
            "instead. Only LAURA reads it back."
        )
    if extension:
        body[LAURA_TYPE_EXTENSION] = extension
    if kind in _LOSSY_KINDS:
        # No element name, so the warning registry collapses a line of them.
        warn(
            f"A LAURA {hardware_type} is written as a PALS {kind}, which drops "
            f"{_LOSSY_KINDS[kind]}."
        )
    return body


def fold_repeated_cells(
    name: str, definitions: Dict[str, Any], line: List[Any]
) -> tuple:
    """Rewrite a repeated run of a line as a nested ``BeamLine`` and a ``repeat``.

    A LAURA section that repeats a cell arrives here already flattened, with
    every copy under its own numbered name.

    The shortest repeating period wins, and a period of one is left alone --
    ``repeat`` would work on it, but a run of same-kind singles (four markers,
    say) is not a cell and folding it only loses their names.

    Returns
    -------
    tuple
        ``(sublines, line)`` -- the nested ``BeamLine`` bodies to define, and
        the line rewritten to name them.
    """
    bodies = [definitions.get(entry) for entry in line]
    sublines: Dict[str, Dict[str, Any]] = {}
    folded: List[Any] = []
    index = 0
    while index < len(line):
        for period in range(2, (len(line) - index) // 2 + 1):
            block = bodies[index : index + period]
            count = 1
            while bodies[index + count * period : index + (count + 1) * period] == block:
                count += 1
            if count > 1:
                break
        else:
            folded.append(line[index])
            index += 1
            continue
        cell = f"{name}_cell{'' if not sublines else f'_{len(sublines) + 1}'}"
        sublines[cell] = {
            "kind": "BeamLine",
            "line": line[index : index + period],
        }
        folded.append({cell: {"repeat": count}})
        index += count * period

    if sublines:
        kept = {
            entry for body in sublines.values() for entry in body["line"]
        } | {entry for entry in folded if isinstance(entry, str)}
        dropped = sorted(set(line) - kept)
        for entry in dropped:
            definitions.pop(entry, None)
        warn(
            f"LAURA section {name!r} repeats a cell, written out as the nested "
            f"BeamLine {', '.join(sublines)}. Every copy of the cell collapses "
            f"onto the first, so {', '.join(dropped)} are no longer names in the "
            "document."
        )
    return sublines, folded


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
        for name, body in beamline.sublines.items():
            if name not in defined:
                defined[name] = body
                facility.append({name: body})

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
                    "What LAURA holds and PALS has no component for: the "
                    "hardware type where the kind covers a family of them, "
                    "and the transfer map of a Taylor. See the LAURA "
                    "documentation."
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
        return type(value)(_plain(item) for item in value)
    if isinstance(value, np.generic):
        return value.item()
    return value
