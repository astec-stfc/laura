"""Alignment errors, exported and imported in LAURA's (Bmad's) convention:
see ``laura/translator/utils/bmad/misalignment.py``."""

import warnings

import numpy as np
import pytest

from laura.models.element import Dipole, Quadrupole, RFCavity, Sextupole
from laura.models.element_list import ElementList, SectionLattice
from laura.translator.converters.codes.elegant import ElegantLatticeImporter
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.section import SectionLatticeTranslator

ERRORS = {
    "position": {"x": 1e-3, "y": -2e-3, "z": 3e-3},
    "rotation": {"theta": 4e-3, "phi": 5e-3, "psi": 6e-3},
}


def quad(error=ERRORS, tilt=0.1):
    return Quadrupole(
        name="q",
        machine_area="S",
        physical={"s": 0.5, "length": 0.5, "error": error},
        magnetic={"length": 0.5, "k1l": 1.0, "tilt": tilt},
    )


def bend(error=ERRORS, tilt=0.2, csr=False):
    return Dipole(
        name="q",
        machine_area="S",
        physical={"s": 0.5, "length": 1.0, "error": error},
        magnetic={"length": 1.0, "angle": 0.1, "tilt": tilt},
        simulation={"csr_enable": csr},
    )


def translator(element):
    return next(iter(translate_elements([element]).values()))


def section(*elements):
    registry = {e.name: e for e in elements}
    lattice = SectionLattice(
        name="line", order=list(registry), elements=ElementList(elements=registry)
    )
    lattice.resolve_positions(lattice.elements.elements)
    return SectionLatticeTranslator.from_section(lattice)


def terms(text):
    text = text.replace("&\n", "").replace(" ", "").lower().rstrip(";\n")
    return dict(term.split("=", 1) for term in text.split(",")[1:])


class TestRoll:
    def test_a_roll_error_adds_to_tilt(self):
        q = translator(quad({"rotation": {"psi": 0.02}}))
        assert "tilt = 0.12" in q.to_madx()
        assert float(terms(q.to_elegant())["tilt"]) == pytest.approx(0.12)

    def test_a_bend_keeps_its_roll_error_apart(self):
        # a bend's tilt rolls its frame in every code
        b = translator(bend({"rotation": {"psi": 0.01}}))
        assert "tilt = 0.2," in b.to_madx()
        assert terms(b.to_elegant())["etilt"] == "0.01"


class TestElegant:
    def test_quad_pitch_and_yaw_need_malign_method_2(self):
        written = terms(translator(quad()).to_elegant())
        assert (written["yaw"], written["pitch"]) == ("-0.004", "0.005")
        assert written["malign_method"] == "2"
        assert (written["dx"], written["dy"], written["dz"]) == (
            "0.001",
            "-0.002",
            "0.003",
        )

    def test_csbend_takes_every_error(self):
        written = terms(translator(bend()).to_elegant())
        assert written["tilt"] == "0.2"
        assert (written["eyaw"], written["epitch"], written["etilt"]) == (
            "-0.004",
            "0.005",
            "0.006",
        )
        assert written["malign_method"] == "2"

    def test_csrcsbend_warns_about_pitch(self):
        with pytest.warns(UserWarning, match="dx_rot, dy_rot"):
            translator(bend(csr=True)).to_elegant()

    def test_the_importer_inverts_the_exporter(self):
        written = terms(translator(bend()).to_elegant())
        raw = {
            "ElementParameter": list(written),
            "ParameterValue": [float(v) for v in written.values()],
        }
        data = {"hardware_type": "Dipole"}
        ElegantLatticeImporter._read_misalignment("q", data, raw)
        error = data["physical"]["error"]
        assert error["position"] == pytest.approx(ERRORS["position"])
        assert error["rotation"] == pytest.approx(ERRORS["rotation"])

    def test_pitch_without_malign_method_is_not_imported(self):
        raw = {"ElementParameter": ["pitch"], "ParameterValue": [1e-3]}
        data = {"hardware_type": "Quadrupole"}
        with pytest.warns(UserWarning, match="MALIGN_METHOD"):
            ElegantLatticeImporter._read_misalignment("q", data, raw)
        assert "error" not in data["physical"]


