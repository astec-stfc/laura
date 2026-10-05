"""Bmad and ELEGANT can write an AC dipole; until now LAURA did not.

``waveform`` gave LAURA somewhere to keep an injection kicker's pulse shape,
and the Bmad importer somewhere to put ``amp_vs_time``. The exports were the
other half and were missing on both sides: ``Horizontal_AC_Dipole`` and
``Vertical_AC_Dipole`` were in ``bmad_unsupported``, and ELEGANT's ``BUMPER``
rules existed with no type mapping to reach them, so an AC dipole came out as
a drift.

Three unit conventions are asserted here rather than assumed, because each one
is a silent factor that produces a lattice which tracks perfectly and kicks by
the wrong amount:

* ``field_amplitude`` [V] is the integrated field in T*m times 1e6. Bmad's
  ``BL_HKICK`` is T*m, so the conversion is a plain factor; its ``HKICK`` is
  radians, which needs a rigidity, which is why the exporter does not use it.
* ELEGANT's ``BUMPER`` states its strength as ``ANGLE`` in radians, so it
  *does* need the rigidity -- passed in, or left out of the file.
* Bmad drives its kicker as a cosine where LAURA, MAD-X and Xtrack drive a
  sine. A quarter turn of phase, invisible in any amplitude check.

The parity tests run the codes. They are the point of the file: everything
above can be got right on paper and still be wrong.
"""

import math
import os
import subprocess
from pathlib import Path
from shutil import which

import pytest

from laura.models.element import HorizontalACDipole, VerticalACDipole
from laura.translator.converters.converter import translate_elements
from laura.translator.utils.ac_dipole import MV_PER_VOLT, SINE_TO_COSINE_TURNS

PULSE = {"time": [0.0, 1.0e-6, 1.2e-6], "factor": [0.0, 1.0, 0.0]}
"""A single-turn injection kicker: 1 us rise, no flat top, 200 ns fall."""

BRHO = 3.335640951981521
"""Rigidity of a 1 GeV/c beam [T*m], i.e. ``1e9 / c``."""

BMAD_DIST = Path(
    os.environ.get("BMAD_DIST")
    or os.environ.get("ACC_ROOT_DIR")
    or Path.home() / "Documents" / "bmad-ecosystem"
).expanduser()
LIBTAO = Path(
    os.environ.get("LAURA_LIBTAO", BMAD_DIST / "production" / "lib" / "libtao.so")
).expanduser()


def dipole(cls=HorizontalACDipole, name="KICK1", directory=None, **simulation):
    element = cls(
        name=name, machine_area="INJ",
        physical={"length": 0.3},
        simulation={"field_amplitude": 1.0e6, **simulation},
    )
    translator = translate_elements([element])[name]
    if directory is not None:
        translator.directory = str(directory)
    return translator


def attribute(definition, key):
    """Pull ``key = value`` out of a one-line element definition."""
    for term in definition.replace("&\n", "").split(","):
        name, _, value = term.partition("=")
        if name.strip().lower() == key:
            return value.strip().rstrip(";").strip()
    return None


