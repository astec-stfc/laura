"""Collimators and apertures become Xsuite black absorbers (thin limits at both ends)."""

import pytest

xt = pytest.importorskip("xtrack")

from laura.models.element import Collimator  # noqa: E402
from laura.translator.converters.converter import translate_elements  # noqa: E402


def _limit(**aperture):
    col = Collimator(name="col", machine_area="S", aperture=aperture,
                     physical={"length": 0.1, "middle": {"z": 0.5}})
    return translate_elements([col])["col"].xsuite_limit()


def test_round_and_elliptical_apertures_are_ellipses():
    cls, props = _limit(shape="circular", radius=1e-3)
    assert cls is xt.LimitEllipse and props == {"a": 1e-3, "b": 1e-3}
    cls, props = _limit(shape="elliptical", horizontal_size=2e-3, vertical_size=4e-3)
    assert cls is xt.LimitEllipse and props == {"a": 1e-3, "b": 2e-3}


def test_slits_limit_only_the_planes_with_a_size():
    cls, props = _limit(shape="planar", horizontal_size=2e-3)
    assert cls is xt.LimitRect and props == {"min_x": -1e-3, "max_x": 1e-3}
    cls, props = _limit(shape="rectangular", horizontal_size=2e-3, vertical_size=4e-3)
    assert props == {"min_x": -1e-3, "max_x": 1e-3, "min_y": -2e-3, "max_y": 2e-3}


def test_an_aperture_without_a_size_has_no_limit():
    assert _limit(shape="rectangular") is None


def test_the_line_gets_a_limit_at_each_end_of_the_collimator():
    from laura.models.element import Marker
    from laura.models.element_list import SectionLattice
    from laura.translator.converters.section import SectionLatticeTranslator

    elements = [
        Marker(name="m1", machine_area="S", hardware_class="Marker", physical={"middle": {"z": 0.0}}),
        Collimator(name="col", machine_area="S", aperture={"shape": "circular", "radius": 1e-3},
                   physical={"length": 0.1, "middle": {"z": 0.5}}),
        Marker(name="m2", machine_area="S", hardware_class="Marker", physical={"middle": {"z": 1.0}}),
    ]
    section = SectionLattice(name="S", elements=elements, order=[e.name for e in elements])
    line = SectionLatticeTranslator.from_section(section).to_xsuite(beam_length=1, save=False)
    names = list(line.element_names)
    i = names.index("col")
    assert names[i - 1] == "col_aperture_entry" and names[i + 1] == "col_aperture_exit"
    assert isinstance(line["col_aperture_entry"], xt.LimitEllipse)
    assert line.get_length() == pytest.approx(1.0)
