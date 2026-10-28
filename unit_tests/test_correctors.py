"""Corrector models and translation; Ocelot/Cheetah correctors are single-plane."""

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
    @pytest.fixture(autouse=True)
    def _requires_ocelot(self):
        pytest.importorskip("ocelot")

    def test_horizontal_and_vertical_correctors(self):
        from ocelot.cpbd.elements import Hcor, Vcor

        h = _hc().to_ocelot()
        v = _vc().to_ocelot()
        assert isinstance(h, Hcor)
        assert h.element.angle == pytest.approx(0.02)
        assert isinstance(v, Vcor)
        assert v.element.angle == pytest.approx(0.03)

    def test_combined_corrector_splits_into_hcor_and_vcor_pair(self):
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
        set_functional_definitions({"hc_kick": 0.06})
        hc = HorizontalCorrector(
            name="hc1", machine_area="S", magnetic={"magnetic_length": 0.1, "horizontal_kick": "hc_kick"}
        )
        obj = translate_elements([hc])["hc1"].to_ocelot()
        # Ocelot has no symbolic support: value is baked in as a number.
        assert obj.element.angle == pytest.approx(0.06)


class TestCheetah:
    @pytest.fixture(autouse=True)
    def _requires_cheetah(self):
        pytest.importorskip("cheetah")

    def test_horizontal_and_vertical_correctors(self):
        from cheetah.accelerator import HorizontalCorrector, VerticalCorrector

        h = _hc().to_cheetah()
        v = _vc().to_cheetah()
        assert isinstance(h, HorizontalCorrector)
        assert float(h.angle) == pytest.approx(0.02)
        assert isinstance(v, VerticalCorrector)
        assert float(v.angle) == pytest.approx(0.03)

    def test_combined_corrector_uses_combined_corrector_class(self):
        from cheetah.accelerator import CombinedCorrector

        obj = _cc(hkick=0.04, vkick=0.05).to_cheetah()
        assert isinstance(obj, CombinedCorrector)
        assert float(obj.horizontal_angle) == pytest.approx(0.04)
        assert float(obj.vertical_angle) == pytest.approx(0.05)


class TestXsuite:
    @pytest.fixture(autouse=True)
    def _requires_xtrack(self):
        pytest.importorskip("xtrack")

    # knl is negated relative to the LAURA/MAD-X/Ocelot/Cheetah kick sign (checked by tracking).
    @pytest.mark.parametrize(
        "build, kicks, knl, ksl",
        [
            (_hc, {"kick": 0.05}, -0.05, 0.0),
            (_vc, {"kick": 0.07}, -0.0, 0.07),
            (_cc, {"hkick": 0.04, "vkick": 0.06}, -0.04, 0.06),
        ],
        ids=["horizontal", "vertical", "combined"],
    )
    def test_kick_planes_map_to_knl_and_ksl(self, build, kicks, knl, ksl):
        _, _, properties = build(**kicks).to_xsuite(beam_length=1)
        assert properties["knl"] == pytest.approx([knl])
        assert properties["ksl"] == pytest.approx([ksl])

    def test_tracking_matches_madx_ocelot_cheetah_sign_convention(self):
        import xtrack as xt

        name, cls, properties = _cc(hkick=0.05, vkick=0.07, length=0.001).to_xsuite(beam_length=1)
        m = cls(**properties)
        p = xt.Particles(x=0, y=0, px=0, py=0, p0c=1e9)
        m.track(p)
        assert p.px[0] == pytest.approx(0.05, abs=1e-9)
        assert p.py[0] == pytest.approx(0.07, abs=1e-9)

    def test_symbolic_kick_is_deferred_and_live(self):
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
        set_functional_definitions({"hc_kick": 0.02})
        set_resolve_functional(True)
        hc = HorizontalCorrector(
            name="hc1", machine_area="S", magnetic={"magnetic_length": 0.1, "horizontal_kick": "hc_kick"}
        )
        name, cls, properties = translate_elements([hc])["hc1"].to_xsuite(beam_length=1)
        assert properties["knl"] == pytest.approx([-0.02])