class TestBmad:
    def test_an_ac_dipole_is_an_ac_kicker(self):
        """It used to be in ``bmad_unsupported`` and came out as a drift."""
        assert dipole(waveform=PULSE).to_bmad().split()[1].rstrip(",") == "ac_kicker"

    def test_the_kick_is_the_integrated_field_not_an_angle(self):
        """``bl_hkick`` is in T*m; ``hkick`` is that over the rigidity, which
        an element translator has no reference momentum to divide by."""
        definition = dipole(field_amplitude=2.0e6, waveform=PULSE).to_bmad()
        assert attribute(definition, "hkick") is None
        assert float(attribute(definition, "bl_hkick")) == pytest.approx(2.0)

    def test_the_vertical_plane_gets_bl_vkick(self):
        definition = dipole(VerticalACDipole, waveform=PULSE).to_bmad()
        assert attribute(definition, "bl_hkick") is None
        assert float(attribute(definition, "bl_vkick")) == pytest.approx(1.0)

    def test_the_waveform_becomes_amp_vs_time(self):
        definition = dipole(waveform=PULSE).to_bmad()
        assert "amp_vs_time = {(0.0, 0.0), (1e-06, 1.0), (1.2e-06, 0.0)}" in definition

    @pytest.mark.parametrize(
        "rule, written", [("linear", "linear"), ("spline", "cubic")]
    )
    def test_each_interpolation_rule_is_named(self, rule, written):
        """Bmad defaults to cubic where every other code defaults to linear,
        so leaving ``interpolation`` off would change the pulse."""
        definition = dipole(waveform={**PULSE, "interpolation": rule}).to_bmad()
        assert attribute(definition, "interpolation") == written

    def test_a_held_waveform_says_it_was_flattened(self):
        """Bmad offers cubic or linear and nothing that steps."""
        with pytest.warns(UserWarning, match="staircase"):
            definition = dipole(waveform={**PULSE, "interpolation": "hold"}).to_bmad()
        assert attribute(definition, "interpolation") == "linear"

    def test_a_sinusoid_becomes_a_single_frequency(self):
        definition = dipole(frequency=1.0e5, phase=90.0).to_bmad()
        assert attribute(definition, "amp_vs_time") is None
        assert "frequencies = {(100000.0, 1.0, 0.0)}" in definition

    def test_the_phase_is_shifted_from_sine_to_cosine(self):
        """A quarter turn: LAURA's zero phase is a sine, Bmad's is a cosine."""
        definition = dipole(frequency=1.0e5, phase=0.0).to_bmad()
        assert f"1.0, {SINE_TO_COSINE_TURNS})" in definition

    def test_a_waveform_wins_over_a_frequency_and_says_so(self):
        """Bmad's AC_Kicker takes ``amp_vs_time`` or ``frequencies``, never
        both; LAURA's schema does not forbid authoring both."""
        with pytest.warns(UserWarning, match="not both"):
            definition = dipole(frequency=1.0e5, waveform=PULSE).to_bmad()
        assert attribute(definition, "frequencies") is None

    def test_a_ramp_envelope_is_reported_as_unwritable(self):
        with pytest.warns(UserWarning, match="ramp1-ramp4"):
            dipole(frequency=1.0e5, ramp=[0, 10, 90, 100]).to_bmad()


class TestElegant:
    """``directory`` is set throughout: a waveform writes an SDDS sidecar
    beside the lattice, and the default is the working directory."""

    def test_an_ac_dipole_is_a_bumper(self, tmp_path):
        """It had no type mapping at all, so it came out as a drift."""
        line = dipole(waveform=PULSE, directory=tmp_path).to_elegant(Brho=BRHO)
        assert line.split()[1].rstrip(",") == "bumper"

    def test_the_angle_is_the_integrated_field_over_the_rigidity(self, tmp_path):
        line = dipole(
            field_amplitude=2.0e6, waveform=PULSE, directory=tmp_path
        ).to_elegant(Brho=BRHO)
        assert float(attribute(line, "angle")) == pytest.approx(2.0 / BRHO)

    def test_without_a_rigidity_the_strength_is_left_out_and_reported(self, tmp_path):
        """Writing ``angle = field_amplitude`` would be a 1e6 radian kick that
        ELEGANT tracks without complaint."""
        with pytest.warns(UserWarning, match="rigidity"):
            line = dipole(waveform=PULSE, directory=tmp_path).to_elegant()
        assert attribute(line, "angle") is None

    def test_the_vertical_plane_is_a_rotated_bumper(self, tmp_path):
        """ELEGANT has no vertical bumper type."""
        line = dipole(
            VerticalACDipole, waveform=PULSE, directory=tmp_path
        ).to_elegant(Brho=BRHO)
        assert float(attribute(line, "tilt")) == pytest.approx(math.pi / 2)

    def test_the_waveform_is_written_as_an_sdds_sidecar(self, tmp_path):
        line = dipole(waveform=PULSE, directory=tmp_path).to_elegant(Brho=BRHO)
        assert attribute(line, "waveform") == '"KICK1_waveform.sdds=t+factor"'
        written = (tmp_path / "KICK1_waveform.sdds").read_text()
        assert "name=t" in written and "name=factor" in written
        assert "1.200000000000000e-06" in written

    def test_the_firing_turn_is_not_written(self, tmp_path):
        """Under the agreed split ``fire_on_pass`` is a study setting, not a
        property of the machine, so it belongs to the tracking code's run
        configuration and not to the lattice LAURA writes."""
        line = dipole(waveform=PULSE, directory=tmp_path).to_elegant(Brho=BRHO)
        assert "fire_on_pass" not in line

    @pytest.mark.parametrize("rule", ["hold", "spline"])
    def test_a_non_linear_waveform_says_it_was_straightened(self, rule, tmp_path):
        """ELEGANT reads a WAVEFORM file by linear interpolation only."""
        with pytest.warns(UserWarning, match="straight lines"):
            dipole(
                waveform={**PULSE, "interpolation": rule}, directory=tmp_path
            ).to_elegant(Brho=BRHO)

    def test_a_section_threads_the_rigidity_down(self, tmp_path):
        """Nothing else in an ELEGANT export needs a rigidity, so there was
        nowhere for one to come from; without the parameter every kicker in a
        whole-lattice export is written with no strength."""
        from laura.models.element_list import SectionLattice
        from laura.translator.converters.section import SectionLatticeTranslator

        kicker = HorizontalACDipole(
            name="KICK1", machine_area="S1", physical={"length": 0.3},
            simulation={"field_amplitude": 2.0e4, "waveform": PULSE},
        )
        section = SectionLattice(name="S1", order=["KICK1"], elements=[kicker])
        translator = SectionLatticeTranslator.from_section(section)
        translator.directory = str(tmp_path)
        written = translator.to_elegant(Brho=BRHO)
        assert f"angle = {2.0e4 * MV_PER_VOLT / BRHO}" in written

    def test_a_sinusoid_reports_that_a_bumper_cannot_be_driven(self):
        """A BUMPER has no frequency of its own. RFDF does, but it is a
        deflecting cavity rather than a dipole, so swapping to it is a
        modelling decision for the person writing the study."""
        with pytest.warns(UserWarning, match="RFDF"):
            dipole(frequency=1.0e5).to_elegant(Brho=BRHO)


