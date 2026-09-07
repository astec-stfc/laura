"""How an element looks to a beam traversing it backwards.

The derivation lives in :mod:`laura.models.reversal`.  The two tests worth
reading first are :meth:`TestTheSignRule.test_a_quadrupole_swaps_its_focusing_plane`
and :meth:`TestTheSignRule.test_a_vertical_corrector_is_unchanged`, because
those are the two physical facts the whole sign rule has to reproduce: a shared
quadrupole focuses counter-propagating beams in opposite planes, and a skew
dipole's kick survives reversal because the lab deflection *and* the frame's
``y`` both flip.
"""

import warnings

import pytest

from laura.models.element import (
    Combined_Corrector,
    Dipole,
    Drift,
    Marker,
    Quadrupole,
    RFCavity,
    Sextupole,
    Solenoid,
)
from laura.models.reversal import (
    ElementNotReversible,
    reversal_obstacles,
    reverse_element,
)


def quad(name="Q", k1l=0.5, **magnetic):
    return Quadrupole(
        name=name,
        hardware_class="Magnet",
        machine_area="S",
        magnetic={"magnetic_length": 0.1, "k1l": k1l, **magnetic},
        physical={"length": 0.1},
    )


def dipole(name="B", **magnetic):
    return Dipole(
        name=name,
        hardware_class="Magnet",
        machine_area="S",
        magnetic={"magnetic_length": 1.0, "k0l": 0.3, **magnetic},
        physical={"length": 1.0},
    )


