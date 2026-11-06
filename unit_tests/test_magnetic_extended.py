"""Tests for laura.models.magnetic."""

import pytest
import numpy as np

from laura.models.magnetic import (
    MagneticElement,
    CombinedSolenoidQuadrupoleMagnet,
    DipoleMagnet,
    QuadrupoleMagnet,
    SextupoleMagnet,
    OctupoleMagnet,
    SolenoidMagnet,
    NonLinearLensMagnet,
    WigglerMagnet,
    Multipole,
    Multipoles,
    FieldIntegral,
    LinearSaturationFit,
    SolenoidFields,
)
from laura.models.base_models import (
    set_functional_definitions,
    set_resolve_functional,
)


class TestMultipole:
    def test_default_values(self):
        m = Multipole()
        assert m.order == 0
        assert m.normal == 0
        assert m.skew == 0
        assert m.radius == 0

    def test_custom_values(self):
        m = Multipole(order=2, normal=1.5, skew=0.3)
        assert m.order == 2
        assert m.normal == 1.5


class TestFieldIntegral:
    def test_current_to_k_linear(self):
        fi = FieldIntegral(coefficients=[0.0, 0.5])  # K = 0.5 * current
        k = fi.current_to_k(10.0, energy=1e9)
        assert isinstance(k, float)

    def test_current_to_k_polynomial(self):
        fi = FieldIntegral(coefficients=[0.0, 1.0, 0.01])
        k = fi.current_to_k(5.0, energy=1e9)
        assert isinstance(k, float)


@pytest.fixture
def lsf():
    return LinearSaturationFit(
        m=0.01, I_max=100.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3
    )


