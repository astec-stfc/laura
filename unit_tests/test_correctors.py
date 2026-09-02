"""Tests for the corrector (Horizontal_Corrector/Vertical_Corrector/Combined_Corrector)
translation across codes.

Correctors use :class:`~laura.models.magnetic.Corrector_Magnet` (explicit
``horizontal_kick``/``vertical_kick`` fields, independent of each other) and
:class:`~laura.translator.converters.magnet.CorrectorTranslator`. These tests cover
the codes that need corrector-specific handling: Ocelot and Cheetah (whose native
elements are single-plane, requiring a split or a dedicated combined class) and
Xsuite (symbolic/functional kick passthrough, and the vertical-plane roll).
"""

import pytest

pytest.importorskip("easygdf")
pytest.importorskip("h5py")

from laura.models.baseModels import (  # noqa: E402
    set_functional_definitions,
    set_resolve_functional,
)
from laura.models.element import (  # noqa: E402
    Horizontal_Corrector,
    Vertical_Corrector,
    Combined_Corrector,
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
    hc = Horizontal_Corrector(
        name="hc1", machine_area="S", magnetic={"magnetic_length": length, "horizontal_kick": kick}
    )
    return translate_elements([hc])["hc1"]


def _vc(kick=0.03, length=0.1):
    vc = Vertical_Corrector(
        name="vc1", machine_area="S", magnetic={"magnetic_length": length, "vertical_kick": kick}
    )
    return translate_elements([vc])["vc1"]


def _cc(hkick=0.04, vkick=0.05, length=0.2):
    cc = Combined_Corrector(
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
        from laura.models.elementList import SectionLattice
        from laura.translator.converters.section import SectionLatticeTranslator

        cc = Combined_Corrector(
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
        hc = Horizontal_Corrector(
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
        hc = Horizontal_Corrector(
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
        cc = Combined_Corrector(
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
        hc = Horizontal_Corrector(
            name="hc1", machine_area="S", magnetic={"magnetic_length": 0.1, "horizontal_kick": "hc_kick"}
        )
        name, cls, properties = translate_elements([hc])["hc1"].to_xsuite(beam_length=1)
        assert properties["knl"] == pytest.approx([-0.02])


class TestCorrectorMagnetIsADipoleMagnet:
    """``Corrector_Magnet`` inherits ``Dipole_Magnet``: the two kicks are the
    normal/skew components of the same ``K0L``, so the whole ``MagneticElement``
    toolkit (calibration, gradient, rho) applies to a corrector."""

    def test_inherits_magnetic_element_toolkit(self):
        from laura.models.magnetic import Corrector_Magnet, Dipole_Magnet, MagneticElement

        m = Corrector_Magnet(magnetic_length=0.2, horizontal_kick=0.02)
        assert isinstance(m, (Dipole_Magnet, MagneticElement))
        assert m.KnL(0) == pytest.approx(0.02)
        assert m.Kn() == pytest.approx(0.1)
        assert m.rho == pytest.approx(10.0)

    def test_kicks_are_the_k0l_components(self):
        from laura.models.magnetic import Corrector_Magnet

        m = Corrector_Magnet(magnetic_length=0.1, horizontal_kick=0.02, vertical_kick=0.03)
        assert (m.multipoles.K0L.normal, m.multipoles.K0L.skew) == (0.02, 0.03)
        m.horizontal_kick = 0.5
        assert m.multipoles.K0L.normal == pytest.approx(0.5)
        assert m.vertical_kick == pytest.approx(0.03)

    @pytest.mark.parametrize("key", ["angle", "k0l", "kl"])
    def test_angle_and_k0l_transfer_to_the_horizontal_kick(self, key):
        from laura.models.magnetic import Corrector_Magnet

        assert Corrector_Magnet(**{"magnetic_length": 0.1, key: 0.02}).horizontal_kick == (
            pytest.approx(0.02)
        )

    @pytest.mark.parametrize(
        "key,lands_in_skew",
        [("angle", True), ("kl", True), ("k0l", False)],
    )
    def test_kick_from_angle_moves_the_value_to_the_named_plane(self, key, lands_in_skew):
        from laura.models.magnetic import Corrector_Magnet

        m = Corrector_Magnet(**{"magnetic_length": 0.1, key: 0.02, "skew": True})
        assert m.vertical_kick == pytest.approx(0.02 if lands_in_skew else 0.0)
        assert m.kick_from_angle() == pytest.approx(0.02)
        assert m.vertical_kick == pytest.approx(0.02)
        assert m.horizontal_kick == pytest.approx(0.0)

    def test_symbolic_kicks_survive_and_resolve(self):
        from laura.models.magnetic import Corrector_Magnet

        set_functional_definitions({"hk": 0.011, "vk": -0.004})
        m = Corrector_Magnet(magnetic_length=0.1, horizontal_kick="hk", vertical_kick="vk")
        assert (m.horizontal_kick, m.vertical_kick) == ("hk", "vk")
        assert m.resolved_kicks() == pytest.approx((0.011, -0.004))

    def test_legacy_lattice_magnetic_block_round_trips(self):
        """A corrector YAML written before this change carries a dipole-shaped
        ``magnetic`` block and no kick keys; it must still load, and must now
        keep the calibration data that ``IgnoreExtra`` used to silently drop."""
        from laura.models.element import Horizontal_Corrector

        legacy = {
            "length": 0.21, "order": 0, "skew": False, "settle_time": 45.0,
            "multipoles": {}, "systematic_multipoles": {}, "random_multipoles": {},
            "field_integral_coefficients": {"coefficients": [0]},
            "linear_saturation_coefficients": {"m": 0.142, "a": 0.0, "d": 0.0,
                                               "f": 0.0, "I0": 0.0, "I_max": 5.0,
                                               "L": 137.8},
            # computed fields present in a dumped file
            "rho": 0, "half_gap": 0.016,
        }
        hc = Horizontal_Corrector(name="hc1", machine_area="S", magnetic=legacy)
        assert hc.magnetic.length == pytest.approx(0.21)
        assert hc.magnetic.horizontal_kick == pytest.approx(0.0)
        assert hc.magnetic.settle_time == pytest.approx(45.0)
        assert hc.magnetic.linear_saturation_coefficients.m == pytest.approx(0.142)
        # Correctors inherit Dipole_Magnet's currentToK, which scales by 1/1000
        # (mrad-calibrated fit data) and adds the `degrees` key.
        converted = hc.magnetic.currentToK(current=1.0, momentum=35e6)
        assert converted["int_strength"] == pytest.approx(0.142 / 1000)
        assert "degrees" in converted
        # dumps by field name, not by the magnetic_length alias
        dumped = hc.model_dump()["magnetic"]
        assert "length" in dumped and "magnetic_length" not in dumped
        assert dumped["horizontal_kick"] == pytest.approx(0.0)