class TestXsuiteUnits:
    """Found while measuring the Bmad and ELEGANT conventions.

    ``to_xsuite`` was passing ``field_amplitude`` straight into xtrack's
    ``volt`` and ``phase`` straight into its ``lag``, where ``to_madx`` -- the
    same two conventions -- divides by 1e6 and by 360.
    """

    def test_volt_is_in_mv(self):
        pytest.importorskip("xtrack")
        _, _, properties = dipole(field_amplitude=2.0e6, frequency=1e5).to_xsuite(1)
        assert properties["volt"] == pytest.approx(2.0)

    def test_lag_is_in_turns(self):
        pytest.importorskip("xtrack")
        _, _, properties = dipole(frequency=1e5, phase=90.0).to_xsuite(1)
        assert properties["lag"] == pytest.approx(0.25)

    def test_the_units_survive_a_round_trip(self):
        """The importer had the mirror image of both errors, so Xsuite was
        self-consistently wrong: out and back gave the element it started
        from, and no single-direction test could see it."""
        xt = pytest.importorskip("xtrack")

        from laura.translator.converters.codes.xsuite import XsuiteLatticeImporter

        name, cls, properties = dipole(
            field_amplitude=2.0e6, frequency=0.31, phase=30.0
        ).to_xsuite(1)
        line = xt.Line(elements=[cls(**properties)], element_names=[name])
        imported = XsuiteLatticeImporter(line=line).create_element_dictionary()[name]
        assert imported.simulation.field_amplitude == pytest.approx(2.0e6)
        assert imported.simulation.phase == pytest.approx(30.0)


