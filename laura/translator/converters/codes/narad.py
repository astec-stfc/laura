"""
Import a NARAD instance into LAURA, and export LAURA as one.

NARAD components carry PALS parameter groups, so rather than a second set of
group readers this module rewrites a NARAD instance as the
:class:`~laura.translator.utils.pals.PalsDocument` the PALS importer reads and
leaves every conversion to :class:`PalsLatticeImporter`. Only what NARAD does
differently from PALS lives here.

The export (:func:`narad_instance`) runs the other way through the PALS writer's
:func:`~laura.translator.utils.pals.pals_element_body`. What NARAD has no slot
for travels in ``MetaP.additional_metadata`` under ``laura.`` keys, which the
import reads back.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from warnings import warn

import numpy as np
import yaml

from ....exporters.yaml_exporter import export_as_yaml
from ....importers.yaml_loader import interpret_yaml_element
from ....models.element import ELEMENT_REGISTRY
from ....models.element_list import _s_start_of
from ....models.physical import Position, Rotation
from ...utils.pals import (
    LAURA_TYPE_EXTENSION,
    PALS_TWISS_COMPONENTS,
    PalsBranch,
    PalsDocument,
    PalsElement,
    PalsLattice,
    laura_type_to_pals_kind,
    pals_element_body,
)
from ..converter import translate_elements
from ..section import _s_bounds
from .pals import PalsLatticeImporter

#: NARAD kind -> (the PALS kind standing for it, the LAURA type that kind alone
#: would not recover).
_KINDS = {
    "NormalConductingRFCavity": ("RFCavity", None),
    "SuperConductingRFCavity": ("RFCavity", None),
    "BeamPositionMonitor": ("Instrument", "Beam_Position_Monitor"),
    "BeamProfileMonitor": ("Instrument", "Screen"),
    "RadiationMonitor": ("Instrument", None),
    "DiagnosticDevice": ("Instrument", None),
    "Aperture": ("Mask", "Aperture"),
}

#: ``native_types`` entries that pin the LAURA type more closely than the kind.
_NATIVE_TYPES = {
    "FaradayCup": ("Instrument", "Faraday_Cup_Monitor"),
    "RFDF": ("CrabCavity", "RFDeflectingCavity"),
}

_PLANES = {"Horizontal": "Horizontal_Corrector", "Vertical": "Vertical_Corrector"}

#: SupportingFacilityComponent ``native_types`` LAURA has a type for. PALS has
#: no kind for them, so they travel as the ``Marker`` LAURA's writer uses.
_SUPPORT_TYPES = {
    "BeamlineValve": "Valve",
    "FastValve": "Valve",
    "ManualValve": "Valve",
    "ColdCathode": "VacuumGauge",
    "QuattroGauge": "VacuumGauge",
}

#: Group carrying what NARAD has and PALS does not, read back by the importer.
_NARAD_GROUP = "NaradP"

#: Prefix of the ``additional_metadata`` keys holding what NARAD has no slot for.
_EXTRA = "laura."

#: NARAD signal role -> the binding predicate that names it.
_PREDICATES = {
    "Setpoint": "HasSetpointSignal",
    "Readback": "HasReadbackSignal",
    "Command": "HasCommandSignal",
    "MinimumLimit": "HasLimitSignal",
    "MaximumLimit": "HasLimitSignal",
    "RangeLimit": "HasLimitSignal",
}

_DATA_TYPES = {"String": str, "Integer": int, "Boolean": bool, "FloatArray": list}

#: Groups whose keys are already PALS's.
_PALS_GROUPS = (
    "BendP",
    "SolenoidP",
    "RFP",
    "BodyShiftP",
    "ApertureP",
    "TwissP",
    "MetaP",
)


def _name(identifier: str) -> str:
    """``inst:MQWK202`` -> ``MQWK202``."""
    return identifier.split(":", 1)[-1]


def _metadata(data: Dict[str, Any], prefix: str = _EXTRA) -> List[Dict[str, Any]]:
    """A nested mapping as ``additional_metadata``, one dotted key per leaf.

    A string is written as itself, anything else as JSON, which :func:`_extras`
    tells apart by the ``String`` datatype.
    ponytail: a key with a dot in it comes back split; escape them if one appears.
    """
    entries: List[Dict[str, Any]] = []
    for key, value in data.items():
        if isinstance(value, dict) and value:
            entries += _metadata(value, f"{prefix}{key}.")
            continue
        value = getattr(value, "value", value)  # an enum member
        entry = {"key": f"{prefix}{key}"}
        if isinstance(value, str):
            entry.update(value=value, datatype="String")
        else:
            entry["value"] = json.dumps(value, default=lambda v: v.tolist())
            datatype = {bool: "Boolean", int: "Integer", float: "Float"}.get(
                type(value)
            )
            if isinstance(value, (list, tuple)) and all(
                isinstance(item, (int, float)) for item in value
            ):
                datatype = "FloatArray"
            if datatype:
                entry["datatype"] = datatype
        entries.append(entry)
    return entries


def _extras(group: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """The ``laura.`` entries of a ``MetaP`` group, nested back up."""
    nested: Dict[str, Any] = {}
    for entry in (group or {}).get("additional_metadata") or []:
        key = str(entry.get("key", ""))
        if not key.startswith(_EXTRA):
            continue
        value = entry["value"]
        if entry.get("datatype") != "String":
            value = json.loads(value)
        *parents, leaf = key[len(_EXTRA) :].split(".")
        node = nested
        for parent in parents:
            node = node.setdefault(parent, {})
        node[leaf] = value
    return nested


def _merged(base: Dict[str, Any], over: Dict[str, Any]) -> Dict[str, Any]:
    """``base`` updated by ``over``, mapping by mapping."""
    merged = dict(base)
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            value = _merged(merged[key], value)
        merged[key] = value
    return merged


def _multipole_group(group: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten ``mag_components`` into PALS's ``Kn1``/``Ks1``/``tilt1`` keys."""
    flat: Dict[str, Any] = {}
    for component in group.get("mag_components") or []:
        order = component.get("order")
        for key in ("Kn", "Ks", "Bn", "Bs", "tilt"):
            if component.get(key) is not None:
                flat[f"{key}{order}"] = component[key]
    return flat


