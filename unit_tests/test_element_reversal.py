"""How an element looks to a beam traversing it backwards."""

import warnings
from pathlib import Path

import pytest

from laura import LAURA
from laura.models.element import (
    Combined_Corrector,
    Dipole,
    Drift,
    Marker,
    Quadrupole,
    RFCavity,
    RFDeflectingCavity,
    Sextupole,
    Solenoid,
)
from laura.models.elementList import MachineModel
from laura.models.reversal import (
    ElementNotReversible,
    reversal_obstacles,
    reverse_element,
    reverse_section,
)
from laura.translator.converters.layout import MachineLayoutTranslator
from unit_tests.helpers import quad, quiet


def drift(name="D", length=1.0):
    return Drift(
        name=name,
        hardware_class="Drift",
        machine_area="S",
        physical={"length": length},
    )


def dipole(name="B", **magnetic):
    return Dipole(
        name=name,
        hardware_class="Magnet",
        machine_area="S",
        magnetic={"magnetic_length": 1.0, "k0l": 0.3, **magnetic},
        physical={"length": 1.0},
    )


def cavity(name="C", **cavity_fields):
    return RFCavity(
        name=name,
        hardware_class="RF",
        machine_area="S",
        physical={"length": 0.1},
        cavity={"frequency": 1.3e9, "phase": 0.0, **cavity_fields},
    )


def symbolic():
    return Quadrupole(
        name="Q",
        hardware_class="Magnet",
        machine_area="S",
        magnetic={"magnetic_length": 0.1, "k1l": "quad_strength"},
        physical={"length": 0.1},
        functional_definitions={"quad_strength": 0.5},
    )


def build_machine(elements, sections, entry):
    """A machine of *sections* whose one layout ``L`` is ``[entry]``."""
    with quiet():
        return MachineModel(
            elements={e.name: e for e in elements},
            section={"sections": sections},
            layout={"layouts": {"L": [entry]}, "default_layout": "L"},
        )


class TestTheSignRule:
    def test_a_quadrupole_swaps_its_focusing_plane(self):
        # the shared-IR-magnet fact: one quad, two beams, opposite planes
        assert reverse_element(quad(k1l=0.5)).magnetic.k1l == pytest.approx(-0.5)

    def test_a_dipole_bends_the_other_way(self):
        # why counter-rotating same-charge beams need opposite dipole polarity
        assert reverse_element(dipole()).magnetic.angle == pytest.approx(-0.3)

    def test_a_sextupole_flips_too(self):
        sextupole = Sextupole(
            name="SX",
            hardware_class="Magnet",
            machine_area="S",
            magnetic={"magnetic_length": 0.1, "k2l": 2.0},
            physical={"length": 0.1},
        )
        assert reverse_element(sextupole).magnetic.multipoles.K2L.normal == (
            pytest.approx(-2.0)
        )

    def test_a_vertical_corrector_is_unchanged(self):
        # a skew dipole: the lab deflection flips and so does the frame's y
        corrector = Combined_Corrector(
            name="HV",
            hardware_class="Magnet",
            machine_area="S",
            magnetic={"length": 0.05, "horizontal_kick": 0.001, "vertical_kick": 0.002},
            physical={"length": 0.05},
        )
        reversed_ = reverse_element(corrector)
        assert reversed_.magnetic.horizontal_kick == pytest.approx(-0.001)
        assert reversed_.magnetic.vertical_kick == pytest.approx(0.002)

    def test_skew_and_normal_at_the_same_order(self):
        both = quad(k1l=0.5)
        both.magnetic.multipoles.K1L.skew = 0.25
        reversed_ = reverse_element(both)
        assert reversed_.magnetic.multipoles.K1L.normal == pytest.approx(-0.5)
        assert reversed_.magnetic.multipoles.K1L.skew == pytest.approx(0.25)

    def test_a_solenoid_field_flips(self):
        solenoid = Solenoid(
            name="SOL",
            hardware_class="Magnet",
            machine_area="S",
            magnetic={"length": 0.2, "fields": {"S0L": 0.4}},
            physical={"length": 0.2},
        )
        assert reverse_element(solenoid).magnetic.fields.S0L == pytest.approx(-0.4)


class TestGeometry:
    def test_the_edge_angles_swap(self):
        reversed_ = reverse_element(
            dipole(entrance_edge_angle=0.1, exit_edge_angle=0.2)
        )
        assert reversed_.magnetic.entrance_edge_angle == pytest.approx(0.2)
        assert reversed_.magnetic.exit_edge_angle == pytest.approx(0.1)

    def test_equal_edge_angles_are_a_no_op(self):
        reversed_ = reverse_element(
            dipole(entrance_edge_angle=0.15, exit_edge_angle=0.15)
        )
        assert reversed_.magnetic.entrance_edge_angle == pytest.approx(0.15)

    def test_the_tilt_negates(self):
        # a roll about the beam axis, and the beam axis has flipped
        assert reverse_element(dipole(tilt=0.05)).magnetic.tilt == pytest.approx(-0.05)

    def test_the_length_is_untouched(self):
        assert reverse_element(dipole()).physical.length == pytest.approx(1.0)


