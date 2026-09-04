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
        # Correctors take MagneticElement's conversions, NOT Dipole_Magnet's
        # extra 1/1000 -- see TestCorrectorCurrentConversion for the check
        # against the CLARA magnet table that settles the scaling.
        converted = hc.magnetic.currentToK(current=1.0, momentum=35.0)
        assert converted["int_strength"] == pytest.approx(0.142)
        # dumps by field name, not by the magnetic_length alias
        dumped = hc.model_dump()["magnetic"]
        assert "length" in dumped and "magnetic_length" not in dumped
        assert dumped["horizontal_kick"] == pytest.approx(0.0)


# The CLARA magnet table is the source of truth for magnet calibration; these
# tests pin corrector behaviour against it rather than against a hand-picked
# expected number. pandas/openpyxl only ship with the [test] extra.
_MAGNET_TABLE = "laura/Importers/CLARA Magnet Table v6.xlsx"


def _corrector_table_rows():
    pd = pytest.importorskip("pandas")
    pytest.importorskip("openpyxl")
    import os
    if not os.path.exists(_MAGNET_TABLE):
        pytest.skip("CLARA magnet table not available")
    df = pd.read_excel(_MAGNET_TABLE, sheet_name="Table", skiprows=2).fillna(0)
    cor = df[df["type"].astype(str).str.upper().isin(["HCOR", "VCOR", "HVCOR"])]
    return cor[(cor["K or angle"] != 0) & (cor["current [A].1"] != 0)]


def _magnet_from_row(row):
    from laura.models.magnetic import Corrector_Magnet

    return Corrector_Magnet(
        magnetic_length=row["magnetic length [mm]"] / 1000,
        linear_saturation_coefficients={
            "m": row["slope [units/A]"], "I_max": row["max current [A]"],
            "f": row["f [units/A³]"], "a": row["a [units/A²]"],
            "I0": row["I0 [A]"], "d": row["d [units]"],
            "L": row["magnetic length [mm]"],
        },
    )


class TestCorrectorCurrentConversion:
    """Current->angle for a corrector, checked against the magnet table.

    The table's own "K or angle" column is reproduced by
    ``angle[rad] = (c/1e9) * slope[T.mm/A] * I[A] / p[MeV/c]`` -- which is
    MagneticElement.currentToK at order 0. Dipole_Magnet rescales that by a
    further 1/1000, so a corrector must NOT inherit the dipole version.
    """

    def test_matches_the_magnet_table_for_every_corrector(self):
        rows = _corrector_table_rows()
        assert len(rows) > 20, "magnet table gave suspiciously few corrector rows"
        for _, row in rows.iterrows():
            mag = _magnet_from_row(row)
            angle_mrad = mag.currentToAngle(row["current [A].1"], row["momentum [MeV/c]"]) * 1000
            assert angle_mrad == pytest.approx(row["K or angle"], rel=1e-6), (
                f"{row['machine']}-{row['region']}-{row['type']}-{int(row['number'])}"
            )

    def test_angle_to_current_is_the_inverse(self):
        for _, row in _corrector_table_rows().iterrows():
            mag = _magnet_from_row(row)
            angle = mag.currentToAngle(row["current [A].1"], row["momentum [MeV/c]"])
            assert mag.angle_to_current(angle, row["momentum [MeV/c]"]) == pytest.approx(
                row["current [A].1"], rel=1e-6
            )

    def test_dipole_and_corrector_agree_on_the_same_fit(self):
        """Both are order-0, so the same coefficients must give the same KL --
        the workbook's DIP and HCOR branches are the same number in radians.
        They differ only in the reporting unit each adds on top."""
        import math
        from laura.models.magnetic import Corrector_Magnet, Dipole_Magnet

        coeffs = {"m": 0.0238, "I_max": 0, "f": 0, "a": 0, "I0": 0, "d": 0, "L": 128.65}
        cor = Corrector_Magnet(magnetic_length=0.12865, linear_saturation_coefficients=coeffs)
        dip = Dipole_Magnet(length=0.12865, linear_saturation_coefficients=coeffs)
        kl = cor.currentToK(1.0, momentum=6.0)["KL"]
        assert dip.currentToK(1.0, momentum=6.0)["KL"] == pytest.approx(kl)
        # corrector reports radians, dipole degrees -- both off the same KL
        assert cor.currentToAngle(1.0, 6.0) == pytest.approx(kl)
        assert dip.currentToAngle(1.0, 6.0) == pytest.approx(math.degrees(kl))


