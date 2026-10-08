"""Exporter tidying options and ``Element.retype``: they change how a machine is
written, never what it is, so each export is reloaded and compared.
"""

import os
from pathlib import Path

import numpy as np
import pytest
import yaml

from laura import LAURA
from laura.exporters.yaml_exporter import export_as_yaml, export_machine
from laura.exporters.yaml_tidy import (
    TEMPLATE_MIN_MEMBERS,
    externalise_shared_fields,
    family_templates,
    rounded,
)
from laura.models.element import (
    Drift,
    HorizontalCorrector,
    Marker,
    Quadrupole,
    RFCavity,
    Screen,
    WireScanner,
)
from laura.translator.utils.fields import FieldMap
from laura.translator.utils.fields.field_parameter import FieldParameter
from laura.translator.utils.units import UnitValue
from unit_tests.helpers import quiet


def _wake(scale=1.0):
    wake = FieldMap(
        field_type="LongitudinalWake",
        z=FieldParameter(name="z", value=UnitValue([0.0, 0.01, 0.02], units="m")),
        Wz=FieldParameter(
            name="Wz", value=UnitValue(scale * np.array([10.0, 5.0, 0.0]), units="V/C")
        ),
    )
    wake.read = True
    return wake


def _cavity(name, z, wake):
    return RFCavity(
        name=name,
        machine_area="L1",
        hardware_model="SBand",
        physical={"length": 3.0, "middle": {"z": z}},
        simulation={"wakefield_definition": wake},
    )


def _quad(name, z, k1l=0.5):
    return Quadrupole(
        name=name,
        machine_area="L1",
        physical={"length": 0.1, "middle": {"z": z}},
        magnetic={
            "length": 0.1,
            "k1l": k1l,
            "gap": 0.03,
            "edge_field_integral": 0.4,
            "multipoles": {"K2L": {"normal": 0.01}},
        },
        simulation={"csr_enable": False, "lsc_enable": False, "sr_enable": False},
        electrical={"max_i": 10.0, "min_i": -10.0},
    )


def _machine(tmp_path, elements):
    source = tmp_path / "source"
    source.mkdir()
    for name, data in (
        ("elements", {e.name: export_as_yaml(None, e, "global") for e in elements}),
        ("sections", {"sections": {"L1": [e.name for e in elements]}}),
        ("layouts", {"default_layout": "beam", "layouts": {"beam": ["L1"]}}),
    ):
        (source / f"{name}.yaml").write_text(yaml.dump(data))
    return _load(source / "elements.yaml", source)


def _load(element_list, root):
    with quiet():
        return LAURA(
            element_list=str(element_list),
            section=str(root / "sections.yaml"),
            layout=str(root / "layouts.yaml"),
            master_lattice=str(root),
        )


def _reload(machine, root, exported):
    for name in ("sections.yaml", "layouts.yaml"):
        (exported / name).write_text((root / "source" / name).read_text())
    return _load(exported, exported)


class TestRounded:
    def test_noise_goes(self):
        quad = _quad("Q1", 2.00000000000004, k1l=0.05099200000000005)
        quad.physical.middle.x = 3e-17
        clean = rounded(quad)
        assert clean.physical.middle.z == 2.0
        assert clean.magnetic.k1l == 0.050992
        assert clean.physical.middle.x == 0.0

    def test_the_original_is_untouched(self):
        quad = _quad("Q1", 2.00000000000004)
        rounded(quad)
        assert quad.physical.middle.z == 2.00000000000004

    def test_positions_keep_a_tenth_of_a_nanometre(self):
        quad = _quad("Q1", 2.00000000012345)
        assert rounded(quad).physical.middle.z == 2.0000000001

    def test_a_value_rounding_to_its_default_is_not_written(self):
        quad = _quad("Q1", 2.0)
        quad.physical.middle.x = 3e-17
        assert "x" in export_as_yaml(None, quad)["physical"]["middle"]
        dump = export_as_yaml(None, quad, round_floats=True)
        assert "x" not in dump["physical"]["middle"]

    def test_sampled_fields_are_left_alone(self):
        wake = _wake(1.00000000000004)
        cavity = rounded(_cavity("C1", 1.0, wake))
        assert cavity.simulation.wakefield_definition.Wz.value[0] == pytest.approx(
            10.0000000000004, abs=0
        )

    def test_a_cavity_is_never_rounded_short_of_its_cells(self):
        # LCLS-II's `9*lambda/2` at 1.3 GHz: 0.1 nm rounds it 4.6e-11 m short
        # of nine cells, and Bmad then fits only eight.
        length = 1.0377431238461539
        cavity = RFCavity(
            name="C9",
            machine_area="L1",
            physical={"length": length, "middle": {"z": 1.00000000000004}},
            cavity={"frequency": 1.3e9, "n_cells": 9},
        )
        clean = rounded(cavity)
        assert clean.physical.length == length
        assert clean.physical.middle.z == 1.0
        cavity.physical.length = 3.00000000012345
        assert rounded(cavity).physical.length == 3.0000000001