class TestItIsAnInvolution:
    @pytest.mark.parametrize(
        "element",
        [
            pytest.param(quad(k1l=0.5), id="quad"),
            pytest.param(
                dipole(entrance_edge_angle=0.1, exit_edge_angle=0.2, tilt=0.05),
                id="dipole",
            ),
            pytest.param(drift(), id="drift"),
        ],
    )
    def test_twice_is_the_identity(self, element):
        there_and_back = reverse_element(reverse_element(element))
        assert there_and_back.model_dump() == element.model_dump()


class TestTheOriginalIsNeverTouched:
    """Reversal belongs to a beam path, not to the installed hardware."""

    def test_the_source_keeps_its_strength(self):
        original = quad(k1l=0.5)
        reverse_element(original)
        assert original.magnetic.k1l == pytest.approx(0.5)

    def test_the_copy_is_independent(self):
        original = quad(k1l=0.5)
        reversed_ = reverse_element(original)
        reversed_.magnetic.multipoles.K1L.normal = 99.0
        assert original.magnetic.k1l == pytest.approx(0.5)


class TestDirectionlessElementsPassStraightThrough:
    @pytest.mark.parametrize(
        "element",
        [
            pytest.param(drift(), id="drift"),
            pytest.param(
                Marker(
                    name="M",
                    hardware_class="Simulation",
                    machine_area="S",
                    physical={"length": 0.0},
                ),
                id="marker",
            ),
        ],
    )
    def test_nothing_is_refused_and_nothing_changes(self, element):
        assert reversal_obstacles(element) == []
        assert reverse_element(element).model_dump() == element.model_dump()


class TestWhatIsRefused:
    @pytest.mark.parametrize(
        "fields, match",
        [
            # A backwards beam counter-propagates with the RF wave.
            pytest.param(
                {"structure_type": "TW"},
                "travelling-wave structure",
                id="travelling-wave",
            ),
            # Power decaying along the structure makes it directional.
            pytest.param({"attenuation_constant": 0.5}, "attenuates", id="attenuating"),
            # Symmetry cannot be assumed from a spelling nobody knows.
            pytest.param(
                {"structure_type": "helical"},
                "not recognised",
                id="unrecognised-structure-type",
            ),
        ],
    )
    def test_a_directional_cavity(self, fields, match):
        with pytest.raises(ElementNotReversible, match=match):
            reverse_element(cavity(**fields))

    def test_a_deflecting_cavity(self):
        """Its kick would flip sign; not yet decided."""
        deflector = RFDeflectingCavity(
            name="TDC",
            machine_area="S",
            physical={"length": 0.1},
        )
        with pytest.raises(ElementNotReversible, match="RFDeflectingCavity"):
            reverse_element(deflector)

    @pytest.mark.parametrize(
        "field, match",
        [
            pytest.param("field_definition", "carries a field map", id="field-map"),
            pytest.param(
                "wakefield_definition", "carries wakefield data", id="wakefield-data"
            ),
        ],
    )
    def test_sampled_field_data(self, field, match):
        sampled = quad()
        setattr(sampled.simulation, field, "data.dat")
        with pytest.raises(ElementNotReversible, match=match):
            reverse_element(sampled)

    def test_a_symbolic_strength(self):
        with pytest.raises(ElementNotReversible, match="symbolic"):
            reverse_element(symbolic())

    def test_every_reason_is_reported_not_just_the_first(self):
        both = quad()
        both.simulation.field_definition = "map.dat"
        both.simulation.wakefield_definition = "wake.dat"
        with pytest.raises(ElementNotReversible) as raised:
            reverse_element(both)
        assert len(raised.value.reasons) == 2

    def test_the_element_is_named(self):
        with pytest.raises(ElementNotReversible, match="CLA-L01-CAV"):
            reverse_element(cavity(name="CLA-L01-CAV", structure_type="TW"))

    def test_obstacles_can_be_checked_without_reversing(self):
        assert reversal_obstacles(cavity(structure_type="TW"))
        assert reversal_obstacles(quad()) == []