@pytest.mark.skipif(not LIBTAO.exists(), reason="libtao is not installed")
class TestBmadParity:
    """What Bmad makes of the file LAURA writes."""

    @staticmethod
    def parsed(tmp_path, *translators):
        from pytao import Tao

        lattice = tmp_path / "lat.bmad"
        line = ", ".join(translator.name for translator in translators)
        lattice.write_text(
            "beginning[beta_a] = 10\nbeginning[beta_b] = 10\n"
            "beginning[e_tot] = 1e9\nparameter[geometry] = open\n"
            "parameter[particle] = electron\n\n"
            + "".join(translator.to_bmad() for translator in translators)
            + "D: drift, l = 1.0\n"
            f"LN: line = ({line}, D)\nuse, LN\n"
        )
        init = tmp_path / "tao.init"
        init.write_text(
            "&tao_start\n  n_universes = 1\n/\n"
            f"&tao_design_lattice\n  design_lattice(1)%file = '{lattice}'\n/\n"
        )
        return Tao(f"-init {init} -noplot", so_lib=str(LIBTAO))

    def test_bmad_reads_the_kick_back_in_tesla_metres(self, tmp_path):
        tao = self.parsed(tmp_path, dipole(field_amplitude=2.0e6, waveform=PULSE))
        attributes = tao.ele_gen_attribs("KICK1")
        assert attributes["units#BL_HKICK"] == "T*m"
        assert attributes["BL_HKICK"] == pytest.approx(2.0)
        # And what the translator avoided writing: an angle, which Bmad
        # derives for itself from the beam it was given.
        assert abs(attributes["HKICK"]) == pytest.approx(2.0 / BRHO, rel=1e-4)

    def test_bmad_reads_the_knots_back_unchanged(self, tmp_path):
        tao = self.parsed(tmp_path, dipole(waveform=PULSE))
        # Tao reports `index;amp;time`, amplitude before time.
        rows = tao.cmd("pipe ele:ac_kicker KICK1|model")
        knots = [row.split(";")[1:] for row in rows if row[0].isdigit()]
        assert [float(time) for _, time in knots] == pytest.approx(PULSE["time"])
        assert [float(amp) for amp, _ in knots] == pytest.approx(PULSE["factor"])
        assert tao.ele_gen_attribs("KICK1")["INTERPOLATION"] == "Linear"

    def test_a_kicker_survives_the_round_trip(self, tmp_path):
        """Export, let Bmad parse it, import it back."""
        from laura.translator.converters.codes.bmad import BmadLatticeImporter

        self.parsed(tmp_path, dipole(field_amplitude=2.0e6, waveform=PULSE))
        importer = BmadLatticeImporter(
            lattice_file=str(tmp_path / "lat.bmad"), libtao=str(LIBTAO)
        )
        imported = importer.create_laura_element_dictionary(1)["LN_1"]["KICK1"]
        assert imported.simulation.field_amplitude == pytest.approx(2.0e6)
        assert imported.simulation.waveform.time == pytest.approx(PULSE["time"])
        assert imported.simulation.waveform.factor == pytest.approx(PULSE["factor"])
        assert imported.simulation.waveform.interpolation == "linear"

    def test_the_phase_survives_the_round_trip(self, tmp_path):
        """The quarter turn has to be undone on the way back in, or two
        exports of one exciter drift apart by 90 degrees each trip."""
        from laura.translator.converters.codes.bmad import BmadLatticeImporter

        self.parsed(tmp_path, dipole(frequency=1.0e5, phase=30.0))
        importer = BmadLatticeImporter(
            lattice_file=str(tmp_path / "lat.bmad"), libtao=str(LIBTAO)
        )
        imported = importer.create_laura_element_dictionary(1)["LN_1"]["KICK1"]
        assert imported.simulation.phase == pytest.approx(30.0)

    def test_bmad_drives_a_cosine(self, tmp_path):
        """The measurement the quarter-turn shift rests on.

        Bmad evaluates ``amp = cos(twopi * (f*t + phi))``, so a lattice held
        at ``f = 0`` reads the phase off directly. A LAURA phase of 90 degrees
        means ``sin(90) = 1``, a full-strength kick; written through unshifted
        it would reach Bmad as ``cos(90) = 0`` and not kick at all.
        """
        # The elements are written by hand because the translator leaves
        # ``frequencies`` off a zero-frequency element -- a DC kicker, which
        # is what f = 0 means to both codes, but not what is under test here.
        lattice = tmp_path / "lat.bmad"
        lattice.write_text(
            "beginning[beta_a] = 10\nbeginning[beta_b] = 10\n"
            "beginning[e_tot] = 1e9\nparameter[geometry] = open\n"
            "parameter[particle] = electron\n\n"
            + "".join(
                f"K{i}: ac_kicker, l = 0, bl_hkick = 1.0, "
                f"frequencies = {{(0.0, 1.0, {phase / 360.0 + SINE_TO_COSINE_TURNS})}}\n"
                for i, phase in enumerate((90.0, 0.0))
            )
            + "LN: line = (K0, K1)\nuse, LN\n"
        )
        init = tmp_path / "tao.init"
        init.write_text(
            "&tao_start\n  n_universes = 1\n/\n"
            f"&tao_design_lattice\n  design_lattice(1)%file = '{lattice}'\n/\n"
        )
        from pytao import Tao

        px = Tao(f"-init {init} -noplot", so_lib=str(LIBTAO)).lat_list(
            "*", "orbit.vec.2"
        )
        # K0 is LAURA's sin(90) = 1, at full strength; K1 is sin(0) = 0 and
        # adds nothing, so the orbit after it is unchanged.
        assert px[1] == pytest.approx(-1.0 / BRHO, rel=1e-4)
        assert px[2] == pytest.approx(px[1], rel=1e-9)


