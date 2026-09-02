"""Tests for the corrector (Horizontal_Corrector/Vertical_Corrector/Combined_Corrector)
translation across codes.

Correctors use :class:`~laura.models.magnetic.CorrectorMagnet` (explicit
``horizontal_kick``/``vertical_kick`` fields, independent of each other) and
:class:`~laura.translator.converters.magnet.CorrectorTranslator`. These tests cover
the codes that need corrector-specific handling: Ocelot and Cheetah (whose native
elements are single-plane, requiring a split or a dedicated combined class) and
Xsuite (symbolic/functional kick passthrough, and the vertical-plane roll).
"""

import pytest

pytest.importorskip("easygdf")
pytest.importorskip("h5py")

from laura.models.base_models import (  # noqa: E402
    set_functional_definitions,
    set_resolve_functional,
)
from laura.models.element import (  # noqa: E402
    HorizontalCorrector,
    VerticalCorrector,
    CombinedCorrector,
)
from laura.translator.converters.converter import translate_elements  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_defs():
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)
    yield
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)


def _hc(kick=0.02, length=0.1):
    hc = HorizontalCorrector(
        name="hc1", machine_area="S", magnetic={"magnetic_length": length, "horizontal_kick": kick}
    )
    return translate_elements([hc])["hc1"]


def _vc(kick=0.03, length=0.1):
    vc = VerticalCorrector(
        name="vc1", machine_area="S", magnetic={"magnetic_length": length, "vertical_kick": kick}
    )
    return translate_elements([vc])["vc1"]


def _cc(hkick=0.04, vkick=0.05, length=0.2):
    cc = CombinedCorrector(
        name="cc1", machine_area="S",
        magnetic={"magnetic_length": length, "horizontal_kick": hkick, "vertical_kick": vkick},
    )
    return translate_elements([cc])["cc1"]


class TestOcelot:
    def test_horizontal_and_vertical_correctors(self):
        pytest.importorskip("ocelot")
        from ocelot.cpbd.elements import Hcor, Vcor

        h = _hc().to_ocelot()
        v = _vc().to_ocelot()
        assert isinstance(h, Hcor)
        assert h.element.angle == pytest.approx(0.02)
        assert isinstance(v, Vcor)
        assert v.element.angle == pytest.approx(0.03)

    def test_combined_corrector_splits_into_hcor_and_vcor_pair(self):
        pytest.importorskip("ocelot")
        from ocelot.cpbd.elements import Hcor, Vcor

        objs = _cc(hkick=0.04, vkick=0.05, length=0.2).to_ocelot()
        assert isinstance(objs, list) and len(objs) == 2
        hcor, vcor = objs
        assert isinstance(hcor, Hcor)
        assert isinstance(vcor, Vcor)
        # each half of the original length
        assert hcor.element.l == pytest.approx(0.1)
        assert vcor.element.l == pytest.approx(0.1)
        assert hcor.element.angle == pytest.approx(0.04)
        assert vcor.element.angle == pytest.approx(0.05)

    def test_section_translator_expands_combined_corrector(self):
        pytest.importorskip("ocelot")
        from laura.models.physical import PhysicalElement, Position
        from laura.models.element_list import SectionLattice
        from laura.translator.converters.section import SectionLatticeTranslator

        cc = CombinedCorrector(
            name="CC1", machine_area="S",
            magnetic={"magnetic_length": 0.2, "horizontal_kick": 0.04, "vertical_kick": 0.05},
            physical=PhysicalElement(length=0.2, middle=Position(x=0, y=0, z=1.0)),
        )
        section = SectionLattice(name="S1", order=["CC1"], elements=[cc])
        maglat = SectionLatticeTranslator.from_section(section).to_ocelot()
        names = [getattr(e, "id", None) for e in maglat.sequence]
        assert "CC1_H" in names
        assert "CC1_V" in names

    def test_functional_kick_is_resolved_numerically(self):
        pytest.importorskip("ocelot")
        set_functional_definitions({"hc_kick": 0.06})
        hc = HorizontalCorrector(
            name="hc1", machine_area="S", magnetic={"magnetic_length": 0.1, "horizontal_kick": "hc_kick"}
        )
        obj = translate_elements([hc])["hc1"].to_ocelot()
        # Ocelot has no symbolic support: value is baked in as a number.
        assert obj.element.angle == pytest.approx(0.06)