class TestSharedFields:
    def test_each_distinct_field_is_written_once(self, tmp_path):
        cavities = [
            _cavity("C1", 1.5, _wake()),
            _cavity("C2", 4.5, _wake()),
            _cavity("C3", 7.5, _wake(2.0)),
        ]
        names = externalise_shared_fields(cavities, str(tmp_path / "Data"), "$data$/")
        assert names == {
            "C1": {"wakefield_definition": "$data$/SBand_3m_wake.hdf5"},
            "C2": {"wakefield_definition": "$data$/SBand_3m_wake.hdf5"},
            "C3": {"wakefield_definition": "$data$/C3_wake.hdf5"},
        }
        assert sorted(os.listdir(tmp_path / "Data")) == [
            "C3_wake.hdf5",
            "SBand_3m_wake.hdf5",
        ]

    def test_the_reference_defaults_to_the_directory(self, tmp_path):
        names = externalise_shared_fields([_cavity("C1", 1.5, _wake())], str(tmp_path))
        assert names["C1"]["wakefield_definition"] == str(tmp_path / "C1_wake.hdf5")

    def test_export_names_the_file_and_reloads_the_wake(self, tmp_path):
        machine = _machine(
            tmp_path, [_cavity("C1", 1.5, _wake()), _cavity("C2", 4.5, _wake())]
        )
        # As an importer holds them; inline YAML samples reload as plain lists.
        for name in ("C1", "C2"):
            machine.elements[name].simulation.wakefield_definition = _wake()
        exported = tmp_path / "exported"
        export_machine(
            str(exported),
            machine,
            field_directory=str(exported / "Data_Files"),
            field_reference="$master_lattice$Data_Files/",
        )
        (path,) = [
            os.path.join(root, f)
            for root, _, files in os.walk(exported)
            for f in files
            if f == "C1.yaml"
        ]
        text = Path(path).read_text()
        assert yaml.safe_load(text)["simulation"]["wakefield_definition"] == (
            "$master_lattice$Data_Files/SBand_3m_wake.hdf5"
        )
        assert "Wz" not in text
        assert isinstance(
            machine.elements["C1"].simulation.wakefield_definition, FieldMap
        )


def _quads(n):
    return [_quad(f"Q{i}", 1.0 + i, k1l=0.5 if i else -0.5) for i in range(n)]


class TestFamilyTemplates:
    def _dumps(self, elements):
        return {e.name: (e, export_as_yaml(None, e)) for e in elements}

    def test_a_family_gets_a_template(self):
        templates, members = family_templates(self._dumps(_quads(TEMPLATE_MIN_MEMBERS)))
        assert list(templates) == ["Quadrupole_L0p1"]
        template = templates["Quadrupole_L0p1"]
        assert template["magnetic"]["gap"] == 0.03
        assert template["electrical"] == {"max_i": 10.0, "min_i": -10.0}
        # Most members share it, so the odd one out keeps its own.
        assert template["magnetic"]["multipoles"]["K1L"]["normal"] == 0.5
        assert "physical" not in template or "middle" not in template["physical"]
        assert set(members) == {f"Q{i}" for i in range(TEMPLATE_MIN_MEMBERS)}

    def test_a_small_family_gets_none(self):
        assert family_templates(self._dumps(_quads(TEMPLATE_MIN_MEMBERS - 1))) == (
            {},
            {},
        )

    def test_drifts_get_none(self):
        drifts = [
            Drift(
                name=f"D{i}",
                machine_area="L1",
                hardware_class="Drift",
                physical={"length": 0.2},
            )
            for i in range(10)
        ]
        assert family_templates(self._dumps(drifts)) == ({}, {})

    def test_an_element_that_already_inherits_is_left_alone(self):
        quads = _quads(TEMPLATE_MIN_MEMBERS + 1)
        quads[0].inherits_from = "SOMETHING"
        _, members = family_templates(self._dumps(quads))
        assert "Q0" not in members