class TestTheSignRule:
    def test_a_quadrupole_swaps_its_focusing_plane(self):
        # the shared-IR-magnet fact: one quad, two beams, opposite planes
        assert reverse_element(quad(k1l=0.5)).magnetic.k1l == pytest.approx(-0.5)

    def test_a_dipole_bends_the_other_way(self):
        # why counter-rotating same-charge beams need opposite dipole polarity
        assert reverse_element(dipole()).magnetic.angle == pytest.approx(-0.3)

    def test_a_sextupole_flips_too(self):
        # the rule is every order, not just the low ones
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
    """Reversing twice must restore the original exactly."""

    @pytest.mark.parametrize(
        "element",
        [
            pytest.param(quad(k1l=0.5), id="quad"),
            pytest.param(
                dipole(entrance_edge_angle=0.1, exit_edge_angle=0.2, tilt=0.05),
                id="dipole",
            ),
            pytest.param(
                Drift(
                    name="D",
                    hardware_class="Drift",
                    machine_area="S",
                    physical={"length": 1.0},
                ),
                id="drift",
            ),
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
            pytest.param(
                Drift(
                    name="D",
                    hardware_class="Drift",
                    machine_area="S",
                    physical={"length": 1.0},
                ),
                id="drift",
            ),
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
    def test_an_rf_cavity(self):
        cavity = RFCavity(
            name="C",
            hardware_class="RF",
            machine_area="S",
            physical={"length": 0.1},
        )
        with pytest.raises(ElementNotReversible, match="zero-phase convention"):
            reverse_element(cavity)

    def test_a_field_map(self):
        mapped = quad()
        mapped.simulation.field_definition = "quad_map.dat"
        with pytest.raises(ElementNotReversible, match="resampled"):
            reverse_element(mapped)

    def test_wakefield_data(self):
        waked = quad()
        waked.simulation.wakefield_definition = "wake.dat"
        with pytest.raises(ElementNotReversible, match="causal"):
            reverse_element(waked)

    def test_a_symbolic_strength(self):
        symbolic = Quadrupole(
            name="Q",
            hardware_class="Magnet",
            machine_area="S",
            magnetic={"magnetic_length": 0.1, "k1l": "quad_strength"},
            physical={"length": 0.1},
            functional_definitions={"quad_strength": 0.5},
        )
        with pytest.raises(ElementNotReversible, match="symbolic"):
            reverse_element(symbolic)

    def test_every_reason_is_reported_not_just_the_first(self):
        both = quad()
        both.simulation.field_definition = "map.dat"
        both.simulation.wakefield_definition = "wake.dat"
        with pytest.raises(ElementNotReversible) as raised:
            reverse_element(both)
        assert len(raised.value.reasons) == 2

    def test_the_element_is_named(self):
        cavity = RFCavity(
            name="CLA-L01-CAV",
            hardware_class="RF",
            machine_area="S",
            physical={"length": 0.1},
        )
        with pytest.raises(ElementNotReversible, match="CLA-L01-CAV"):
            reverse_element(cavity)

    def test_obstacles_can_be_checked_without_reversing(self):
        cavity = RFCavity(
            name="C",
            hardware_class="RF",
            machine_area="S",
            physical={"length": 0.1},
        )
        assert reversal_obstacles(cavity)
        assert reversal_obstacles(quad()) == []


class TestNonStrict:
    """For a caller that has decided a partial reversal is acceptable."""

    def test_it_warns_and_reverses_what_it_can(self):
        mapped = quad(k1l=0.5)
        mapped.simulation.field_definition = "quad_map.dat"
        with pytest.warns(UserWarning, match="only partly reversible"):
            reversed_ = reverse_element(mapped, strict=False)
        assert reversed_.magnetic.k1l == pytest.approx(-0.5)

    def test_a_symbolic_strength_is_left_alone_rather_than_mangled(self):
        symbolic = Quadrupole(
            name="Q",
            hardware_class="Magnet",
            machine_area="S",
            magnetic={"magnetic_length": 0.1, "k1l": "quad_strength"},
            physical={"length": 0.1},
            functional_definitions={"quad_strength": 0.5},
        )
        with pytest.warns(UserWarning):
            reversed_ = reverse_element(symbolic, strict=False)
        assert reversed_.magnetic.multipoles.K1L.normal == "quad_strength"


class TestMisalignment:
    def test_an_aligned_element_says_nothing(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            reverse_element(quad())

    def test_a_surveyed_element_warns_that_it_is_not_transformed(self):
        misaligned = Quadrupole(
            name="Q",
            hardware_class="Magnet",
            machine_area="S",
            magnetic={"magnetic_length": 0.1, "k1l": 0.5},
            physical={"length": 0.1, "error": {"position": {"x": 0.001}}},
        )
        with pytest.warns(UserWarning, match="measured misalignment"):
            reverse_element(misaligned)


# ---------------------------------------------------------------------------
# whole sections
# ---------------------------------------------------------------------------


class TestReverseSection:
    """A reversed section is an ordinary section, so exporters need no changes.

    The oracle is :meth:`test_reversing_twice_restores_the_forward_geometry`:
    the transform and the re-placement must undo each other exactly.
    """

    LENGTHS = {"Q1": 0.1, "D1": 0.4, "B1": 1.0, "D2": 0.9, "Q2": 0.2}
    ORDER = ["Q1", "D1", "B1", "D2", "Q2"]

    @pytest.fixture
    def machine(self):
        from laura.models.elementList import MachineModel

        elements = [
            quad("Q1", k1l=0.5),
            Drift(
                name="D1",
                hardware_class="Drift",
                machine_area="S",
                physical={"length": 0.4},
            ),
            Dipole(
                name="B1",
                hardware_class="Magnet",
                machine_area="S",
                magnetic={"magnetic_length": 1.0, "k0l": 0.3},
                physical={"length": 1.0},
            ),
            Drift(
                name="D2",
                hardware_class="Drift",
                machine_area="S",
                physical={"length": 0.9},
            ),
            Quadrupole(
                name="Q2",
                hardware_class="Magnet",
                machine_area="S",
                magnetic={"magnetic_length": 0.2, "k1l": -0.5},
                physical={"length": 0.2},
            ),
        ]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return MachineModel(
                elements={e.name: e for e in elements},
                section={"sections": {"S": list(self.ORDER)}},
                layout={"layouts": {"L": ["S"]}, "default_layout": "L"},
            )

    @pytest.fixture
    def reversed_section(self, machine):
        from laura.models.reversal import reverse_section

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
        from laura.models.reversal import reverse_section

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
        from laura.models.reversal import reverse_section

        machine.sections["S"].order = self.ORDER + ["GHOST"]
        with pytest.raises(KeyError, match="GHOST"):
            reverse_section(machine.sections["S"], machine.elements)

    def test_strict_reaches_the_elements(self, machine):
        from laura.models.reversal import reverse_section

        machine.elements["B1"].simulation.field_definition = "map.dat"
        with pytest.raises(ElementNotReversible):
            reverse_section(machine.sections["S"], machine.elements)

    def test_a_real_gap_is_preserved(self):
        """A section is not always drift-filled, and reversal must not close it.

        Accumulating lengths along the reversed order would abut everything, so
        a 1.2 m line holding a 1.0 m gap with no drift element in it came back
        0.2 m long. Each element's arc length is mirrored from its forward one
        instead.
        """
        from laura.models.elementList import MachineModel
        from laura.models.reversal import reverse_section

        spaced = [
            Quadrupole(
                name="Q1",
                hardware_class="Magnet",
                machine_area="S",
                magnetic={"magnetic_length": 0.1, "k1l": 0.5},
                physical={"length": 0.1, "s": 0.1, "s_point": "end"},
            ),
            Quadrupole(
                name="Q2",
                hardware_class="Magnet",
                machine_area="S",
                magnetic={"magnetic_length": 0.1, "k1l": 0.5},
                physical={"length": 0.1, "s": 1.2, "s_point": "end"},
            ),
        ]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            machine = MachineModel(
                elements={e.name: e for e in spaced},
                section={"sections": {"S": ["Q1", "Q2"]}},
                layout={"layouts": {"L": ["S"]}, "default_layout": "L"},
            )
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
        """The one hook: substitution happens once, so no exporter changes."""
        from laura.models.elementList import MachineModel
        from laura.translator.converters.layout import MachineLayoutTranslator

        def build(entry):
            elements = [
                quad("Q1", k1l=0.5),
                Drift(
                    name="D1",
                    hardware_class="Drift",
                    machine_area="S",
                    physical={"length": 0.4},
                ),
                Dipole(
                    name="B1",
                    hardware_class="Magnet",
                    machine_area="S",
                    magnetic={"magnetic_length": 1.0, "k0l": 0.3},
                    physical={"length": 1.0},
                ),
            ]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                machine = MachineModel(
                    elements={e.name: e for e in elements},
                    section={"sections": {"ARC": ["Q1", "D1", "B1"]}},
                    layout={"layouts": {"L": [entry]}, "default_layout": "L"},
                )
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