@pytest.mark.skipif(which("elegant") is None, reason="elegant is not installed")
class TestElegantParity:
    """What ELEGANT makes of the file LAURA writes.

    ELEGANT applies ``ANGLE * factor(t - t_ref)``, where ``t_ref`` is the
    bunch's own arrival time -- so the two particles below straddle it, and
    the later one lands exactly on the waveform's 1 us peak.
    """

    # 0.02 T*m, a plausible injection kicker. The size matters: ELEGANT bends
    # by the angle rather than adding it to the slope, so a radian-scale kick
    # would come back as its tangent and say nothing about the units.
    FIELD = 2.0e4
    ANGLE = FIELD * MV_PER_VOLT / BRHO

    def test_the_kick_is_the_angle_times_the_waveform(self, tmp_path):
        kicker = dipole(
            field_amplitude=self.FIELD, waveform=PULSE, directory=tmp_path
        )
        self.track(tmp_path, kicker.to_elegant(Brho=BRHO))
        assert self.kicks(tmp_path, "xp") == pytest.approx(
            [0.0, self.ANGLE], rel=1e-4, abs=1e-12
        )

    def test_a_vertical_kicker_kicks_vertically(self, tmp_path):
        kicker = dipole(
            VerticalACDipole, field_amplitude=self.FIELD, waveform=PULSE,
            directory=tmp_path,
        )
        self.track(tmp_path, kicker.to_elegant(Brho=BRHO))
        assert self.kicks(tmp_path, "xp") == pytest.approx([0.0, 0.0], abs=1e-12)
        assert self.kicks(tmp_path, "yp") == pytest.approx(
            [0.0, self.ANGLE], rel=1e-4, abs=1e-12
        )

    @staticmethod
    def track(tmp_path, definition):
        (tmp_path / "lat.lte").write_text(
            definition + 'W1: watch, filename="out.sdds", mode=coordinate\n'
            "LN: line=(KICK1, W1)\n"
        )
        (tmp_path / "beam.sdds").write_text(
            "SDDS1\n"
            "&column name=x, units=m, type=double &end\n"
            "&column name=xp, type=double &end\n"
            "&column name=y, units=m, type=double &end\n"
            "&column name=yp, type=double &end\n"
            "&column name=t, units=s, type=double &end\n"
            '&column name=p, units="m$be$nc", type=double &end\n'
            "&column name=particleID, type=long &end\n"
            "&data mode=ascii, no_row_counts=1 &end\n"
            "0 0 0 0 0.0e-6 1957 1\n"
            "0 0 0 0 2.0e-6 1957 2\n"
        )
        (tmp_path / "run.ele").write_text(
            "&run_setup\n  lattice = lat.lte, use_beamline = LN,\n"
            "  p_central = 1957, default_order = 1\n&end\n"
            "&run_control n_steps = 1 &end\n"
            "&sdds_beam input = beam.sdds &end\n&track &end\n"
        )
        subprocess.run(
            ["elegant", "run.ele"], cwd=tmp_path, check=True, capture_output=True
        )

    @staticmethod
    def kicks(tmp_path, column):
        output = subprocess.run(
            ["sdds2stream", f"-col=particleID,{column}", "out.sdds"],
            cwd=tmp_path, check=True, capture_output=True, text=True,
        ).stdout
        rows = sorted(
            (int(line.split()[0]), float(line.split()[1]))
            for line in output.splitlines() if line.strip()
        )
        return [value for _, value in rows]
