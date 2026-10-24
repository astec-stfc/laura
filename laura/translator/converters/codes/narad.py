"""
Import a NARAD instance into LAURA.

NARAD components carry PALS parameter groups, so rather than a second set of
group readers this module rewrites a NARAD instance as the
:class:`~laura.translator.utils.pals.PalsDocument` the PALS importer reads and
leaves every conversion to :class:`PalsLatticeImporter`. Only what NARAD does
differently from PALS lives here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from warnings import warn

import yaml

from ....models.control import ControlsInformation
from ...utils.pals import (
    LAURA_TYPE_EXTENSION,
    PalsBranch,
    PalsDocument,
    PalsElement,
    PalsLattice,
)
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
    text = signal.get("native_data_type") == "String"
    variable = {
        "identifier": _name(signal["id"]),
        "protocol": signal.get("source_system", ""),
        "units": signal.get("native_unit"),
        "description": signal.get("native_description"),
        "read_only": signal.get("signal_role") != "Setpoint",
        "dtype": str if text else float,
        "control_type": "string" if text else "scalar",
    }
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
        if hardware_type is None:
            return None
        kind = "Marker"
    if kind in _KINDS:
        kind, hardware_type = _KINDS[kind]
    for native in component.get("native_types") or []:
        if native in _NATIVE_TYPES:
            kind, hardware_type = _NATIVE_TYPES[native]
    if kind == "Kicker":
        hardware_type = _PLANES.get(component.get("plane"))

    name = _name(component["id"])
    placement = component.get("LongitudinalPlacementP")
    if placement is None:
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
    if "FloorP" in component:
        floor = dict(component["FloorP"], user_set=True)  # facility data, not computed
        for angle in ("theta", "phi", "psi"):
            if floor.get(angle) is not None:
                floor[angle] = float(floor[angle]) * floor_angle_scale
        parameters["FloorP"] = floor
    if hardware_type:
        parameters[LAURA_TYPE_EXTENSION] = {"hardware_type": hardware_type}
    if hardware_class:
        parameters[LAURA_TYPE_EXTENSION]["hardware_class"] = hardware_class
    narad = {
        "controls": controls,
        "off_beamline": component.get("beamline_relation") == "AttachedToPipe",
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
        if start is not None:
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
    at whichever face the instance puts it."""

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
            converted.controls = ControlsInformation(variables=narad["controls"])
        if narad.get("off_beamline"):
            # positioned, but out of the section order and drift generation
            converted.subelement = True
        return converted