class TestASymmetricCavityIsReversible:
    """A symmetric standing-wave cavity reverses as a no-op. The return phase stays
    authored: it is set by path length and the LLRF, which reversal cannot know.
    """

    def test_a_standing_wave_cavity_has_no_obstacles(self):
        assert reversal_obstacles(cavity()) == []

    @pytest.mark.parametrize(
        "spelling", ["StandingWave", "SW", "sw", "standing-wave", "Standing Wave"]
    )
    def test_the_usual_spellings_are_recognised(self, spelling):
        assert reversal_obstacles(cavity(structure_type=spelling)) == []

    def test_reversing_it_changes_nothing_about_it(self):
        forward = cavity(phase=30.0)
        backward = reverse_element(forward)
        assert backward.cavity.phase == pytest.approx(30.0)
        assert backward.cavity.frequency == forward.cavity.frequency
        assert backward.physical.length == pytest.approx(forward.physical.length)

    def test_the_phase_is_not_flipped(self):
        assert reverse_element(cavity(phase=0.0)).cavity.phase == pytest.approx(0.0)

    def test_the_source_is_untouched(self):
        forward = cavity(phase=30.0)
        reverse_element(forward)
        assert forward.cavity.phase == pytest.approx(30.0)


class TestNonStrict:
    def test_it_warns_and_reverses_what_it_can(self):
        mapped = quad(k1l=0.5)
        mapped.simulation.field_definition = "quad_map.dat"
        with pytest.warns(UserWarning, match="only partly reversible"):
            reversed_ = reverse_element(mapped, strict=False)
        assert reversed_.magnetic.k1l == pytest.approx(-0.5)

    def test_a_symbolic_strength_is_left_alone_rather_than_mangled(self):
        with pytest.warns(UserWarning):
            reversed_ = reverse_element(symbolic(), strict=False)
        assert reversed_.magnetic.multipoles.K1L.normal == "quad_strength"


