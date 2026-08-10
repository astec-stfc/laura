"""Extended tests for laura.models.magnetic — MagneticElement, LinearSaturationFit inverses, Wiggler, Solenoid."""

import pytest
import numpy as np

from laura.models.magnetic import (
    MagneticElement,
    CombinedSolenoidQuadrupole_Magnet,
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
from laura.models.baseModels import (
    IgnoreExtra,
    set_functional_definitions,
    set_resolve_functional,
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

    def test_kn(self):
        # Kn == KnL / length
        me = MagneticElement(order=1, length=0.5)
        me.kl = 3.0
        assert me.Kn(1) == pytest.approx(3.0 / 0.5)

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
# CombinedSolenoidQuadrupole
# ---------------------------------------------------------------------------

class TestCombinedSolenoidQuadrupoleMagnet:
    def test_default(self):
        sq = CombinedSolenoidQuadrupole_Magnet()
        assert sq.order == 1
        assert sq.KnL(1) == 0.0
        assert sq.ks == 0.0

    def test_ks_property(self):
        # ks is handled in CombinedSolenoidQuadrupole_Magnet.__init__, not as
        # a Pydantic field -- mirrors Solenoid_Magnet's own ks handling.
        sq = CombinedSolenoidQuadrupole_Magnet(ks=1.5)
        assert sq.ks == pytest.approx(1.5)

    def test_ks_setter(self):
        sq = CombinedSolenoidQuadrupole_Magnet()
        sq.ks = 2.0
        assert sq.ks == pytest.approx(2.0)

    def test_quad_strength_and_ks_together(self):
        # k1l (quad strength, via the inherited MagneticElement.__init__)
        # and ks (solenoid field, via this class's own __init__) must both
        # be settable from the constructor at once.
        sq = CombinedSolenoidQuadrupole_Magnet(length=2.0, k1l=0.6, ks=0.8)
        assert sq.KnL(1) == pytest.approx(0.6)
        assert sq.ks == pytest.approx(0.8)
        assert sq.solenoid_fields.S0L == pytest.approx(0.8)


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


# ---------------------------------------------------------------------------
# Functional parameters
# ---------------------------------------------------------------------------

class TestFunctionalParameters:
    """A strength may be given as a string naming a functional definition; the
    string is stored verbatim and only resolved to a number on computation."""

    @pytest.fixture(autouse=True)
    def _defs(self):
        # Provide a clean set of functional definitions for each test, then
        # reset the shared registry and resolution mode afterwards.
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
        set_resolve_functional(False)
        yield
        set_functional_definitions({}, merge=False)
        set_resolve_functional(False)

    def test_dipole_angle_raw_resolved_flag(self):
        dm = Dipole_Magnet(k0l="dip_angle", length=0.5)
        # configured accessor follows the flag (raw name by default)
        assert dm.angle == "dip_angle"
        assert dm.KnL(0) == pytest.approx(0.1)  # resolved for computation
        assert dm.rho == pytest.approx(0.5 / 0.1)  # rho resolves the angle
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
        # functional edge resolves; "angle/2" references the (resolved) bend angle
        assert dt.e1 == pytest.approx(0.05)
        assert dt.e2 == pytest.approx(0.1 / 2)

    def test_resolution_mode_flag(self):
        qm = Quadrupole_Magnet(k1l="quad1_k1l", length=0.3)
        sol = Solenoid_Magnet(length=0.2, ks="sol_field")
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
        qm = Quadrupole_Magnet(k1l="quad1_k1l", length=0.3)
        # stored symbolically
        assert qm.multipoles.K1L.normal == "quad1_k1l"
        # the plain accessor returns the raw configured value (no auto-resolve)
        assert qm.k1l == "quad1_k1l"
        # KnL is the resolved-number path used for computation
        assert qm.KnL(1) == pytest.approx(-2.0)

    def test_multipole_skew_string(self):
        m = Multipoles(K1L=Multipole(order=1, skew="skew1"))
        # Multipoles.skew returns the raw stored value
        assert m.skew(1) == "skew1"

    def test_undefined_parameter_raises_on_resolution(self):
        qm = Quadrupole_Magnet(k1l="not_defined", length=0.3)
        # storing and reading the raw value never raises
        assert qm.multipoles.K1L.normal == "not_defined"
        assert qm.k1l == "not_defined"
        # only resolution (for computation) raises
        with pytest.raises(KeyError):
            qm.KnL(1)

    def test_solenoid_string(self):
        sol = Solenoid_Magnet(length=0.2, ks="sol_field")
        assert sol.fields.S0L == "sol_field"
        # ks is raw; field_amplitude is the resolved computation (ks/length)
        assert sol.ks == "sol_field"
        assert sol.field_amplitude == pytest.approx(1.5 / 0.2)

    def test_nll_string(self):
        nll = NonLinearLens_Magnet(knll="nll_k", cnll="nll_c")
        assert nll.integrated_strength == "nll_k"
        assert nll.resolved("integrated_strength") == pytest.approx(0.4)
        assert nll.resolved("dimensional_parameter") == pytest.approx(0.01)

    def test_wiggler_string(self):
        w = Wiggler_Magnet(K="wig_K", helical=True)
        assert w.strength == "wig_K"
        assert w.normalized_strength == pytest.approx(1.0)

    def test_float_still_supported(self):
        qm = Quadrupole_Magnet(k1l=-2.5, length=0.3)
        assert qm.k1l == pytest.approx(-2.5)

    def test_get_gradient_resolves(self):
        qm = Quadrupole_Magnet(k1l="quad1_k1l", length=0.3)
        # get_gradient is a computation and resolves the functional strength
        assert qm.get_gradient(momentum=1e9) == pytest.approx(
            -2.0 * 3.3356 * 1e9 / 1e9 / 0.3
        )

    def test_serialisation_keeps_symbolic_value(self):
        qm = Quadrupole_Magnet(k1l="quad1_k1l", length=0.3)
        dumped = qm.model_dump()
        assert dumped["multipoles"]["K1L"]["normal"] == "quad1_k1l"
        # round-trips
        qm2 = Quadrupole_Magnet(**dumped)
        assert qm2.multipoles.K1L.normal == "quad1_k1l"
        assert qm2.k1l == "quad1_k1l"
        assert qm2.KnL(1) == pytest.approx(-2.0)