class TestLinearSaturationFit:
    def test_current_to_k(self, lsf):
        result = lsf.current_to_k(50.0, momentum=1e9)
        assert isinstance(result, dict)
        assert "KL" in result

    def test_kl_to_current(self, lsf):
        kl = lsf.current_to_k(50.0, momentum=1e9)["KL"]
        current = lsf.kl_to_current(kl, momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_k_to_current(self, lsf):
        k_result = lsf.current_to_k(50.0, momentum=1e9)
        k = k_result["K"]
        current = lsf.k_to_current(k, momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_from_string(self):
        lsf = LinearSaturationFit.from_string("0.01,100,0.9,0.001,0,0,0.3")
        assert lsf.m == pytest.approx(0.01)
        assert lsf.I_max == pytest.approx(100.0)
        assert lsf.L == pytest.approx(0.3)


class TestMagneticElement:
    def test_default_values(self):
        me = MagneticElement()
        assert me.order == -1
        assert me.length == 0

    def test_kl_property(self):
        me = MagneticElement(order=1, length=0.3)
        me.kl = 2.0
        assert me.kl == pytest.approx(2.0)

    def test_knl(self):
        me = MagneticElement(order=1, length=0.3)
        me.kl = 1.5
        knl = me.KnL(1)
        assert isinstance(knl, float)

    def test_kn(self):
        me = MagneticElement(order=1, length=0.5)
        me.kl = 3.0
        assert me.Kn(1) == pytest.approx(3.0 / 0.5)

    def test_half_gap(self):
        me = MagneticElement(gap=0.04)
        assert me.half_gap == pytest.approx(0.02)

    def test_exit_face_defaults_to_the_entrance(self):
        me = MagneticElement(gap=0.04, edge_field_integral=0.3)
        assert me.exit_gap is None
        assert me.edge_field_integral_entrance == pytest.approx(0.3)
        assert me.edge_field_integral_exit == pytest.approx(0.3)
        assert me.exit_half_gap == pytest.approx(0.02)
        assert me.exit_fringe_integral == pytest.approx(0.3)

    def test_exit_face_is_used_when_it_is_given(self):
        me = MagneticElement(
            gap=0.0, edge_field_integral=0.0, exit_gap=0.03,
            edge_field_integral_exit=0.45,
        )
        assert me.half_gap == 0.0
        assert me.edge_field_integral == 0.0
        assert me.exit_half_gap == pytest.approx(0.015)
        assert me.exit_fringe_integral == pytest.approx(0.45)

    def test_the_resolved_faces_are_serialised_but_the_read_helpers_are_not(self):
        dumped = MagneticElement(gap=0.04, edge_field_integral=0.3).model_dump(
            exclude_defaults=True
        )
        assert dumped["edge_field_integral_entrance"] == pytest.approx(0.3)
        assert dumped["edge_field_integral_exit"] == pytest.approx(0.3)
        assert "exit_half_gap" not in dumped
        assert "exit_fringe_integral" not in dumped
        assert "exit_gap" not in dumped


class TestDipoleMagnet:
    def test_defaults(self):
        dm = DipoleMagnet()
        assert dm.order == 0
        assert dm.angle == 0

    def test_angle(self):
        # angle reads multipoles.K0L.normal, set via k0l
        dm = DipoleMagnet(k0l=0.1)
        assert dm.angle == pytest.approx(0.1)

    def test_rho(self):
        dm = DipoleMagnet(k0l=0.1, length=1.0)
        assert dm.rho == pytest.approx(10.0)


class TestQuadrupoleMagnet:
    def test_defaults(self):
        qm = QuadrupoleMagnet()
        assert qm.order == 1
        assert qm.k1l == 0

    def test_k1l(self):
        qm = QuadrupoleMagnet(k1l=-2.5)
        assert qm.k1l == pytest.approx(-2.5)


class TestSextupleMagnet:
    def test_defaults(self):
        sm = SextupoleMagnet()
        assert sm.order == 2
        assert sm.k2l == 0

    def test_k2l(self):
        sm = SextupoleMagnet(k2l=100.0)
        assert sm.k2l == pytest.approx(100.0)


class TestOctupleMagnet:
    def test_defaults(self):
        om = OctupoleMagnet()
        assert om.order == 3
        assert om.k3l == 0


class TestSolenoidMagnet:
    def test_default(self):
        sol = SolenoidMagnet()
        assert sol.ks == 0.0

    def test_ks_property(self):
        # ks is handled in Solenoid_Magnet.__init__, not as a Pydantic field
        sol = SolenoidMagnet(ks=1.5)
        assert sol.ks == pytest.approx(1.5)

    def test_ks_setter(self):
        sol = SolenoidMagnet()
        sol.ks = 2.0
        assert sol.ks == pytest.approx(2.0)


class TestCombinedSolenoidQuadrupoleMagnet:
    def test_default(self):
        sq = CombinedSolenoidQuadrupoleMagnet()
        assert sq.order == 1
        assert sq.KnL(1) == 0.0
        assert sq.ks == 0.0

    def test_ks_property(self):
        sq = CombinedSolenoidQuadrupoleMagnet(ks=1.5)
        assert sq.ks == pytest.approx(1.5)

    def test_ks_setter(self):
        sq = CombinedSolenoidQuadrupoleMagnet()
        sq.ks = 2.0
        assert sq.ks == pytest.approx(2.0)

    def test_quad_strength_and_ks_together(self):
        sq = CombinedSolenoidQuadrupoleMagnet(length=2.0, k1l=0.6, ks=0.8)
        assert sq.KnL(1) == pytest.approx(0.6)
        assert sq.ks == pytest.approx(0.8)
        assert sq.solenoid_fields.S0L == pytest.approx(0.8)


class TestNonLinearLensMagnet:
    def test_default(self):
        nll = NonLinearLensMagnet()
        assert nll.length == 0
        assert nll.integrated_strength == 0
        assert nll.dimensional_parameter == 0


class TestWigglerMagnet:
    def test_default(self):
        w = WigglerMagnet()
        assert w.strength == 0
        assert w.period == 0

    def test_with_values(self):
        w = WigglerMagnet(
            length=2.0,
            strength=1.5,
            period=0.02,
            num_periods=100,
            helical=False,
        )
        assert w.length == pytest.approx(2.0)
        assert w.strength == pytest.approx(1.5)
        assert w.num_periods == 100
        assert w.helical is False

    def test_poles_property(self):
        w = WigglerMagnet(num_periods=50)
        assert w.poles == 100

    def test_normalized_strength_planar(self):
        w = WigglerMagnet(strength=1.0, helical=False)
        # For planar: normalized_strength = K / sqrt(2)
        assert w.normalized_strength == pytest.approx(1.0 / np.sqrt(2))

    def test_normalized_strength_helical(self):
        w = WigglerMagnet(strength=1.0, helical=True)
        # For helical: normalized_strength = K
        assert w.normalized_strength == pytest.approx(1.0)


class TestFunctionalParameters:
    """Functional strengths are stored verbatim and resolved only on computation."""

    @pytest.fixture(autouse=True)
    def _defs(self):
        # conftest resets the registry and resolution mode around every test
        set_functional_definitions(
            {
                "quad1_k1l": -2.0,
                "skew1": 0.5,
                "sol_field": 1.5,
                "nll_k": 0.4,
                "nll_c": 0.01,
                "wig_K": 1.0,
                "dip_angle": 0.1,
                "dip_e1": 0.05,
            },
            merge=False,
        )

    def test_dipole_angle_raw_resolved_flag(self):
        dm = DipoleMagnet(k0l="dip_angle", length=0.5)
        # configured accessor follows the flag (raw name by default)
        assert dm.angle == "dip_angle"
        assert dm.KnL(0) == pytest.approx(0.1)
        assert dm.rho == pytest.approx(0.5 / 0.1)
        set_resolve_functional(True)
        assert dm.angle == pytest.approx(0.1)

    def test_dipole_edge_angle_functional(self):
        from laura.translator.converters.magnet import DipoleTranslator
        from laura.models.element import Dipole
        d = Dipole(
            name="D", machine_area="ARC",
            magnetic={"magnetic_length": 0.5, "k0l": "dip_angle",
                      "entrance_edge_angle": "dip_e1", "exit_edge_angle": "angle/2"},
        )
        dt = DipoleTranslator.model_validate(d.model_dump())
        # "angle/2" references the resolved bend angle
        assert dt.e1 == pytest.approx(0.05)
        assert dt.e2 == pytest.approx(0.1 / 2)

    def test_resolution_mode_flag(self):
        qm = QuadrupoleMagnet(k1l="quad1_k1l", length=0.3)
        sol = SolenoidMagnet(length=0.2, ks="sol_field")
        # default (off): configured accessors render the functional name
        assert qm.k1l == "quad1_k1l"
        assert sol.ks == "sol_field"
        # on: configured accessors present the resolved number
        set_resolve_functional(True)
        assert qm.k1l == pytest.approx(-2.0)
        assert sol.ks == pytest.approx(1.5)
        # KnL / field_amplitude always resolve, regardless of mode
        set_resolve_functional(False)
        assert qm.KnL(1) == pytest.approx(-2.0)
        assert sol.field_amplitude == pytest.approx(1.5 / 0.2)

    def test_quad_k1l_raw_and_resolved(self):
        qm = QuadrupoleMagnet(k1l="quad1_k1l", length=0.3)
        assert qm.multipoles.K1L.normal == "quad1_k1l"
        assert qm.k1l == "quad1_k1l"
        assert qm.KnL(1) == pytest.approx(-2.0)

    def test_multipole_skew_string(self):
        m = Multipoles(K1L=Multipole(order=1, skew="skew1"))
        assert m.skew(1) == "skew1"

    def test_undefined_parameter_raises_on_resolution(self):
        qm = QuadrupoleMagnet(k1l="not_defined", length=0.3)
        assert qm.multipoles.K1L.normal == "not_defined"
        assert qm.k1l == "not_defined"
        with pytest.raises(KeyError):
            qm.KnL(1)

    def test_solenoid_string(self):
        sol = SolenoidMagnet(length=0.2, ks="sol_field")
        assert sol.fields.S0L == "sol_field"
        # field_amplitude resolves ks/length
        assert sol.ks == "sol_field"
        assert sol.field_amplitude == pytest.approx(1.5 / 0.2)

    def test_nll_string(self):
        nll = NonLinearLensMagnet(knll="nll_k", cnll="nll_c")
        assert nll.integrated_strength == "nll_k"
        assert nll.resolved("integrated_strength") == pytest.approx(0.4)
        assert nll.resolved("dimensional_parameter") == pytest.approx(0.01)

    def test_wiggler_string(self):
        w = WigglerMagnet(K="wig_K", helical=True)
        assert w.strength == "wig_K"
        assert w.normalized_strength == pytest.approx(1.0)

    def test_float_still_supported(self):
        qm = QuadrupoleMagnet(k1l=-2.5, length=0.3)
        assert qm.k1l == pytest.approx(-2.5)

    def test_get_gradient_resolves(self):
        qm = QuadrupoleMagnet(k1l="quad1_k1l", length=0.3)
        assert qm.get_gradient(momentum=1e9) == pytest.approx(
            -2.0 * 3.3356 * 1e9 / 1e9 / 0.3
        )

    def test_serialisation_keeps_symbolic_value(self):
        qm = QuadrupoleMagnet(k1l="quad1_k1l", length=0.3)
        dumped = qm.model_dump()
        assert dumped["multipoles"]["K1L"]["normal"] == "quad1_k1l"
        qm2 = QuadrupoleMagnet(**dumped)
        assert qm2.multipoles.K1L.normal == "quad1_k1l"
        assert qm2.k1l == "quad1_k1l"
        assert qm2.KnL(1) == pytest.approx(-2.0)


class TestFieldIntegralCoercion:
    @pytest.mark.parametrize(
        "authored",
        [[1, 2, 3], "1,2,3", {"coefficients": [1, 2, 3]}],
        ids=["list", "csv", "dict"],
    )
    def test_every_authored_form_gives_the_same_coefficients(self, authored):
        me = MagneticElement(field_integral_coefficients=authored)
        assert me.field_integral_coefficients.coefficients == [1.0, 2.0, 3.0]
        assert list(iter(me.field_integral_coefficients)) == [1.0, 2.0, 3.0]

    def test_an_instance_is_kept_rather_than_rebuilt(self):
        fi = FieldIntegral(coefficients=[1, 2])
        assert MagneticElement(field_integral_coefficients=fi).field_integral_coefficients is fi

    def test_none_passthrough(self):
        me = MagneticElement(field_integral_coefficients=None)
        assert me.field_integral_coefficients is None

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            MagneticElement(field_integral_coefficients=5)


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, (None, None, None)),
        ({"edge_field_integral": 0.2}, (0.2, 0.2, 0.2)),
        ({"edge_field_integral": 0.2, "edge_field_integral_entrance": 0.9}, (0.2, 0.9, 0.2)),
        ({"edge_field_integral": 0.2, "edge_field_integral_exit": 0.9}, (0.2, 0.2, 0.9)),
        (
            {"edge_field_integral": 0.2, "edge_field_integral_entrance": 0.3, "edge_field_integral_exit": 0.4},
            (0.2, 0.3, 0.4),
        ),
        # A face is used as given; the rest stay None, deferring to the target code.
        ({"edge_field_integral_entrance": 0.7}, (None, 0.7, None)),
        ({"edge_field_integral_exit": 0.7}, (None, None, 0.7)),
        ({"edge_field_integral_entrance": 0.3, "edge_field_integral_exit": 0.7}, (None, 0.3, 0.7)),
    ],
    ids=[
        "none_set",
        "efi_fills_both_edges",
        "efi_and_entrance_fills_exit",
        "efi_and_exit_fills_entrance",
        "all_three_untouched",
        "only_entrance_isolated",
        "only_exit_isolated",
        "entrance_and_exit_leave_efi_none",
    ],
)
def test_edge_field_integral_resolution(kwargs, expected):
    me = MagneticElement(**kwargs)
    assert (me.edge_field_integral, me.edge_field_integral_entrance, me.edge_field_integral_exit) == expected