class TestCorrectorMagnetIsADipoleMagnet:
    """The two kicks are the normal/skew parts of one ``K0L``."""

    def test_inherits_magnetic_element_toolkit(self):
        from laura.models.magnetic import CorrectorMagnet, DipoleMagnet, MagneticElement

        m = CorrectorMagnet(magnetic_length=0.2, horizontal_kick=0.02)
        assert isinstance(m, (DipoleMagnet, MagneticElement))
        assert m.KnL(0) == pytest.approx(0.02)
        assert m.Kn() == pytest.approx(0.1)
        assert m.rho == pytest.approx(10.0)

    def test_kicks_are_the_k0l_components(self):
        from laura.models.magnetic import CorrectorMagnet

        m = CorrectorMagnet(magnetic_length=0.1, horizontal_kick=0.02, vertical_kick=0.03)
        assert (m.multipoles.K0L.normal, m.multipoles.K0L.skew) == (0.02, 0.03)
        m.horizontal_kick = 0.5
        assert m.multipoles.K0L.normal == pytest.approx(0.5)
        assert m.vertical_kick == pytest.approx(0.03)

    @pytest.mark.parametrize("key", ["angle", "k0l", "kl"])
    def test_angle_and_k0l_transfer_to_the_horizontal_kick(self, key):
        from laura.models.magnetic import CorrectorMagnet

        assert CorrectorMagnet(**{"magnetic_length": 0.1, key: 0.02}).horizontal_kick == (
            pytest.approx(0.02)
        )

    @pytest.mark.parametrize(
        "key,lands_in_skew",
        [("angle", True), ("kl", True), ("k0l", False)],
    )
    def test_kick_from_angle_moves_the_value_to_the_named_plane(self, key, lands_in_skew):
        from laura.models.magnetic import CorrectorMagnet

        m = CorrectorMagnet(**{"magnetic_length": 0.1, key: 0.02, "skew": True})
        assert m.vertical_kick == pytest.approx(0.02 if lands_in_skew else 0.0)
        assert m.kick_from_angle() == pytest.approx(0.02)
        assert m.vertical_kick == pytest.approx(0.02)
        assert m.horizontal_kick == pytest.approx(0.0)

    def test_symbolic_kicks_survive_and_resolve(self):
        from laura.models.magnetic import CorrectorMagnet

        set_functional_definitions({"hk": 0.011, "vk": -0.004})
        m = CorrectorMagnet(magnetic_length=0.1, horizontal_kick="hk", vertical_kick="vk")
        assert (m.horizontal_kick, m.vertical_kick) == ("hk", "vk")
        assert m.resolved_kicks() == pytest.approx((0.011, -0.004))

    def test_legacy_lattice_magnetic_block_round_trips(self):
        """Older corrector YAML has a dipole-shaped ``magnetic`` block and no kick keys."""
        from laura.models.element import HorizontalCorrector

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
        hc = HorizontalCorrector(name="hc1", machine_area="S", magnetic=legacy)
        assert hc.magnetic.length == pytest.approx(0.21)
        assert hc.magnetic.horizontal_kick == pytest.approx(0.0)
        assert hc.magnetic.settle_time == pytest.approx(45.0)
        assert hc.magnetic.linear_saturation_coefficients.m == pytest.approx(0.142)
        converted = hc.magnetic.current_to_k(current=1.0, momentum=35.0)
        assert converted["int_strength"] == pytest.approx(0.142)
        dumped = hc.model_dump()["magnetic"]
        assert "length" in dumped and "magnetic_length" not in dumped
        assert dumped["horizontal_kick"] == pytest.approx(0.0)


# The CLARA magnet table is the calibration source of truth; openpyxl ships only with [test].
_MAGNET_TABLE = "laura/importers/CLARA Magnet Table v6.xlsx"


def _magnet_table():
    """Blanks read as 0; a repeated header gets ``.1`` (``current [A].1`` is the operating current)."""
    openpyxl = pytest.importorskip("openpyxl")
    import os
    if not os.path.exists(_MAGNET_TABLE):
        pytest.skip("CLARA magnet table not available")
    sheet = openpyxl.load_workbook(_MAGNET_TABLE, read_only=True, data_only=True)["Table"]
    rows = list(sheet.iter_rows(values_only=True))
    header = [f"{h}.1" if h in rows[2][:i] else h for i, h in enumerate(rows[2])]
    return [{k: 0 if v is None else v for k, v in zip(header, r)} for r in rows[3:]]


def _corrector_table_rows():
    return [r for r in _magnet_table()
            if str(r["type"]).upper() in ("HCOR", "VCOR", "HVCOR")
            and r["K or angle"] != 0 and r["current [A].1"] != 0]


def _magnet_from_row(row):
    from laura.models.magnetic import CorrectorMagnet

    return CorrectorMagnet(
        magnetic_length=row["magnetic length [mm]"] / 1000,
        linear_saturation_coefficients={
            "m": row["slope [units/A]"], "I_max": row["max current [A]"],
            "f": row["f [units/A³]"], "a": row["a [units/A²]"],
            "I0": row["I0 [A]"], "d": row["d [units]"],
            "L": row["magnetic length [mm]"],
        },
    )


