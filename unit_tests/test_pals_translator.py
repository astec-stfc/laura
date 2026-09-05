"""Tests for the PALS exporter (``to_pals``).

Three kinds of check, in increasing order of how much they prove:

* the document says what it should -- shape, groups and values, read straight
  out of the emitted YAML;
* it round trips -- a lattice written out and read back is the one that went
  in, which is the strongest statement LAURA can make on its own;
* it is understood by something that is not LAURA. The last class runs the
  document through ``palsparserpy``'s own ``pals_to_bmad`` and checks the Bmad
  lattice *that* produces against the LAURA elements the document was written
  from. Nothing LAURA wrote is consulted in the comparison, so a convention
  LAURA has backwards in both directions -- which a round trip cannot see --
  shows up here.

Everything is skipped where ``palsparserpy`` is not installed.
"""

import os
import re
import subprocess
import sys

import pytest
import yaml
from scipy.constants import speed_of_light

from laura.translator.converters.codes.pals import PalsLatticeImporter
from laura.translator.converters.model import MachineModelTranslator
from laura.translator.utils.pals import (
    PALS_RESERVED_NAMES,
    pals_kind_round_trips,
    pals_safe_names,
    parser_available,
)

_DATA = os.path.join(os.path.dirname(__file__), "data")
_LATTICE = os.path.join(_DATA, "pals_test_lattice.pals.yaml")
_BRANCHES = os.path.join(_DATA, "pals_test_branches.pals.yaml")

pytestmark = pytest.mark.skipif(
    not parser_available(), reason="palsparserpy is not installed"
)


def _model(source):
    importer = PalsLatticeImporter(source_file=source)
    with pytest.warns(UserWarning):
        # The fixtures state their edge-field integrals as the fint*hgap
        # product and fork to a branch LAURA cannot follow; both warn on import.
        return importer.create_machine_model()


def _facility(document):
    """The document's facility entries, keyed by name."""
    entries = yaml.safe_load(document)["PALS"]["facility"]
    return {name: body for entry in entries for name, body in entry.items()}


@pytest.fixture(scope="module")
def machine():
    return _model(_LATTICE)


@pytest.fixture(scope="module")
def document(machine):
    return MachineModelTranslator.from_machine(machine).to_pals()["lat1"]


@pytest.fixture(scope="module")
def facility(document):
    return _facility(document)


@pytest.fixture(scope="module")
def elements(machine):
    section = next(iter(next(iter(machine.lattices.values())).sections.values()))
    return {element.name: element for element in section._get_all_elements()}


class TestDocumentShape:
    def test_document_is_a_pals_root_with_a_facility(self, document):
        loaded = yaml.safe_load(document)
        assert set(loaded) == {"PALS"}
        # The standard has not settled its version numbering; its own examples
        # leave this null rather than claim one.
        assert loaded["PALS"]["version"] is None
        assert isinstance(loaded["PALS"]["facility"], list)

    def test_the_branch_is_named_used_and_holds_every_element(self, facility):
        assert facility["use"] == "lat1"
        assert facility["lat1"] == {"kind": "Lattice", "branches": ["main_line"]}
        line = facility["main_line"]["line"]
        assert facility["main_line"]["kind"] == "BeamLine"
        # Everything after the beginning element is a plain name, defined once
        # in the facility above the line.
        assert all(name in facility for name in line[1:])

    def test_the_line_opens_with_its_reference_state(self, facility):
        begin = facility["main_line"]["line"][0]["main_line_begin"]
        assert begin["kind"] == "BeginningEle"
        assert begin["ReferenceP"] == {
            "species_ref": "electron",
            "E_tot_ref": 1.0e9,
        }

    def test_the_run_up_is_stated_rather_than_drifted(self, facility, elements):
        # The fixture's first element starts a metre in. `s_position` is an
        # input on the beginning element, so the distance is stated there
        # instead of being written out as a leading drift.
        begin = facility["main_line"]["line"][0]["main_line_begin"]
        assert begin["s_position"] == pytest.approx(1.0)
        assert not any(name.endswith("lead_drift") for name in facility)

    def test_gaps_between_elements_become_drifts(self, facility):
        drift = facility["main_line_drift_1"]
        assert drift["kind"] == "Drift"
        assert drift["length"] == pytest.approx(0.5)

    def test_an_open_lattice_is_not_periodic(self, facility):
        assert "periodic" not in facility["main_line"]

    def test_a_ring_is_periodic(self):
        document = MachineModelTranslator.from_machine(_model(_BRANCHES)).to_pals()
        assert _facility(document["lat1"])["ring"]["periodic"] is True