class TestAutoTemplatesRoundTrip:
    def test_members_inherit_and_reload_unchanged(self, tmp_path):
        machine = _machine(tmp_path, _quads(5))
        exported = tmp_path / "exported"
        export_machine(str(exported), machine, auto_templates=True)

        assert (exported / "_Quadrupole_L0p1.yaml").exists()
        quads = exported / "Magnet" / "Quadrupole"
        q1 = yaml.safe_load((quads / "Q1.yaml").read_text())
        assert q1["inherits_from"] == "Quadrupole_L0p1"
        assert "gap" not in q1.get("magnetic", {})
        q0 = yaml.safe_load((quads / "Q0.yaml").read_text())
        assert q0["magnetic"]["multipoles"]["K1L"]["normal"] == -0.5

        reloaded = _reload(machine, tmp_path, exported)
        for name, original in machine.elements.items():
            again = reloaded.elements[name]
            assert again.magnetic.k1l == original.magnetic.k1l
            assert again.magnetic.gap == original.magnetic.gap
            assert again.electrical.max_i == original.electrical.max_i
            assert again.physical.middle.z == original.physical.middle.z

    def test_the_machine_that_went_out_is_untouched(self, tmp_path):
        machine = _machine(tmp_path, _quads(5))
        export_machine(str(tmp_path / "exported"), machine, auto_templates=True)
        assert all(e.inherits_from is None for e in machine.elements.values())


class TestRetype:
    def _marker(self):
        return Marker(
            name="BK1",
            machine_area="L2",
            physical={"length": 0.3, "middle": {"z": 12.0}},
            simulation={"csr_enable": False, "lsc_enable": False},
            controls={"identifier_pattern": "KICK:LI21:957", "variables": {}},
        )

    def test_keeps_identity_and_place(self):
        corrector = self._marker().retype("Horizontal_Corrector")
        assert isinstance(corrector, HorizontalCorrector)
        assert corrector.name == "BK1"
        assert corrector.machine_area == "L2"
        assert corrector.physical.length == 0.3
        assert corrector.physical.middle.z == 12.0
        assert corrector.controls.identifier_pattern == "KICK:LI21:957"

    def test_leaves_the_original_alone(self):
        marker = self._marker()
        marker.retype(HorizontalCorrector).physical.middle.z = 99.0
        assert marker.physical.middle.z == 12.0

    def test_shared_simulation_fields_carry_over(self):
        corrector = self._marker().retype(HorizontalCorrector)
        assert corrector.simulation.csr_enable is False
        assert corrector.simulation.lsc_enable is False

    def test_like_supplies_what_the_old_type_did_not_have(self):
        imported = HorizontalCorrector(
            name="XC1", machine_area="L2", simulation={"sr_enable": False}
        )
        assert self._marker().retype(HorizontalCorrector).simulation.sr_enable is True
        corrector = self._marker().retype(HorizontalCorrector, like=imported)
        assert corrector.simulation.sr_enable is False
        assert corrector.simulation.csr_enable is False

    def test_same_kind_of_simulation_is_kept_whole(self):
        screen = Screen(
            name="YAG1",
            machine_area="L2",
            physical={"length": 0.0},
            simulation={"lsc_enable": False, "horizontal_offset": 0.001},
        )
        wire = screen.retype(WireScanner)
        assert wire.simulation.horizontal_offset == 0.001
        assert wire.simulation.lsc_enable is False

    def test_fields_override(self):
        corrector = self._marker().retype("Horizontal_Corrector", machine_area="L3")
        assert corrector.machine_area == "L3"