class TestMadx:
    def test_errors_go_in_a_macro_run_after_use(self):
        text = section(quad()).to_madx(beam={"particle": "electron", "energy": 1.0})
        assert "line_errors: macro = {" in text
        assert text.rstrip().endswith("exec, line_errors;")
        ealign = next(line for line in text.splitlines() if line.startswith("ealign"))
        # pivot moved from the centre to the entrance
        assert "dx = 0.002," in ealign and "dtheta = -0.004" in ealign
        assert "dpsi" not in ealign  # folded into tilt

    def test_aligned_lattices_are_unchanged(self):
        assert "macro" not in section(quad(error={})).to_madx(beam={"energy": 1.0})

    @pytest.mark.parametrize("make", [quad, bend], ids=["quad", "bend"])
    def test_the_importer_inverts_the_exporter(self, make, tmp_path):
        pytest.importorskip("cpymad")
        from laura.translator.converters.codes.madx import MadxLatticeImporter

        source = tmp_path / "line.madx"
        source.write_text(
            section(make()).to_madx(beam={"particle": "electron", "energy": 1.0})
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            imported = MadxLatticeImporter(
                source_file=str(source)
            ).create_laura_element_dictionary()["q"]
        error = imported.physical.error
        assert [error.position.x, error.position.y, error.position.z] == pytest.approx(
            [1e-3, -2e-3, 3e-3]
        )
        assert [error.rotation.theta, error.rotation.phi] == pytest.approx([4e-3, 5e-3])
        if make is bend:
            assert error.rotation.psi == pytest.approx(6e-3)
            assert imported.magnetic.tilt == pytest.approx(0.2)
        else:  # the roll error came back folded into tilt
            assert imported.magnetic.tilt == pytest.approx(0.106)


CASES = {
    "dx": {"position": {"x": 1e-3}},
    "dy": {"position": {"y": 1e-3}},
    "dz": {"position": {"z": 1e-3}},
    "dx_rot": {"rotation": {"theta": 1e-3}},
    "dy_rot": {"rotation": {"phi": 1e-3}},
    "dz_rot": {"rotation": {"psi": 1e-2}},
}


@pytest.mark.parametrize("make", [quad, bend], ids=["quad", "bend"])
@pytest.mark.parametrize("case", CASES)
def test_madx_and_xsuite_agree(make, case):
    """Both were checked against Bmad; compared on first-order effects only."""
    madx_class = pytest.importorskip("cpymad.madx").Madx
    xt = pytest.importorskip("xtrack")

    def madx(element):
        m = madx_class(stdout=False)
        m.input(section(element).to_madx(beam={"particle": "electron", "energy": 1}))
        tw = m.twiss(betx=1, bety=1)
        return np.array([tw.x[-1], tw.px[-1], tw.y[-1], tw.py[-1]])

    def xsuite(element):
        line = section(element).to_xsuite(beam_length=1, save=False)
        line.particle_ref = xt.Particles(p0c=1e9, mass0=xt.ELECTRON_MASS_EV)
        p = line.build_particles(x=0, px=0, y=0, py=0)
        line.track(p)
        return np.array([p.x[0], p.px[0], p.y[0], p.py[0]])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        by_madx = madx(make(CASES[case])) - madx(make({}))
        by_xsuite = xsuite(make(CASES[case])) - xsuite(make({}))
    if np.abs(by_madx).max() < 1e-5:
        pytest.skip("second-order effect; the codes' maps differ there")
    np.testing.assert_allclose(by_madx, by_xsuite, atol=1e-2 * np.abs(by_madx).max())


def strong_bend(error, tilt=0.2, angle=0.8):
    """Strong enough that the pivots' sagitta and the frame roll show."""
    return Dipole(
        name="q",
        machine_area="S",
        physical={"s": 0.5, "length": 1.0, "error": error},
        magnetic={
            "length": 1.0,
            "tilt": tilt,
            "multipoles": {
                "K0L": {"order": 0, "normal": angle},
                "K1L": {"order": 1, "normal": 0.6},
            },
        },
    )


def negative_bend(error):
    return strong_bend(error, tilt=-0.3, angle=-0.8)


@pytest.mark.parametrize("code", ["madx", "xsuite"])
@pytest.mark.parametrize(
    "make", [quad, strong_bend, negative_bend], ids=["quad", "bend", "negative_bend"]
)
@pytest.mark.parametrize("case", CASES)
def test_tracking_agrees_with_bmad(code, make, case, tmp_path):
    """Tracked off axis so a quad's roll shows."""
    from unit_tests.test_ac_dipole_export import LIBTAO, TestBmadParity

    if not LIBTAO.exists():
        pytest.skip("libtao is not installed")
    start = (1e-3, 5e-4)

    def by_madx(element):
        m = pytest.importorskip("cpymad.madx").Madx(stdout=False)
        m.input(section(element).to_madx(beam={"particle": "electron", "energy": 1}))
        tw = m.twiss(betx=1, bety=1, x=start[0], y=start[1])
        return np.array([tw.x[-1], tw.px[-1], tw.y[-1], tw.py[-1]])

    def by_bmad(element, run):
        tao = TestBmadParity.parsed(tmp_path / run, translator(element))
        tao.cmd(f"set particle_start x = {start[0]}")
        tao.cmd(f"set particle_start y = {start[1]}")
        orbit = tao.ele_orbit("Q")
        return np.array([orbit[k] for k in ("x", "px", "y", "py")])

    def by_xsuite(element):
        xt = pytest.importorskip("xtrack")
        line = section(element).to_xsuite(beam_length=1, save=False)
        line.particle_ref = xt.Particles(p0c=1e9, mass0=xt.ELECTRON_MASS_EV)
        p = line.build_particles(x=start[0], px=0, y=start[1], py=0)
        line.track(p)
        return np.array([p.x[0], p.px[0], p.y[0], p.py[0]])

    track = {"madx": by_madx, "xsuite": by_xsuite}[code]
    (tmp_path / "bare").mkdir()
    (tmp_path / "error").mkdir()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bare = by_bmad(make({}), "bare")
        np.testing.assert_allclose(track(make({})), bare, atol=1e-6)
        want = by_bmad(make(CASES[case]), "error") - bare
        got = track(make(CASES[case])) - track(make({}))
    np.testing.assert_allclose(got, want, atol=1e-2 * np.abs(want).max())


class TestXsuite:
    def test_bend_roll_error_rolls_the_field_only(self):
        pytest.importorskip("xtrack")
        native = section(bend()).to_xsuite(beam_length=1, save=False)["q"]
        assert native.rot_s_rad == pytest.approx(0.2)
        assert native.rot_s_rad_no_frame == pytest.approx(0.006)
        assert (native.rot_y_rad, native.rot_x_rad) == pytest.approx((-4e-3, -5e-3))
        assert native.rot_shift_anchor == pytest.approx(0.5)

    def test_misalignments_and_tilt_survive_the_round_trip(self, tmp_path):
        pytest.importorskip("xtrack")
        from laura.translator.converters.codes.xsuite import XsuiteLatticeImporter

        sext = Sextupole(
            name="sext",
            machine_area="S",
            physical={"s": 0.5, "length": 0.2, "error": ERRORS},
            magnetic={"length": 0.2, "k2l": 0.3, "tilt": 0.1},
        )
        cavity = RFCavity(
            name="cavity",
            machine_area="S",
            physical={"s": 1.5, "length": 0.5, "error": {"rotation": {"psi": 0.05}}},
            cavity={"frequency": 5e8},
            simulation={"field_amplitude": 1e6},
        )
        exported = section(sext, cavity)
        exported.directory = str(tmp_path)
        exported.to_xsuite(beam_length=1, save=True)
        importer = XsuiteLatticeImporter(source_file=str(tmp_path / "line.json"))
        imported = importer.create_element_dictionary()
        error = imported["sext"].physical.error
        assert [error.position.x, error.position.y, error.position.z] == pytest.approx(
            [1e-3, -2e-3, 3e-3]
        )
        assert [error.rotation.theta, error.rotation.phi] == pytest.approx([4e-3, 5e-3])
        assert imported["sext"].magnetic.tilt == pytest.approx(0.106)
        assert imported["cavity"].physical.error.rotation.psi == pytest.approx(0.05)

    def test_a_bend_round_trips_about_its_chord(self):
        pytest.importorskip("xtrack")
        from laura.translator.converters.codes.xsuite import xsuite_misalignment

        native = section(strong_bend(ERRORS)).to_xsuite(beam_length=1, save=False)["q"]
        assert native.shift_y != pytest.approx(-2e-3)  # moved to xtrack's roll axis
        imported = xsuite_misalignment(native)
        assert [imported[k] for k in ("dx", "dy", "dz", "dx_rot", "dy_rot", "dz_rot")] == (
            pytest.approx([1e-3, -2e-3, 3e-3, 4e-3, 5e-3, 6e-3])
        )
        assert imported["roll"] == pytest.approx(0.2)

    def test_an_entrance_anchor_is_re_centred(self):
        xt = pytest.importorskip("xtrack")
        from laura.translator.converters.codes.xsuite import xsuite_misalignment

        native = xt.Quadrupole(
            length=0.5, k1=1.0, shift_x=1e-3, rot_y_rad=-4e-3, rot_x_rad=-5e-3
        )
        centred = xsuite_misalignment(native)
        recentred = xt.Quadrupole(
            length=0.5,
            k1=1.0,
            shift_x=centred["dx"],
            shift_y=centred["dy"],
            shift_s=centred["dz"],
            rot_y_rad=-centred["dx_rot"],
            rot_x_rad=-centred["dy_rot"],
            rot_shift_anchor=0.25,
        )

        def track(element):
            line = xt.Line(elements=[element])
            line.particle_ref = xt.Particles(p0c=1e9)
            p = line.build_particles(x=0, px=0, y=0, py=0)
            line.track(p)
            return [p.x[0], p.px[0], p.y[0], p.py[0]]

        assert track(recentred) == pytest.approx(track(native), abs=1e-9)


def test_ocelot_round_trip():
    pytest.importorskip("ocelot")
    from laura.translator.converters.codes.ocelot import OcelotLatticeImporter

    error = {"position": {"x": 1e-3, "y": -2e-3}}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lattice = section(quad(error)).to_ocelot()
        imported = OcelotLatticeImporter(
            magnetic_lattice=lattice, name="line"
        ).create_laura_element_dictionary()
    q = imported["q"]
    assert [q.physical.error.position.x, q.physical.error.position.y] == pytest.approx(
        [1e-3, -2e-3]
    )
    assert q.magnetic.tilt == pytest.approx(0.1)


def test_cheetah_writes_offsets_and_roll():
    pytest.importorskip("cheetah")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        segment = section(quad()).to_cheetah()
    q = next(e for e in segment.elements if e.name == "q")
    assert q.misalignment.tolist() == pytest.approx([1e-3, -2e-3])
    assert float(q.tilt) == pytest.approx(0.106)