class TestElementBodies:
    def test_a_magnet_states_its_integrated_normalised_strength(self, facility):
        # Both sides put the 1/N! in the field expansion, so the numbers are
        # LAURA's own with nothing scaled.
        assert facility["q1"] == {
            "kind": "Quadrupole",
            "length": 0.5,
            "MagneticMultipoleP": {"Kn1L": pytest.approx(0.4)},
        }
        assert facility["s1"]["MagneticMultipoleP"] == {"Kn2L": pytest.approx(1.5)}
        assert facility["o1"]["MagneticMultipoleP"] == {
            "Kn3L": pytest.approx(3.0),
            "Ks3L": pytest.approx(0.5),
        }

    def test_a_bend_states_its_curvature_not_its_angle(self, facility):
        bend = facility["b1"]["BendP"]
        # PALS derives one from the other given the length. See the writer for
        # why the curvature is the one written.
        assert bend["g_ref"] == pytest.approx(0.15 / 1.5)
        assert "angle_ref" not in bend
        assert bend["e1"] == pytest.approx(0.05)
        assert bend["e2"] == pytest.approx(0.03)
        # PALS states one number where LAURA holds two: the fint*hgap product.
        assert bend["edge1_int"] == pytest.approx(0.02)
        assert bend["edge2_int"] == pytest.approx(0.04)
        assert bend["tilt_ref"] == pytest.approx(0.1)

    def test_a_bend_does_not_state_its_dipole_field_twice(self, facility):
        # `g_ref` is the bending field and `tilt_ref` its roll; repeating
        # either in the multipole group would be read as a second, superimposed
        # magnet.
        body = facility["b1"]
        assert "MagneticMultipoleP" not in body

    def test_a_solenoid_states_its_strength_per_metre(self, facility):
        assert facility["sol1"]["SolenoidP"] == {"Ksol": pytest.approx(0.6)}

    def test_a_cavity_states_its_phase_in_turns(self, facility):
        rf = facility["cav1"]["RFP"]
        assert rf["frequency"] == pytest.approx(1.3e9)
        assert rf["voltage"] == pytest.approx(2.0e7)
        # LAURA measures the phase in degrees from the zero crossing, PALS in
        # turns from the accelerating crest.
        assert rf["phase"] == pytest.approx(0.25)
        assert rf["num_cells"] == 9
        assert rf["cavity_type"] == "STANDING_WAVE"

    def test_a_corrector_states_a_kick_of_the_opposite_sign(self, facility):
        # A positive Kn0L bends towards negative x, a positive horizontal kick
        # towards positive x.
        assert facility["kick1"]["MagneticMultipoleP"] == {"Kn0L": pytest.approx(0.001)}
        assert facility["kick2"]["MagneticMultipoleP"] == {"Ks0L": pytest.approx(0.002)}
        assert facility["kick3"]["MagneticMultipoleP"] == {
            "Kn0L": pytest.approx(0.003),
            "Ks0L": pytest.approx(0.004),
        }

    def test_an_aperture_is_written_as_signed_edges(self, facility):
        # An elliptical aperture is inactive unless all four edges are set, so
        # edges are what is written for every shape.
        assert facility["col1"]["ApertureP"] == {
            "x_min": pytest.approx(-0.01),
            "x_max": pytest.approx(0.01),
            "y_min": pytest.approx(-0.02),
            "y_max": pytest.approx(0.02),
            "shape": "RECTANGULAR",
            "location": "EVERYWHERE",
        }

    def test_a_misalignment_becomes_a_body_shift(self, facility):
        assert facility["off1"]["BodyShiftP"] == {
            "x_offset": pytest.approx(0.001),
            # y_rot turns the opposite way from LAURA's theta.
            "y_rot": pytest.approx(0.002),
            "z_rot": pytest.approx(0.003),
        }

    def test_a_zero_length_element_omits_its_length(self, facility):
        assert facility["mark1"] == {"kind": "Marker"}


