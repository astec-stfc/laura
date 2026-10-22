import numpy as np
import pytest

at = pytest.importorskip("at")

from laura.models.element import (
    BeamPositionMonitor,
    CombinedCorrector,
    CrabCavity,
    Dipole,
    HorizontalACDipole,
    Marker,
    MatrixTransform,
    Quadrupole,
    RFCavity,
    Sextupole,
    Solenoid,
    VerticalACDipole,
    Wiggler,
)
from laura.models.element_list import ElementList, SectionLattice
from laura.translator import ATLatticeImporter
from laura.translator.converters.section import SectionLatticeTranslator

ENERGY = 3e9


def _section(elements):
    elements = {e.name: e for e in elements}
    section = SectionLattice(
        name="line", order=list(elements), elements=ElementList(elements=elements)
    )
    section.resolve_positions(section.elements.elements)
    return section


def _to_at(section, **kwargs):
    kwargs.setdefault("energy", ENERGY)
    return SectionLatticeTranslator.from_section(section).to_at(particle="electron", **kwargs)


def _element(**kwargs):
    return {"machine_area": "test", **kwargs}


def _matrix():
    r = np.eye(6)
    r[0, 1], r[4, 5] = 0.5, 0.01
    t = np.zeros((6, 6, 6))
    t[0, 0, 0] = 0.2
    return {"r_matrix": r, "t_matrix": t, "c_matrix": np.array([1e-4, 0, 0, 0, 2e-5, 0])}


def _every_type():
    return [
        Marker(name="start", **_element(physical={"s": 0.0})),
        Dipole(
            name="bend",
            **_element(
                physical={"s": 1.0, "length": 1.0},
                magnetic={
                    "length": 1.0,
                    "multipoles": {
                        "K0L": {"order": 0, "normal": 0.1},
                        "K1L": {"order": 1, "normal": -0.05},
                    },
                    "entrance_edge_angle": 0.05,
                    "exit_edge_angle": 0.04,
                    "gap": 0.02,
                    "edge_field_integral_entrance": 0.5,
                    "edge_field_integral_exit": 0.4,
                },
            ),
        ),
        Quadrupole(
            name="quad",
            **_element(
                physical={"s": 2.0, "length": 0.2, "error": {"position": {"x": 1e-3, "y": -2e-3}}},
                magnetic={"length": 0.2, "k1l": 0.3, "tilt": 0.1},
                aperture={"shape": "elliptical", "horizontal_size": 0.04, "vertical_size": 0.02},
            ),
        ),
        Sextupole(
            name="sext",
            **_element(
                physical={"s": 3.0, "length": 0.1},
                magnetic={"length": 0.1, "k2l": 1.2},
                aperture={"shape": "rectangular", "horizontal_size": 0.06, "vertical_size": 0.03},
            ),
        ),
        CombinedCorrector(
            name="kick",
            **_element(
                physical={"s": 3.5, "length": 0.1},
                magnetic={"length": 0.1, "horizontal_kick": 1e-4, "vertical_kick": -2e-4},
            ),
        ),
        BeamPositionMonitor(name="bpm", **_element(physical={"s": 4.0})),
        RFCavity(
            name="cav",
            **_element(
                physical={"s": 5.0, "length": 0.5},
                cavity={"frequency": 5e8, "phase": -30.0},
                simulation={"field_amplitude": 1e6},
            ),
        ),
        CrabCavity(
            name="crab",
            **_element(
                physical={"s": 6.0, "length": 0.5},
                cavity={"frequency": 4e8, "phase": 20.0},
                simulation={"field_amplitude": 2e6},
            ),
        ),
        Wiggler(
            name="wig",
            **_element(
                physical={"s": 8.0, "length": 1.0},
                magnetic={"length": 1.0, "period": 0.1, "num_periods": 10, "peak_magnetic_field": 1.2},
            ),
        ),
        Solenoid(
            name="sol",
            **_element(
                physical={"s": 9.0, "length": 0.5},
                magnetic={"length": 0.5, "fields": {"S0L": 0.25}},
            ),
        ),
        MatrixTransform(name="mat", **_element(physical={"s": 9.5}, simulation=_matrix())),
        HorizontalACDipole(
            name="hacd",
            **_element(
                physical={"s": 10.0},
                simulation={"field_amplitude": 100.0, "frequency": 1e4, "phase": 30.0, "ramp": [0, 10, 100, 110]},
            ),
        ),
        VerticalACDipole(
            name="vacd",
            **_element(
                physical={"s": 10.5},
                simulation={"field_amplitude": -50.0, "frequency": 2e4, "ramp": [0, 10, 100, 110]},
            ),
        ),
    ]


def _attributes(elem):
    return {k: v for k, v in vars(elem).items() if k != "FamName"}