def _beamline_order(
    beamline_id: str, relations: List[Dict[str, Any]], components: Dict[str, Any]
) -> List[str]:
    """Component ids of one beamline, upstream first, from its ``Precedes`` chain.

    A single linear chain per beamline; a fork (one subject preceding
    two objects) or a ring raises rather than guessing.
    """
    chain = [
        relation
        for relation in relations
        if relation.get("predicate") == "Precedes"
        and relation.get("beamline_context") == beamline_id
    ]
    if not chain:
        return list(components)
    following = {relation["subject"]: relation["object"] for relation in chain}
    heads = set(following) - set(following.values())
    if len(following) != len(chain) or len(heads) != 1:
        raise ValueError(
            f"NARAD beamline {beamline_id!r} is not a single linear Precedes "
            "chain; forks and rings are not supported yet."
        )
    order = [heads.pop()]
    while order[-1] in following:
        order.append(following[order[-1]])
    return order


def _variable(signal: Dict[str, Any]) -> Dict[str, Any]:
    """A NARAD ``Signal`` as a LAURA control variable."""
    data_type = signal.get("native_data_type")
    role = signal.get("signal_role")
    variable = {
        "identifier": _name(signal["id"]),
        "protocol": signal.get("source_system", ""),
        "units": signal.get("native_unit"),
        "description": signal.get("native_description"),
        "read_only": role not in ("Setpoint", "Command"),
        "dtype": _DATA_TYPES.get(data_type, float),
        "control_type": "string" if data_type == "String" else "scalar",
        "role": role,
        "canonical_type": signal.get("canonical_signal_type"),
        "quantity_kind": signal.get("quantity_kind"),
        "access_protocol": signal.get("access_protocol"),
    }
    variable.update(_extras(signal.get("MetaP")))
    if "type" in variable:  # LAURA's own word for it, from the export
        variable["control_type"] = variable.pop("type")
    return {key: value for key, value in variable.items() if value is not None}