class TestCombinedCorrectorHasTwoMagnets:
    """The two planes are separate magnets with separate windings; the magnet
    table gives them different slopes and lengths, so they must not share a
    calibration."""

    def test_planes_are_independent_objects(self):
        # A shared flat block is copied to both planes; writing one plane's
        # calibration must not touch the other's.
        cc = Combined_Corrector(
            name="cc", machine_area="S",
            magnetic={"linear_saturation_coefficients": {"m": 0.024493, "I_max": 0, "f": 0,
                                                         "a": 0, "I0": 0, "d": 0, "L": 130.0}},
        )
        assert cc.magnetic.horizontal is not cc.magnetic.vertical
        cc.magnetic.vertical.linear_saturation_coefficients.m = 0.023798
        assert cc.magnetic.vertical.linear_saturation_coefficients.m == pytest.approx(0.023798)
        assert cc.magnetic.horizontal.linear_saturation_coefficients.m == pytest.approx(0.024493)

    def test_current_conversion_is_per_plane(self):
        # CLA-S01 corrector 1, both planes, straight from the magnet table.
        cc = Combined_Corrector(
            name="cc", machine_area="S",
            magnetic={
                "horizontal": {"magnetic_length": 0.131245, "linear_saturation_coefficients":
                               {"m": 0.024493122, "I_max": 0, "f": 0, "a": 0, "I0": 0,
                                "d": 0, "L": 131.245312}},
                "vertical": {"magnetic_length": 0.128651, "linear_saturation_coefficients":
                             {"m": 0.023797567, "I_max": 0, "f": 0, "a": 0, "I0": 0,
                              "d": 0, "L": 128.650950}},
            },
        )
        h = cc.magnetic.currentToAngle(1.0, 6.0) * 1000
        v = cc.magnetic.currentToAngle(1.0, 6.0, skew=True) * 1000
        assert h == pytest.approx(1.223797, rel=1e-5)
        assert v == pytest.approx(1.189055, rel=1e-5)
        assert h != v

    def test_legacy_flat_magnetic_block_still_loads(self):
        """All 137 combined-corrector files predate the split and carry one flat
        magnetic block; it must load, copying the shared calibration to both
        planes while each plane keeps only its own kick."""
        cc = Combined_Corrector(
            name="cc", machine_area="S",
            magnetic={"length": 0.21, "order": 0, "horizontal_kick": 0.004,
                      "vertical_kick": 0.006, "settle_time": 45.0,
                      "linear_saturation_coefficients": {"m": 0.142, "I_max": 0, "f": 0,
                                                         "a": 0, "I0": 0, "d": 0, "L": 137.8}},
        )
        assert cc.magnetic.horizontal_kick == pytest.approx(0.004)
        assert cc.magnetic.vertical_kick == pytest.approx(0.006)
        assert cc.magnetic.length == pytest.approx(0.21)
        assert cc.magnetic.settle_time == pytest.approx(45.0)   # __getattr__ fallback
        for plane in (cc.magnetic.horizontal, cc.magnetic.vertical):
            assert plane.linear_saturation_coefficients.m == pytest.approx(0.142)
        # each plane holds only its own kick, so neither deflects in both planes
        assert cc.magnetic.horizontal.vertical_kick == pytest.approx(0.0)
        assert cc.magnetic.vertical.horizontal_kick == pytest.approx(0.0)

    def test_round_trips_through_model_dump(self):
        cc = Combined_Corrector(
            name="cc", machine_area="S",
            magnetic={"length": 0.21, "horizontal_kick": 0.004, "vertical_kick": 0.006,
                      "linear_saturation_coefficients": {"m": 0.142, "I_max": 0, "f": 0,
                                                         "a": 0, "I0": 0, "d": 0, "L": 137.8}},
        )
        cc.magnetic.vertical.linear_saturation_coefficients.m = 0.15
        rt = Combined_Corrector(name="cc", machine_area="S",
                                magnetic=cc.model_dump()["magnetic"])
        assert rt.magnetic.horizontal_kick == pytest.approx(0.004)
        assert rt.magnetic.vertical_kick == pytest.approx(0.006)
        assert rt.magnetic.vertical.linear_saturation_coefficients.m == pytest.approx(0.15)

    def test_translator_keeps_both_planes_and_the_length(self):
        cc = Combined_Corrector(
            name="cc1", machine_area="S",
            magnetic={"magnetic_length": 0.2, "horizontal_kick": 0.04, "vertical_kick": 0.05},
        )
        t = translate_elements([cc])["cc1"]
        assert t.hangle == pytest.approx(0.04)
        assert t.vangle == pytest.approx(0.05)
        assert t.length == pytest.approx(0.2)


