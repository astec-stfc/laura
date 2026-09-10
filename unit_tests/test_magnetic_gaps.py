"""Additional tests for laura.models.magnetic covering branches not exercised by
test_magnetic.py / test_magnetic_extended.py: field-integral coercion variants,
Multipoles validator branches and dunders, LinearSaturationFit list/update-from
paths and saturation branches, MagneticElement init edge cases, and the
setter/dunder methods of the Dipole/Quadrupole/Octupole/Solenoid/Wiggler subtypes."""

import numpy as np
import pytest

from laura.models.magnetic import (
    MagneticElement,
    Multipole,
    Multipoles,
    FieldIntegral,
    LinearSaturationFit,
    DipoleMagnet,
    QuadrupoleMagnet,
    SextupoleMagnet,
    OctupoleMagnet,
    SolenoidFields,
    SolenoidMagnet,
    WigglerMagnet,
)


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


class TestEdgeFieldIntegralResolution:
    def test_none_set_stays_none(self):
        me = MagneticElement()
        assert (me.edge_field_integral, me.edge_field_integral_entrance, me.edge_field_integral_exit) == (None, None, None)

    def test_only_edge_field_integral_set_fills_both_edges(self):
        me = MagneticElement(edge_field_integral=0.2)
        assert me.edge_field_integral_entrance == 0.2
        assert me.edge_field_integral_exit == 0.2

    def test_efi_and_entrance_set_fills_exit(self):
        me = MagneticElement(edge_field_integral=0.2, edge_field_integral_entrance=0.9)
        assert me.edge_field_integral_entrance == 0.9
        assert me.edge_field_integral_exit == 0.2

    def test_efi_and_exit_set_fills_entrance(self):
        me = MagneticElement(edge_field_integral=0.2, edge_field_integral_exit=0.9)
        assert me.edge_field_integral_entrance == 0.2
        assert me.edge_field_integral_exit == 0.9

    def test_all_three_set_left_untouched(self):
        me = MagneticElement(edge_field_integral=0.2, edge_field_integral_entrance=0.3, edge_field_integral_exit=0.4)
        assert (me.edge_field_integral, me.edge_field_integral_entrance, me.edge_field_integral_exit) == (0.2, 0.3, 0.4)

    def test_only_entrance_set_stays_isolated(self):
        # No cross-inference: entrance is used as given, exit and
        # edge_field_integral itself stay None (deferring to the target
        # code's own default) since edge_field_integral was never given.
        me = MagneticElement(edge_field_integral_entrance=0.7)
        assert me.edge_field_integral_entrance == 0.7
        assert me.edge_field_integral_exit is None
        assert me.edge_field_integral is None

    def test_only_exit_set_stays_isolated(self):
        me = MagneticElement(edge_field_integral_exit=0.7)
        assert me.edge_field_integral_entrance is None
        assert me.edge_field_integral_exit == 0.7
        assert me.edge_field_integral is None

    def test_entrance_and_exit_set_without_efi_leaves_efi_none(self):
        me = MagneticElement(edge_field_integral_entrance=0.3, edge_field_integral_exit=0.7)
        assert me.edge_field_integral_entrance == 0.3
        assert me.edge_field_integral_exit == 0.7
        assert me.edge_field_integral is None


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


class TestFieldIntegralIter:
    def test_iter_yields_coefficients(self):
        fi = FieldIntegral(coefficients=[1.0, 2.0, 3.0])
        assert list(iter(fi)) == [1.0, 2.0, 3.0]


class TestLinearSaturationFitListPaths:
    def test_from_string_list_branch(self):
        lsf = LinearSaturationFit.from_string([0.01, 100, 0.9, 0.001, 0, 0, 0.3, 1])
        assert lsf.order == 1
        assert lsf.L == pytest.approx(0.3)

    def test_from_string_invalid_type_raises(self):
        with pytest.raises(ValueError):
            LinearSaturationFit.from_string(5)

    def test_update_from_string_string_branch(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3)
        lsf.update_from_string("0.02,200,0.8,0.002,0,0,0.4")
        assert lsf.m == pytest.approx(0.02)
        assert lsf.L == pytest.approx(0.4)

    def test_update_from_string_list_branch(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3)
        lsf.update_from_string([0.02, 200, 0.8, 0.002, 0, 0, 0.4])
        assert lsf.m == pytest.approx(0.02)

    def test_iter(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3)
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

    def test_kl_to_current_from_dict_with_kl_key(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3)
        result = lsf.current_to_k(50.0, momentum=1e9)
        current = lsf.kl_to_current({"KL": result["KL"]}, momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_kl_to_current_from_dict_with_k_key(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3)
        result = lsf.current_to_k(50.0, momentum=1e9)
        current = lsf.kl_to_current({"K": result["K"]}, momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_k_to_current_from_dict_with_kl_key(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3)
        result = lsf.current_to_k(50.0, momentum=1e9)
        current = lsf.k_to_current({"KL": result["KL"]}, momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_k_to_current_dict_without_known_key_raises(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3)
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

    def test_element_level_current_k_delegation(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100, f=0.9, a=0.001, I0=0, d=0, L=0.3)
        me = MagneticElement(order=1, length=0.3, linear_saturation_coefficients=lsf)
        result = me.current_to_k(50.0, momentum=1e9)
        assert "KL" in result
        current = me.k_to_current(result["K"], momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)
        current2 = me.kl_to_current(result["KL"], momentum=1e9)
        assert current2 == pytest.approx(50.0, rel=0.01)

    def test_element_level_current_to_angle(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100, f=0.9, a=0.001, I0=0, d=0, L=0.3)
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

    def test_current_to_angle(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100, f=0.9, a=0.001, I0=0, d=0, L=0.3)
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        angle = dm.current_to_angle(50.0, momentum=1e9)
        assert isinstance(angle, float)

    def test_current_to_k_scales_and_adds_degrees(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100, f=0.9, a=0.001, I0=0, d=0, L=0.3)
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        result = dm.current_to_k(50.0, momentum=1e9)
        assert "degrees" in result

    def test_k_to_current_float(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100, f=0.9, a=0.001, I0=0, d=0, L=0.3)
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        current = dm.k_to_current(dm.current_to_k(50.0, momentum=1e9)["K"], momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_k_to_current_dict(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100, f=0.9, a=0.001, I0=0, d=0, L=0.3)
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        k_result = dm.current_to_k(50.0, momentum=1e9)
        current = dm.k_to_current(k_result, momentum=1e9)
        assert isinstance(current, (float, complex, np.floating, np.complexfloating))

    def test_kl_to_current_float(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100, f=0.9, a=0.001, I0=0, d=0, L=0.3)
        dm = DipoleMagnet(length=1.0, linear_saturation_coefficients=lsf)
        kl_result = dm.current_to_k(50.0, momentum=1e9)
        current = dm.kl_to_current(kl_result["KL"], momentum=1e9)
        assert isinstance(current, (float, complex, np.floating, np.complexfloating))

    def test_kl_to_current_dict(self):
        lsf = LinearSaturationFit(m=0.01, I_max=100, f=0.9, a=0.001, I0=0, d=0, L=0.3)
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
    """Each subclass exposes its own order as a named property over the shared
    multipole store; the setter has to reach the right order, not just any."""
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
        # __init__ sets ks = field_amplitude / length: 2.0 / 0.5 = 4.0
        sol = SolenoidMagnet(field_amplitude=2.0, length=0.5)
        assert sol.ks == pytest.approx(4.0)

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