class TestTypeExtension:
    def test_a_family_member_states_its_laura_type(self, facility):
        # PALS has one Kicker where LAURA has three correctors and one
        # Instrument where it has eleven diagnostics.
        assert facility["kick1"]["LauraP"] == {"hardware_type": "Horizontal_Corrector"}
        assert facility["mon1"]["LauraP"] == {"hardware_type": "Beam_Position_Monitor"}

    def test_the_generic_member_of_a_family_does_not(self, facility):
        assert "LauraP" not in facility["kick3"]
        assert "LauraP" not in facility["inst1"]
        assert "LauraP" not in facility["q1"]

    def test_a_drift_is_not_labelled(self, facility):
        # A drift is left out of the importer's kind table because LAURA
        # regenerates drifts rather than importing them, which is not the same
        # as the kind failing to round trip.
        assert pals_kind_round_trips("Drift")
        assert "LauraP" not in facility["main_line_drift_1"]

    def test_the_extension_is_declared(self, document):
        names = yaml.safe_load(document)["PALS"]["extension_labels"]["names"]
        assert "LauraP" in names

    def test_a_document_that_needs_no_extension_declares_none(self):
        # The ring fixture is quadrupoles, bends and a marker: every kind is
        # the whole of its LAURA family.
        document = MachineModelTranslator.from_machine(_model(_BRANCHES)).to_pals()
        assert "extension_labels" not in yaml.safe_load(document["lat1"])["PALS"]


class TestReservedNames:
    def test_a_command_name_is_renamed(self):
        renames = pals_safe_names(["q1", "use", "set"])
        assert renames == {"use": "use_element", "set": "set_element"}

    def test_an_ordinary_name_is_left_alone(self):
        # PALS is permissive about names; only the facility command keys are
        # dangerous.
        assert pals_safe_names(["q.1", "q-2", "Q1#2", "drift"]) == {}

    def test_a_clash_with_the_replacement_is_broken(self):
        renames = pals_safe_names(["use", "use_element"])
        assert renames["use"] == "use_element_2"

    def test_every_reserved_name_is_lower_case(self):
        assert all(name == name.lower() for name in PALS_RESERVED_NAMES)


@pytest.fixture(scope="module")
def returned(document, tmp_path_factory):
    """The exported document, read back in."""
    path = tmp_path_factory.mktemp("pals") / "roundtrip.pals.yaml"
    path.write_text(document)
    return _model(str(path))


class TestRoundTrip:
    """A lattice written out and read back is the lattice that went in."""

    def test_every_element_comes_home(self, machine, returned):
        def names(model):
            return [
                element.name
                for lattice in model.lattices.values()
                for section in lattice.sections.values()
                for element in section._get_all_elements()
            ]

        assert names(returned) == names(machine)

    def test_every_element_comes_home_unchanged(self, elements, returned):
        section = next(iter(next(iter(returned.lattices.values())).sections.values()))
        for element in section._get_all_elements():
            original = elements[element.name]
            expected = original.model_dump(exclude_none=True)
            actual = element.model_dump(exclude_none=True)
            if original.hardware_type == "Dipole":
                # PALS holds only the fint*hgap product, so the two sides of
                # the split are free to differ as long as the product does not.
                for dump in (expected, actual):
                    magnetic = dump["magnetic"]
                    magnetic["edge_field_integral"] *= magnetic.pop("half_gap")
                    magnetic.pop("gap", None)
            assert actual == expected, element.name

    def test_the_branch_keeps_its_reference_state(self, machine, returned):
        def state(model):
            section = next(iter(next(iter(model.lattices.values())).sections.values()))
            return section.geometry, section.reference_energy

        assert state(returned) == state(machine)


