"""Tests for the NARAD importer (``NaradLatticeImporter``).

The instance is built inline, in the shape of the UITF one, so these run
without the PALS parser: a NARAD instance is already expanded.
"""

import math
import warnings

import pytest
from scipy.constants import physical_constants, speed_of_light

from laura.translator.converters.codes.narad import (
    NaradLatticeImporter,
    narad_document,
    narad_instance,
)

_REFERENCE = {"pc_ref": 0.465144443755972, "species_ref": "electron"}


def _component(name, kind, s, length=0.0, **groups):
    return {
        "id": f"{name}",
        "kind": kind,
        "native_types": groups.pop("native_types", []),
        "LongitudinalPlacementP": {"length": length, "s_position": s},
        "ReferenceP": dict(_REFERENCE),
        "MetaP": groups.pop("MetaP", {"additional_metadata": []}),
        **groups,
    }


def _instance(components, order=None):
    order = order or [c["id"] for c in components]
    return {
        "kind": "PALSAccelerator",
        "facility": {
            "components": components,
            "beamlines": [{"id": "LINE", "kind": "BeamLine"}],
            "component_relations": [
                {
                    "subject": a,
                    "predicate": "Precedes",
                    "object": b,
                    "beamline_context": "LINE",
                }
                for a, b in zip(order, order[1:])
            ],
            "signals": _SIGNALS,
            "signal_bindings": [
                {
                    "subject": "BEND",
                    "predicate": "HasSetpointSignal",
                    "object": s["id"],
                }
                for s in _SIGNALS
            ],
        },
    }


_SIGNALS = [
    {
        "id": "MBEND.S",
        "signal_role": "Setpoint",
        "source_system": "EPICS",
        "native_description": "current setpoint",
        "native_data_type": "Float",
        "native_unit": "A",
        "alias": ["current_setpoint"],
    },
    {
        "id": "MBEND.STAT",
        "signal_role": "Readback",
        "source_system": "EPICS",
        "access_protocol": "EPICS Channel Access",
        "native_data_type": "String",
        "native_unit": "none",
        "alias": ["status"],
    },
]


_UITF_LIKE = [
    # listed out of beam order: the Precedes chain, not the list, decides
    _component("SOL", "Solenoid", 0.5, 0.1, SolenoidP={"Ksol": -10.0}),
    _component(
        "GUN",
        "NormalConductingRFCavity",
        0.0,
        TwissP={"beta_a": 0.2, "beta_b": 0.3, "alpha_a": -2.0, "alpha_b": 1.5},
    ),
    _component("HK", "Kicker", 0.6, plane="Horizontal"),
    _component("VK", "Kicker", 0.6, plane="Vertical"),
    _component("BPM", "BeamPositionMonitor", 0.6),
    _component(
        "FC", "BeamProfileMonitor", 0.7, native_types=["DiagnosticDevice", "FaradayCup"]
    ),
    _component("BLM", "RadiationMonitor", 0.7),
    _component(
        "PUMP",
        "SupportingFacilityComponent",
        0.8,
        native_types=["Drift", "UHVPump"],
        beamline_relation="AttachedToPipe",
    ),
    _component("ODD", "SupportingFacilityComponent", 0.8),  # no native type
    _component(
        "VALVE",
        "SupportingFacilityComponent",
        0.8,
        native_types=["Drift", "BeamlineValve"],
        beamline_relation="AttachedToPipe",
    ),
    _component(
        "BEND",
        "Bend",
        1.0,
        0.2,
        BendP={"angle_ref": -0.26, "e1": -0.13, "e2": -0.13},
        MagneticMultipoleP={"mag_components": [{"order": 1, "Kn": -5.0}]},
        MetaP={"alias": ["15 Deg Bend"], "additional_metadata": []},
        FloorP={
            "x": 10.0,
            "y": 21.0,
            "z": 31.0,
            "theta": -15.0,
            "phi": 0.0,
            "psi": 0.0,
        },
    ),
    _component(
        "DEFL", "NormalConductingRFCavity", 1.5, 0.3, native_types=["Drift", "RFDF"]
    ),
    _component("APER", "Aperture", 1.6),
]
_ORDER = [
    f"{n}"
    for n in (
        "GUN",
        "SOL",
        "HK",
        "VK",
        "BPM",
        "FC",
        "BLM",
        "PUMP",
        "ODD",
        "VALVE",
        "BEND",
        "DEFL",
        "APER",
    )
]


@pytest.fixture
def elements():
    with pytest.warns(UserWarning, match="SupportingFacilityComponents"):
        document = narad_document(
            _instance(_UITF_LIKE, _ORDER),
            pc_ref_scale=1e6,
            s_position_at="exit",
            floor_angle_scale=math.pi / 180,
        )
    return NaradLatticeImporter(document=document).create_laura_element_dictionary()


def test_beam_order_follows_the_precedes_chain(elements):
    assert list(elements) == ["LINE_begin"] + [
        n for n in _ORDER if n != "ODD"
    ]