class TestCheetah:
    def test_horizontal_and_vertical_correctors(self):
        pytest.importorskip("cheetah")
        from cheetah.accelerator import HorizontalCorrector, VerticalCorrector

        h = _hc().to_cheetah()
        v = _vc().to_cheetah()
        assert isinstance(h, HorizontalCorrector)
        assert float(h.angle) == pytest.approx(0.02)
        assert isinstance(v, VerticalCorrector)
        assert float(v.angle) == pytest.approx(0.03)

    def test_combined_corrector_uses_combined_corrector_class(self):
        pytest.importorskip("cheetah")
        from cheetah.accelerator import CombinedCorrector

        obj = _cc(hkick=0.04, vkick=0.05).to_cheetah()
        assert isinstance(obj, CombinedCorrector)
        assert float(obj.horizontal_angle) == pytest.approx(0.04)
        assert float(obj.vertical_angle) == pytest.approx(0.05)


class TestXsuite:
    def _magnitudes(self, obj):
        name, cls, properties = obj
        return cls, properties

    def test_horizontal_corrector_knl(self):
        pytest.importorskip("xtrack")
        cls, properties = self._magnitudes(_hc(kick=0.05).to_xsuite(beam_length=1))
        # knl is negated relative to the LAURA/MAD-X/Ocelot/Cheetah kick sign
        # convention, verified against those codes by direct particle tracking.
        assert properties["knl"] == pytest.approx([-0.05])
        assert properties["ksl"] == pytest.approx([0.0])

    def test_vertical_corrector_ksl(self):
        pytest.importorskip("xtrack")
        cls, properties = self._magnitudes(_vc(kick=0.07).to_xsuite(beam_length=1))
        assert properties["knl"] == pytest.approx([-0.0])
        assert properties["ksl"] == pytest.approx([0.07])

    def test_combined_corrector_carries_both_planes(self):
        pytest.importorskip("xtrack")
        cls, properties = self._magnitudes(_cc(hkick=0.04, vkick=0.06).to_xsuite(beam_length=1))
        assert properties["knl"] == pytest.approx([-0.04])
        assert properties["ksl"] == pytest.approx([0.06])

    def test_tracking_matches_madx_ocelot_cheetah_sign_convention(self):
        pytest.importorskip("xtrack")
        import xtrack as xt

        # A positive kick deflects toward positive px/py, matching MAD-X's
        # HKICKER/VKICKER, Ocelot's Hcor/Vcor, and Cheetah's
        # Horizontal/VerticalCorrector (all verified directly).
        name, cls, properties = _cc(hkick=0.05, vkick=0.07, length=0.001).to_xsuite(beam_length=1)
        m = cls(**properties)
        p = xt.Particles(x=0, y=0, px=0, py=0, p0c=1e9)
        m.track(p)
        assert p.px[0] == pytest.approx(0.05, abs=1e-9)
        assert p.py[0] == pytest.approx(0.07, abs=1e-9)

    def test_symbolic_kick_is_deferred_and_live(self):
        pytest.importorskip("xtrack")
        import xtrack as xt

        set_functional_definitions({"hc_kick": 0.02})
        hc = HorizontalCorrector(
            name="hc1", machine_area="S", magnetic={"magnetic_length": 0.1, "horizontal_kick": "hc_kick"}
        )
        name, cls, properties = translate_elements([hc])["hc1"].to_xsuite(beam_length=1)
        assert properties["knl"] == ["-(hc_kick)"]

        env = xt.Environment()
        env["hc_kick"] = 0.02
        env.new(name, cls, **properties)
        line = env.new_line(components=[name])
        assert line[name].knl[0] == pytest.approx(-0.02)
        env["hc_kick"] = 0.09
        assert line[name].knl[0] == pytest.approx(-0.09)

    def test_combined_corrector_both_planes_symbolic_and_live(self):
        pytest.importorskip("xtrack")
        import xtrack as xt

        set_functional_definitions({"h_kick": 0.04, "v_kick": 0.06})
        cc = CombinedCorrector(
            name="cc1", machine_area="S",
            magnetic={"magnetic_length": 0.1, "horizontal_kick": "h_kick", "vertical_kick": "v_kick"},
        )
        name, cls, properties = translate_elements([cc])["cc1"].to_xsuite(beam_length=1)
        env = xt.Environment()
        env["h_kick"] = 0.04
        env["v_kick"] = 0.06
        env.new(name, cls, **properties)
        line = env.new_line(components=[name])
        assert line[name].knl[0] == pytest.approx(-0.04)
        assert line[name].ksl[0] == pytest.approx(0.06)
        env["v_kick"] = 0.5
        assert line[name].ksl[0] == pytest.approx(0.5)

    def test_resolved_mode_bakes_numbers(self):
        pytest.importorskip("xtrack")
        set_functional_definitions({"hc_kick": 0.02})
        set_resolve_functional(True)
        hc = HorizontalCorrector(
            name="hc1", machine_area="S", magnetic={"magnetic_length": 0.1, "horizontal_kick": "hc_kick"}
        )
        name, cls, properties = translate_elements([hc])["hc1"].to_xsuite(beam_length=1)
        assert properties["knl"] == pytest.approx([-0.02])