def _controls(facility: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Component id -> its signals as control variables, keyed by signal alias."""
    signals = {signal["id"]: signal for signal in facility.get("signals") or []}
    controls: Dict[str, Dict[str, Any]] = {}
    for binding in facility.get("signal_bindings") or []:
        signal = signals.get(binding.get("object"))
        if signal is None:
            continue
        key = (signal.get("alias") or [_name(signal["id"])])[0]
        controls.setdefault(binding["subject"], {})[key] = _variable(signal)
    return controls


def _element(
    component: Dict[str, Any],
    previous_exit: float,
    pc_ref_scale: float,
    s_position_at: str,
    controls: Optional[Dict[str, Any]] = None,
    floor_angle_scale: float = 1.0,
) -> Optional[PalsElement]:
    """One NARAD component as the PALS element the importer reads."""
    kind, hardware_type, hardware_class = component["kind"], None, None
    laura = _extras(component.get("MetaP"))
    stated = laura.get("hardware_type")
    stated_class = laura.get("hardware_class")
    if kind == "SupportingFacilityComponent":
        native = component.get("native_types") or []
        hardware_type = next(
            (_SUPPORT_TYPES[n] for n in native if n in _SUPPORT_TYPES), None
        )
        if hardware_type is None:
            # no LAURA class: a generic element named by its native type
            hardware_type = next(
                (n for n in native if n not in ("Drift", "Marker")), None
            )
            hardware_class = "Generic"  # LAURA's classes are a closed enum
        if hardware_type is None and not stated:
            return None
        kind = "Marker"
    if kind in _KINDS:
        kind, hardware_type = _KINDS[kind]
    for native in component.get("native_types") or []:
        if native in _NATIVE_TYPES:
            kind, hardware_type = _NATIVE_TYPES[native]
    if kind == "Kicker":
        hardware_type = _PLANES.get(component.get("plane"))
    if stated and kind != "BeginningEle":  # LAURA wrote it, naming the type outright
        kind = laura_type_to_pals_kind(stated) or "Marker"  # a stand-in kind
        hardware_type, hardware_class = stated, stated_class

    name = _name(component["id"])
    # NARAD gives a Marker no placement, so LAURA's export keeps it as an extra
    placement = component.get("LongitudinalPlacementP") or laura.pop(
        "LongitudinalPlacementP", None
    )
    if placement is None and kind != "BeginningEle":
        warn(
            f"NARAD component {name!r} has no LongitudinalPlacementP; it was "
            "placed, zero length, at the exit of the component before it."
        )
        placement = {"length": 0.0, "s_position": previous_exit}
        s_position_at = "exit"
    length = float(placement.get("length") or 0.0)
    s_position = float(placement.get("s_position") or 0.0)
    if s_position_at == "exit":
        s_position -= length

    parameters: Dict[str, Any] = {"length": length, "s_position": s_position}
    for group in _PALS_GROUPS:
        if group in component:
            parameters[group] = component[group]
    if "MagneticMultipoleP" in component:
        parameters["MagneticMultipoleP"] = _multipole_group(
            component["MagneticMultipoleP"]
        )
    if "ReferenceP" in component:
        reference = dict(component["ReferenceP"])
        if reference.get("pc_ref") is not None:
            reference["pc_ref"] = float(reference["pc_ref"]) * pc_ref_scale
        parameters["ReferenceP"] = reference
    # LAURA's export marks a FloorP it computed, which places the element
    # rather than surveys it
    computed = laura.pop("FloorP", None) == "computed"
    floor = None
    if "FloorP" in component:
        floor = dict(component["FloorP"])
        for angle in ("theta", "phi", "psi"):
            if floor.get(angle) is not None:
                floor[angle] = float(floor[angle]) * floor_angle_scale
        if not computed:
            parameters["FloorP"] = dict(floor, user_set=True)  # facility data

    if hardware_type:
        parameters[LAURA_TYPE_EXTENSION] = {"hardware_type": hardware_type}
    if hardware_class:
        parameters[LAURA_TYPE_EXTENSION]["hardware_class"] = hardware_class
    narad = {
        "controls": controls,
        "off_beamline": component.get("beamline_relation")
        in ("AttachedToPipe", "AssociatedWithBeamLine"),
        "laura": laura,
        "floor": dict(floor, face=s_position_at) if computed and floor else None,
    }
    parameters[_NARAD_GROUP] = {key: value for key, value in narad.items() if value}
    return PalsElement(name=name, kind=kind, parameters=parameters)


def narad_document(
    source: Union[str, Path, Dict[str, Any]],
    pc_ref_scale: float = 1.0,
    s_position_at: Literal["entrance", "exit"] = "entrance",
    floor_angle_scale: float = 1.0,
) -> PalsDocument:
    """Rewrite a NARAD instance (a path, or the loaded mapping) as a PALS document."""
    if isinstance(source, dict):
        instance, path = source, Path("narad")
    else:
        path = Path(source).expanduser().resolve()
        instance = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.CSafeLoader)
    facility = instance.get("facility", instance)
    components = {
        component["id"]: component for component in facility.get("components") or []
    }
    relations = facility.get("component_relations") or []
    controls = _controls(facility)

    lattice = PalsLattice(name=path.name.split(".")[0])
    skipped: List[str] = []
    for beamline in facility.get("beamlines") or []:
        branch = PalsBranch(name=_name(beamline["id"]))
        previous_exit = 0.0
        for identifier in _beamline_order(beamline["id"], relations, components):
            element = _element(
                components[identifier],
                previous_exit,
                pc_ref_scale,
                s_position_at,
                controls.get(identifier),
                floor_angle_scale,
            )
            if element is None:
                skipped.append(_name(identifier))
                continue
            previous_exit = element.s_end
            branch.elements.append(element)
        start = next((e for e in branch.elements if e.group("ReferenceP")), None)
        if start is not None and start.kind != "BeginningEle":
            beginning = {
                "s_position": start.s_start,
                "ReferenceP": start.group("ReferenceP"),
            }
            if start.group("TwissP"):
                beginning["TwissP"] = start.group("TwissP")
            branch.elements.insert(
                0, PalsElement(f"{branch.name}_begin", "BeginningEle", beginning)
            )
        lattice.branches.append(branch)
    if skipped:
        warn(
            f"{len(skipped)} NARAD SupportingFacilityComponents have no native "
            f"type to name a LAURA element by and were skipped: {', '.join(skipped)}"
        )
    return PalsDocument(source=path, lattices=[lattice])


class NaradLatticeImporter(PalsLatticeImporter):
    """Read a ``*.narad.yaml`` instance into LAURA elements, sections and layouts."""

    pc_ref_scale: float = 1.0
    """eV per unit of the instance's ``pc_ref``. PALS states eV; NARAD states no
    unit."""

    s_position_at: Literal["entrance", "exit"] = "entrance"
    """Which face ``s_position`` marks. PALS says the entrance; NARAD does not say."""

    floor_angle_scale: float = 1.0
    """Radians per unit of the instance's ``FloorP`` angles. PALS states radians.
    ``FloorP`` is kept as ``physical.survey``, as given,
    at whichever face the instance puts it; one LAURA computed places the element."""

    def create_laura_element_dictionary(
        self, branch: Optional[str] = None
    ) -> Dict[str, Any]:
        elements = super().create_laura_element_dictionary(branch)
        inline = [
            element.physical
            for element in elements.values()
            if not element.is_subelement()
            and getattr(element, "physical", None) is not None
        ]
        if any(physical.middle is None for physical in inline):
            # a section cannot be placed partly by FloorP, so s places all of it
            for physical in inline:
                physical.middle = None
                physical.global_rotation = Rotation(theta=0.0, phi=0.0, psi=0.0)
        return elements

    def _document(self) -> PalsDocument:
        if self.document is None:
            if not self.source_file:
                raise ValueError(
                    "NaradLatticeImporter needs either source_file or document."
                )
            self.document = narad_document(
                self.source_file,
                self.pc_ref_scale,
                self.s_position_at,
                self.floor_angle_scale,
            )
        return self.document

    def _convert(
        self, numbered_name: str, element: PalsElement, switch: Dict[str, str]
    ):
        converted = super()._convert(numbered_name, element, switch)
        if converted is None:
            return None
        alias = element.group("MetaP").get("alias")
        if alias:
            converted.alias = list(alias)
        narad = element.group(_NARAD_GROUP)
        if narad.get("controls"):
            # a mapping, so each type validates it into its own controls class
            converted.controls = {"variables": narad["controls"]}
        if narad.get("off_beamline"):
            # positioned, but out of the section order and drift generation
            converted.subelement = True
            # no section resolves a loose one, and dumps drop s_point
            physical = converted.physical
            physical.s, physical.s_point = physical.s - physical.length / 2, "middle"
        laura = narad.get("laura")
        if laura:  # LAURA's own record; NARAD adds only what the export left out
            dump = export_as_yaml(None, converted)
            placed = {
                key: dump[key] for key in _SLOTTED + ("subelement",) if key in dump
            }
            if "physical" in dump:
                placed["physical"] = {
                    key: value
                    for key, value in dump["physical"].items()
                    if key in _POSITION_FIELDS
                }
                # which face s marks, which dumps leave out
                placed["physical"]["s_point"] = converted.physical.s_point
            merged = interpret_yaml_element(_merged(laura, placed))
            if merged is None:
                warn(
                    f"LAURA's own fields for {numbered_name!r} did not load and were "
                    "dropped; it was read from its NARAD groups alone."
                )
            converted = merged or converted
        floor = narad.get("floor")
        if floor:  # LAURA computed it, so it is where the element actually is
            physical = converted.physical
            face = "end" if floor["face"] == "exit" else "start"
            # undo the export's mirror of LAURA's floor x and psi
            theta = floor["theta"] + (
                physical._physical_angle if face == "end" else 0.0
            )
            own = physical.rotation
            physical.global_rotation = Rotation(
                theta=theta - own.theta,
                phi=floor["phi"] - own.phi,
                psi=-floor["psi"] - own.psi,
            )
            at_face = np.array([-floor["x"], floor["y"], floor["z"]])
            physical.middle = Position.from_list(
                list(at_face - physical.offset_from_middle(face))
            )
        return converted


# LAURA type -> the NARAD kind naming it more closely than its PALS kind does.
_TYPE_KINDS = {
    laura_type: kind for kind, (_, laura_type) in _KINDS.items() if laura_type
}
_TYPE_KINDS.update(
    {
        laura_type: "SupportingFacilityComponent"
        for laura_type in _SUPPORT_TYPES.values()
    }
)

# PALS kind -> NARAD kind, where NARAD names it differently.
# Every cavity is written normal conducting; LAURA does not say which.
_PALS_KINDS = {
    "Instrument": "DiagnosticDevice",
    "Mask": "Aperture",
    "RFCavity": "NormalConductingRFCavity",
}

# NARAD's virtual kinds, and the function each has to state.
_FUNCTIONS = {"Marker": "Mark", "BeginningEle": "Mark", "Drift": "DriftSpace"}

# Groups the PALS kind has and the NARAD kind does not.
_MISSING_GROUPS = {
    "Marker": {"LongitudinalPlacementP"},
    "BeginningEle": {"LongitudinalPlacementP"},
    "Drift": {"BodyShiftP"},
    "DiagnosticDevice": {"BodyShiftP"},
    "Aperture": {"BodyShiftP"},
    "CrabCavity": {"RFP"},
}

# PALS groups NARAD has, as the writer gives them.
_EXPORTED_GROUPS = ("BendP", "SolenoidP", "RFP", "BodyShiftP")

# Element fields NARAD's own slots carry.
_SLOTTED = ("name", "alias", "controls")

# ``physical`` fields saying where the element is, which NARAD's placement
# and ``FloorP`` say instead.
_POSITION_FIELDS = (
    "middle",
    "position",
    "centre",
    "s",
    "s_point",
    "survey",
    "global_rotation",
    "reference_placement",
)

# Control variable field -> the NARAD ``Signal`` slot holding it.
_SIGNAL_SLOTS = {
    "protocol": "source_system",
    "units": "native_unit",
    "description": "native_description",
    "canonical_type": "canonical_signal_type",
    "quantity_kind": "quantity_kind",
    "access_protocol": "access_protocol",
}

_NARAD_DATA_TYPES = {
    "float": "Float",
    "int": "Integer",
    "str": "String",
    "bool": "Boolean",
    "list": "FloatArray",
}

# ``Signal`` slots NARAD requires that LAURA may not know.
_REQUIRED_SIGNAL_SLOTS = ("canonical_signal_type", "quantity_kind", "native_unit")


def _s_start(element: Any) -> float:
    """Arc-length at an element's entrance."""
    physical = element.physical
    if physical.s is None:
        return _s_bounds(element)[0]
    return _s_start_of(physical)


def _floor(
    element: Any, face: str, floor_angle_scale: float
) -> Tuple[Optional[Dict[str, Any]], bool]:
    """``FloorP`` at one face, and whether LAURA computed it: the survey if the
    element has one, else LAURA's own.

    ``None`` for an element LAURA has not placed in space (a loose subelement).
    """
    physical = element.physical
    survey = physical.survey
    if survey is not None and not any(
        (
            *survey.position,
            *(survey.rotation.theta, survey.rotation.phi, survey.rotation.psi),
        )
    ):
        survey = None  # LAURA fills one in, all zeros, where nothing was surveyed
    if survey is None and physical.middle is None:
        return None, False
    if survey is not None:
        x, y, z = survey.position
        rotation = survey.rotation
        theta, phi, psi = rotation.theta, rotation.phi, rotation.psi
    else:
        # LAURA's floor x points the opposite way to PALS's, so x and psi flip.
        x, y, z = physical.start if face == "entrance" else physical.end
        x = -x
        theta = physical.rotation.theta + physical.global_rotation.theta
        if face == "exit":
            theta -= physical._physical_angle
        phi = physical.rotation.phi + physical.global_rotation.phi
        psi = -(physical.rotation.psi + physical.global_rotation.psi)
    floor = {"x": x, "y": y, "z": z}
    for key, angle in (("theta", theta), ("phi", phi), ("psi", psi)):
        floor[key] = angle / floor_angle_scale
    # + 0.0 so a mirrored zero is written 0.0, not -0.0
    return {key: float(value) + 0.0 for key, value in floor.items()}, survey is None


def _mag_components(group: Dict[str, Any], length: float) -> List[Dict[str, Any]]:
    """The writer's ``Kn1L``/``Ks1L``/``tilt1`` keys as NARAD's per-metre ``mag_components``."""
    components: Dict[int, Dict[str, Any]] = {}
    for key, value in group.items():
        if key.startswith("tilt"):
            order, slot = int(key[4:]), "tilt"
        else:
            order, slot = int(key[2:-1]), key[:2]
            value = value / length
        components.setdefault(order, {"order": order})[slot] = value
    return [components[order] for order in sorted(components)]


def _component(
    element: Any,
    translator: Any,
    s_position_at: str,
    floor_angle_scale: float,
    warned: set,
    off_line: bool,
) -> Dict[str, Any]:
    """One LAURA element as a NARAD component; ``off_line`` if not in the line itself."""
    name, hardware_type = element.name, element.hardware_type
    hardware_class = getattr(element.hardware_class, "value", element.hardware_class)
    body = pals_element_body(translator)
    kind = _TYPE_KINDS.get(hardware_type)
    if kind is None and (
        hardware_class == "Vacuum" or hardware_type not in ELEMENT_REGISTRY
    ):
        kind = "SupportingFacilityComponent"
    kind = kind or _PALS_KINDS.get(body["kind"], body["kind"])

    component: Dict[str, Any] = {"id": f"inst:{name}", "kind": kind}
    if kind in _FUNCTIONS:
        component["functions"] = [_FUNCTIONS[kind]]
        component["beamline_relation"] = (
            "AssociatedWithBeamLine" if off_line else "Inline"
        )
    else:
        component["beamline_relation"] = "AttachedToPipe" if off_line else "Inline"
    if kind == "SupportingFacilityComponent":
        component["facility_functions"] = ["Support"]
    if kind == "Kicker" and hardware_type in _PLANES.values():
        component["plane"] = hardware_type.split("_")[0]

    length = float(element.physical.length or 0.0)
    start = _s_start(element)
    placement = {
        "length": length,
        "s_position": start if s_position_at == "entrance" else start + length,
    }
    dump = export_as_yaml(None, element)
    extras = {key: value for key, value in dump.items() if key not in _SLOTTED}
    extras["hardware_class"] = hardware_class  # a default the dump leaves out
    controls = {
        key: value
        for key, value in dump.get("controls", {}).items()
        if key not in ("variables", "schema")
    }
    if controls:
        extras["controls"] = controls
    physical = {
        key: value
        for key, value in extras.pop("physical", {}).items()
        if key not in _POSITION_FIELDS
    }
    if physical:
        extras["physical"] = physical
    groups: Dict[str, Any] = {"LongitudinalPlacementP": placement}
    for group in _EXPORTED_GROUPS:
        if body.get(group):
            groups[group] = dict(body[group])
    groups.get("RFP", {}).pop("gradient", None)  # NARAD's RFP has none
    multipoles = body.get("MagneticMultipoleP")
    if multipoles and length:
        groups["MagneticMultipoleP"] = {
            "mag_components": _mag_components(multipoles, length)
        }
    elif multipoles and "thin" not in warned:
        warned.add("thin")
        warn(
            "NARAD states multipole strengths per metre, so a zero-length "
            f"element's (such as {name!r}) are kept only in its MetaP."
        )
    for group, value in groups.items():
        if group in _MISSING_GROUPS.get(kind, ()):
            extras[group] = value  # the import reads it back from there
        else:
            component[group] = {"id": f"inst:{name}/{group}", **value}
    floor, computed = _floor(element, s_position_at, floor_angle_scale)
    if floor is not None:
        component["FloorP"] = {"id": f"inst:{name}/FloorP", **floor}
    if computed:  # so the import does not take it for a survey
        extras["FloorP"] = "computed"
    meta: Dict[str, Any] = {"id": f"inst:{name}/MetaP"}
    if element.alias:
        meta["alias"] = list(element.alias)
    meta["additional_metadata"] = _metadata(extras)
    component["MetaP"] = meta
    return component


def _beginning(
    seed: Any, section: Any, particle: Optional[str], floor_angle_scale: float
) -> Dict[str, Any]:
    """A section's leading ``TwissMatch`` as the ``BeginningEle`` setting its reference."""
    name = seed.name
    reference = {"species_ref": particle, "E_tot_ref": section.reference_energy}
    twiss = {
        pals_key: getattr(seed.simulation, laura_key, None)
        for pals_key, laura_key in PALS_TWISS_COMPONENTS.items()
    }
    extras = {
        key: value
        for key, value in export_as_yaml(None, seed).items()
        if key not in _SLOTTED and key != "physical"
    }
    extras["LongitudinalPlacementP"] = {"length": 0.0, "s_position": _s_start(seed)}
    component: Dict[str, Any] = {
        "id": f"inst:{name}",
        "kind": "BeginningEle",
        "functions": ["Mark"],
        "beamline_relation": "Inline",
    }
    for group, values in (("ReferenceP", reference), ("TwissP", twiss)):
        values = {key: value for key, value in values.items() if value is not None}
        if values:
            component[group] = {"id": f"inst:{name}/{group}", **values}
    floor, computed = _floor(seed, "entrance", floor_angle_scale)
    if floor is not None:
        component["FloorP"] = {"id": f"inst:{name}/FloorP", **floor}
    if computed:
        extras["FloorP"] = "computed"
    component["MetaP"] = {
        "id": f"inst:{name}/MetaP",
        "additional_metadata": _metadata(extras),
    }
    return component


def _signals(element: Any, missing: set) -> tuple:
    """An element's control variables as NARAD signals and their bindings."""
    signals, bindings = [], []
    controls = getattr(element, "controls", None)
    for key, variable in (controls.variables if controls else {}).items():
        data = variable.model_dump()
        identifier = data.pop("identifier", None) or f"{element.name}.{key}"
        role = data.pop("role", None) or (
            "Readback" if variable.read_only else "Setpoint"
        )
        data.pop("read_only", None)  # the role says it
        signal: Dict[str, Any] = {
            "id": f"inst:{identifier}",
            "kind": "Signal",
            "signal_role": role,
        }
        for field, slot in _SIGNAL_SLOTS.items():
            if data.get(field) is not None:
                signal[slot] = data.pop(field)
        dtype = data.pop("dtype", "float")
        data_type = _NARAD_DATA_TYPES.get(dtype)
        if data.get("type") == "waveform":
            data_type = "FloatArray"
        if data_type is None:
            data["dtype"] = dtype
        else:
            signal["native_data_type"] = data_type
        missing.update(slot for slot in _REQUIRED_SIGNAL_SLOTS if slot not in signal)
        signal["alias"] = [key]
        data = {field: value for field, value in data.items() if value is not None}
        if data:
            signal["MetaP"] = {
                "id": f"inst:{identifier}/MetaP",
                "additional_metadata": _metadata(data),
            }
        signals.append(signal)
        bindings.append(
            {
                "id": f"inst:{element.name}_{key}",
                "subject": f"inst:{element.name}",
                "predicate": _PREDICATES.get(role, "HasReadbackSignal"),
                "object": signal["id"],
            }
        )
    return signals, bindings


def _section_members(machine: Any) -> Dict[str, List[Any]]:
    """Section name -> its elements in s order, with the loose subelements.

    A subelement no section holds goes to the first section whose s range
    contains it.
    ponytail: s restarts on each lattice, so with several lattices a loose
    subelement can land on the wrong one; place them by parent or floor
    position if that bites.
    """
    rank = {name: index for index, name in enumerate(machine.elements)}
    members = {
        name: list(section.elements.elements.values())
        for name, section in machine.sections.items()
    }
    held = {element.name for elements in members.values() for element in elements}
    loose = [
        element
        for element in machine.elements.values()
        if element.name not in held
        and getattr(element, "physical", None) is not None
        and element.is_subelement()
    ]
    ranges = {
        name: (
            min(_s_start(element) for element in elements),
            max(_s_start(element) + element.physical.length for element in elements),
        )
        for name, elements in members.items()
        if elements
    }
    skipped = len(machine.elements) - len(held)
    for element in loose:
        start = _s_start(element)
        section = next(
            (name for name, (low, high) in ranges.items() if low <= start <= high),
            None,
        )
        if section is not None:
            members[section].append(element)
            skipped -= 1
    if skipped:
        warn(f"{skipped} elements in no section were not written to NARAD.")
    return {
        name: sorted(
            elements,
            key=lambda element: (
                round(_s_start(element), 9),
                rank.get(element.name, 0),
            ),
        )
        for name, elements in members.items()
    }


def narad_instance(
    machine: Any,
    s_position_at: Literal["entrance", "exit"] = "entrance",
    floor_angle_scale: float = 1.0,
) -> Dict[str, Any]:
    """
    Write a LAURA machine as a NARAD instance, one beamline per section.

    Parameters
    ----------
    machine: MachineModel
        The machine to write.
    s_position_at: str
        Which face ``s_position`` and ``FloorP`` mark (see
        :class:`NaradLatticeImporter`).
    floor_angle_scale: float
        Radians per unit of the written ``FloorP`` angles.

    Returns
    -------
    dict
        The instance, ready for ``yaml.dump``. What NARAD has no slot for is in
        each ``MetaP.additional_metadata`` under ``laura.`` keys, so
        :class:`NaradLatticeImporter` reads the machine back.
    """
    components: Dict[str, Dict[str, Any]] = {}
    beamlines, signals, bindings, relations = [], {}, [], []
    warned: set = set()
    missing: set = set()
    unphysical = 0
    for section_name, members in _section_members(machine).items():
        section = machine.sections[section_name]
        beamline = f"inst:{section_name}"
        beamlines.append(
            {
                "id": beamline,
                "kind": "BeamLine",
                "functions": ["BeamLineSection"],
                "beamline_relation": "Inline",
            }
        )
        ordered = section._get_all_elements()
        seed = (
            ordered[0] if ordered and ordered[0].hardware_type == "TwissMatch" else None
        )
        physical = [
            element
            for element in members
            if element is not seed and getattr(element, "physical", None) is not None
        ]
        unphysical += len(members) - len(physical) - (seed is not None)
        translators = translate_elements(
            physical, master_lattice=section.master_lattice
        )
        line = []
        if seed is not None:
            components.setdefault(
                seed.name,
                _beginning(seed, section, machine.particle, floor_angle_scale),
            )
            line.append(seed.name)
        line_end = None
        for element in physical:
            # as the PALS writer superimposes: the import would push an overlap along
            start = _s_start(element)
            off_line = element.is_subelement() or (
                line_end is not None and start < line_end - 1e-12
            )
            if not off_line:
                line_end = start + element.physical.length
            if element.name not in components:
                components[element.name] = _component(
                    element,
                    translators[element.name],
                    s_position_at,
                    floor_angle_scale,
                    warned,
                    off_line,
                )
                element_signals, element_bindings = _signals(element, missing)
                signals.update((signal["id"], signal) for signal in element_signals)
                bindings += element_bindings
            line.append(element.name)
        for upstream, downstream in zip(line, line[1:]):
            relations.append(
                {
                    "id": f"inst:{upstream}_to_{downstream}",
                    "subject": f"inst:{upstream}",
                    "predicate": "Precedes",
                    "object": f"inst:{downstream}",
                    "context": "beamline_order",
                    "beamline_context": beamline,
                }
            )
    if unphysical:
        warn(f"{unphysical} elements with no physical placement were not written.")
    if missing:
        warn(
            "Some signals lack slots NARAD requires, which LAURA does not know: "
            f"{', '.join(sorted(missing))}. They were left out, not guessed."
        )
    return {
        "description": "A NARAD instance written by LAURA.",
        "kind": "PALSAccelerator",
        "version": None,
        "facility": {
            "components": list(components.values()),
            "beamlines": beamlines,
            "signals": list(signals.values()),
            "signal_bindings": bindings,
            "component_relations": relations,
        },
    }