class TestCorrectorCurrentConversion:
    """The table's "K or angle" is ``(c/1e9) * slope[T.mm/A] * I[A] / p[MeV/c]`` rad."""

    def test_matches_the_magnet_table_for_every_corrector(self):
        rows = _corrector_table_rows()
        assert len(rows) > 20, "magnet table gave suspiciously few corrector rows"
        for row in rows:
            mag = _magnet_from_row(row)
            angle_mrad = mag.current_to_angle(row["current [A].1"], row["momentum [MeV/c]"]) * 1000
            assert angle_mrad == pytest.approx(row["K or angle"], rel=1e-6), (
                f"{row['machine']}-{row['region']}-{row['type']}-{int(row['number'])}"
            )

    def test_angle_to_current_is_the_inverse(self):
        for row in _corrector_table_rows():
            mag = _magnet_from_row(row)
            angle = mag.current_to_angle(row["current [A].1"], row["momentum [MeV/c]"])
            assert mag.angle_to_current(angle, row["momentum [MeV/c]"]) == pytest.approx(
                row["current [A].1"], rel=1e-6
            )

    def test_dipole_and_corrector_agree_on_the_same_fit(self):
        """Both are order 0: same KL, differing only in reporting unit."""
        import math
        from laura.models.magnetic import CorrectorMagnet, DipoleMagnet

        coeffs = {"m": 0.0238, "I_max": 0, "f": 0, "a": 0, "I0": 0, "d": 0, "L": 128.65}
        cor = CorrectorMagnet(magnetic_length=0.12865, linear_saturation_coefficients=coeffs)
        dip = DipoleMagnet(length=0.12865, linear_saturation_coefficients=coeffs)
        kl = cor.current_to_k(1.0, momentum=6.0)["KL"]
        assert dip.current_to_k(1.0, momentum=6.0)["KL"] == pytest.approx(kl)
        # corrector reports radians, dipole degrees -- both off the same KL
        assert cor.current_to_angle(1.0, 6.0) == pytest.approx(kl)
        assert dip.current_to_angle(1.0, 6.0) == pytest.approx(math.degrees(kl))


