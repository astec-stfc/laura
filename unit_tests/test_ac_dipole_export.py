"""AC dipole export to Bmad and ELEGANT.

* ``field_amplitude`` [V] is the integrated field [T*m] times 1e6; Bmad's ``BL_HKICK`` is T*m.
* ELEGANT's ``BUMPER`` ``ANGLE`` is in radians, so it needs the rigidity.
* Bmad drives a cosine where LAURA, MAD-X and Xtrack drive a sine.
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
    for term in definition.replace("&\n", "").split(","):
        name, _, value = term.partition("=")
        if name.strip().lower() == key:
            return value.strip().rstrip(";").strip()
    return None


class TestBmad:
    def test_an_ac_dipole_is_an_ac_kicker(self):
        assert dipole(waveform=PULSE).to_bmad().split()[1].rstrip(",") == "ac_kicker"

    def test_the_kick_is_the_integrated_field_not_an_angle(self):
        """``hkick`` would need a rigidity the element translator does not have."""
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
        """Bmad defaults to cubic; every other code to linear."""
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
        definition = dipole(frequency=1.0e5, phase=0.0).to_bmad()
        assert f"1.0, {SINE_TO_COSINE_TURNS})" in definition

    def test_a_waveform_wins_over_a_frequency_and_says_so(self):
        """Bmad's AC_Kicker takes ``amp_vs_time`` or ``frequencies``, never both."""
        with pytest.warns(UserWarning, match="not both"):
            definition = dipole(frequency=1.0e5, waveform=PULSE).to_bmad()
        assert attribute(definition, "frequencies") is None

    def test_a_ramp_envelope_is_reported_as_unwritable(self):
        with pytest.warns(UserWarning, match="ramp1-ramp4"):
            dipole(frequency=1.0e5, ramp=[0, 10, 90, 100]).to_bmad()


class TestElegant:
    """A waveform writes an SDDS sidecar beside the lattice, hence ``directory``."""

    def test_an_ac_dipole_is_a_bumper(self, tmp_path):
        line = dipole(waveform=PULSE, directory=tmp_path).to_elegant(Brho=BRHO)
        assert line.split()[1].rstrip(",") == "bumper"

    def test_the_angle_is_the_integrated_field_over_the_rigidity(self, tmp_path):
        line = dipole(
            field_amplitude=2.0e6, waveform=PULSE, directory=tmp_path
        ).to_elegant(Brho=BRHO)
        assert float(attribute(line, "angle")) == pytest.approx(2.0 / BRHO)

    def test_without_a_rigidity_the_strength_is_left_out_and_reported(self, tmp_path):
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
        """``fire_on_pass`` is a run setting, not a lattice property."""
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
        """A BUMPER has no frequency; RFDF does, but is a deflecting cavity."""
        with pytest.warns(UserWarning, match="RFDF"):
            dipole(frequency=1.0e5).to_elegant(Brho=BRHO)


class TestXsuiteUnits:
    """xtrack's ``volt`` is in MV and ``lag`` in turns, as in MAD-X."""

    @pytest.fixture(autouse=True)
    def _xtrack(self):
        pytest.importorskip("xtrack")

    def test_volt_is_in_mv(self):
        _, _, properties = dipole(field_amplitude=2.0e6, frequency=1e5).to_xsuite(1)
        assert properties["volt"] == pytest.approx(2.0)

    def test_lag_is_in_turns(self):
        _, _, properties = dipole(frequency=1e5, phase=90.0).to_xsuite(1)
        assert properties["lag"] == pytest.approx(0.25)

    def test_the_units_survive_a_round_trip(self):
        import xtrack as xt

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
    @staticmethod
    def tao(tmp_path, body):
        """Write a 1 GeV electron lattice holding ``body`` and open it in Tao."""
        from pytao import Tao

        lattice = tmp_path / "lat.bmad"
        lattice.write_text(
            "beginning[beta_a] = 10\nbeginning[beta_b] = 10\n"
            "beginning[e_tot] = 1e9\nparameter[geometry] = open\n"
            "parameter[particle] = electron\n\n" + body
        )
        init = tmp_path / "tao.init"
        init.write_text(
            "&tao_start\n  n_universes = 1\n/\n"
            f"&tao_design_lattice\n  design_lattice(1)%file = '{lattice}'\n/\n"
        )
        return Tao(f"-init {init} -noplot", so_lib=str(LIBTAO))

    @classmethod
    def parsed(cls, tmp_path, *translators):
        line = ", ".join(translator.name for translator in translators)
        return cls.tao(
            tmp_path,
            "".join(translator.to_bmad() for translator in translators)
            + "D: drift, l = 1.0\n"
            f"LN: line = ({line}, D)\nuse, LN\n",
        )

    @classmethod
    def round_trip(cls, tmp_path, translator):
        from laura.translator.converters.codes.bmad import BmadLatticeImporter

        cls.parsed(tmp_path, translator)
        importer = BmadLatticeImporter(
            lattice_file=str(tmp_path / "lat.bmad"), libtao=str(LIBTAO)
        )
        return importer.create_laura_element_dictionary(1)["LN_1"]["KICK1"]

    def test_bmad_reads_the_kick_back_in_tesla_metres(self, tmp_path):
        tao = self.parsed(tmp_path, dipole(field_amplitude=2.0e6, waveform=PULSE))
        attributes = tao.ele_gen_attribs("KICK1")
        assert attributes["units#BL_HKICK"] == "T*m"
        assert attributes["BL_HKICK"] == pytest.approx(2.0)
        # Bmad derives the angle itself from the beam energy.
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
        imported = self.round_trip(tmp_path, dipole(field_amplitude=2.0e6, waveform=PULSE))
        assert imported.simulation.field_amplitude == pytest.approx(2.0e6)
        assert imported.simulation.waveform.time == pytest.approx(PULSE["time"])
        assert imported.simulation.waveform.factor == pytest.approx(PULSE["factor"])
        assert imported.simulation.waveform.interpolation == "linear"

    def test_the_phase_survives_the_round_trip(self, tmp_path):
        imported = self.round_trip(tmp_path, dipole(frequency=1.0e5, phase=30.0))
        assert imported.simulation.phase == pytest.approx(30.0)

    def test_bmad_drives_a_cosine(self, tmp_path):
        """Bmad evaluates ``amp = cos(twopi * (f*t + phi))``, so at f = 0 the phase reads off directly."""
        # Hand-written: the translator omits ``frequencies`` at f = 0 (a DC kicker).
        px = self.tao(
            tmp_path,
            "".join(
                f"K{i}: ac_kicker, l = 0, bl_hkick = 1.0, "
                f"frequencies = {{(0.0, 1.0, {phase / 360.0 + SINE_TO_COSINE_TURNS})}}\n"
                for i, phase in enumerate((90.0, 0.0))
            )
            + "LN: line = (K0, K1)\nuse, LN\n",
        ).lat_list("*", "orbit.vec.2")
        # K0 is LAURA's sin(90) = 1; K1 is sin(0) = 0.
        assert px[1] == pytest.approx(-1.0 / BRHO, rel=1e-4)
        assert px[2] == pytest.approx(px[1], rel=1e-9)


@pytest.mark.skipif(which("elegant") is None, reason="elegant is not installed")
class TestElegantParity:
    """ELEGANT applies ``ANGLE * factor(t - t_ref)``, t_ref being the bunch arrival time;
    the later particle lands on the 1 us peak."""

    # 0.02 T*m; kept small because ELEGANT bends by the angle, returning its tangent.
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
