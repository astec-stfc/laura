import pytest


xt = pytest.importorskip("xtrack")

from laura.translator.converters.codes.xsuite import XsuiteLatticeImporter


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