def test_every_supported_type_round_trips_through_at():
    first = _to_at(_section(_every_type()))
    imported = ATLatticeImporter(lattice=first, name="line").create_section()["line"]
    second = _to_at(imported)
    assert [type(e).__name__ for e in second] == [type(e).__name__ for e in first]
    for a, b in zip(first, second):
        assert a.FamName == b.FamName
        attributes = _attributes(a)
        assert attributes.keys() == _attributes(b).keys(), a.FamName
        for key, value in attributes.items():
            if isinstance(value, str):
                assert getattr(b, key) == value, f"{a.FamName}.{key}"
                continue
            np.testing.assert_allclose(
                np.asarray(getattr(b, key), dtype=float),
                np.asarray(value, dtype=float),
                rtol=1e-12,
                atol=1e-15,
                err_msg=f"{a.FamName}.{key}",
            )
    assert imported.reference_energy == ENERGY


def test_imported_values_carry_laura_conventions():
    ring = _to_at(_section(_every_type()))
    elements = ATLatticeImporter(lattice=ring).create_element_dictionary()
    assert elements["quad"].magnetic.tilt == pytest.approx(0.1)
    assert elements["quad"].physical.error.position.x == pytest.approx(1e-3)
    assert elements["cav"].cavity.phase == pytest.approx(-30.0)
    assert elements["crab"].cavity.phase == pytest.approx(20.0)
    assert elements["sol"].magnetic.ks == pytest.approx(0.25)
    assert elements["hacd"].simulation.field_amplitude == pytest.approx(100.0)
    assert type(elements["vacd"]) is VerticalACDipole
    assert elements["vacd"].simulation.field_amplitude == pytest.approx(-50.0)
    for key, value in _matrix().items():
        np.testing.assert_allclose(getattr(elements["mat"].simulation, key), value)
    assert "drift" not in " ".join(elements).lower()


def test_matrix_r56_is_bmads():
    """Bmad's z is positive ahead, AT's ct positive behind: with R56 > 0 a
    particle with more energy arrives earlier."""
    r = np.eye(6)
    r[4, 5] = 1.0
    ring = _to_at(_section([MatrixTransform(name="mat", **_element(simulation={"r_matrix": r}))]))
    out, *_ = ring.track(np.array([[0.0], [0], [0], [0], [1e-3], [0]]), nturns=1)
    assert out[5].ravel() == pytest.approx([-1e-3])


def test_conventions_match_the_madx_route(tmp_path):
    """Kicks, tilt and voltage agree with ``at.load_madx``. AT's loader ignores
    ``LAG``, and exhausts memory parsing the alignment-error macro, so the
    quad's error is cleared."""
    section = _section([e for e in _every_type() if e.name in ("start", "quad", "kick", "cav")])
    quad = section.elements.elements["quad"]
    quad.physical.error = type(quad.physical.error)()
    native = _to_at(section)
    path = tmp_path / "line.madx"
    path.write_text(SectionLatticeTranslator.from_section(section).to_madx())
    madx = at.load_madx(str(path), use="line", energy=ENERGY)
    names = {e.FamName.lower(): e for e in madx}
    for elem in native:
        if elem.FamName in ("quad", "kick", "cav"):
            ref = names[elem.FamName]
            for key in ("R1", "R2", "KickAngle", "Voltage"):
                if hasattr(elem, key):
                    np.testing.assert_allclose(getattr(elem, key), getattr(ref, key), atol=1e-12)


def test_bend_pass_method_follows_edge_flags():
    bend = _every_type()[1]
    assert _to_at(_section([bend]))[0].PassMethod == "BndMPoleSymplectic4E2Pass"
    bend.simulation.edge2_effects = False
    native = _to_at(_section([bend]))[0]
    assert native.PassMethod == "BndMPoleSymplectic4Pass"
    assert native.FringeBendExit == 0
    imported = ATLatticeImporter(lattice=at.Lattice([native], energy=ENERGY)).create_element_dictionary()
    assert imported["bend"].simulation.edge2_effects is False


def test_steps_scale_with_length():
    bend = _every_type()[1]
    assert _to_at(_section([bend]))[0].NumIntSteps == 200


def test_energy_is_required():
    with pytest.raises(ValueError, match="design energy"):
        _to_at(_section(_every_type()[:2]), energy=None)


def test_importer_needs_exactly_one_source():
    with pytest.raises(ValueError, match="exactly one"):
        ATLatticeImporter()


def test_importer_reads_a_saved_lattice(tmp_path):
    ring = _to_at(_section(_every_type()[:4]))
    path = tmp_path / "line.m"
    at.save_m(ring, str(path))
    elements = ATLatticeImporter(source_file=str(path)).create_element_dictionary()
    assert list(elements) == ["start", "bend", "quad", "sext"]
