# python
from laura.models.magnetic import (
    Multipole,
    Multipoles,
    FieldIntegral,
    LinearSaturationFit,
    MagneticElement,
    Dipole_Magnet,
    Quadrupole_Magnet,
    Sextupole_Magnet,
    Octupole_Magnet,
    Solenoid_Magnet,
    SolenoidFields,
    NonLinearLens_Magnet,
    Wiggler_Magnet,
    Corrector_Magnet,
)
from laura.models._generated import (
    _SolenoidMagnetBase,
    _WigglerMagnetBase,
    _NonLinearLensMagnetBase,
    _CorrectorMagnetBase,
    _SolenoidFieldsBase,
)


def test_multipole_initialization():
    m = Multipole(order=1, normal=0.5, skew=0.2)
    assert m.order == 1
    assert m.normal == 0.5
    assert m.skew == 0.2


def test_multipoles_operations():
    multipoles = Multipoles(K1L={"order": 1, "normal": 0.5})
    assert multipoles.normal(1) == 0.5
    assert multipoles.K1L.order == 1


def test_field_integral_current_to_k():
    fi = FieldIntegral(coefficients=[1, 2, 3])
    k = fi.currentToK(current=10, energy=100)
    assert k > 0


def test_linear_saturation_fit_current_to_k():
    lsf = LinearSaturationFit(m=1, I_max=10, f=0.1, a=0.2, I0=5, d=0.3, L=1)
    result = lsf.currentToK(current=5, momentum=100)
    assert "K" in result
    assert result["K"] > 0


def test_magnetic_element_properties():
    me = MagneticElement(
        order=1, length=2.0, multipoles={"K1L": {"order": 1, "normal": 0.5}}
    )
    assert me.KnL(1) == 0.5
    assert me.get_gradient(momentum=100) > 0


def test_dipole_magnet_properties():
    dipole = Dipole_Magnet(length=2.0)
    dipole.angle = 0.1
    assert dipole.rho > 0
    assert dipole.field_strength(momentum=100) > 0


def test_quadrupole_magnet_properties():
    quad = Quadrupole_Magnet(length=1.0, k1l=0.2)
    assert quad.k1l == 0.2


def test_sextupole_magnet_properties():
    sext = Sextupole_Magnet(length=1.0, k2l=0.2)
    assert sext.k2l == 0.2


def test_octupole_magnet_properties():
    sext = Octupole_Magnet(length=1.0, k3l=0.2)
    assert sext.k3l == 0.2


def test_solenoid_magnet_properties():
    solenoid = Solenoid_Magnet(length=1.0, ks=0.3)
    assert solenoid.ks == 0.3


def test_nonlinear_lens_magnet():
    lens = NonLinearLens_Magnet(length=1.0, integrated_strength=0.5)
    assert lens.integrated_strength == 0.5


def test_wiggler_magnet_properties():
    wiggler = Wiggler_Magnet(length=2.0, strength=1.0, period=0.1, num_periods=10)
    assert wiggler.normalized_strength > 0
    assert wiggler.poles == 20


def test_solenoid_fields():
    fields = SolenoidFields(S0L=0.5, S1L=0.3)
    assert fields.S0L == 0.5
    assert fields.S1L == 0.3


class TestGeneratedBaseWiring:
    """Solenoid_Magnet, Wiggler_Magnet, NonLinearLens_Magnet, Corrector_Magnet and
    SolenoidFields inherit their LinkML-generated ``_XxxBase`` counterpart
    (unlike Dipole_Magnet/Quadrupole_Magnet/Sextupole_Magnet/Octupole_Magnet,
    which reach _MagneticElementBase only via MagneticElement -- there is no
    per-order generated magnetic-field base to wire onto for those). This class
    guards the wiring itself and the two traps that come with it."""

    def test_classes_inherit_generated_bases(self):
        assert issubclass(Solenoid_Magnet, _SolenoidMagnetBase)
        assert issubclass(Wiggler_Magnet, _WigglerMagnetBase)
        assert issubclass(NonLinearLens_Magnet, _NonLinearLensMagnetBase)
        assert issubclass(Corrector_Magnet, _CorrectorMagnetBase)
        assert issubclass(SolenoidFields, _SolenoidFieldsBase)

    def test_legacy_yaml_aliases_still_load(self):
        """The generated bases don't declare these legacy aliases (the schema
        chunk doesn't list them), so the hand-written Field(alias=...)
        overrides must still be in effect, not shadowed by the generated
        field of the same name."""
        sol = Solenoid_Magnet(magnetic_length=0.3, mag_set_max_wait_time=99.0)
        assert sol.length == 0.3
        assert sol.settle_time == 99.0

        wig = Wiggler_Magnet(K=1.5, B=0.8, lambdau=0.05, nwig=40, kx=0.1)
        assert wig.strength == 1.5
        assert wig.peak_magnetic_field == 0.8
        assert wig.period == 0.05
        assert wig.num_periods == 40
        assert wig.quadratic_roll_off_x == 0.1

        nll = NonLinearLens_Magnet(magnetic_length=0.2, knll=1.0, cnll=0.01)
        assert nll.integrated_strength == 1.0
        assert nll.dimensional_parameter == 0.01

    def test_functional_string_values_still_accepted(self):
        """The generated bases type these slots as plain float; the
        hand-written Union[float, str] override (for functional-definition
        names) must win, not the generated float-only field."""
        wig = Wiggler_Magnet(K="wiggler_k_expr")
        assert wig.strength == "wiggler_k_expr"

        corr = Corrector_Magnet(horizontal_kick="hcorr_expr")
        assert corr.horizontal_kick == "hcorr_expr"

        nll = NonLinearLens_Magnet(knll="nll_k_expr")
        assert nll.integrated_strength == "nll_k_expr"

        fields = SolenoidFields(S0L="sol_expr")
        assert fields.S0L == "sol_expr"

    def test_model_dump_uses_field_names_not_aliases(self):
        """Regression guard: _SolenoidMagnetBase etc. pull in
        ConfiguredBaseModel's serialize_by_alias=True. Combined with the
        Field(alias=...) overrides above -- alias is bidirectional, unlike the
        generated classes' input-only validation_alias -- model_dump() would
        emit YAML aliases ("knll", "mag_set_max_wait_time", ...) instead of
        field names, silently breaking flatten_dict()-based full_dump() and
        any other export path keyed by field name. Each class pins
        serialize_by_alias back to False to prevent this."""
        nll = NonLinearLens_Magnet(magnetic_length=0.1, knll=0.4, cnll=0.01)
        dumped = nll.model_dump()
        assert "integrated_strength" in dumped
        assert "knll" not in dumped

        sol = Solenoid_Magnet(magnetic_length=0.3, mag_set_max_wait_time=99.0)
        dumped = sol.model_dump()
        assert "settle_time" in dumped
        assert "mag_set_max_wait_time" not in dumped

        wig = Wiggler_Magnet(K=1.5)
        dumped = wig.model_dump()
        assert "strength" in dumped
        assert "K" not in dumped

        corr = Corrector_Magnet(magnetic_length=0.1)
        dumped = corr.model_dump()
        assert "length" in dumped
        assert "magnetic_length" not in dumped
