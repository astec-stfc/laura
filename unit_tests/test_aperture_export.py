"""Apertures reach every code with their shape, half sizes and offset."""

import warnings

import numpy as np
import pytest

from laura.models.element import Aperture, Collimator
from laura.models.element_list import ElementList, SectionLattice
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.section import SectionLatticeTranslator

# a rectangle from x = -8 mm to +12 mm, y = +-20 mm
RECT = {
    "shape": "rectangular",
    "horizontal_size": 0.01,
    "vertical_size": 0.02,
    "horizontal_offset": 0.002,
}
# x inside / outside each edge of RECT; the thick collimator must cut at both ends
X = [-0.0085, -0.0075, 0.0115, 0.0125]
SURVIVES = [False, True, True, False]


def collimator(aperture=RECT, length=0.1, error=None):
    return Collimator(
        name="c1",
        machine_area="S",
        physical={"s": 0.5, "length": length, "error": error or {}},
        aperture=aperture,
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


def quiet(call, *args, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return call(*args, **kwargs)


@pytest.mark.parametrize(
    "method, expected",
    [
        ("to_elegant", "c1: rcol, x_max = 0.01, y_max = 0.02, l = 0.1, dx = 0.002"),
        ("to_madx", "apertype = rectangle, aperture = {0.01, 0.02}, aper_offset = {0.002, 0.0}"),
        ("to_bmad", "x1_limit = 0.008, x2_limit = 0.012, y1_limit = 0.02, y2_limit = 0.02"),
    ],
)
def test_text_exporters_write_the_offset_rectangle(method, expected):
    assert expected in getattr(translator(collimator()), method)()


def test_opal_writes_sizes_on_a_shaped_collimator():
    written = translator(collimator()).to_opal(0.0)
    assert written.startswith("c1: rcollimator, xsize = 0.01, ysize = 0.02")
    assert "dx = 0.002" in written


def test_radius_only_aperture_is_a_local_elliptical_collimator():
    """Not elegant's MAXAMP, which would limit every element downstream."""
    a1 = translator(
        Aperture(name="a1", machine_area="S", aperture={"radius": 0.01, "shape": "circular"})
    )
    assert a1.to_elegant().startswith("a1: ecol, x_max = 0.01, y_max = 0.01")
    assert a1.to_opal(0.0).startswith("a1: ecollimator, xsize = 0.01, ysize = 0.01")
    assert "apertype = ellipse, aperture = {0.01, 0.01}" in a1.to_madx()


@pytest.mark.parametrize(
    "aperture, error",
    [
        (RECT, None),
        # the ellipse's offset rides on shift_x, so a misalignment must add to it
        (RECT | {"shape": "elliptical", "horizontal_offset": 0.001}, {"position": {"x": 1e-3}}),
    ],
    ids=["rectangle", "ellipse_offset_plus_misalignment"],
)
def test_xsuite_tracks_the_aperture(aperture, error):
    xt = pytest.importorskip("xtrack")
    line = quiet(section(collimator(aperture, error=error)).to_xsuite, 4, save=False)
    assert line.element_names[-3:] == ["c1_entry", "c1", "c1_exit"]
    line.particle_ref = xt.Particles(p0c=1e9)
    line.build_tracker()
    # x' carries an entrance-centred particle out through the exit edge
    particles = line.build_particles(x=[0.0, *X], px=[0.13, 0, 0, 0, 0])
    line.track(particles)
    order = np.argsort(particles.particle_id)
    assert (particles.state[order] > 0).tolist() == [False, *SURVIVES]


def test_ocelot_aperture_cuts_at_its_offset():
    pytest.importorskip("ocelot")
    from ocelot import Navigator, ParticleArray, track

    lattice = quiet(section(collimator()).to_ocelot)
    apertures = [e for e in lattice.sequence if type(e).__name__ == "Aperture"]
    assert [(e.xmax, e.dx, e.type) for e in apertures] == [(0.01, 0.002, "rect")] * 2
    beam = ParticleArray(n=len(X))
    beam.rparticles[:] = 0.0
    beam.rparticles[0] = X
    beam.E = 1.0
    navi = Navigator(lattice)
    navi.activate_apertures()
    quiet(track, lattice, beam, navi, print_progress=False)
    assert sorted(beam.x()) == pytest.approx([x for x, s in zip(X, SURVIVES) if s])


def test_cheetah_aperture_cuts_at_both_ends():
    pytest.importorskip("cheetah")
    import torch
    from cheetah import ParticleBeam

    segment = quiet(section(collimator(RECT | {"horizontal_offset": 0.0})).to_cheetah)
    x = torch.tensor([0.0, 0.0095, 0.0105], dtype=torch.float64)
    px = torch.tensor([0.13, 0.0, 0.0], dtype=torch.float64)
    particles = torch.zeros(3, 7, dtype=torch.float64)
    particles[:, 0], particles[:, 1], particles[:, 6] = x, px, 1.0
    beam = ParticleBeam(particles, energy=torch.tensor(1e9, dtype=torch.float64))
    out = segment.track(beam)
    assert (out.survival_probabilities > 0.5).tolist() == [False, True, False]


def test_cheetah_warns_that_it_drops_the_offset():
    pytest.importorskip("cheetah")
    with pytest.warns(UserWarning, match="Cheetah apertures are centred"):
        translator(collimator()).to_cheetah()


def test_ocelot_round_trip_keeps_shape_size_and_offset():
    pytest.importorskip("ocelot")
    from laura.translator.converters.codes.ocelot import OcelotLatticeImporter

    thin = RECT | {"shape": "elliptical"}
    lattice = quiet(section(collimator(thin, length=0.0)).to_ocelot)
    imported = quiet(
        OcelotLatticeImporter(magnetic_lattice=lattice, name="line").create_laura_element_dictionary
    )
    aperture = next(e for e in imported.values() if e.hardware_type == "Aperture").aperture
    assert aperture.shape == "elliptical"
    assert [aperture.horizontal_size, aperture.vertical_size] == pytest.approx([0.01, 0.02])
    assert aperture.horizontal_offset == pytest.approx(0.002)
