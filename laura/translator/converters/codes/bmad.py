import math
import re
import tempfile
from itertools import permutations
from pathlib import Path
from typing import Any, Dict, List, Literal, NamedTuple, Optional, Union, get_args
from warnings import warn

import numpy as np
from pydantic import BaseModel, Field, PrivateAttr, model_validator
from scipy.constants import speed_of_light

import laura.models.element as laura_elements
from laura.models.element import (
    CombinedCorrector,
    Element,
    HorizontalCorrector,
    VerticalCorrector,
)
from laura.models.element_list import (
    ElementList,
    MachineLayout,
    MachineModel,
    SectionLattice,
)

from ....exporters.yaml_exporter import PositionMode, export_machine_combined_file
from ...utils.bmad import (
    BMAD_SR_WAKE_SAMPLES,
    bmad_floor_angles_to_laura,
    is_flat_roll,
    sample_bmad_sr_wake,
)
from ...utils.fields import FieldMap
from ...utils.fields.field_parameter import FieldParameter
from ...utils.functions import merge_layout_elements, number_repeated_names
from ...utils.units import UnitValue
from .. import keyword_conversion_rules_bmad, type_conversion_rules_bmad
from . import magnetic_orders
from .importer import read_with_calls

_DRIFT_TYPES = ("Drift", "Pipe")
"""Bmad types with no physics of their own."""

_CANCELS_TOL = 1e-9
"""How exactly a pair of drifts has to cancel, in metres, to be merged."""


def _absorb_negative_drifts(names, types, lengths, spos, params, children):
    """Fold each backwards drift into the neighbour that undoes it.

    A drift of negative length is how a Bmad lattice moves its own s-origin,
    but LAURA does not (currently) support negative drifts.

    Only an exact cancellation is folded; anything else is left for the element
    loop to drop with a warning. Returns children reindexed onto the
    shortened lists; the other five are modified in place.
    """
    drop = set()
    for index, length in enumerate(lengths):
        if length >= 0.0 or types[index] not in _DRIFT_TYPES:
            continue
        for other in (index + 1, index - 1):
            if not 0 <= other < len(lengths) or other in drop:
                continue
            if types[other] not in _DRIFT_TYPES:
                continue
            if abs(lengths[other] + length) > _CANCELS_TOL:
                continue
            first, last = min(index, other), max(index, other)
            lengths[other] = 0.0
            if "L" in params[other]:
                params[other]["L"] = 0.0
            spos[other] = spos[last]
            entrance = params[first].get("_FLOOR_ENTRANCE")
            if entrance is not None:
                params[other]["_FLOOR"] = entrance
                params[other]["_FLOOR_ENTRANCE"] = entrance
            drop.add(index)
            break
    if not drop:
        return children
    kept = [index for index in range(len(names)) if index not in drop]
    moved = {old: new for new, old in enumerate(kept)}
    for column in (names, types, lengths, spos, params):
        column[:] = [column[index] for index in kept]
    return {
        moved[child]: moved[lord]
        for child, lord in children.items()
        if child in moved and lord in moved
    }


_CAVITY_TYPES = ("Lcavity", "RFCavity", "Crab_Cavity", "E_Gun")

_COLLIMATOR_TYPES = ("ECollimator", "RCollimator")

_COLLIMATOR_SHAPES = {"ECollimator": "elliptical", "RCollimator": "rectangular"}
"""The aperture shape each Bmad collimator class stands for."""

_SPACE_CHARGE_COM = {
    "n_bin": "number_of_bins",
    "ds_track_step": "step_size",
    "beam_chamber_height": "chamber_height",
    "n_shield_images": "shield_images",
    "particle_bin_span": "bin_span",
    "lsc_sigma_cutoff": "sigma_cutoff",
}
"""Bmad's ``space_charge_com`` namelist under LAURA's section-level names."""

_MULTIPOLE_TYPES = ("Multipole", "AB_multipole", "Thick_Multipole", "Sad_Mult")

_MARKER_TYPES = ("Marker", "Monitor", "Instrument", "Fixer")

_PATCH_GEOMETRIC_ATTRIBUTES = (
    "X_OFFSET",
    "Y_OFFSET",
    "X_PITCH",
    "Y_PITCH",
    "TILT",
)

_PATCH_ENERGY_ATTRIBUTES = ("DELTA_E_REF",)

_PATCH_TRANSFORM_ATTRIBUTES = _PATCH_GEOMETRIC_ATTRIBUTES + _PATCH_ENERGY_ATTRIBUTES

_PATCH_TRANSFORM_TOLERANCE = 1e-12

_ORDER_TYPES = {0: "Dipole", 1: "Quadrupole", 2: "Sextupole", 3: "Octupole"}

_CALL_RE = re.compile(r"(?im)^\s*call\s*,\s*file\s*=\s*([^\s;]+)\s*;?\s*$")

_MULTIPASS_SLAVE_NAME = re.compile(r"^(?P<base>.+)\\(?P<number>\d+)$")

_MULTIPASS_OVERRIDES = {
    "PHI0_MULTIPASS": ("cavity.phase", lambda value: -360.0 * value)
}
"""Bmad attributes a multipass slave holds on its own, and the LAURA override
they come back as. The inverse of
:data:`~laura.translator.converters.layout.bmad_per_pass_attributes`."""

bmad_unsupported = [
    "Horizontal_AC_Dipole",
    "Vertical_AC_Dipole",
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
    "Wire",
]


def _layout_entries(
    layout: MachineLayout, sections: List[str], renamed: Dict[str, str]
) -> List[Any]:
    """The layout's beam order as :class:`MachineModel` wants it written.

    A section entered once is its bare name; a multipass section carries
    ``multipass`` and whatever that pass overrides, which is the only form
    :class:`~laura.models.elementList.LayoutPass` can be rebuilt from.
    """
    if not any(entry.number for entry in layout.passes):
        return sections
    entries: List[Any] = []
    for entry in layout.passes:
        name = renamed.get(entry.section)
        if name is None:
            continue
        if entry.number is None:
            entries.append(name)
            continue
        settings: Dict[str, Any] = {"multipass": entry.number}
        if entry.overrides:
            settings["overrides"] = entry.overrides
        entries.append({name: settings})
    return entries


def _multipass_slave(name: str, parameters: Dict[str, Any]) -> Optional[tuple]:
    """``(hardware name, pass number)`` if this is a Bmad multipass slave.

    Bmad calls the Nth visit to a multipass element ``NAME\\N``. The name on its
    own is not proof, so the status Tao reports has to agree.
    """
    if parameters.get("slave_status") != "Multipass_Slave":
        return None
    match = _MULTIPASS_SLAVE_NAME.match(name)
    return (match["base"], int(match["number"])) if match else None


def _switch_dict() -> Dict[str, str]:
    """Bmad element key -> LAURA hardware type."""
    switch = {
        native_type.lower(): laura_type
        for laura_type, native_type in type_conversion_rules_bmad.items()
    }
    switch.update(
        {
            "drift": "Drift",
            "pipe": "Drift",
            "lcavity": "RFCavity",
            "rfcavity": "RFCavity",
            "match": "MatrixTransform",
            "rbend": "Dipole",
            "rcollimator": "Collimator",
            "undulator": "Wiggler",
            "e_gun": "RFCavity",
            "beambeam": "BeamBeam",
            "instrument": "Diagnostic",
            "fixer": "Marker",
        }
    )
    return switch


def _floor_to_physical(
    floor: Dict[str, Any],
    position_key: str = "datum",
    orientation: Optional[Dict[str, Any]] = None,
    roll: float = 0.0,
) -> Dict[str, Dict[str, float]]:
    """
    Convert a Tao ``ele_floor`` record to LAURA ``datum``/``global_rotation``.
    The three floor angles are re-expressed by
    :func:`bmad_floor_angles_to_laura`, which goes through the rotation matrix
    rather than renaming axes -- see there for why a rename cannot work.

    ``position_key`` selects where the position lands. ``"datum"`` is the
    section's reference point, used for the ``Beginning_Ele``. ``"middle"`` is
    the element centre and is what actually *places* an element.

    ``orientation`` supplies the angles from a *different* record than the
    position, and floor mode passes the ``where="beginning"`` one.

    ``roll`` is a bend's ``REF_TILT``, which has to be added here rather than
    read off the floor record.
    """
    reference = floor.get("Reference")
    if reference is None or len(reference) < 6:
        return {}
    angles = (orientation or floor).get("Reference")
    if angles is None or len(angles) < 6:
        angles = reference
    x, y, z = (float(v) for v in reference[:3])
    theta, phi, psi = (float(v) for v in angles[3:6])
    return {
        position_key: {"x": x, "y": y, "z": z},
        "global_rotation": bmad_floor_angles_to_laura(theta, phi, psi + roll),
    }