def _bmad_statements(text):
    """A Bmad file as one string per statement, comments and wrapping gone.

    Enough of a reader for the file this module compares against: the
    reference translator wraps a statement over several indented lines, so
    continuations are joined back on before anything is split.
    """
    statements = []
    for line in text.splitlines():
        line = line.split("!")[0].rstrip()
        if not line.strip():
            continue
        if line[0].isspace() and statements:
            statements[-1] += " " + line.strip()
        else:
            statements.append(line.strip())
    return statements


def _bmad_definitions(text):
    """``{name: (type, {attribute: value})}`` from a Bmad lattice file."""
    definitions = {}
    for statement in _bmad_statements(text):
        match = re.match(r"^([\w.]+)\s*:\s*(\w+)\s*(.*)$", statement)
        if not match or match.group(2).lower() == "line":
            continue
        name, kind, rest = match.groups()
        attributes = {}
        for pair in rest.split(","):
            if "=" not in pair:
                continue
            key, value = pair.split("=", 1)
            try:
                attributes[key.strip().lower()] = float(value.strip())
            except ValueError:
                attributes[key.strip().lower()] = value.strip().lower()
        definitions[name] = (kind.lower(), attributes)
    return definitions


def _bmad_line(text, name):
    """The element names of the Bmad ``line`` called ``name``, in order."""
    for statement in _bmad_statements(text):
        match = re.match(rf"^{name}\s*:\s*line\s*=\s*\((.*)\)\s*$", statement, re.I)
        if match:
            return [part.strip() for part in match.group(1).split(",") if part.strip()]
    raise AssertionError(f"no line called {name!r} in the reference output")


@pytest.fixture(scope="module")
def reference_text(document, tmp_path_factory):
    """The document, translated to Bmad by ``palsparserpy`` rather than LAURA."""
    to_bmad = pytest.importorskip("palsparserpy.to_bmad")
    assert hasattr(to_bmad, "pals_to_bmad")

    directory = tmp_path_factory.mktemp("differential")
    source = directory / "laura.pals.yaml"
    source.write_text(document)
    target = directory / "reference.bmad"
    # In a subprocess for the same reason the reader parses in one: the parser
    # is a ctypes wrapper around a C library, and a fault there would take the
    # test session down with it rather than failing a test.
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys\n"
            "from palsparserpy import parse_file\n"
            "from palsparserpy.to_bmad import pals_to_bmad, write_bmad_file\n"
            "write_bmad_file(pals_to_bmad(parse_file(sys.argv[1])), sys.argv[2])\n",
            str(source),
            str(target),
        ],
        check=True,
        capture_output=True,
    )
    return target.read_text()


@pytest.fixture(scope="module")
def reference_bmad(reference_text):
    return _bmad_definitions(reference_text)


