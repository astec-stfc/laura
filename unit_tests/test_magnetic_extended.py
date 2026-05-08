"""Extended tests for laura.models.magnetic — MagneticElement, LinearSaturationFit inverses, Wiggler, Solenoid."""

import pytest
import numpy as np

from laura.models.magnetic import (
    MagneticElement,
    Dipole_Magnet,
    Quadrupole_Magnet,
    Sextupole_Magnet,
    Octupole_Magnet,
    Solenoid_Magnet,
    NonLinearLens_Magnet,
    Wiggler_Magnet,
    Multipole,
    Multipoles,
    FieldIntegral,
    LinearSaturationFit,
)

# ---------------------------------------------------------------------------
# Multipole
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# FieldIntegral
# ---------------------------------------------------------------------------


class TestFieldIntegral:
    def test_current_to_k_linear(self):
        fi = FieldIntegral(coefficients=[0.0, 0.5])  # K = 0.5 * current
        k = fi.currentToK(10.0, energy=1e9)
        assert isinstance(k, float)

    def test_current_to_k_polynomial(self):
        fi = FieldIntegral(coefficients=[0.0, 1.0, 0.01])
        k = fi.currentToK(5.0, energy=1e9)
        assert isinstance(k, float)


# ---------------------------------------------------------------------------
# LinearSaturationFit
# ---------------------------------------------------------------------------


class TestLinearSaturationFit:
    @pytest.fixture
    def lsf(self):
        return LinearSaturationFit(
            m=0.01, I_max=100.0, f=0.9, a=0.001, I0=0.0, d=0.0, L=0.3
        )

    def test_current_to_k(self, lsf):
        result = lsf.currentToK(50.0, momentum=1e9)
        assert isinstance(result, dict)
        assert "KL" in result

    def test_kl_to_current(self, lsf):
        # Get the KL from a known current
        kl = lsf.currentToK(50.0, momentum=1e9)["KL"]
        current = lsf.KLToCurrent(kl, momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_k_to_current(self, lsf):
        k_result = lsf.currentToK(50.0, momentum=1e9)
        K = k_result["K"]
        current = lsf.KToCurrent(K, momentum=1e9)
        assert current == pytest.approx(50.0, rel=0.01)

    def test_from_string(self):
        lsf = LinearSaturationFit.from_string("0.01,100,0.9,0.001,0,0,0.3")
        assert lsf.m == pytest.approx(0.01)
        assert lsf.I_max == pytest.approx(100.0)
        assert lsf.L == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# MagneticElement
# ---------------------------------------------------------------------------


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

    def test_half_gap(self):
        me = MagneticElement(gap=0.04)
        # half_gap is a computed field: gap / 2
        assert me.half_gap == pytest.approx(0.02)


# ---------------------------------------------------------------------------
# Magnet subtypes
# ---------------------------------------------------------------------------


class TestDipoleMagnet:
    def test_defaults(self):
        dm = Dipole_Magnet()
        assert dm.order == 0
        assert dm.angle == 0

    def test_angle(self):
        # angle is a property reading multipoles.K0L.normal;
        # set via k0l in the MagneticElement constructor
        dm = Dipole_Magnet(k0l=0.1)
        assert dm.angle == pytest.approx(0.1)

    def test_rho(self):
        dm = Dipole_Magnet(k0l=0.1, length=1.0)
        assert dm.rho == pytest.approx(10.0)


class TestQuadrupoleMagnet:
    def test_defaults(self):
        qm = Quadrupole_Magnet()
        assert qm.order == 1
        assert qm.k1l == 0

    def test_k1l(self):
        qm = Quadrupole_Magnet(k1l=-2.5)
        assert qm.k1l == pytest.approx(-2.5)


class TestSextupleMagnet:
    def test_defaults(self):
        sm = Sextupole_Magnet()
        assert sm.order == 2
        assert sm.k2l == 0

    def test_k2l(self):
        sm = Sextupole_Magnet(k2l=100.0)
        assert sm.k2l == pytest.approx(100.0)


class TestOctupleMagnet:
    def test_defaults(self):
        om = Octupole_Magnet()
        assert om.order == 3
        assert om.k3l == 0


# ---------------------------------------------------------------------------
# Solenoid
# ---------------------------------------------------------------------------


class TestSolenoidMagnet:
    def test_default(self):
        sol = Solenoid_Magnet()
        assert sol.ks == 0.0

    def test_ks_property(self):
        # ks is handled in Solenoid_Magnet.__init__, not as a Pydantic field
        sol = Solenoid_Magnet(ks=1.5)
        assert sol.ks == pytest.approx(1.5)

    def test_ks_setter(self):
        sol = Solenoid_Magnet()
        sol.ks = 2.0
        assert sol.ks == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# NonLinearLens
# ---------------------------------------------------------------------------


class TestNonLinearLensMagnet:
    def test_default(self):
        nll = NonLinearLens_Magnet()
        assert nll.length == 0
        assert nll.integrated_strength == 0
        assert nll.dimensional_parameter == 0


# ---------------------------------------------------------------------------
# Wiggler
# ---------------------------------------------------------------------------


class TestWigglerMagnet:
    def test_default(self):
        w = Wiggler_Magnet()
        assert w.strength == 0
        assert w.period == 0

    def test_with_values(self):
        w = Wiggler_Magnet(
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
        w = Wiggler_Magnet(num_periods=50)
        assert w.poles == 100

    def test_normalized_strength_planar(self):
        w = Wiggler_Magnet(strength=1.0, helical=False)
        # For planar: normalized_strength = K / sqrt(2)
        assert w.normalized_strength == pytest.approx(1.0 / np.sqrt(2))

    def test_normalized_strength_helical(self):
        w = Wiggler_Magnet(strength=1.0, helical=True)
        # For helical: normalized_strength = K
        assert w.normalized_strength == pytest.approx(1.0)