def _misalignment(parameters: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Convert an element's Bmad misalignment attributes to LAURA's
    ``physical.error``.

    Neither code names these for the axis the rotation turns about. Bmad's
    ``x_pitch`` is a rotation about **y** and ``y_pitch`` is about x; LAURA's
    ``Rotation`` is read through
    :func:`~laura.utils.rotation_matrix.euler_angles_to_rotation_matrix`, where
    ``theta`` is the ``Ry`` factor, ``phi`` the ``Rx`` and ``psi`` the ``Rz``.
    So ``x_pitch`` pairs with ``theta`` and ``y_pitch`` with ``phi``.

    Both cross over in sign, and that is not a guess: a ``patch, x_pitch = 0.05``
    surveys to a Bmad floor ``theta`` of ``+0.05``, which
    :func:`bmad_floor_angles_to_laura` -- the matrix conversion, which is the
    definition of what these angles mean in LAURA -- turns into a LAURA ``theta``
    of ``-0.05``; the same holds for ``y_pitch`` and ``phi``. LAURA's ``Ry``
    factor carries the opposite sign to an ordinary right-handed ``Ry``, so a
    Bmad pitch and a LAURA angle of the same number are opposite rotations. The
    two were copied straight across until 2026-09-01, which left an imported
    misalignment disagreeing in sign with the ``global_rotation`` of the very
    same element, since that comes through the matrix conversion. A round trip
    could not see it: the export made the same mistake and cancelled it.

    ``psi`` does not cross over -- the roll is the one angle LAURA and Bmad
    already agree on.

    The roll, ``psi``, comes from ``ROLL``, which only a bend has: a bend keeps
    its design plane in ``REF_TILT`` and its roll error in ``ROLL``, so the two
    are separable. Every other type has just ``TILT``, which Bmad defines as the
    design tilt and the roll error added together and offers no way to take
    apart; it is read as ``magnetic.tilt`` in full, and ``psi`` stays zero
    rather than counting the same angle twice.
    """
    position = {
        axis: float(parameters.get(f"{axis.upper()}_OFFSET", 0.0) or 0.0)
        for axis in ("x", "y", "z")
    }
    rotation = {
        "phi": -float(parameters.get("Y_PITCH", 0.0) or 0.0),
        "psi": float(parameters.get("ROLL", 0.0) or 0.0),
        "theta": -float(parameters.get("X_PITCH", 0.0) or 0.0),
    }
    if not any(position.values()) and not any(rotation.values()):
        return {}
    return {"error": {"position": position, "rotation": rotation}}


def _aperture(parameters: Dict[str, Any], etype: str = "") -> Dict[str, Dict[str, Any]]:
    """Convert an element's Bmad aperture limits to a LAURA ``aperture`` dict.

    The shape comes from the element class.
    A collimator keeps its shape even with every limit at zero.
    """
    limits = {
        key: float(parameters.get(key, 0.0) or 0.0)
        for key in ("X1_LIMIT", "X2_LIMIT", "Y1_LIMIT", "Y2_LIMIT")
    }
    shape = _COLLIMATOR_SHAPES.get(etype)
    if not any(limits.values()) and shape is None:
        return {}
    return {
        "aperture": {
            "horizontal_size": limits["X1_LIMIT"] + limits["X2_LIMIT"],
            "vertical_size": limits["Y1_LIMIT"] + limits["Y2_LIMIT"],
            "shape": shape or "rectangular",
        }
    }


def _an_bn_multipoles(parameters: Dict[str, Any]) -> Dict[int, Dict[str, float]]:
    """The ``an``/``bn`` content of an ordinary magnet, as integrated strengths.

    Bmad's ``an``/``bn`` are defined with a ``1/n!``, so the factorial goes back
    in here -- the same scaling the multipole-element branch applies, and the
    inverse of what :meth:`BaseElementTranslator._add_bmad_multipoles` writes.

    The ``An``/``Bn`` columns are the right ones to read. Tao has already folded
    ``scale_multipoles`` into them, so a lattice that leaves it at Bmad's default
    ``T`` reports the effective strength rather than the written coefficient. The
    ``(w/Tilt)`` columns are deliberately *not* used: they rotate the components
    by the element's ``tilt``, which LAURA stores separately and re-applies on
    export, so reading those would apply the roll twice.
    """
    components: Dict[int, Dict[str, float]] = {}
    for row in (parameters.get("_MULTIPOLES") or {}).get("data", []):
        order = int(row["index"])
        scale = math.factorial(order)
        normal = (row.get("Bn") or 0.0) * scale
        skew = (row.get("An") or 0.0) * scale
        if normal or skew:
            components[order] = {"normal": normal, "skew": skew}
    return components


def _native_keyword(hardware_type: str, laura_field: str) -> str:
    """Return the Tao/Bmad spelling for a LAURA field."""
    rules = keyword_conversion_rules_bmad["general"]
    key = hardware_type.lower()
    if key in keyword_conversion_rules_bmad:
        rules = keyword_conversion_rules_bmad[key] | rules
    return rules.get(laura_field, laura_field).upper()


def _bmad_cavity_cells(
    n_cell: Any, l_active: Any, length: float, cell_length: float
) -> int:
    """How many cells Bmad actually gave a cavity, not how many were asked for.

    ``n_cell`` is a request. A non-positive value -- ``-1``
    means "fill the element with as many half-wavelength cells as
    will fit". A positive value is still capped: a nine-cell request in a
    one-cell-long element gets one cell.

    An ``l_active`` longer than the element is not this element's: a super-slave
    reports the whole lord's active length.
    :meth:`BmadLatticeImporter._collapse_super_lords` normally means no
    slice gets this far, so fall back to the length that does fit.
    """
    if cell_length <= 0.0:
        return int(n_cell) if n_cell and n_cell >= 1 else 1
    fits = int(length // cell_length)
    if n_cell and n_cell >= 1:
        wanted = int(n_cell)
    elif l_active and float(l_active) <= length + cell_length:
        wanted = round(l_active / cell_length)
    else:
        wanted = fits
    return max(min(wanted, fits), 1)


def _wake_tables(tao, element_id: str) -> Dict[str, Any] | None:
    """Read one element's short-range wake, or ``None`` if it has none.

    ``ele_wake`` is the only wake accessor pytao offers, and it *errors* rather
    than returning empty for an element without a wake, so the exception is the
    test. Read the scalars from here rather than from the ``call::`` file the
    lattice names: the file's values may be expressions the lattice evaluates
    (``z_scale = 1/0.0017``) and the lattice may override them per element
    (``RWWAKE3H[sr_wake%amp_scale] = 182``).
    """
    try:
        base = tao.ele_wake(element_id, who="base")
    except Exception:
        return None
    if not base:
        return None

    def table(who: str) -> List[Any]:
        try:
            return list(tao.ele_wake(element_id, who=who) or [])
        except Exception:
            return []

    tables = {
        "base": base,
        "sr_long": table("sr_long_table"),
        "sr_trans": table("sr_trans_table"),
    }
    if not tables["sr_long"] and not tables["sr_trans"]:
        if base.get("has#lr_mode") or base.get("has#sr_z_long"):
            warn(
                f"Bmad element {element_id!r} carries a long-range or "
                "tabulated short-range wake. Only short-range pseudo-mode "
                "wakes are imported, so this one is dropped."
            )
        return None
    return tables


def _lord_wakes(tao, universe: int, branch_index: int) -> Dict[int, Dict[str, Any]]:
    """Wakes that live on a super-lord, keyed by the tracking index they act on.

    ``lat_list`` returns the tracking elements only. A structure Bmad has split
    -- ``K30_6A`` into ``K30_6A#1`` .. ``#6`` -- keeps its wake on the lord, and
    ``ele_wake`` on a slave errors. In LCLS ``cu_hxr`` that is 84 of the 300
    elements carrying a wake, all of them accelerating structures, so skipping
    the lord region loses most of the linac's longitudinal wake.
    """
    found: Dict[int, Dict[str, Any]] = {}
    try:
        info = tao.lat_branch_list(ix_uni=universe)[branch_index]
        first, last = int(info["n_ele_track"]) + 1, int(info["n_ele_max"])
    except Exception:
        return found
    for index in range(first, last + 1):
        element_id = f"{universe}@{branch_index}>>{index}"
        tables = _wake_tables(tao, element_id)
        if not tables:
            continue
        try:
            rows = tao.ele_lord_slave(element_id)
        except Exception:
            continue
        location = f"{branch_index}>>{index}"
        # The response walks the whole hierarchy; the section that opens on
        # this element is the only one whose slaves are its own.
        mine = False
        for row in rows:
            if row.get("type") == "Element":
                mine = row.get("location_name") == location
            elif mine and row.get("type") == "Slave":
                slave = str(row.get("location_name") or "")
                if slave.startswith(f"{branch_index}>>"):
                    found.setdefault(int(slave.split(">>")[1]), tables)
    return found


def _holds_a_wake_field(hardware_type: str) -> bool:
    """Can this LAURA element hold a sampled wake, rather than just a file name?

    ``wakefield_definition`` is generated as a ``str``; only the classes that
    widen it to ``str | field`` can take the arrays a Bmad pseudo-mode wake
    samples down to. Asked here so an unexpected element type warns instead of
    raising a validation error part-way through an import.
    """
    element = getattr(laura_elements, hardware_type, None)
    simulation = getattr(element, "model_fields", {}).get("simulation")
    if simulation is None:
        return False
    for candidate in get_args(simulation.annotation) or (simulation.annotation,):
        definition = getattr(candidate, "model_fields", {}).get("wakefield_definition")
        if definition is not None and FieldMap in get_args(definition.annotation):
            return True
    return False


def _simulation_fields(hardware_type: str) -> frozenset:
    """The simulation attributes a LAURA element of this type can hold.

    LAURA spreads these over a class per element family, so the settings Bmad
    reports for every element alike have to be filtered before they are handed
    to a constructor that would reject them.
    """
    element = getattr(laura_elements, hardware_type, None)
    simulation = getattr(element, "model_fields", {}).get("simulation")
    if simulation is None:
        return frozenset()
    fields: set = set()
    for candidate in get_args(simulation.annotation) or (simulation.annotation,):
        fields.update(getattr(candidate, "model_fields", {}))
    return frozenset(fields)


def _collective_settings(
    parameters: Dict[str, Any], bmad_com: Dict[str, Any], hardware_type: str
) -> Dict[str, Any]:
    """The collective-effect and radiation settings an element carries.

    LAURA has no global container for collective effects, so the globals ride on every
    element that can hold them and
    :meth:`~laura.models.element_list.SectionLattice._collective_default`
    gathers them back into one ``bmad_com[...]`` statement on export.
    A method is only recorded when it is not ``Off``.
    """
    holds = _simulation_fields(hardware_type)
    settings: Dict[str, Any] = {}
    methods = parameters.get("_METHODS") or {}
    for method in ("csr_method", "space_charge_method"):
        value = str(methods.get(method, "Off"))
        if method in holds and value.lower() != "off":
            settings[method] = value
    csr_ds_step = parameters.get("CSR_DS_STEP")
    if "csrdz" in holds and csr_ds_step:
        settings["csrdz"] = csr_ds_step
    if bmad_com:
        collective = bool(bmad_com.get("csr_and_space_charge_on"))
        for switch, flag in (
            (collective, "csr_enable"),
            (collective, "lsc_enable"),
            (bool(bmad_com.get("radiation_damping_on")), "sr_enable"),
            (bool(bmad_com.get("radiation_fluctuations_on")), "isr_enable"),
        ):
            if flag in holds:
                settings[flag] = switch
    return settings


_BMAD_FRINGE_DEFAULTS: Dict[str, str] = {
    "sbend": "basic_bend",
    "rbend": "basic_bend",
    "e_gun": "full",
    "em_field": "full",
    "lcavity": "full",
    "rfcavity": "full",
}


def _fringe_model(
    parameters: Dict[str, Any], etype: str, hardware_type: str
) -> Dict[str, Any]:
    """The fringe model an element asks for, when it differs from the default.

    Recorded under LAURA's ``fringe_model``.
    Only magnets hold the field, so a cavity's ``Full`` is dropped here --
    it is Bmad's own default for cavities in any case.
    """
    value = parameters.get("FRINGE_TYPE")
    if not value or "fringe_model" not in _simulation_fields(hardware_type):
        return {}
    default = _BMAD_FRINGE_DEFAULTS.get(etype.lower(), "none")
    if str(value).lower() == default:
        return {}
    return {"fringe_model": str(value).lower()}


def _ac_kicker_data(tao, element_id: str) -> Dict[str, list]:
    # pytao cannot parse the nested ele:ac_kicker response in current releases.
    result = {"frequencies": [], "amp_vs_time": []}
    section = None
    for line in tao.cmd(f"pipe ele:ac_kicker {element_id}|model"):
        if line.startswith("has#"):
            section = line.partition("#")[2].lower()
        elif section in result:
            result[section].append(tuple(float(value) for value in line.split(";")[1:]))
    return result


def _taylor_matrices(taylor: Dict[str, Any]):
    """Convert a Bmad orbital Taylor map of order <= 3 to C/R/T/U arrays."""
    c_matrix = np.zeros(6)
    r_matrix = np.zeros((6, 6))
    t_matrix = np.zeros((6, 6, 6))
    u_matrix = np.zeros((6, 6, 6, 6))
    ref = np.zeros(6)
    for section in taylor["data"]:
        ref[section["index"] - 1] = section["ref"]

    for section in taylor["data"]:
        output = section["index"] - 1
        for term in section["data"]:
            powers = [int(term[f"exp{i}"]) for i in range(1, 7)]
            degree = sum(powers)
            coefficient = term["coef"]
            if degree > 3:
                raise ValueError(f"contains an orbital term of order {degree}")
            indices = [
                index for index, power in enumerate(powers) for _ in range(power)
            ]
            if degree == 0:
                c_matrix[output] += coefficient
            elif degree == 1:
                r_matrix[output, indices[0]] += coefficient
            else:
                unique_indices = set(permutations(indices))
                tensor = t_matrix if degree == 2 else u_matrix
                for tensor_indices in unique_indices:
                    tensor[(output, *tensor_indices)] += coefficient / len(
                        unique_indices
                    )

    t_feeddown = np.einsum("ijk,k->ij", t_matrix, ref)
    u_feeddown = np.einsum("ijkl,l->ijk", u_matrix, ref)
    c_matrix = (
        c_matrix
        - r_matrix @ ref
        + t_feeddown @ ref
        - np.einsum("ijkl,j,k,l->i", u_matrix, ref, ref, ref)
    )
    r_matrix = (
        r_matrix - 2 * t_feeddown + 3 * np.einsum("ijkl,k,l->ij", u_matrix, ref, ref)
    )
    t_matrix = t_matrix - 3 * u_feeddown
    return c_matrix, r_matrix, t_matrix, u_matrix


class _NativeElement(NamedTuple):
    """One Bmad element as read from Tao, handed to a ``_build_*`` method."""

    universe: int
    branch: str
    name: str
    etype: str
    hardware_type: Optional[str]
    length: float
    parameters: Dict[str, Any]
    physical: dict

    @property
    def base_name(self) -> str:
        """``name`` as :meth:`BmadLatticeImporter._symbol` looks it up."""
        return self.name.split(".", 1)[0]

    def keyword(self, laura_field: str) -> str:
        return _native_keyword(self.hardware_type, laura_field)


# Bmad element key -> the BmadLatticeImporter method that builds it.
_BUILDERS = {
    **dict.fromkeys(("Kicker", "HKicker", "VKicker"), "_build_kicker"),
    **dict.fromkeys(magnetic_orders, "_build_magnet"),
    **dict.fromkeys(_CAVITY_TYPES, "_build_cavity"),
    **dict.fromkeys(("Wiggler", "Undulator"), "_build_wiggler"),
    "Solenoid": "_build_solenoid",
    "Sol_Quad": "_build_sol_quad",
    "ELSeparator": "_build_separator",
    "Match": "_build_match",
    "Taylor": "_build_taylor",
    **dict.fromkeys(_COLLIMATOR_TYPES, "_build_collimator"),
    **dict.fromkeys(_MULTIPOLE_TYPES, "_build_multipole"),
    "AC_Kicker": "_build_ac_kicker",
    "BeamBeam": "_build_beam_beam",
    **dict.fromkeys(_MARKER_TYPES, "_build_marker"),
    "Beginning_Ele": "_build_beginning",
    "Patch": "_build_patch",
    **dict.fromkeys(_DRIFT_TYPES, "_build_drift"),
}


class BmadTaoInit(BaseModel):
    """Minimal Tao init file for one Bmad lattice and optional line selections."""

    lattice_file: str
    lines: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_lines(self):  # noqa: N804
        if any(not line.strip() for line in self.lines):
            raise ValueError("Bmad line names cannot be empty.")
        return self

    def render(self) -> str:
        targets = [f"{self.lattice_file}@{line}" for line in self.lines] or [
            self.lattice_file
        ]
        entries = "\n".join(
            "  design_lattice({})%file = '{}'".format(index, target.replace("'", "''"))
            for index, target in enumerate(targets, 1)
        )
        return f"&tao_design_lattice\n  n_universes = {len(targets)}\n{entries}\n/\n"

    def write(self, path: str | Path) -> Path:
        path = Path(path)
        path.write_text(self.render())
        return path


class BmadLatticeImporter(BaseModel):
    machine_area: str = "Lattice"

    tao_init: Optional[str] = None
    """Name of Tao init file which produces."""

    lattice_file: Optional[str] = None
    """Original BMAD lattice file, used instead of ``tao_init``."""

    lines: List[str] = Field(default_factory=list)
    """Bmad lines to load as separate Tao universes from ``lattice_file``."""

    libtao: Optional[str] = None
    """libtao.so file"""

    wake_samples: int = BMAD_SR_WAKE_SAMPLES
    """Points used when a Bmad pseudo-mode wake is sampled onto a grid.

    See :data:`~laura.translator.utils.bmad.BMAD_SR_WAKE_SAMPLES`. Raising it
    tightens the agreement with Bmad's own mode tracking at the cost of a
    proportionally larger wake sidecar per element on export.
    """

    position_mode: Literal["floor", "s"] = "floor"
    """How element placement is taken from Tao.

    ``"floor"`` (default) reads Tao's surveyed floor coordinates for every
    element and places it in absolute world coordinates, so LAURA inherits the
    machine geometry rather than re-deriving it.

    ``"s"`` instead hands Bmad's cumulative arc-length to LAURA as
    ``physical.s``. The resulting ``s`` is exact, but the *world*
    coordinates are not; use with caution.
    """

    elements: Dict = {}
    """Dictionary containing converted LAURA element objects"""

    functional_definitions: Dict[str, Union[int, float]] = {}

    n_universes: int = 1

    names: Dict[int, Dict[str, List[str]]] = {}

    names_numbered: Dict[int, Dict[str, List[str]]] = {}

    types: Dict[int, Dict[str, List[str]]] = {}

    lengths: Dict[int, Dict[str, List[float]]] = {}

    spos: Dict[int, Dict[str, List[float]]] = {}
    """Cumulative arc-length at the *exit* of each element (Bmad's ``ele.s``)."""

    params: Dict[int, Dict[str, List[Dict[str, Any]]]] = {}

    branch_params: Dict[int, Dict[str, Dict[str, Any]]] = {}
    """Tao ``branch1`` records, holding ``param_geometry`` and ``param_particle``."""

    bmad_com: Dict[str, Any] = {}
    """Bmad's global switches, as Tao resolved them."""

    space_charge_com: Dict[str, Any] = {}
    """Bmad's collective-field resolution, as Tao resolved it."""

    super_lord_children: Dict[int, Dict[str, Dict[str, str]]] = {}
    """``{child name: lord name}`` per branch, for elements Bmad superimposed
    inside another one. Set by :meth:`_collapse_super_lords`; read back when
    the element dictionary is built to give the child a ``subelement``."""

    laura_elems: Dict[int, Dict[str, Dict[str, Element]]] = {}

    branches: Dict[int, List[str]] = {}

    deferred_parameters: Dict[str, Dict[str, str]] = {}

    multipass_passes: Dict[int, Dict[str, List[Dict[str, Any]]]] = {}
    """Beam order for a branch :meth:`_split_multipass` had to break up, as
    :class:`~laura.models.elementList.LayoutPass` keyword arguments. Empty for
    a branch with no Bmad multipass in it, which is one section and one pass."""

    _generated_tao_init: Any = PrivateAttr(default=None)

    @model_validator(mode="after")
    def _check_input(self):  # noqa: N804
        if (self.tao_init is None) == (self.lattice_file is None):
            raise ValueError("Give exactly one of tao_init or lattice_file.")
        if self.tao_init and self.lines:
            raise ValueError("lines can only be used with lattice_file.")
        return self

    def _tao_init_path(self) -> str:
        if self.tao_init:
            return self.tao_init
        self._generated_tao_init = tempfile.TemporaryDirectory(prefix="laura-bmad-")
        path = Path(self._generated_tao_init.name) / "tao.init"
        return str(
            BmadTaoInit(
                lattice_file=str(Path(self.lattice_file).resolve()), lines=self.lines
            ).write(path)
        )

    def _read_functional_definitions(self) -> None:
        if not self.lattice_file:
            return
        text = read_with_calls(Path(self.lattice_file), _CALL_RE)
        text = text.replace("&\n", " ")
        statements = [statement.strip() for statement in re.split(r";|\n", text)]
        values = {}
        deferred = {}
        for statement in statements:
            scalar = re.fullmatch(
                r"([A-Za-z_][\w.]*)\s*=\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)",
                statement,
            )
            if scalar:
                values[scalar.group(1)] = float(scalar.group(2))
                continue
            element = re.match(r"([^:]+):\s*[^,]+,(.*)", statement, re.S)
            if not element:
                continue
            for attribute, expression in re.findall(
                r"([A-Za-z_][\w.]*)\s*:=\s*([^,]+)", element.group(2)
            ):
                deferred.setdefault(element.group(1).strip().lower(), {})[
                    attribute.upper()
                ] = expression.strip()
        used = {
            token
            for parameters in deferred.values()
            for expression in parameters.values()
            for token in re.findall(r"[A-Za-z_][\w.]*", expression)
        }
        self.deferred_parameters = deferred
        self.functional_definitions = {
            name: value for name, value in values.items() if name in used
        }

    def _symbol(self, element: str, attribute: str, length=0.0) -> str | None:
        expression = self.deferred_parameters.get(element.lower(), {}).get(attribute)
        if not expression:
            return None
        compact = expression.lower().replace(" ", "").replace("(", "").replace(")", "")
        for name in self.functional_definitions:
            if compact == name.lower():
                return name
            if length and compact.startswith(name.lower() + "/"):
                try:
                    if math.isclose(float(compact.split("/", 1)[1]), length):
                        return name
                except ValueError:
                    pass
        return None

    def model_post_init(self, __context: Any) -> None:
        from pytao import Tao

        self._read_functional_definitions()

        tao = Tao(f"-init {self._tao_init_path()} -noplot", so_lib=self.libtao)
        self.bmad_com = dict(tao.bmad_com())
        self.space_charge_com = dict(tao.space_charge_com())
        universe_count = tao.super_universe()["n_universe"]
        while self.n_universes <= universe_count:
            self.branches.update(
                {
                    self.n_universes: [
                        f"{i['branch_name']}_{self.n_universes}"
                        for i in tao.lat_branch_list(ix_uni=self.n_universes)
                    ]
                }
            )
            self.names.update({self.n_universes: {}})
            self.names_numbered.update({self.n_universes: {}})
            self.types.update({self.n_universes: {}})
            self.lengths.update({self.n_universes: {}})
            self.spos.update({self.n_universes: {}})
            self.params.update({self.n_universes: {}})
            self.branch_params.update({self.n_universes: {}})
            self.laura_elems.update({self.n_universes: {}})
            self.super_lord_children.update({self.n_universes: {}})
            for ind, b in enumerate(self.branches[self.n_universes]):
                kwa = {
                    "ix_uni": str(self.n_universes),
                    "ix_branch": str(ind),
                }
                self.branch_params[self.n_universes][b] = tao.branch1(
                    ix_uni=self.n_universes, ix_branch=ind
                )
                names = [i for i in tao.lat_list("*", "ele.name", **kwa)]
                types = [i for i in tao.lat_list("*", "ele.key", **kwa)]
                lengths = [i for i in tao.lat_list("*", "ele.l", **kwa)]
                spos = [i for i in tao.lat_list("*", "ele.s", **kwa)]
                params = [
                    self._element_attributes(tao, self.n_universes, ind, i, etype)
                    for i, etype in enumerate(types)
                ]
                for index, wake in _lord_wakes(tao, self.n_universes, ind).items():
                    if 0 <= index < len(params):
                        params[index].setdefault("_WAKE", wake)
                children = self._collapse_super_lords(
                    tao,
                    self.n_universes,
                    ind,
                    names,
                    types,
                    lengths,
                    spos,
                    params,
                )
                children = _absorb_negative_drifts(
                    names, types, lengths, spos, params, children
                )
                names_numbered = number_repeated_names(names)
                self.super_lord_children[self.n_universes][b] = {
                    names_numbered[index]: names_numbered[lord]
                    for index, lord in children.items()
                }
                self.names[self.n_universes].update({b: names})
                self.names_numbered[self.n_universes].update({b: names_numbered})
                self.types[self.n_universes].update({b: types})
                self.lengths[self.n_universes].update({b: lengths})
                self.spos[self.n_universes].update({b: spos})
                self.params[self.n_universes].update({b: params})
                self.laura_elems[self.n_universes].update({b: {}})
            self.n_universes += 1
        self.branches = {
            k: [f"{i['branch_name']}_{k}" for i in tao.lat_branch_list(ix_uni=k)]
            for k in range(1, self.n_universes)
        }

    def _element_attributes(
        self, tao, universe: int, branch_index: int, index: int, etype: str
    ) -> Dict[str, Any]:
        """One Bmad element's attributes, with the per-key extras Tao keeps
        behind their own accessors folded in under ``_``-prefixed keys.

        ``index`` may address a lord as readily as a tracking element, so
        :meth:`_collapse_super_lords` can read a super-lord the same way.
        """
        element_id = f"{universe}@{branch_index}>>{index}"
        attributes = tao.ele_gen_attribs(element_id)
        # the general attribute table.
        attributes["_METHODS"] = tao.ele_methods(element_id)
        if self.position_mode == "floor":
            attributes["_FLOOR"] = tao.ele_floor(element_id, where="center")
            attributes["_FLOOR_ENTRANCE"] = tao.ele_floor(element_id, where="beginning")
        if etype == "Match":
            matrix = tao.ele_mat6(element_id, who="mat6")
            attributes["_MAT6"] = [matrix[str(row)] for row in range(1, 7)]
            attributes["_VEC0"] = tao.ele_mat6(element_id, who="vec0")["vec0"]
        elif etype == "Taylor":
            attributes["_TAYLOR"] = tao.ele_taylor(element_id)
            attributes["_SPIN_TAYLOR"] = tao.ele_spin_taylor(element_id)
        elif etype in _MULTIPOLE_TYPES or etype in magnetic_orders:
            attributes["_MULTIPOLES"] = tao.ele_multipoles(element_id)
        elif etype == "AC_Kicker":
            attributes["_AC_KICKER"] = _ac_kicker_data(tao, element_id)
        elif etype == "Beginning_Ele":
            attributes["_TWISS"] = tao.ele_twiss(element_id)
            attributes["_FLOOR"] = tao.ele_floor(element_id)
            attributes["_COUPLING"] = tao.twiss_at_s(
                ix_uni=universe,
                ele=f"{branch_index}>>{index}",
                s_offset=0.0,
            )
        elif etype == "Fixer":
            attributes["_ACTIVE"] = bool(tao.ele_head(element_id).get("is_on"))
            if attributes["_ACTIVE"]:
                attributes["_TWISS"] = tao.ele_twiss(element_id)
                attributes["_COUPLING"] = tao.twiss_at_s(
                    ix_uni=universe,
                    ele=f"{branch_index}>>{index}",
                    s_offset=0.0,
                )
        wake = _wake_tables(tao, element_id)
        if wake:
            attributes["_WAKE"] = wake
        return attributes

    def _collapse_super_lords(
        self,
        tao,
        universe: int,
        branch_index: int,
        names: List[str],
        types: List[str],
        lengths: List[float],
        spos: List[float],
        params: List[Dict[str, Any]],
    ) -> Dict[int, int]:
        """Put super-lords back in place of the slices Bmad cut them into.

        Superimposing anything on an element makes Bmad replace it with a
        lord plus numbered super-slaves; for an
        ``lcavity``:

        * every slave reports the *lord's* ``l_active``, the whole-cell length
          the RF actually fills. .
        * the entrance and exit focusing kicks belong to the lord's ends.

        Slices are merged back into
        the lord and the elements that split it become its ``subelement``
        children. These become ``superimpose`` statements on export.

        The lists are rewritten in place. Returns ``{child index: lord index}``
        into the rewritten lists, for the superimposed elements.
        """
        lords: Dict[int, List[int]] = {}
        try:
            info = tao.lat_branch_list(ix_uni=universe)[branch_index]
            first, last = int(info["n_ele_track"]) + 1, int(info["n_ele_max"])
        except Exception:
            return {}
        for index in range(first, last + 1):
            element_id = f"{universe}@{branch_index}>>{index}"
            try:
                rows = tao.ele_lord_slave(element_id)
            except Exception:
                continue
            location = f"{branch_index}>>{index}"
            mine = False
            for row in rows:
                if row.get("type") == "Element":
                    mine = (
                        row.get("location_name") == location
                        and row.get("status") == "Super_Lord"
                    )
                elif mine and row.get("type") == "Slave":
                    slave = str(row.get("location_name") or "")
                    if row.get("status") == "Super_Slave" and slave.startswith(
                        f"{branch_index}>>"
                    ):
                        lords.setdefault(index, []).append(int(slave.split(">>")[1]))

        every_slave = {index for slaves in lords.values() for index in slaves}
        merge: Dict[int, int] = {}  # first slave index -> lord index
        drop: set = set()  # the other slave indices
        children: Dict[int, int] = {}  # child index -> lord index
        for lord, slaves in sorted(lords.items()):
            slaves = sorted(slaves)
            if not slaves or max(slaves) >= len(names):
                continue
            inside = [
                index
                for index in range(slaves[0], slaves[-1] + 1)
                if index not in set(slaves)
            ]
            reason = None
            if any(index in every_slave for index in inside):
                reason = "it overlaps another superimposed element"
            elif any(abs(float(lengths[index])) > 1e-12 for index in inside):
                reason = "an element with length was superimposed on it"
            elif any(index in merge or index in drop for index in slaves):
                reason = "its slices are shared with another lord"
            if reason:
                warn(
                    f"Bmad super-lord {names[slaves[0]]!r} was left as "
                    f"{len(slaves)} slices because {reason}. An lcavity "
                    "imported this way splits its energy gain and its edge "
                    "focusing between the slices, which Bmad does not."
                )
                continue
            merge[slaves[0]] = lord
            drop.update(slaves[1:])
            children.update({index: lord for index in inside})

        if not merge:
            return {}

        new_names, new_types, new_lengths, new_spos, new_params = [], [], [], [], []
        lord_row: Dict[int, int] = {}  # lord index -> row in the rewritten lists
        child_row: Dict[int, int] = {}  # child row -> lord index
        for index in range(len(names)):
            if index in drop:
                continue
            if index in merge:
                lord = merge[index]
                head = tao.ele_head(f"{universe}@{branch_index}>>{lord}")
                attributes = self._element_attributes(
                    tao, universe, branch_index, lord, head["key"]
                )
                lord_row[lord] = len(new_names)
                new_names.append(head["name"])
                new_types.append(head["key"])
                new_lengths.append(float(attributes.get("L", 0.0)))
                new_spos.append(float(head["s"]))
                new_params.append(attributes)
                continue
            if index in children:
                child_row[len(new_names)] = children[index]
            new_names.append(names[index])
            new_types.append(types[index])
            new_lengths.append(lengths[index])
            new_spos.append(spos[index])
            new_params.append(params[index])

        names[:] = new_names
        types[:] = new_types
        lengths[:] = new_lengths
        spos[:] = new_spos
        params[:] = new_params
        return {row: lord_row[lord] for row, lord in child_row.items()}

    def _wake_field(
        self,
        name: str,
        parameters: Dict[str, Any],
        length: float,
        hardware_type: str,
    ) -> Dict[str, Any]:
        """Sample this element's Bmad wake into a LAURA ``field``, if it has one."""
        tables = parameters.get("_WAKE")
        if not tables:
            return {}
        if not _holds_a_wake_field(hardware_type):
            warn(
                f"Bmad element {name!r} carries a short-range wake but LAURA's "
                f"{hardware_type} holds wakefield_definition as a file name only; "
                "the wake was not imported."
            )
            return {}
        sampled = sample_bmad_sr_wake(
            tables["base"],
            tables["sr_long"],
            tables["sr_trans"],
            length=length,
            name=name,
            samples=self.wake_samples,
        )
        if not sampled:
            return {}
        units = {"z": "m", "Wz": "V/C", "Wx": "V/C/m", "Wy": "V/C/m"}
        transverse = "Wx" in sampled or "Wy" in sampled
        if not transverse:
            field_type = "LongitudinalWake"
        elif "Wz" in sampled:
            field_type = "3DWake"
        else:
            field_type = "TransverseWake"
        wake = FieldMap(
            field_type=field_type,
            origin_code="Bmad",
            length=length,
            filename=re.sub(r"[^A-Za-z0-9_.-]", "_", name) + "_wake.bmad",
            **{
                key: FieldParameter(name=key, value=UnitValue(values, units=units[key]))
                for key, values in sampled.items()
            },
        )
        wake.read = True
        return {"simulation": {"wakefield_definition": wake}}

    def _physical_common(self, universe: int, b: str, i: int) -> dict:
        """Build this element's shared ``physical`` sub-dict (position + length).

        Under ``position_mode="s"`` Bmad's own cumulative arc-length is handed
        straight to LAURA as ``physical.s``/``s_point``, fed into
        ``resolve_positions()``.

        Under ``position_mode="floor"`` the element is placed directly at Tao's
        surveyed coordinates instead.
        """
        parameters = self.params[universe][b][i]
        common = {
            "length": float(self.lengths[universe][b][i]),
            **_misalignment(parameters),
        }
        angle = parameters.get("ANGLE")
        roll = 0.0
        if angle:
            common["physical_angle"] = -float(angle)
            roll = float(parameters.get("REF_TILT") or 0.0)
            if is_flat_roll(roll):
                roll = 0.0  # the layout rolls a flat bend by ``magnetic.tilt``
        if self.position_mode == "floor":
            floor = _floor_to_physical(
                parameters.get("_FLOOR", {}),
                "middle",
                parameters.get("_FLOOR_ENTRANCE"),
                roll,
            )
            if floor:
                return {**common, **floor}
        return {
            "s": self.spos[universe][b][i],
            "s_point": "end",
            **common,
        }

    def create_element_dictionary(self, universe: int) -> Dict[str, Dict[str, Element]]:
        return self.create_laura_element_dictionary(universe)

    def _subelement_of(self, universe: int, branch: str, name: str) -> dict:
        """``{"subelement": lord}`` if Bmad superimposed *name* inside another
        element, else empty. See :meth:`_collapse_super_lords`."""
        lord = self.super_lord_children.get(universe, {}).get(branch, {}).get(name)
        return {"subelement": lord} if lord else {}

    def _store_marker(
        self,
        universe: int,
        branch: str,
        name: str,
        physical: dict,
        parameters: Dict[str, Any],
        hardware_type: str,
    ) -> None:
        """Store *name* as a point-like element, keeping only its placement.

        Used both for Bmad's genuinely point-like keys and as the fallback for
        elements LAURA has no strength model for.
        """
        extra = self._wake_field(
            name,
            parameters,
            float(physical.get("length") or 0.0),
            hardware_type,
        )
        settings = _collective_settings(
            parameters, getattr(self, "bmad_com", {}), hardware_type
        )
        if settings:
            extra["simulation"] = settings | dict(extra.get("simulation") or {})
        self.laura_elems[universe][branch].update(
            {
                name: getattr(laura_elements, hardware_type)(
                    physical=dict(physical),
                    name=name,
                    hardware_type=hardware_type,
                    machine_area=getattr(self, "machine_area", "Lattice"),
                    **self._subelement_of(universe, branch, name),
                    **_aperture(parameters),
                    **extra,
                )
            }
        )

    def _store_twiss_point(
        self,
        universe: int,
        branch: str,
        name: str,
        physical: dict,
        parameters: Dict[str, Any],
    ) -> None:
        """Store *name* as the point where the design Twiss is declared.

        Bmad has two elements that do this and no third: ``beginning_ele``, at
        the head of every branch, and the one ``fixer`` a branch may nominate in
        its place. Neither touches the beam, and LAURA holds both as a zero-length
        ``TwissMatch``.

        The export is not symmetric; `TwissMatch` is faithful, while a mid-line
        fixer imports faithfully and exports approximately.
        """
        twiss = parameters.get("_TWISS", {})
        if not twiss:
            return
        self._warn_unsupported_coupling(twiss, parameters, name)
        self.laura_elems[universe][branch].update(
            {
                name: laura_elements.TwissMatch(
                    physical=dict(physical),
                    name=name,
                    hardware_type="TwissMatch",
                    machine_area=getattr(self, "machine_area", "Lattice"),
                    simulation=_collective_settings(
                        parameters, getattr(self, "bmad_com", {}), "TwissMatch"
                    )
                    | {
                        "beta_x": twiss["beta_a"],
                        "beta_y": twiss["beta_b"],
                        "alpha_x": twiss["alpha_a"],
                        "alpha_y": twiss["alpha_b"],
                        "eta_x": twiss["eta_x"],
                        "eta_y": twiss["eta_y"],
                        "eta_xp": twiss["etap_x"],
                        "eta_yp": twiss["etap_y"],
                        "from_beam": False,
                    },
                )
            }
        )

    def create_laura_element_dictionary(
        self, universe: int
    ) -> Dict[str, Dict[str, Element]]:
        switch_dict = _switch_dict()
        for b, names in self.names_numbered[universe].items():
            for i, nam in enumerate(names):
                etype = self.types[universe][b][i]
                native = _NativeElement(
                    universe=universe,
                    branch=b,
                    name=nam,
                    etype=etype,
                    hardware_type=switch_dict.get(etype.lower()),
                    length=float(self.lengths[universe][b][i]),
                    parameters=self.params[universe][b][i],
                    physical=self._physical_common(universe, b, i),
                )
                builder = _BUILDERS.get(etype)
                if builder is None:
                    warn(
                        f"Could not parse Bmad element type {etype!r} for "
                        f"{nam!r}; skipping."
                    )
                    continue
                elem_data = getattr(self, builder)(native)
                if elem_data:
                    self._store_element(native, elem_data)
        return self.laura_elems[universe]

    def _store_element(self, e: "_NativeElement", elem_data: dict) -> None:
        """Add the settings every element shares to ``elem_data`` and store it.

        A Bmad ``kicker`` is stored as a ``Combined_Corrector`` followed by its
        horizontal and vertical halves.
        """
        hardware_type = elem_data.get("hardware_type", "")
        simulation = (
            _collective_settings(
                e.parameters, getattr(self, "bmad_com", {}), hardware_type
            )
            | _fringe_model(e.parameters, e.etype, hardware_type)
            | dict(elem_data.get("simulation") or {})
        )
        wake_data = self._wake_field(e.name, e.parameters, e.length, hardware_type)
        if wake_data:
            simulation.update(wake_data["simulation"])
        if simulation:
            elem_data["simulation"] = simulation
        data = {
            "physical": dict(e.physical),
            "name": e.name,
            "machine_area": getattr(self, "machine_area", "Lattice"),
            **_aperture(e.parameters, e.etype),
            **elem_data,
            **self._subelement_of(e.universe, e.branch, e.name),
        }
        stored = self.laura_elems[e.universe][e.branch]
        if e.etype != "Kicker":
            stored[e.name] = getattr(laura_elements, data["hardware_type"])(**data)
            return
        stored[e.name] = CombinedCorrector(**data)
        for suffix, cls, hardware_type, kick in (
            ("_H", HorizontalCorrector, "Horizontal_Corrector", "horizontal_kick"),
            ("_V", VerticalCorrector, "Vertical_Corrector", "vertical_kick"),
        ):
            stored[e.name + suffix] = cls(
                **{
                    **data,
                    "physical": dict(e.physical),
                    "name": e.name + suffix,
                    "hardware_type": hardware_type,
                    "magnetic": {"length": e.length, kick: data["magnetic"][kick]},
                    "subelement": e.name,
                }
            )

    def _build_kicker(self, e: "_NativeElement") -> dict:
        planes = {
            "HKicker": ("horizontal_kick",),
            "VKicker": ("vertical_kick",),
        }.get(e.etype, ("horizontal_kick", "vertical_kick"))
        magnetic = {"length": e.length}
        for target in planes:
            kick = e.keyword(target)
            magnetic[target] = self._symbol(e.base_name, kick) or e.parameters[kick]
        return {"hardware_type": e.hardware_type, "magnetic": magnetic}

    def _build_magnet(self, e: "_NativeElement") -> dict:
        parameters = e.parameters
        order = magnetic_orders[e.hardware_type]
        magnetic = {"order": order, "length": e.length}
        strength = f"K{order}"
        normal = self._symbol(e.base_name, strength, e.length)
        if normal is None and strength in parameters:
            normal = parameters[strength] * e.length
        if normal is None:
            normal = self._symbol(e.base_name, "ANGLE") or parameters["ANGLE"]
            for edge in ("entrance_edge_angle", "exit_edge_angle"):
                magnetic[edge] = parameters[e.keyword(edge)]
        poles = {f"K{order}L": {"normal": normal, "order": order}}
        magnetic["multipoles"] = poles
        for field, native, scale in (
            ("gap", "gap", 1),
            ("gap", "half_gap", 2),
            ("edge_field_integral", "edge_field_integral", 1),
            ("exit_gap", "exit_half_gap", 2),
            ("edge_field_integral_exit", "edge_field_integral_exit", 1),
        ):
            native = e.keyword(native)
            if native in parameters:
                magnetic[field] = scale * parameters[native]
        for exit_field, entrance_field in (
            ("edge_field_integral_exit", "edge_field_integral"),
            ("exit_gap", "gap"),
        ):
            if magnetic.get(exit_field) == magnetic.get(entrance_field):
                magnetic.pop(exit_field, None)
        tilt = parameters.get(e.keyword("tilt")) or parameters.get("TILT")
        if tilt:
            magnetic["tilt"] = tilt
        for extra_order, components in _an_bn_multipoles(parameters).items():
            pole = poles.setdefault(f"K{extra_order}L", {"order": extra_order})
            for component, value in components.items():
                standing = pole.get(component) or 0.0
                if isinstance(standing, str):
                    warn(
                        f"Bmad {e.etype} {e.name!r} has both a functional "
                        f"K{extra_order} and a fixed "
                        f"{'a' if component == 'skew' else 'b'}"
                        f"{extra_order} = {value}; LAURA holds one "
                        "value per component, so the functional "
                        "definition was kept and the fixed term "
                        "dropped."
                    )
                    continue
                pole[component] = standing + value
        main = poles.get(f"K{order}L", {})
        if main.get("skew") and not main.get("normal"):
            magnetic["skew"] = True
        return {"hardware_type": e.hardware_type, "magnetic": magnetic}

    def _build_cavity(self, e: "_NativeElement") -> dict:
        parameters = e.parameters
        frequency = parameters[e.keyword("frequency")]
        cell_length = speed_of_light / (2.0 * frequency) if frequency else 0.0
        n_cells = _bmad_cavity_cells(
            parameters.get(e.keyword("n_cells"), 1),
            parameters.get("L_ACTIVE"),
            e.length,
            cell_length,
        )
        simulation = {"field_amplitude": parameters[e.keyword("field_amplitude")]}
        if parameters.get("N_RF_STEPS"):
            simulation["n_kicks"] = int(parameters["N_RF_STEPS"])
        return {
            "hardware_type": e.hardware_type,
            "cavity": {
                "phase": -360.0 * parameters.get(e.keyword("phase"), 0.0),
                "frequency": frequency,
                "n_cells": n_cells,
                "cell_length": cell_length or e.length / n_cells,
                "structure_type": str(
                    parameters.get(e.keyword("structure_type"), "Standing_Wave")
                ).replace("_", ""),
            },
            "simulation": simulation,
        }

    def _build_wiggler(self, e: "_NativeElement") -> dict:
        b_max = e.parameters.get(e.keyword("peak_magnetic_field"), 0.0)
        l_period = e.parameters.get(e.keyword("period"), 0.0)
        return {
            "hardware_type": e.hardware_type,
            "magnetic": {
                "length": e.length,
                "peak_magnetic_field": b_max,
                "period": l_period,
                "num_periods": int(e.parameters.get(e.keyword("num_periods"), 0)),
                # K = 0.934 B[T] lambda_u[cm]
                "strength": 0.934 * b_max * (l_period * 100.0),
            },
        }

    def _build_solenoid(self, e: "_NativeElement") -> dict:
        ks = e.parameters.get(e.keyword("ks"), 0.0)
        return {
            "hardware_type": e.hardware_type,
            "magnetic": {"length": e.length, "fields": {"S0L": ks * e.length}},
        }

    def _build_sol_quad(self, e: "_NativeElement") -> dict:
        k1 = e.keyword("k1l")
        ks = e.parameters.get(e.keyword("ks"), 0.0)
        return {
            "hardware_type": e.hardware_type,
            "magnetic": {
                "length": e.length,
                "k1l": self._symbol(e.base_name, k1, e.length)
                or e.parameters.get(k1, 0.0) * e.length,
                "solenoid_fields": {"S0L": ks * e.length},
            },
        }

    def _build_separator(self, e: "_NativeElement") -> dict:
        field = e.parameters.get(e.keyword("field_amplitude"), 0.0)
        hkick = e.parameters.get(e.keyword("horizontal_kick"), 0.0)
        vkick = e.parameters.get(e.keyword("vertical_kick"), 0.0)
        kick = math.hypot(hkick, vkick)
        if kick:
            horizontal, vertical = hkick / kick, vkick / kick
        else:
            tilt = e.parameters.get("TILT", 0.0)
            horizontal, vertical = math.sin(tilt), math.cos(tilt)
        return {
            "hardware_type": e.hardware_type,
            "simulation": {
                "horizontal_field": field * horizontal,
                "vertical_field": field * vertical,
            },
        }

    def _build_match(self, e: "_NativeElement") -> dict:
        return {
            "hardware_type": e.hardware_type,
            "simulation": {
                "apply": True,
                "c_matrix": e.parameters["_VEC0"],
                "r_matrix": e.parameters["_MAT6"],
            },
        }

    def _build_taylor(self, e: "_NativeElement") -> Optional[dict]:
        try:
            c_matrix, r_matrix, t_matrix, u_matrix = _taylor_matrices(
                e.parameters["_TAYLOR"]
            )
        except ValueError as exc:
            warn(f"Could not import Bmad Taylor element {e.name!r}: {exc}.")
            return None
        return {
            "hardware_type": e.hardware_type,
            "simulation": {
                "apply": True,
                "c_matrix": c_matrix,
                "r_matrix": r_matrix,
                "t_matrix": t_matrix,
                "u_matrix": u_matrix,
                "spin_taylor": e.parameters["_SPIN_TAYLOR"],
            },
        }

    def _build_collimator(self, e: "_NativeElement") -> dict:
        return {"hardware_type": e.hardware_type}

    def _build_multipole(self, e: "_NativeElement") -> Optional[dict]:
        poles = {}
        for row in e.parameters.get("_MULTIPOLES", {}).get("data", []):
            order = int(row["index"])
            normal = row.get("Bn", row.get("Bn (equiv)", 0.0)) or 0.0
            skew = row.get("An", row.get("An (equiv)", 0.0)) or 0.0
            if normal or skew:
                scale = math.factorial(order)
                poles[f"K{order}L"] = {
                    "order": order,
                    "normal": normal * scale,
                    "skew": skew * scale,
                }
        if not poles:
            warn(
                f"Bmad {e.etype} {e.name!r} has no multipole content; "
                "imported as a Marker, since there is no order to "
                "give a zero-strength magnet."
                + (
                    f" Its {e.length} m length is dependent on the"
                    " Bmad element key and is dropped on export."
                    if e.length
                    else ""
                )
            )
            self._store_marker(
                e.universe, e.branch, e.name, e.physical, e.parameters, "Marker"
            )
            return None
        highest = max(int(k[1:-1]) for k in poles)
        return {
            "hardware_type": _ORDER_TYPES.get(highest, "Magnet"),
            "magnetic": {"order": highest, "length": e.length, "multipoles": poles},
        }

    def _build_ac_kicker(self, e: "_NativeElement") -> dict:
        hkick = e.parameters.get("HKICK", 0.0) or 0.0
        vkick = e.parameters.get("VKICK", 0.0) or 0.0
        vertical = abs(vkick) > abs(hkick)
        amplitude = vkick if vertical else hkick
        simulation = {"field_amplitude": amplitude}
        ac_data = e.parameters.get("_AC_KICKER", {})
        frequencies = ac_data.get("frequencies", [])
        if frequencies:
            frequency, scale, phase = max(frequencies, key=lambda row: abs(row[1]))
            simulation.update(
                {
                    "field_amplitude": amplitude * scale,
                    "frequency": frequency,
                    "phase": phase * 360,
                }
            )
            if len(frequencies) > 1:
                warn(
                    f"Bmad AC_Kicker {e.name!r} has multiple frequencies; "
                    "LAURA stores one, so the largest-amplitude component "
                    "was imported."
                )
        if ac_data.get("amp_vs_time"):
            warn(
                f"Bmad AC_Kicker {e.name!r} uses amp_vs_time; LAURA has no "
                "equivalent sampled-time waveform, so it was not imported."
            )
        if hkick and vkick:
            warn(
                f"Bmad AC_Kicker {e.name!r} kicks in both planes "
                f"(hkick={hkick}, vkick={vkick}); LAURA models a single "
                "plane per element, so only the larger kick is imported."
            )
        return {
            "hardware_type": (
                "Vertical_AC_Dipole" if vertical else "Horizontal_AC_Dipole"
            ),
            "simulation": simulation,
        }

    def _build_beam_beam(self, e: "_NativeElement") -> dict:
        get = e.parameters.get
        return {
            "hardware_type": e.hardware_type,
            "simulation": {
                "n_particles": get("N_PARTICLE"),
                "charge": get("CHARGE"),
                "horizontal_sigma": get("SIG_X"),
                "vertical_sigma": get("SIG_Y"),
                "width": get("SIG_Z"),
            },
        }

    def _build_marker(self, e: "_NativeElement") -> None:
        if e.etype == "Fixer" and e.parameters.get("_ACTIVE"):
            self._store_twiss_point(
                e.universe, e.branch, e.name, e.physical, e.parameters
            )
            return
        if e.etype == "Fixer":
            warn(
                f"Bmad Fixer {e.name!r} is not the active fixer, so "
                "its stored orbit and Twiss are not this "
                "branch's; it is imported as a Marker and they "
                "are dropped."
            )
        self._store_marker(
            e.universe, e.branch, e.name, e.physical, e.parameters, e.hardware_type
        )

    def _build_beginning(self, e: "_NativeElement") -> None:
        if e.parameters.get("_TWISS"):
            physical = dict(e.physical)
            physical.update(_floor_to_physical(e.parameters.get("_FLOOR", {})))
            self._store_twiss_point(
                e.universe, e.branch, e.name, physical, e.parameters
            )

    def _build_patch(self, e: "_NativeElement") -> None:
        """Warn about what LAURA loses from a patch; nothing is stored."""
        transform = {
            key: e.parameters[key]
            for key in _PATCH_TRANSFORM_ATTRIBUTES
            if abs(e.parameters.get(key) or 0.0) > _PATCH_TRANSFORM_TOLERANCE
        }

        def described(keys) -> str:
            return ", ".join(
                f"{key}={value}" for key, value in transform.items() if key in keys
            )

        geometric = described(_PATCH_GEOMETRIC_ATTRIBUTES)
        if geometric and self.position_mode == "s":
            warn(
                f"Bmad Patch {e.name!r} moves the reference frame "
                f"({geometric}). position_mode='s' integrates"
                " geometry from element lengths and bend angles and"
                " cannot represent the shift, so every element after"
                " this one is placed as though the patch were"
                " absent. Import with position_mode='floor' to take"
                " the placement from Tao instead."
            )
        energy = described(_PATCH_ENERGY_ATTRIBUTES)
        if energy:
            warn(
                f"Bmad Patch {e.name!r} changes the reference energy "
                f"({energy}). LAURA has no element for a"
                " reference-energy jump, so it is dropped and the"
                " reference energy downstream of this patch is"
                " wrong."
            )

    def _build_drift(self, e: "_NativeElement") -> Optional[dict]:
        if e.length < 0.0:
            warn(
                f"Bmad drift {e.name!r} has negative length ({e.length} "
                "m), which LAURA cannot hold, and nothing adjacent "
                "cancels it, so it is dropped. Everything "
                f"downstream of it sits {-2 * e.length} m too far "
                "along the beam line."
            )
            return None
        return {"hardware_type": "Drift", "hardware_class": "Drift"}

    def _reference_energy(self, universe: int, branch: str) -> float | None:
        """Reference total energy [eV] at the start of ``branch``."""
        types = self.types.get(universe, {}).get(branch, [])
        for index, etype in enumerate(types):
            if etype == "Beginning_Ele":
                e_tot = self.params[universe][branch][index].get("E_TOT")
                return float(e_tot) if e_tot is not None else None
        return None

    def _warn_unsupported_coupling(
        self, twiss: Dict[str, Any], attributes: Dict[str, Any], name: str
    ) -> None:
        """Warn that Bmad's transverse coupling description is not imported."""
        if twiss.get("mode_flip") or attributes.get("MODE_FLIP"):
            warn(f"Bmad lattice has mode_flip=True at {name!r}: currently unsupported.")
        coupling = attributes.get("_COUPLING", {})
        cmat = [coupling.get(f"c_mat{ij}", 0.0) for ij in ("11", "12", "21", "22")]
        if any(cmat):
            warn(
                f"Bmad lattice has transverse coupling at {name!r} "
                f"(cmat = {cmat}, gamma_c = {coupling.get('gamma_c')}): "
                "currently unsupported."
            )

    def _space_charge_settings(self) -> Dict[str, Any]:
        """The section's collective-field resolution, read from Bmad's
        ``space_charge_com``. Only positive values are carried.
        """
        return {
            field: value
            for key, field in _SPACE_CHARGE_COM.items()
            if isinstance(value := self.space_charge_com.get(key), (int, float))
            and value > 0
        }

    def create_section(self, universe: int, branch: str) -> Dict[str, SectionLattice]:
        if not self.laura_elems[universe][branch]:
            self.create_laura_element_dictionary(universe)
        elems = self.laura_elems[universe][branch]
        self.elements = elems
        order = [n for n, e in elems.items() if not e.is_subelement()]
        branch_params = self.branch_params.get(universe, {}).get(branch, {})
        geometry = branch_params.get("param_geometry")
        seclat = SectionLattice(
            order=order,
            elements=ElementList(elements=elems),
            name=branch,
            functional_definitions=self.functional_definitions,
            geometry=str(geometry).lower() if geometry else None,
            reference_energy=self._reference_energy(universe, branch),
            space_charge=self._space_charge_settings() or None,
        )
        seclat.resolve_positions(elems)
        if self.position_mode == "floor":
            self._restore_arc_length(universe, branch, elems)
        superimposed = self.super_lord_children.get(universe, {}).get(branch, {})
        for name, elem in elems.items():
            if elem.is_subelement() and name not in superimposed:
                parent = elems.get(elem.subelement)
                if parent is not None and parent.physical.middle is not None:
                    elem.physical.s = parent.physical.s
                    elem.physical.s_point = parent.physical.s_point
                    elem.physical.middle = parent.physical.middle
                    elem.physical.rotation = parent.physical.rotation
                    elem.physical.global_rotation = parent.physical.global_rotation
        sections = self._split_multipass(universe, branch, seclat)
        return sections if sections else {branch: seclat}

    def _multipass_numbers(self, universe: int, branch: str) -> Dict[str, tuple]:
        """``{element name: (hardware name, pass number)}`` for this branch's
        multipass slaves, keyed as :attr:`laura_elems` keys them."""
        numbered = self.names_numbered[universe][branch]
        names = self.names[universe][branch]
        params = self.params[universe][branch]
        found = {}
        for index, key in enumerate(numbered):
            slave = _multipass_slave(names[index], params[index])
            if slave is not None:
                found[key] = slave
        return found

    def _split_multipass(
        self, universe: int, branch: str, section: SectionLattice
    ) -> Dict[str, SectionLattice]:
        """One section per multipass traversal, or ``{}`` if the branch has none.

        Bmad's multipass unit is a *line*, LAURA's is a *section*, and
        ``lat_list`` gives back neither -- only a flat run of elements with the
        slaves called ``NAME\\N``. So the line is recovered as the run of
        consecutive slaves sharing a pass number, and the free elements between
        two of those runs become ordinary sections. Pass 1 supplies the
        hardware, under its unnumbered name; the later passes are read for what
        they change and then dropped, since they are the same device.

        Two *different* multipass lines with nothing between them come back as
        one section. That is coarser than the original but not wrong: the same
        run recurs on every pass, so it still round-trips.
        """
        slaves = self._multipass_numbers(universe, branch)
        if not slaves:
            return {}

        groups: List[tuple] = []
        for name in section.order:
            number = slaves[name][1] if name in slaves else None
            if groups and groups[-1][0] == number:
                groups[-1][1].append(name)
            else:
                groups.append((number, [name]))

        elements = section.elements.elements
        children = {}
        for name, element in elements.items():
            if element.is_subelement():
                children.setdefault(element.subelement, []).append(name)

        sections: Dict[str, SectionLattice] = {}
        passes: List[Dict[str, Any]] = []
        by_hardware: Dict[tuple, str] = {}
        for number, members in groups:
            hardware = tuple(slaves.get(name, (name,))[0] for name in members)
            existing = by_hardware.get(hardware)
            if existing is not None:
                passes.append(
                    {
                        "section": existing,
                        "number": number,
                        "overrides": self._multipass_overrides(
                            universe, branch, members, slaves
                        ),
                    }
                )
                continue
            name = f"{branch}_{len(sections) + 1}"
            order = []
            members_and_children = {}
            for member, base in zip(members, hardware):
                element = elements[member]
                element.name = base
                order.append(base)
                members_and_children[base] = element
                for child in children.get(member, []):
                    members_and_children[elements[child].name] = elements[child]
            sections[name] = SectionLattice(
                order=order,
                elements=ElementList(elements=members_and_children),
                name=name,
                functional_definitions=self.functional_definitions,
                geometry=section.geometry,
                reference_energy=section.reference_energy,
                space_charge=section.space_charge,
            )
            by_hardware[hardware] = name
            passes.append({"section": name, "number": number, "overrides": {}})

        self.multipass_passes.setdefault(universe, {})[branch] = passes
        return sections

    def _multipass_overrides(
        self, universe: int, branch: str, members: List[str], slaves: Dict[str, tuple]
    ) -> Dict[str, Dict[str, Any]]:
        """What this pass changes relative to pass 1.

        Only the attributes Bmad lets a slave hold on its own can differ, and
        those are the ones :data:`_MULTIPASS_OVERRIDES` names. Reference energy
        is deliberately *not* read back as ``momentum``: Bmad keeps strength on
        the multipass lord, so both passes really do share one ``k1``, and
        stating a per-pass momentum would make LAURA scale it on the way out.
        """
        numbered = self.names_numbered[universe][branch]
        params = self.params[universe][branch]
        first = {
            slaves[key][0]: params[index]
            for index, key in enumerate(numbered)
            if key in slaves and slaves[key][1] == 1
        }
        overrides: Dict[str, Dict[str, Any]] = {}
        for member in members:
            hardware = slaves[member][0]
            reference = first.get(hardware)
            if reference is None:
                continue
            parameters = params[numbered.index(member)]
            for attribute, (path, convert) in _MULTIPASS_OVERRIDES.items():
                value = parameters.get(attribute)
                if value is None or value == reference.get(attribute):
                    continue
                overrides.setdefault(hardware, {})[path] = convert(value)
        return overrides

    def _restore_arc_length(
        self, universe: int, branch: str, elems: Dict[str, Element]
    ) -> None:
        """Write Bmad's own arc-length back after a ``floor``-mode resolve."""
        lengths = self.lengths[universe][branch]
        spos = self.spos[universe][branch]
        for i, name in enumerate(self.names_numbered[universe][branch]):
            element = elems.get(name)
            if element is None or element.physical is None:
                continue
            physical = element.physical
            physical._syncing = True
            try:
                # Bmad reports s at the exit; LAURA holds it at the centre.
                physical.s = spos[i] - float(lengths[i]) / 2.0
                physical.s_point = "middle"
            finally:
                physical._syncing = False

    def create_layout(self, universe: int, name: Optional[str] = None) -> MachineLayout:
        layout = {}
        passes = []
        for branch in list(self.names_numbered[universe].keys()):
            sections = self.create_section(universe, branch)
            layout.update(sections)
            passes.extend(
                self.multipass_passes.get(universe, {}).get(branch)
                or [{"section": section} for section in sections]
            )
        return MachineLayout(
            name=name or str(universe),
            sections=layout,
            passes=passes,
            functional_definitions=self.functional_definitions,
            particle=self._particle(universe),
        )

    def _particle(self, universe: int) -> str | None:
        """Design particle species."""
        for branch_params in self.branch_params.get(universe, {}).values():
            particle = branch_params.get("param_particle")
            if particle:
                return str(particle)
        return None

    def create_machine_model(self, min_section_length: int = 5) -> MachineModel:
        """Build a model with one layout per Tao universe.
        Branches become sections. Elements with the same name are given a
        ``name__layout`` copy when shared between branches because
        :class:`MachineModel` stores one placement per name.

        Parameters
        ----------
        min_section_length: int
            Sections are only created if they are longer than this value.

        Returns
        -------
        MachineModel
            The full machine model containing all branches and universes.
        """
        if min_section_length < 1:
            raise ValueError("min_section_length must be at least 1.")

        layout_names = {}
        if self.tao_init:
            text = Path(self.tao_init).read_text()
            layout_names = {
                int(universe): Path(filename).stem
                for universe, filename in re.findall(
                    r"design_lattice\((\d+)\)%file\s*=\s*['\"]([^'\"]+)['\"]",
                    text,
                    re.I,
                )
            }

        elements = {}
        section_definitions = {}
        layout_definitions = {}
        section_metadata = {}
        layout_particles = {}
        skipped_sections = []

        for universe in sorted(self.branches):
            default_name = (
                Path(self.lattice_file).stem if self.lattice_file else str(universe)
            )
            layout_name = layout_names.get(universe, default_name)
            if layout_name in layout_definitions:
                layout_name = f"{layout_name}_{universe}"
            layout = self.create_layout(universe, name=layout_name)
            layout_sections = []
            renamed = {}
            for source_name, section in layout.sections.items():
                if len(section.order) < min_section_length:
                    skipped_sections.append(f"{layout_name}/{source_name}")
                    continue
                section_name = source_name
                if section_name in section_definitions:
                    section_name = f"{layout_name}_{section_name}"
                renamed[source_name] = section_name
                merge_layout_elements(
                    elements,
                    section_definitions,
                    section_name,
                    section.elements.elements.items(),
                    section.order,
                    layout_name,
                )
                if section.space_charge is not None:
                    section_definitions[section_name] = {
                        "elements": section_definitions[section_name],
                        "space_charge": section.space_charge.model_dump(
                            exclude_none=True
                        ),
                    }
                section_metadata[section_name] = (
                    section.geometry,
                    section.reference_energy,
                )
                layout_sections.append(section_name)
            if layout_sections:
                layout_definitions[layout_name] = _layout_entries(
                    layout, layout_sections, renamed
                )
                layout_particles[layout_name] = layout.particle

        if skipped_sections:
            warn(
                "Skipped BMAD branches shorter than min_section_length="
                f"{min_section_length}: {', '.join(skipped_sections)}"
            )
        if not layout_definitions:
            raise ValueError(
                f"No BMAD layouts meet min_section_length={min_section_length}."
            )

        source = self.tao_init or self.lattice_file
        particles = {p for p in layout_particles.values() if p}
        model = MachineModel(
            elements=elements,
            section={"sections": section_definitions},
            layout={
                "layouts": layout_definitions,
                "default_layout": next(iter(layout_definitions)),
            },
            master_lattice=str(Path(source).resolve().parent),
            functional_definitions=self.functional_definitions,
            particle=particles.pop() if len(particles) == 1 else None,
        )
        for section_name, metadata in section_metadata.items():
            section = model.sections.get(section_name)
            if section is None:
                continue
            section.geometry, section.reference_energy = metadata
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