@pytest.mark.parametrize(
    "name, hardware_type",
    [
        ("GUN", "RFCavity"),
        ("HK", "Horizontal_Corrector"),
        ("VK", "Vertical_Corrector"),
        ("BPM", "Beam_Position_Monitor"),
        ("FC", "Faraday_Cup_Monitor"),
        ("BLM", "Diagnostic"),
        ("BEND", "Dipole"),
        ("DEFL", "RFDeflectingCavity"),
        ("APER", "Aperture"),
    ],
)
def test_narad_kinds_become_laura_types(elements, name, hardware_type):
    assert elements[name].hardware_type == hardware_type


def test_pc_ref_scale_feeds_the_solenoid_field(elements):
    momentum = _REFERENCE["pc_ref"] * 1e6
    expected = 10.0 * momentum / speed_of_light * 0.1  # K = qB/P0, q = -e
    assert elements["SOL"].magnetic.fields.S0L == pytest.approx(expected)


def test_exit_face_positions(elements):
    physical = elements["BEND"].physical
    assert (physical.s, physical.s_point, physical.length) == (
        pytest.approx(1.0),
        "end",
        pytest.approx(0.2),
    )


def test_multipole_components_are_integrated(elements):
    assert elements["BEND"].magnetic.multipoles.K1L.normal == pytest.approx(-1.0)
    assert elements["BEND"].magnetic.entrance_edge_angle == pytest.approx(-0.13)


def test_meta_alias_is_kept(elements):
    assert elements["BEND"].alias == ["15 Deg Bend"]


def test_attached_valve_is_positioned_off_the_beamline(elements):
    valve = elements["VALVE"]
    assert (valve.hardware_type, valve.is_subelement()) == ("Valve", True)
    assert valve.physical.s == pytest.approx(0.8)


def test_floor_placement_is_kept_beside_s(elements):
    physical = elements["BEND"].physical
    survey = physical.survey
    assert (survey.position.x, survey.position.y, survey.position.z) == (
        10.0,
        21.0,
        31.0,
    )
    assert survey.rotation.theta == pytest.approx(math.radians(-15.0))
    assert physical.s == pytest.approx(1.0)  # s, not FloorP, still places it


def test_a_pump_without_a_laura_class_is_a_generic_element(elements):
    pump = elements["PUMP"]
    assert type(pump).__name__ == "PhysicalBaseElement"
    assert (pump.hardware_type, pump.hardware_class, pump.is_subelement()) == (
        "UHVPump",
        "Generic",
        True,
    )


def test_signals_become_controls_keyed_by_alias(elements):
    variables = elements["BEND"].controls.variables
    setpoint, status = variables["current_setpoint"], variables["status"]
    assert (setpoint.identifier, setpoint.protocol, setpoint.units) == (
        "MBEND.S",
        "EPICS",
        "A",
    )
    assert (setpoint.read_only, setpoint.dtype) == (False, float)
    assert (status.read_only, status.dtype, status.control_type) == (
        True,
        str,
        "string",
    )
    # the transport, where there is one, rather than the control system
    assert status.protocol == "CA"


def test_first_reference_becomes_the_design_optics(elements):
    twiss = elements["LINE_begin"].simulation
    assert (twiss.beta_x, twiss.beta_y, twiss.alpha_x) == (0.2, 0.3, -2.0)


def test_reference_energy_is_recovered_from_pc_ref():
    importer = NaradLatticeImporter(
        document=narad_document(_instance(_UITF_LIKE[:2], _ORDER[:2]), pc_ref_scale=1e6)
    )
    rest = physical_constants["electron mass energy equivalent in MeV"][0] * 1e6
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        section = importer.create_section()["LINE"]
    # exactly 180 keV kinetic: the check that the UITF pc_ref is MeV/c
    assert section.reference_energy - rest == pytest.approx(180e3, abs=1.0)


def test_missing_placement_sits_at_the_previous_exit():
    monitor = _component("M", "BeamPositionMonitor", 0.0)
    del monitor["LongitudinalPlacementP"]
    instance = _instance([_UITF_LIKE[0], monitor], ["SOL", "M"])
    with pytest.warns(UserWarning, match="no LongitudinalPlacementP"):
        document = narad_document(instance)
    assert document.branch("LINE").elements[-1].s_start == pytest.approx(0.6)


@pytest.mark.parametrize("kind", ["BeginningEle", "Marker"])  # NARAD gives them none
def test_a_bookkeeping_component_needs_no_placement(kind):
    beginning = _component("B", kind, 0.0)
    del beginning["LongitudinalPlacementP"]
    instance = _instance([beginning, _UITF_LIKE[0]], ["B", "SOL"])
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)  # and says nothing about it
        document = narad_document(instance)
    assert document.branch("LINE").elements[0].s_start == 0.0