class TestMultipolesValidatorBranches:
    def test_none_becomes_default_multipole(self):
        mp = Multipoles(K1L=None)
        assert mp.K1L == Multipole()

    def test_two_element_list(self):
        mp = Multipoles(K1L=[1, 0.5])
        assert mp.K1L.order == 1
        assert mp.K1L.normal == 0.5

    def test_four_element_list(self):
        mp = Multipoles(K1L=[1, 0.5, 0.2, 0.1])
        assert mp.K1L == Multipole(order=1, normal=0.5, skew=0.2, radius=0.1)

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            Multipoles(K1L=5)

    def test_neq(self):
        mp = Multipoles()
        assert mp != {"not": "matching"}


class TestLinearSaturationFitListPaths:
    def test_from_string_list_branch(self):
        lsf = LinearSaturationFit.from_string([0.01, 100, 0.9, 0.001, 0, 0, 0.3, 1])
        assert lsf.order == 1
        assert lsf.L == pytest.approx(0.3)

    def test_from_string_invalid_type_raises(self):
        with pytest.raises(ValueError):
            LinearSaturationFit.from_string(5)

    def test_update_from_string_string_branch(self, lsf):
        lsf.update_from_string("0.02,200,0.8,0.002,0,0,0.4")
        assert lsf.m == pytest.approx(0.02)
        assert lsf.L == pytest.approx(0.4)

    def test_update_from_string_list_branch(self, lsf):
        lsf.update_from_string([0.02, 200, 0.8, 0.002, 0, 0, 0.4])
        assert lsf.m == pytest.approx(0.02)

    def test_iter(self, lsf):
        assert list(iter(lsf)) == pytest.approx([0.01, 100.0, 0.9, 0.001, 0.0, 0.0, 0.3])


