import pytest


xt = pytest.importorskip("xtrack")

from laura.translator.converters.codes.xsuite import XsuiteLatticeImporter
from laura.models.element import Combined_Corrector, Marker
from laura.models.elementList import ElementList, SectionLattice
from laura.translator.converters.section import SectionLatticeTranslator


def test_xsuite_importer_uses_common_s_lifecycle():
    line = xt.Line(
        elements=[
            xt.Drift(length=1.0),
            xt.Quadrupole(length=0.5, k1=0.2),
            xt.Bend(length=0.4, angle=0.1),
            xt.Cavity(voltage=3e6, frequency=4e8, lag=30),
            xt.Marker(),
        ],
        element_names=["drift", "quad", "bend", "cavity", "marker"],
    )

    importer = XsuiteLatticeImporter(line=line, name="test")
    elements = importer.create_element_dictionary()
    layout = importer.create_layout()

    assert list(elements) == ["quad", "bend", "cavity", "marker"]
    assert elements["quad"].magnetic.KnL(1) == pytest.approx(0.1)
    assert elements["bend"].magnetic.KnL(0) == pytest.approx(-0.1)
    assert elements["cavity"].cavity.phase == pytest.approx(30)
    assert layout.sections["test"].order == list(elements)
    assert elements["quad"].physical.middle.z == pytest.approx(1.25)


def test_xsuite_importer_retains_environment_reference(tmp_path):
    env = xt.Environment()
    env["quad_k1l"] = 0.3
    env.new("quad", xt.Quadrupole, length=0.5, k1="quad_k1l / 0.5")
    line = env.new_line(components=["quad"])
    source = tmp_path / "line.json"
    line.to_json(source)

    importer = XsuiteLatticeImporter(source_file=str(source), name="test")
    elements = importer.create_element_dictionary()
    layout = importer.create_layout()

    assert importer.functional_definitions == {"quad_k1l": pytest.approx(0.3)}
    assert elements["quad"].magnetic.multipoles.K1L.normal == "quad_k1l"
    assert layout.functional_definitions == {"quad_k1l": pytest.approx(0.3)}
    assert layout.sections["test"].functional_definitions == {
        "quad_k1l": pytest.approx(0.3)
    }


def test_xsuite_environment_json_builds_one_section_per_line(tmp_path):
    env = xt.Environment()
    env["quad_k1l"] = 0.3
    env.new("q1", xt.Quadrupole, length=0.5, k1="quad_k1l / 0.5")
    env.new("q2", xt.Quadrupole, length=0.5, k1="quad_k1l / 0.5")
    env.new_line(name="section_a", components=["q1"])
    env.new_line(name="section_b", components=["q2"])
    source = tmp_path / "environment.json"
    env.to_json(source)

    layout = XsuiteLatticeImporter(source_file=str(source)).create_layout()

    assert list(layout.sections) == ["section_a", "section_b"]
    assert layout.functional_definitions == {"quad_k1l": pytest.approx(0.3)}


def test_xsuite_importer_maps_monitors_and_transverse_limits():
    line = xt.Line(
        elements=[
            xt.BeamPositionMonitor(
                start_at_turn=0, stop_at_turn=1, frev=1, sampling_frequency=1
            ),
            xt.BeamProfileMonitor(
                start_at_turn=0,
                stop_at_turn=1,
                frev=1,
                sampling_frequency=1,
                n=4,
                range=0.02,
            ),
            xt.ParticlesMonitor(start_at_turn=0, stop_at_turn=1, num_particles=1),
            xt.LimitEllipse(a=0.02, b=0.01),
            xt.LimitRect(min_x=-0.03, max_x=0.01, min_y=-0.01, max_y=0.01),
            xt.LimitPolygon(
                x_vertices=[-0.02, 0.02, 0.01],
                y_vertices=[-0.01, -0.01, 0.02],
            ),
            xt.LongitudinalLimitRect(
                min_zeta=-0.1,
                max_zeta=0.1,
                min_pzeta=-0.01,
                max_pzeta=0.01,
            ),
        ],
        element_names=["bpm", "profile", "particles", "ellipse", "rect", "polygon", "long"],
    )

    with pytest.warns(UserWarning) as caught:
        elements = XsuiteLatticeImporter(line=line).create_element_dictionary()

    assert elements["bpm"].hardware_type == "Beam_Position_Monitor"
    assert elements["profile"].hardware_type == "Screen"
    assert elements["particles"].hardware_type == "Screen"
    assert elements["ellipse"].hardware_type == "Collimator"
    assert elements["ellipse"].aperture.shape == "elliptical"
    assert elements["ellipse"].aperture.horizontal_size == pytest.approx(0.04)
    assert elements["rect"].aperture.horizontal_size == pytest.approx(0.04)
    assert elements["polygon"].aperture.vertical_size == pytest.approx(0.03)
    assert "long" not in elements

    messages = [str(item.message) for item in caught]
    assert any(
        "ParticlesMonitor" in message and "reduced to a Screen" in message
        for message in messages
    )
    assert any("LimitPolygon" in message and "bounding size" in message for message in messages)
    assert any("LongitudinalLimitRect" in message and "skipping" in message for message in messages)


def test_laura_xsuite_json_preserves_ambiguous_types_and_definitions(tmp_path):
    elements = {
        "marker": Marker(
            name="marker", machine_area="test", physical={"s": 0, "length": 0}
        ),
        "corrector": Combined_Corrector(
            name="corrector",
            machine_area="test",
            physical={"s": 0.5, "length": 0.1},
            magnetic={
                "length": 0.1,
                "horizontal_kick": 0.02,
                "vertical_kick": 0.03,
            },
        ),
    }
    section = SectionLattice(
        name="line",
        order=list(elements),
        elements=ElementList(elements=elements),
        functional_definitions={"unused_zero": 0},
    )
    section.resolve_positions(elements)
    translator = SectionLatticeTranslator.from_section(section)
    translator.directory = str(tmp_path)
    translator.to_xsuite(beam_length=1, save=True)

    importer = XsuiteLatticeImporter(source_file=str(tmp_path / "line.json"))
    imported = importer.create_element_dictionary()

    assert imported["marker"].hardware_type == "Marker"
    assert imported["corrector"].hardware_type == "Combined_Corrector"
    assert imported["corrector"].magnetic.horizontal_kick == pytest.approx(0.02)
    assert imported["corrector"].magnetic.vertical_kick == pytest.approx(0.03)
    assert importer.functional_definitions == {"unused_zero": 0}