def test_cebaf_injector_shapes():
    """As CEBAF's INJECTOR writes them: a bare PhysicalComponent, a supply
    off the beamline, and BodyShiftP rotations in degrees."""
    ladder = _component(
        "LADDER", "PhysicalComponent", 0.2, native_types=["Instrument", "TargetLadder"]
    )
    supply = _component(
        "HV",
        "SupportingFacilityComponent",
        0.3,
        native_types=["Drift", "WienHV"],
        beamline_relation="SupportingFacility",
    )
    bpm = _component("BPM", "BeamPositionMonitor", 0.4, BodyShiftP={"z_rot": 45.0})
    instance = _instance([ladder, supply, bpm])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        document = narad_document(instance, floor_angle_scale=math.pi / 180)
        elements = NaradLatticeImporter(
            document=document
        ).create_laura_element_dictionary()
    assert elements["LADDER"].hardware_type == "Diagnostic"
    assert elements["HV"].is_subelement()
    assert elements["BPM"].physical.error.rotation.psi == pytest.approx(math.pi / 4)


def test_a_beamline_of_beamlines_is_the_layout_not_a_section():
    """As UITF writes it: KV and MV are IsPartOf GUN_thru_MV, which repeats
    their Precedes chains."""
    instance = _instance([dict(c) for c in _UITF_LIKE[:3]], ["GUN", "SOL", "HK"])
    facility = instance["facility"]
    chain = facility["component_relations"]
    facility["beamlines"] = [{"id": name, "kind": "BeamLine"} for name in ("LINE", "KV", "MV")]
    # KV is GUN -> SOL, MV is SOL -> HK
    chain += [dict(chain[0], beamline_context="KV"), dict(chain[1], beamline_context="MV")]
    chain += [
        {"subject": part, "predicate": "IsPartOf", "object": "LINE"}
        for part in ("KV", "MV")
    ]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        document = narad_document(instance)
    (lattice,) = document.lattices
    assert lattice.name == "LINE"
    assert [branch.name for branch in lattice.branches] == ["KV", "MV"]


def test_legacy_inst_prefixed_ids_lose_the_prefix():
    """``inst:`` CURIEs, as instances before pals-facility-config wrote them."""
    instance = _instance([dict(_UITF_LIKE[0]), dict(_UITF_LIKE[2])])
    facility = instance["facility"]
    for component in facility["components"]:
        component["id"] = "inst:" + component["id"]
    for relation in facility["component_relations"]:
        relation.update(
            subject="inst:" + relation["subject"],
            object="inst:" + relation["object"],
            beamline_context="inst:LINE",
        )
    facility["beamlines"][0]["id"] = "inst:LINE"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        document = narad_document(instance)
    assert [e.name for e in document.branch("LINE").elements] == [
        "LINE_begin",
        "SOL",
        "HK",
    ]


def test_a_ring_in_the_eic_toy_shape():
    """As the EIC toy ring writes it: ReferenceP on the BeginningEle alone,
    fields as Bn, ``pals:`` CURIE predicates, a periodic beamline, PVAccess."""
    beginning = _component("B", "BeginningEle", 0.0)
    beginning["ReferenceP"] = {"pc_ref": 18e9, "species_ref": "electron"}
    quad = _component(
        "Q",
        "Quadrupole",
        0.5,
        0.5,
        MagneticMultipoleP={"mag_components": [{"order": 1, "Bn": -8.58}]},
    )
    del quad["ReferenceP"]
    instance = _instance([beginning, quad])
    facility = instance["facility"]
    facility["beamlines"][0]["periodic"] = True
    for relation in facility["component_relations"]:
        relation["predicate"] = "pals:precedes"
    facility["components"].reverse()  # so only the chain gives the order
    facility["signals"] = [dict(_SIGNALS[1], access_protocol="EPICS PVAccess")]
    facility["signal_bindings"] = [{"subject": "Q", "object": "MBEND.STAT"}]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        document = narad_document(instance, s_position_at="exit")
        importer = NaradLatticeImporter(document=document)
        quad = importer.create_laura_element_dictionary()["Q"]
        section = importer.create_section()["LINE"]
    names = [e.name for e in document.branch("LINE").elements]
    assert names == ["B", "Q"]
    # K1 = q c Bn / pc, the electron's charge flipping the sign
    assert quad.magnetic.k1l == pytest.approx(8.58 * speed_of_light / 18e9 * 0.5)
    assert getattr(section.geometry, "value", section.geometry) == "closed"
    controls = document.branch("LINE").elements[1].group("NaradP")["controls"]
    assert controls["status"]["protocol"] == "PVA"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        machine = importer.create_machine_model(min_section_length=1)
        written = narad_instance(machine, s_position_at="exit")["facility"]
    assert written["beamlines"][0]["periodic"] is True


def test_a_forked_chain_is_refused():
    instance = _instance(_UITF_LIKE[:3], ["GUN", "SOL"])
    instance["facility"]["component_relations"].append(
        {
            "subject": "GUN",
            "predicate": "Precedes",
            "object": "HK",
            "beamline_context": "LINE",
        }
    )
    with pytest.raises(ValueError, match="single linear"):
        narad_document(instance)