class TestLinearSaturationFitCurrentToKBranches:
    def test_without_momentum_returns_gradient_only(self):
        lsf = LinearSaturationFit(m=0.01, I_max=10.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3)
        result = lsf.current_to_k(50.0, momentum=None)
        assert set(result.keys()) == {"gradient", "int_strength"}

    def test_saturation_branch_f_zero(self):
        lsf = LinearSaturationFit(m=0.01, I_max=10.0, f=0.0, a=0.5, I0=5.0, d=1.0, L=0.3)
        result = lsf.current_to_k(50.0, momentum=1e9)
        current = lsf.k_to_current(result["K"], momentum=1e9)
        assert isinstance(current, (float, np.floating))

    def test_saturation_branch_f_nonzero_does_not_raise(self):
        lsf = LinearSaturationFit(m=0.01, I_max=10.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3)
        result = lsf.current_to_k(50.0, momentum=1e9)
        # Cubic-root branch; just exercise it without asserting a particular value.
        lsf.k_to_current(result["K"], momentum=1e9)

    def test_kl_to_current_from_dict_with_kl_key(self, lsf):
        result = lsf.current_to_k(50.0, momentum=1e9)
        current = lsf.kl_to_current({"KL": result["KL"]}, momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_kl_to_current_from_dict_with_k_key(self, lsf):
        result = lsf.current_to_k(50.0, momentum=1e9)
        current = lsf.kl_to_current({"K": result["K"]}, momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_k_to_current_from_dict_with_kl_key(self, lsf):
        result = lsf.current_to_k(50.0, momentum=1e9)
        current = lsf.k_to_current({"KL": result["KL"]}, momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_k_to_current_dict_without_known_key_raises(self, lsf):
        with pytest.raises(ValueError):
            lsf.k_to_current({"nope": 1}, momentum=1e9)


class TestMagneticElementInitEdgeCases:
    def test_multipoles_auto_created_when_none_and_strength_given(self):
        me = MagneticElement(multipoles=None, k1l=0.5)
        assert me.multipoles is not None
        assert me.multipoles.K1L.normal == pytest.approx(0.5)

    def test_kl_kwarg_sets_strength(self):
        me = MagneticElement(kl=0.7, order=1)
        assert me.kl == pytest.approx(0.7)

    def test_skew_with_kl_sets_skew_component(self):
        me = MagneticElement(skew=True, kl=0.3, order=1)
        assert me.multipoles.K1L.skew == pytest.approx(0.3)
        assert me.multipoles.K1L.normal == 0.0

    def test_plane_none_passthrough(self):
        me = MagneticElement(plane=None)
        assert me.plane is None

    def test_kl_raw_negative_order_returns_zero(self):
        me = MagneticElement()
        assert me.order == -1
        assert me.kl_raw() == 0

    def test_kl_raw_no_multipoles_returns_zero(self):
        me = MagneticElement(multipoles=None)
        assert me.kl_raw() == 0

    def test_kl_setter_creates_multipoles_when_none(self):
        me = MagneticElement(order=1)
        me.multipoles = None
        me.kl = 0.9
        assert me.kl == pytest.approx(0.9)

    def test_get_gradient_uses_explicit_gradient_field(self):
        me = MagneticElement(gradient=5.0)
        assert me.get_gradient(momentum=1e9) == 5.0

    def test_element_level_current_k_delegation(self, lsf):
        me = MagneticElement(order=1, length=0.3, linear_saturation_coefficients=lsf)
        result = me.current_to_k(50.0, momentum=1e9)
        assert "KL" in result
        current = me.k_to_current(result["K"], momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)
        current2 = me.kl_to_current(result["KL"], momentum=1e9)
        assert current2 == pytest.approx(50.0, rel=0.01)

    def test_element_level_current_to_angle(self, lsf):
        me = MagneticElement(order=1, length=0.3, linear_saturation_coefficients=lsf)
        angle = me.current_to_angle(50.0, momentum=1e9)
        assert isinstance(angle, float)


class TestDipoleMagnetSettersAndConversions:
    def test_angle_setter(self):
        dm = DipoleMagnet(k0l=0.1, length=1.0)
        dm.angle = 0.2
        assert dm.angle == pytest.approx(0.2)

    def test_angle_setter_creates_multipoles_when_none(self):
        dm = DipoleMagnet(multipoles=None)
        dm.angle = 0.3
        assert dm.angle == pytest.approx(0.3)

    def test_current_to_angle(self, lsf):
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        angle = dm.current_to_angle(50.0, momentum=1e9)
        assert isinstance(angle, float)

    def test_current_to_k_scales_and_adds_degrees(self, lsf):
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        result = dm.current_to_k(50.0, momentum=1e9)
        assert "degrees" in result

    def test_k_to_current_float(self, lsf):
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        current = dm.k_to_current(dm.current_to_k(50.0, momentum=1e9)["K"], momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_k_to_current_dict(self, lsf):
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        k_result = dm.current_to_k(50.0, momentum=1e9)
        current = dm.k_to_current(k_result, momentum=1e9)
        assert isinstance(current, (float, complex, np.floating, np.complexfloating))

    def test_kl_to_current_float(self, lsf):
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        kl_result = dm.current_to_k(50.0, momentum=1e9)
        current = dm.kl_to_current(kl_result["KL"], momentum=1e9)
        assert isinstance(current, (float, complex, np.floating, np.complexfloating))

    def test_kl_to_current_dict(self, lsf):
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        kl_result = dm.current_to_k(50.0, momentum=1e9)
        current = dm.kl_to_current(kl_result, momentum=1e9)
        assert isinstance(current, (float, complex, np.floating, np.complexfloating))


@pytest.mark.parametrize(
    "cls, attribute",
    [
        (QuadrupoleMagnet, "k1l"),
        (SextupoleMagnet, "k2l"),
        (OctupoleMagnet, "k3l"),
    ],
    ids=lambda v: getattr(v, "__name__", v),
)
def test_the_order_specific_strength_setter_round_trips(cls, attribute):
    magnet = cls(length=1.0)
    setattr(magnet, attribute, 3.3)
    assert getattr(magnet, attribute) == pytest.approx(3.3)


class TestSolenoidFieldsDunders:
    def test_repr_contains_class_name(self):
        sf = SolenoidFields(S0L=0.5)
        assert "SolenoidFields" in repr(sf)

    def test_normal(self):
        sf = SolenoidFields(S0L=0.5)
        assert sf.normal(0) == 0.5

    def test_eq_and_neq(self):
        sf = SolenoidFields()
        assert not (sf == {"S0L": 0.0})  # partial dict never matches ser_model
        assert sf != {"S0L": 0.0}


class TestSolenoidMagnetFieldAmplitude:
    def test_field_amplitude_kwarg_sets_ks(self):
        # `ks`/`S0L` is integrated, so __init__ multiplies by length: 2.0 * 0.5 = 1.0.
        sol = SolenoidMagnet(field_amplitude=2.0, length=0.5)
        assert sol.ks == pytest.approx(1.0)

    def test_field_amplitude_kwarg_round_trips(self):
        sol = SolenoidMagnet(field_amplitude=2.0, length=0.5)
        assert sol.field_amplitude == pytest.approx(2.0)

    def test_field_amplitude_setter(self):
        sol = SolenoidMagnet(length=0.5)
        sol.field_amplitude = 4.0
        assert sol.ks == pytest.approx(2.0)

    def test_field_integral_coefficients_none_raises(self):
        with pytest.raises(ValueError):
            SolenoidMagnet(field_integral_coefficients=None)


class TestWigglerNormalizedStrengthAndPolesSetters:
    def test_normalized_strength_setter_planar(self):
        w = WigglerMagnet(helical=False)
        w.normalized_strength = 1.0
        assert w.strength == pytest.approx(np.sqrt(2))

    def test_normalized_strength_setter_helical(self):
        w = WigglerMagnet(helical=True)
        w.normalized_strength = 2.0
        assert w.strength == pytest.approx(2.0)

    def test_poles_setter(self):
        w = WigglerMagnet()
        w.poles = 10
        assert w.num_periods == 5