class TestAgainstMagnetTableFormulas:
    """LAURA's excitation-curve maths, checked against the workbook's own
    formulas rather than against hand-picked numbers.

    Column AC is ``SWITCH(type, "DIP", 360/(2000*PI()), "QUAD", 1000/Y,
    "HCOR", 1, "VCOR", 1) * c_ * AA / A`` with ``c_ = 299.792458`` and AA the
    integrated strength. Both order-0 branches reduce to the *same* thing in
    radians -- ``angle[rad] = (c/1e9) * AA / p`` -- because 360/(2000*pi) is
    exactly (180/pi)/1000. That is `LinearSaturationFit.currentToK`'s order-0
    ``KL``, for dipoles and correctors alike.
    """

    def test_dipole_and_corrector_angle_branches_agree_in_radians(self):
        import math
        c_ = 299.792458
        dip_to_rad = 360 / (2000 * math.pi) * math.pi / 180   # AC[deg] -> rad
        cor_to_rad = 1 / 1000                                  # AC[mrad] -> rad
        assert dip_to_rad == pytest.approx(cor_to_rad, rel=1e-15)
        from laura.models.constants import speed_of_light
        assert dip_to_rad * c_ == pytest.approx(speed_of_light / 1e9, rel=1e-12)

    def test_forward_conversions_match_every_row(self):
        import math
        rows = _corrector_table_rows()
        for _, row in rows.iterrows():
            mag = _magnet_from_row(row)
            out = mag.linear_saturation_coefficients.currentToK(
                current=row["current [A].1"], momentum=row["momentum [MeV/c]"])
            assert out["int_strength"] == pytest.approx(
                row["integrated strength.1"], rel=1e-9)
            assert out["KL"] * 1000 == pytest.approx(row["K or angle"], rel=1e-7)

    def test_saturating_reverse_branch_is_real_and_correct(self):
        """The trigonometric cubic needs sqrt(-(p/3)**3) with a positive cube
        root. Both signs were wrong, so a fit with f < 0 (real quadrupole fits
        have it) drove Sqrt negative and returned a complex current ~40% low."""
        from laura.models.magnetic import LinearSaturationFit

        pd = pytest.importorskip("pandas")
        pytest.importorskip("openpyxl")
        import os
        if not os.path.exists(_MAGNET_TABLE):
            pytest.skip("CLARA magnet table not available")
        df = pd.read_excel(_MAGNET_TABLE, sheet_name="Table", skiprows=2).fillna(0)
        # A real quadrupole fit with f < 0, driven above its threshold current.
        sat = df[(df["type"].astype(str).str.upper() == "QUAD")
                 & (df["f [units/A³]"] < 0)
                 & (df["max current [A]"] > 0)
                 & (df["current [A].1"].abs() >= df["max current [A]"])]
        if not len(sat):
            pytest.skip("no saturating quadrupole row in the magnet table")
        row = sat.iloc[0]
        lsf = LinearSaturationFit(
            m=row["slope [units/A]"], I_max=row["max current [A]"],
            f=row["f [units/A³]"], a=row["a [units/A²]"], I0=row["I0 [A]"],
            d=row["d [units]"], L=row["magnetic length [mm]"])
        lsf.order = 1
        current, momentum = row["current [A].1"], row["momentum [MeV/c]"]
        K = lsf.currentToK(current, momentum=momentum)["K"]
        back = lsf.KToCurrent(K, momentum)
        assert not isinstance(back, complex), "cubic branch returned a complex current"
        assert float(back) == pytest.approx(current, rel=1e-6)

    def test_dipole_current_to_angle_has_no_extra_thousandth(self):
        """CLA-SP3-MAG-DIP-01 is a 30 deg spectrometer dipole with a 240 MeV/c
        nominal momentum. 300 A over a 30 deg bend must give ~238 MeV/c, not
        0.238: `Dipole_Magnet` used to rescale `LinearSaturationFit`'s already
        correct order-0 KL by a further 1/1000."""
        import math
        from laura.models.magnetic import Dipole_Magnet

        dip = Dipole_Magnet(length=0.4, linear_saturation_coefficients=dict(
            m=1.3966746927879516, I_max=246.90388362886958, f=0,
            a=-0.0020829194836779275, I0=596.1589358551605,
            d=598.7346914311352, L=400.0))
        kl_per_mev = dip.currentToK(300.0, momentum=1.0)["KL"]
        assert kl_per_mev / math.radians(30.0) == pytest.approx(238.2, rel=1e-3)
        # and the reported angle is degrees, round-tripping back to the current
        out = dip.currentToK(300.0, momentum=238.209)
        assert out["degrees"] == pytest.approx(30.0, rel=1e-4)
        assert dip.currentToAngle(300.0, 238.209) == pytest.approx(30.0, rel=1e-4)
        assert float(dip.KLToCurrent(out["KL"], 238.209)) == pytest.approx(300.0, rel=1e-6)

    def test_every_dipole_row_matches_the_table(self):
        import math
        pd = pytest.importorskip("pandas")
        pytest.importorskip("openpyxl")
        import os
        if not os.path.exists(_MAGNET_TABLE):
            pytest.skip("CLARA magnet table not available")
        from laura.models.magnetic import Dipole_Magnet

        df = pd.read_excel(_MAGNET_TABLE, sheet_name="Table", skiprows=2).fillna(0)
        rows = df[(df["type"].astype(str).str.upper() == "DIP")
                  & (df["K or angle"] != 0) & (df["current [A].1"] != 0)
                  & (df["magnetic length [mm]"] != 0)]
        assert len(rows) >= 2, "no usable DIP rows in the in-repo magnet table"
        for _, row in rows.iterrows():
            dip = Dipole_Magnet(
                length=row["magnetic length [mm]"] / 1000,
                linear_saturation_coefficients={
                    "m": row["slope [units/A]"], "I_max": row["max current [A]"],
                    "f": row["f [units/A³]"], "a": row["a [units/A²]"],
                    "I0": row["I0 [A]"], "d": row["d [units]"],
                    "L": row["magnetic length [mm]"]})
            I, p = row["current [A].1"], row["momentum [MeV/c]"]
            assert dip.currentToAngle(I, p) == pytest.approx(row["K or angle"], rel=1e-7)
            assert float(dip.KLToCurrent(dip.currentToK(I, p)["KL"], p)) == pytest.approx(
                I, rel=1e-6)