class TestCombinedCorrectorHasTwoMagnets:
    """The magnet table gives the two planes different slopes and lengths."""

    def test_planes_are_independent_objects(self):
        cc = CombinedCorrector(
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
        cc = CombinedCorrector(
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
        h = cc.magnetic.current_to_angle(1.0, 6.0) * 1000
        v = cc.magnetic.current_to_angle(1.0, 6.0, skew=True) * 1000
        assert h == pytest.approx(1.223797, rel=1e-5)
        assert v == pytest.approx(1.189055, rel=1e-5)
        assert h != v

    def test_legacy_flat_magnetic_block_still_loads(self):
        """Older files carry one flat block: calibration goes to both planes, each keeps its own kick."""
        cc = CombinedCorrector(
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
        assert cc.magnetic.horizontal.vertical_kick == pytest.approx(0.0)
        assert cc.magnetic.vertical.horizontal_kick == pytest.approx(0.0)

    def test_round_trips_through_model_dump(self):
        cc = CombinedCorrector(
            name="cc", machine_area="S",
            magnetic={"length": 0.21, "horizontal_kick": 0.004, "vertical_kick": 0.006,
                      "linear_saturation_coefficients": {"m": 0.142, "I_max": 0, "f": 0,
                                                         "a": 0, "I0": 0, "d": 0, "L": 137.8}},
        )
        cc.magnetic.vertical.linear_saturation_coefficients.m = 0.15
        rt = CombinedCorrector(name="cc", machine_area="S",
                                magnetic=cc.model_dump()["magnetic"])
        assert rt.magnetic.horizontal_kick == pytest.approx(0.004)
        assert rt.magnetic.vertical_kick == pytest.approx(0.006)
        assert rt.magnetic.vertical.linear_saturation_coefficients.m == pytest.approx(0.15)

    def test_translator_keeps_both_planes_and_the_length(self):
        cc = CombinedCorrector(
            name="cc1", machine_area="S",
            magnetic={"magnetic_length": 0.2, "horizontal_kick": 0.04, "vertical_kick": 0.05},
        )
        t = translate_elements([cc])["cc1"]
        assert t.hangle == pytest.approx(0.04)
        assert t.vangle == pytest.approx(0.05)
        assert t.length == pytest.approx(0.2)


class TestAgainstMagnetTableFormulas:
    """Workbook column AC is ``SWITCH(type, "DIP", 360/(2000*PI()), "HCOR", 1, ...) * c_ * AA / A``;
    both order-0 branches are ``(c/1e9) * AA / p`` in radians."""

    def test_dipole_and_corrector_angle_branches_agree_in_radians(self):
        import math
        c_ = 299.792458
        dip_to_rad = 360 / (2000 * math.pi) * math.pi / 180   # AC[deg] -> rad
        cor_to_rad = 1 / 1000                                  # AC[mrad] -> rad
        assert dip_to_rad == pytest.approx(cor_to_rad, rel=1e-15)
        from laura.models.constants import speed_of_light
        assert dip_to_rad * c_ == pytest.approx(speed_of_light / 1e9, rel=1e-12)

    def test_forward_conversions_match_every_row(self):
        rows = _corrector_table_rows()
        for row in rows:
            mag = _magnet_from_row(row)
            out = mag.linear_saturation_coefficients.current_to_k(
                current=row["current [A].1"], momentum=row["momentum [MeV/c]"])
            assert out["int_strength"] == pytest.approx(
                row["integrated strength.1"], rel=1e-9)
            assert out["KL"] * 1000 == pytest.approx(row["K or angle"], rel=1e-7)

    def test_saturating_reverse_branch_is_real_and_correct(self):
        """The trigonometric cubic needs sqrt(-(p/3)**3) and a positive cube root when f < 0."""
        from laura.models.magnetic import LinearSaturationFit

        sat = [r for r in _magnet_table()
               if str(r["type"]).upper() == "QUAD" and r["f [units/A³]"] < 0
               and r["max current [A]"] > 0 and abs(r["current [A].1"]) >= r["max current [A]"]]
        if not sat:
            pytest.skip("no saturating quadrupole row in the magnet table")
        row = sat[0]
        lsf = LinearSaturationFit(
            m=row["slope [units/A]"], I_max=row["max current [A]"],
            f=row["f [units/A³]"], a=row["a [units/A²]"], I0=row["I0 [A]"],
            d=row["d [units]"], L=row["magnetic length [mm]"])
        lsf.order = 1
        current, momentum = row["current [A].1"], row["momentum [MeV/c]"]
        K = lsf.current_to_k(current, momentum=momentum)["K"]
        back = lsf.k_to_current(K, momentum)
        assert not isinstance(back, complex), "cubic branch returned a complex current"
        assert float(back) == pytest.approx(current, rel=1e-6)

    def test_dipole_current_to_angle_has_no_extra_thousandth(self):
        """CLA-SP3-MAG-DIP-01: 300 A over its 30 deg bend is ~238 MeV/c."""
        import math
        from laura.models.magnetic import DipoleMagnet

        dip = DipoleMagnet(length=0.4, linear_saturation_coefficients=dict(
            m=1.3966746927879516, I_max=246.90388362886958, f=0,
            a=-0.0020829194836779275, I0=596.1589358551605,
            d=598.7346914311352, L=400.0))
        kl_per_mev = dip.current_to_k(300.0, momentum=1.0)["KL"]
        assert kl_per_mev / math.radians(30.0) == pytest.approx(238.2, rel=1e-3)
        # the reported angle is in degrees
        out = dip.current_to_k(300.0, momentum=238.209)
        assert out["degrees"] == pytest.approx(30.0, rel=1e-4)
        assert dip.current_to_angle(300.0, 238.209) == pytest.approx(30.0, rel=1e-4)
        assert float(dip.kl_to_current(out["KL"], 238.209)) == pytest.approx(300.0, rel=1e-6)

    def test_every_dipole_row_matches_the_table(self):
        from laura.models.magnetic import DipoleMagnet

        rows = [r for r in _magnet_table()
                if str(r["type"]).upper() == "DIP" and r["K or angle"] != 0
                and r["current [A].1"] != 0 and r["magnetic length [mm]"] != 0]
        assert len(rows) >= 2, "no usable DIP rows in the in-repo magnet table"
        for row in rows:
            dip = DipoleMagnet(
                length=row["magnetic length [mm]"] / 1000,
                linear_saturation_coefficients={
                    "m": row["slope [units/A]"], "I_max": row["max current [A]"],
                    "f": row["f [units/A³]"], "a": row["a [units/A²]"],
                    "I0": row["I0 [A]"], "d": row["d [units]"],
                    "L": row["magnetic length [mm]"]})
            current, p = row["current [A].1"], row["momentum [MeV/c]"]
            assert dip.current_to_angle(current, p) == pytest.approx(
                row["K or angle"], rel=1e-7)
            assert float(
                dip.kl_to_current(dip.current_to_k(current, p)["KL"], p)
            ) == pytest.approx(current, rel=1e-6)
