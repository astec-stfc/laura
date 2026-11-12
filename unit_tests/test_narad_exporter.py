"""Tests for the NARAD exporter (``narad_instance``), mostly as round trips
through the importer, on the UITF-like instance of ``test_narad_importer``."""

import math
import warnings

import pytest

from laura.exporters.yaml_exporter import export_as_yaml
from laura.translator.converters.codes.narad import (
    NaradLatticeImporter,
    narad_document,
    narad_instance,
)

from .test_narad_importer import _ORDER, _UITF_LIKE, _instance

_UITF = {"s_position_at": "exit", "floor_angle_scale": math.pi / 180}


def _machine(instance, **convention):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        document = narad_document(instance, **convention)
        return NaradLatticeImporter(document=document).create_machine_model(
            min_section_length=1
        )


def _export(machine, **convention):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return narad_instance(machine, **convention)


def _rounded(value):
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, dict):
        return {key: _rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_rounded(item) for item in value]
    return value


@pytest.fixture
def machine():
    return _machine(_instance(_UITF_LIKE, _ORDER), pc_ref_scale=1e6, **_UITF)


@pytest.fixture
def exported(machine):
    return _export(machine, **_UITF)["facility"]


def test_a_narad_instance_comes_back_the_same(machine, exported):
    back = _machine({"facility": exported}, **_UITF)
    assert set(back.elements) == set(machine.elements)
    for name, element in machine.elements.items():
        assert _rounded(export_as_yaml(None, back.elements[name])) == _rounded(
            export_as_yaml(None, element)
        ), name


def test_bindings_and_order_are_kept(exported):
    source = _instance(_UITF_LIKE, _ORDER)["facility"]

    def pairs(facility):
        return {(b["subject"], b["object"]) for b in facility["signal_bindings"]}

    assert pairs(exported) == pairs(source)
    predicates = {b["object"]: b["predicate"] for b in exported["signal_bindings"]}
    # from the signal's role, where the fixture binds it as a setpoint regardless
    assert predicates["inst:MBEND.STAT"] == "HasReadbackSignal"
    line = [relation["subject"] for relation in exported["component_relations"]]
    # the leading TwissMatch is written as the BeginningEle; ODD was never read
    assert line[1:] == [n for n in _ORDER if n != "inst:ODD"][:-1]


def test_components_carry_what_narad_requires(exported):
    for component in exported["components"]:
        assert {"id", "kind", "beamline_relation"} <= set(component)
        for group, value in component.items():
            if group.endswith("P"):
                assert value["id"] == f"{component['id']}/{group}"
    kinds = {c["id"]: c for c in exported["components"]}
    assert kinds["inst:LINE_begin"]["kind"] == "BeginningEle"
    assert kinds["inst:LINE_begin"]["functions"] == ["Mark"]
    assert kinds["inst:HK"]["plane"] == "Horizontal"
    assert kinds["inst:PUMP"]["kind"] == "SupportingFacilityComponent"
    assert kinds["inst:PUMP"]["beamline_relation"] == "AttachedToPipe"
    assert kinds["inst:BEND"]["MagneticMultipoleP"]["mag_components"] == [
        {"order": 1, "Kn": pytest.approx(-5.0)}
    ]


def test_signals_state_role_and_data_type(exported):
    signals = {signal["id"]: signal for signal in exported["signals"]}
    setpoint, status = signals["inst:MBEND.S"], signals["inst:MBEND.STAT"]
    assert (setpoint["signal_role"], setpoint["native_data_type"]) == (
        "Setpoint",
        "Float",
    )
    assert (status["signal_role"], status["native_data_type"]) == (
        "Readback",
        "String",
    )
    assert (status["source_system"], status["access_protocol"]) == (
        "EPICS",
        "EPICS Channel Access",
    )
    assert setpoint["source_system"] == "EPICS"


def test_control_fields_narad_lacks_travel_in_meta(machine):
    machine.elements["BEND"].controls.variables["status"].states = {"OK": 0}
    exported = _export(machine, **_UITF)["facility"]
    status = next(s for s in exported["signals"] if s["id"] == "inst:MBEND.STAT")
    keys = {entry["key"] for entry in status["MetaP"]["additional_metadata"]}
    assert keys == {"laura.type", "laura.states.OK"}
    back = _machine({"facility": exported}, **_UITF)
    variable = back.elements["BEND"].controls.variables["status"]
    assert (variable.states, variable.control_type) == ({"OK": 0}, "string")


@pytest.mark.parametrize("unsurveyed", [None, {}])  # {}: the all-zero default
def test_floor_is_computed_in_pals_frame_without_a_survey(machine, unsurveyed):
    for element in machine.elements.values():
        if getattr(element, "physical", None) is not None:
            element.physical.survey = unsurveyed
    exported = _export(machine, s_position_at="exit")["facility"]
    floor = {c["id"]: c["FloorP"] for c in exported["components"] if "FloorP" in c}
    bend, deflector = floor["inst:BEND"], floor["inst:DEFL"]
    # angle_ref -0.26 turns PALS's heading to +0.26, which heads along +x
    assert bend["theta"] == pytest.approx(0.26)
    run = 0.5  # BEND's exit at s = 1.0 to DEFL's at 1.5
    assert deflector["x"] - bend["x"] == pytest.approx(run * math.sin(0.26))
    assert deflector["z"] - bend["z"] == pytest.approx(run * math.cos(0.26))


@pytest.mark.parametrize("face", ["entrance", "exit"])
def test_a_computed_floor_places_the_element_where_it_was(machine, face):
    for element in machine.elements.values():
        if getattr(element, "physical", None) is not None:
            element.physical.survey = None
    exported = _export(machine, s_position_at=face)["facility"]
    back = _machine({"facility": exported}, s_position_at=face)
    for name in ("BEND", "DEFL", "APER"):  # after the bend, so its angle counts
        before, after = machine.elements[name].physical, back.elements[name].physical
        assert list(after.middle) == pytest.approx(list(before.middle)), name
        assert after.rotation_matrix == pytest.approx(before.rotation_matrix), name
        assert after.survey is None or not any(after.survey.position), name


def test_an_element_inside_another_is_written_off_the_line(machine):
    machine.elements["APER"].physical.s = 1.3  # within DEFL, 1.2 to 1.5
    exported = _export(machine, **_UITF)["facility"]
    component = next(c for c in exported["components"] if c["id"] == "inst:APER")
    assert component["beamline_relation"] == "AttachedToPipe"
    back = _machine({"facility": exported}, **_UITF)
    assert back.elements["APER"].physical.s == pytest.approx(1.3)