class TestAgainstTheReferenceTranslator:
    """What an independent reader makes of a document LAURA wrote.

    The comparison is always reference-output against the *LAURA elements*,
    never against LAURA's own Bmad export: the point is to check the PALS
    conventions against someone else's reading of them, and going through a
    second LAURA exporter would only compare LAURA with itself.
    """

    def test_the_line_comes_out_in_order(self, reference_text, facility):
        # The reference translator drops the beginning element, so the LAURA
        # line is compared without it. Everything after that has to hold its
        # place: an element read into the wrong slot is a lattice with the
        # right parts in the wrong machine.
        written = [
            name for name in facility["main_line"]["line"] if isinstance(name, str)
        ]
        assert _bmad_line(reference_text, "main_line") == written

    def test_the_geometry_comes_out(self, reference_text, machine):
        section = next(iter(next(iter(machine.lattices.values())).sections.values()))
        geometry = getattr(section.geometry, "value", section.geometry)
        assert f"parameter[geometry] = {geometry}" in reference_text

    def test_every_element_survives_with_its_length(self, reference_bmad, elements):
        for name, element in elements.items():
            assert name in reference_bmad, name
            length = reference_bmad[name][1].get("l", 0.0)
            assert length == pytest.approx(element.physical.length), name

    def test_magnet_strengths_agree(self, reference_bmad, elements):
        # Bmad's k1/k2/k3 are per metre; LAURA holds them integrated.
        for name, order in (("q1", 1), ("q2", 1), ("s1", 2), ("o1", 3)):
            attributes = reference_bmad[name][1]
            element = elements[name]
            assert attributes[f"k{order}"] == pytest.approx(
                element.magnetic.KnL(order) / element.physical.length
            ), name

    def test_the_bend_agrees(self, reference_bmad, elements):
        kind, attributes = reference_bmad["b1"]
        bend = elements["b1"]
        assert kind == "sbend"
        assert attributes["g"] * bend.physical.length == pytest.approx(
            bend.magnetic.KnL(0)
        )
        assert attributes["e1"] == pytest.approx(bend.magnetic.entrance_edge_angle)
        assert attributes["e2"] == pytest.approx(bend.magnetic.exit_edge_angle)
        assert attributes["ref_tilt"] == pytest.approx(bend.magnetic.tilt)
        # Only the fint*hgap product is physical, and it is all PALS carries;
        # the reference translator splits it its own way.
        assert attributes["fint"] * attributes["hgap"] == pytest.approx(
            bend.magnetic.edge_field_integral * bend.magnetic.half_gap
        )
        assert attributes["fintx"] * attributes["hgapx"] == pytest.approx(
            bend.magnetic.exit_edge_field_integral * bend.magnetic.exit_half_gap
        )

    def test_the_solenoid_agrees(self, reference_bmad, elements):
        kind, attributes = reference_bmad["sol1"]
        solenoid = elements["sol1"]
        assert kind == "solenoid"
        # Bmad's ks is the normalised strength per metre, which is what LAURA
        # holds integrated over the length.
        assert attributes["ks"] == pytest.approx(
            solenoid.magnetic.fields.S0L / solenoid.physical.length
        )

    def test_the_cavity_agrees(self, reference_bmad, elements):
        attributes = reference_bmad["cav1"][1]
        cavity = elements["cav1"]
        assert attributes["rf_frequency"] == pytest.approx(cavity.cavity.frequency)
        assert attributes["voltage"] == pytest.approx(
            cavity.simulation.field_amplitude
        )
        assert attributes["n_cell"] == cavity.cavity.n_cells
        # Bmad's phi0 is in turns, as PALS's phase is; LAURA's is in degrees
        # from the zero crossing.
        assert attributes["phi0"] == pytest.approx(-cavity.cavity.phase / 360.0)
        assert cavity.cavity.cell_length == pytest.approx(
            speed_of_light / (2 * cavity.cavity.frequency)
        )

    def test_the_correctors_agree(self, reference_bmad, elements):
        # The reference translator writes a PALS Kn0L as Bmad's B0 multipole,
        # which bends the opposite way to a LAURA horizontal kick.
        assert reference_bmad["kick1"][1]["b0"] == pytest.approx(
            -elements["kick1"].magnetic.horizontal_kick
        )
        assert reference_bmad["kick2"][1]["a0"] == pytest.approx(
            elements["kick2"].magnetic.vertical_kick
        )
        combined = reference_bmad["kick3"][1]
        assert combined["b0"] == pytest.approx(
            -elements["kick3"].magnetic.horizontal_kick
        )
        assert combined["a0"] == pytest.approx(
            elements["kick3"].magnetic.vertical_kick
        )

    def test_the_aperture_agrees(self, reference_bmad, elements):
        attributes = reference_bmad["col1"][1]
        aperture = elements["col1"].aperture
        assert attributes["x1_limit"] == pytest.approx(aperture.horizontal_size / 2)
        assert attributes["x2_limit"] == pytest.approx(aperture.horizontal_size / 2)
        assert attributes["y1_limit"] == pytest.approx(aperture.vertical_size / 2)
        assert attributes["y2_limit"] == pytest.approx(aperture.vertical_size / 2)
        assert attributes["aperture_type"] == "rectangular"

    def test_the_misalignment_agrees(self, reference_bmad, elements):
        attributes = reference_bmad["off1"][1]
        error = elements["off1"].physical.error
        assert attributes["x_offset"] == pytest.approx(error.position.x)
        # Bmad's x_pitch is a rotation about x, as PALS's x_rot is; LAURA's
        # theta turns the other way.
        assert attributes["x_pitch"] == pytest.approx(-error.rotation.theta)
        assert attributes["tilt"] == pytest.approx(error.rotation.psi)