class TestMisalignment:
    def test_an_aligned_element_says_nothing(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            reverse_element(quad())

    def test_a_surveyed_element_warns_that_it_is_not_transformed(self):
        misaligned = quad(error={"position": {"x": 0.001}})
        with pytest.warns(UserWarning, match="measured misalignment"):
            reverse_element(misaligned)


class TestReverseSection:
    """A reversed section is an ordinary section, so exporters need no changes."""

    LENGTHS = {"Q1": 0.1, "D1": 0.4, "B1": 1.0, "D2": 0.9, "Q2": 0.2}
    ORDER = ["Q1", "D1", "B1", "D2", "Q2"]

    @pytest.fixture
    def machine(self):
        elements = [
            quad("Q1", k1l=0.5),
            drift("D1", 0.4),
            dipole("B1"),
            drift("D2", 0.9),
            quad("Q2", 0.2, -0.5),
        ]
        return build_machine(elements, {"S": list(self.ORDER)}, "S")

    @pytest.fixture
    def reversed_section(self, machine):
        return reverse_section(machine.sections["S"], machine.elements)

    def _entrance(self, section, name):
        phys = section.elements[name].physical
        return phys.s - phys.length / 2

    def test_the_order_is_reversed(self, reversed_section):
        assert reversed_section.order == list(reversed(self.ORDER))

    def test_it_is_as_long_as_the_forward_line(self, reversed_section):
        last = reversed_section.elements[reversed_section.order[-1]].physical
        assert last.s + last.length / 2 == pytest.approx(sum(self.LENGTHS.values()))

    def test_every_element_lands_at_its_mirrored_arc_length(
        self, machine, reversed_section
    ):
        total = sum(self.LENGTHS.values())
        for name in self.ORDER:
            forward = machine.elements[name].physical
            forward_exit = forward.s + forward.length / 2
            assert self._entrance(reversed_section, name) == pytest.approx(
                total - forward_exit
            )

    def test_the_bend_is_negated(self, machine, reversed_section):
        assert machine.elements["B1"].magnetic.angle == pytest.approx(0.3)
        assert reversed_section.elements["B1"].magnetic.angle == pytest.approx(-0.3)

    def test_reversing_twice_restores_the_forward_geometry(
        self, machine, reversed_section
    ):
        back = reverse_section(reversed_section, reversed_section.elements.elements)
        assert back.order == self.ORDER
        for name in self.ORDER:
            assert self._entrance(back, name) == pytest.approx(
                self._entrance(machine.sections["S"], name)
            )
        assert back.elements["B1"].magnetic.angle == pytest.approx(0.3)

    def test_the_source_machine_is_untouched(self, machine, reversed_section):
        assert machine.elements["B1"].magnetic.angle == pytest.approx(0.3)
        assert machine.sections["S"].order == self.ORDER
        assert machine.elements["Q1"].physical.s == pytest.approx(0.05)

    def test_a_section_the_registry_cannot_satisfy(self, machine):
        machine.sections["S"].order = self.ORDER + ["GHOST"]
        with pytest.raises(KeyError, match="GHOST"):
            reverse_section(machine.sections["S"], machine.elements)

    def test_strict_reaches_the_elements(self, machine):
        machine.elements["B1"].simulation.field_definition = "map.dat"
        with pytest.raises(ElementNotReversible):
            reverse_section(machine.sections["S"], machine.elements)

    def test_a_real_gap_is_preserved(self):
        """Arc lengths are mirrored, not re-summed, so a drift-less gap survives."""
        spaced = [
            quad("Q1", s=0.1, s_point="end"),
            quad("Q2", s=1.2, s_point="end"),
        ]
        machine = build_machine(spaced, {"S": ["Q1", "Q2"]}, "S")
        reversed_section = reverse_section(machine.sections["S"], machine.elements)

        def entrance(section, name):
            phys = section.elements[name].physical
            return phys.s - phys.length / 2

        assert entrance(reversed_section, "Q2") == pytest.approx(0.0)
        assert entrance(reversed_section, "Q1") == pytest.approx(1.1)
        gap = entrance(reversed_section, "Q1") - (
            entrance(reversed_section, "Q2") + 0.1
        )
        assert gap == pytest.approx(1.0)

    def test_the_layout_translator_reverses_a_marked_section(self):
        def build(entry):
            elements = [quad("Q1", k1l=0.5), drift("D1", 0.4), dipole("B1")]
            machine = build_machine(elements, {"ARC": ["Q1", "D1", "B1"]}, entry)
            return machine, MachineLayoutTranslator.from_layout(machine.lattices["L"])

        machine, forward = build("ARC")
        assert forward.sections["ARC"].order == ["Q1", "D1", "B1"]
        assert forward.sections["ARC"].elements["B1"].magnetic.angle == (
            pytest.approx(0.3)
        )

        machine, backward = build({"ARC": {"direction": -1}})
        assert backward.sections["ARC"].order == ["B1", "D1", "Q1"]
        assert backward.sections["ARC"].elements["B1"].magnetic.angle == (
            pytest.approx(-0.3)
        )
        # the machine's own section is untouched: another path may run it forwards
        assert machine.sections["ARC"].order == ["Q1", "D1", "B1"]
        assert machine.elements["B1"].magnetic.angle == pytest.approx(0.3)


class TestTheReversalExample:
    """``examples/testing/reversal_*.yaml``: one arc, two beams, opposite ways."""

    EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "testing"
    FORWARD = ["QUAD_A", "DRIFT_IN", "BEND", "DRIFT_OUT", "QUAD_B"]

    @pytest.fixture
    def machine(self):
        with quiet():
            return LAURA(
                element_list=str(self.EXAMPLES / "reversal_elements.yaml"),
                section=str(self.EXAMPLES / "reversal_sections.yaml"),
                layout=str(self.EXAMPLES / "reversal_layouts.yaml"),
            )

    def test_both_beam_paths_exist_over_one_section(self, machine):
        assert sorted(machine.lattices) == ["BEAM_1", "BEAM_2"]
        assert (
            machine.lattices["BEAM_1"].sections["ARC"]
            is (machine.lattices["BEAM_2"].sections["ARC"])
        )

    def test_only_the_second_path_is_marked(self, machine):
        assert machine.lattices["BEAM_1"]._direction == {}
        assert machine.lattices["BEAM_2"]._direction == {"ARC": -1}

    def test_the_two_paths_mirror_each_other(self, machine):
        forward = machine.lattices["BEAM_1"].arc_lengths()
        backward = machine.lattices["BEAM_2"].arc_lengths()
        total = sum(machine[n].physical.length for n in self.FORWARD)
        for name in self.FORWARD:
            length = machine[name].physical.length
            assert backward[name] == pytest.approx(total - forward[name] - length)

    def test_the_second_path_meets_the_arc_the_other_way_round(self, machine):
        backward = machine.lattices["BEAM_2"].arc_lengths()
        assert sorted(backward, key=backward.get) == list(reversed(self.FORWARD))

    def test_exporting_the_reversed_path_transforms_the_physics(self, machine):
        beam2 = MachineLayoutTranslator.from_layout(machine.lattices["BEAM_2"])
        arc = beam2.sections["ARC"]
        assert arc.order == list(reversed(self.FORWARD))
        # a shared quadrupole focuses the two beams in opposite planes
        assert arc.elements["QUAD_A"].magnetic.k1l == pytest.approx(-0.6)
        assert arc.elements["BEND"].magnetic.angle == pytest.approx(-0.25)

    def test_the_installed_hardware_is_never_modified(self, machine):
        assert machine.sections["ARC"].order == self.FORWARD
        assert machine["QUAD_A"].magnetic.k1l == pytest.approx(0.6)
        assert machine["BEND"].magnetic.angle == pytest.approx(0.25)
