"""Tests for laura.translator.converters.*.to_rftrack() and the RF-Track
conversion-rule builder functions.

RF-Track is not installed in CI/dev environments by default (it is not on
PyPI). Tests that need the real package are guarded with
``pytest.importorskip("RF_Track")`` and will skip until it is installed.
Everything else here uses a lightweight fake ``RF_Track`` module (monkeypatched
into ``rftrack_conversion``) so the conversion logic itself — argument values,
units, dispatch — is covered without the real dependency.
"""

import pytest

from laura.models.element import Quadrupole, Dipole, Drift, Marker, Aperture
from laura.models.elementList import SectionLattice, ElementList
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.section import SectionLatticeTranslator
from laura.translator.conversion_rules.codes import rftrack_conversion


# ---------------------------------------------------------------------------
# Fake RF_Track module — captures constructor calls without the real package
# ---------------------------------------------------------------------------

class _FakeElement:
    def __init__(self, cls_name, *args):
        self.cls_name = cls_name
        self.args = args
        self.name = None
        self.aperture = None

    def set_name(self, name):
        self.name = name

    def set_aperture(self, rx, ry, shape):
        self.aperture = (rx, ry, shape)

    def set_phid(self, phid):
        self.phid = phid


class _FakeLattice:
    def __init__(self):
        self.elements = []

    def append(self, element):
        self.elements.append(element)


class _FakeRFTrack:
    def Drift(self, *args):
        return _FakeElement("Drift", *args)

    def Quadrupole(self, *args):
        return _FakeElement("Quadrupole", *args)

    def SBend(self, *args):
        return _FakeElement("SBend", *args)

    def Corrector(self, *args):
        return _FakeElement("Corrector", *args)

    def Solenoid(self, *args):
        return _FakeElement("Solenoid", *args)

    def Undulator(self, *args):
        return _FakeElement("Undulator", *args)

    def Multipole(self, *args):
        return _FakeElement("Multipole", *args)

    def Bpm(self, *args):
        return _FakeElement("Bpm", *args)

    def Screen(self, *args):
        return _FakeElement("Screen", *args)

    def Pillbox_Cavity(self, *args):
        return _FakeElement("Pillbox_Cavity", *args)

    def Lattice(self):
        return _FakeLattice()


@pytest.fixture
def fake_rftrack(monkeypatch):
    fake = _FakeRFTrack()
    monkeypatch.setattr(rftrack_conversion, "_rft", fake)
    monkeypatch.setattr(rftrack_conversion, "_RFTRACK_AVAILABLE", True)
    return fake


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_quad():
    return Quadrupole(
        name="Q1",
        machine_area="SEC",
        magnetic={"length": 0.3, "k1l": -1.5},
        physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
    )


@pytest.fixture
def sample_dipole():
    return Dipole(
        name="D1",
        machine_area="SEC",
        magnetic={"length": 0.5, "angle": 0.1, "entrance_edge_angle": 0.05, "exit_edge_angle": 0.05},
        physical={"length": 0.5, "middle": {"x": 0.0, "y": 0.0, "z": 2.0}},
    )


@pytest.fixture
def sample_drift():
    return Drift(
        name="DR1",
        machine_area="SEC",
        hardware_class="Drift",
        physical={"length": 1.0, "middle": {"x": 0.0, "y": 0.0, "z": 0.5}},
    )


# ---------------------------------------------------------------------------
# rftrack_conversion_rules dict
# ---------------------------------------------------------------------------

class TestConversionRulesTable:
    @pytest.mark.parametrize(
        "hardware_type",
        [
            "Drift", "Quadrupole", "Dipole", "Sextupole", "Octupole", "Solenoid",
            "Undulator", "Horizontal_Corrector", "Vertical_Corrector",
            "Combined_Corrector", "RFCavity", "Beam_Position_Monitor", "Screen",
            "Aperture", "Collimator", "Marker",
        ],
    )
    def test_hardware_type_mapped(self, hardware_type):
        assert hardware_type in rftrack_conversion.rftrack_conversion_rules
        assert callable(rftrack_conversion.rftrack_conversion_rules[hardware_type])

    def test_get_rftrack_raises_clear_error_when_not_installed(self, monkeypatch):
        monkeypatch.setattr(rftrack_conversion, "_RFTRACK_AVAILABLE", False)
        monkeypatch.setattr(rftrack_conversion, "_rft", None)
        with pytest.raises(ImportError, match="RF_Track is not installed"):
            rftrack_conversion.get_rftrack()


# ---------------------------------------------------------------------------
# Element-level to_rftrack()
# ---------------------------------------------------------------------------

class TestElementToRFTrack:
    def test_quadrupole(self, sample_quad, fake_rftrack):
        translated = translate_elements([sample_quad])["Q1"]
        obj = translated.to_rftrack()
        assert obj.cls_name == "Quadrupole"
        length, p_q, k1 = obj.args
        assert length == pytest.approx(0.3)
        assert p_q != p_q  # NaN check (P_Q deferred to autophase)
        assert k1 == pytest.approx(-1.5 / 0.3)
        assert obj.name == "Q1"

    def test_dipole_uses_sbend_with_edge_angles(self, sample_dipole, fake_rftrack):
        translated = translate_elements([sample_dipole])["D1"]
        with pytest.warns(UserWarning, match="No P_Q"):
            obj = translated.to_rftrack()
        assert obj.cls_name == "SBend"
        # RF_Track_reference_manual.pdf SS4.2.3: SBend(L, angle, P_Q, E1, E2).
        length, angle, p_q, e1, e2 = obj.args
        assert length == pytest.approx(0.5)
        assert angle == pytest.approx(0.1)
        assert e1 == pytest.approx(0.05)
        assert e2 == pytest.approx(0.05)

    def test_dipole_without_p_q_warns_and_uses_placeholder(self, sample_dipole, fake_rftrack):
        translated = translate_elements([sample_dipole])["D1"]
        with pytest.warns(UserWarning, match="No P_Q"):
            obj = translated.to_rftrack()
        assert obj.args[2] == 1.0

    def test_dipole_with_p_q_uses_supplied_value(self, sample_dipole, fake_rftrack):
        translated = translate_elements([sample_dipole])["D1"]
        obj = translated.to_rftrack(P_Q=-100.0)
        assert obj.args[2] == pytest.approx(-100.0)

    def test_quadrupole_p_q_always_nan_regardless_of_caller(self, sample_quad, fake_rftrack):
        """Quadrupole should ignore any caller-supplied P_Q and always defer to autophase()."""
        translated = translate_elements([sample_quad])["Q1"]
        obj = translated.to_rftrack(P_Q=-100.0)
        p_q = obj.args[1]
        assert p_q != p_q  # still NaN

    def test_drift(self, sample_drift, fake_rftrack):
        translated = translate_elements([sample_drift])["DR1"]
        obj = translated.to_rftrack()
        assert obj.cls_name == "Drift"
        assert obj.args == (1.0,)

    def test_unmapped_type_falls_back_to_drift_with_warning(self, fake_rftrack):
        elem = Marker(
            name="MK1",
            machine_area="SEC",
            hardware_type="TwissMatch",  # not in rftrack_conversion_rules
            physical={"length": 0.0, "middle": {"x": 0, "y": 0, "z": 0}},
        )
        translated = translate_elements([elem])["MK1"]
        with pytest.warns(UserWarning, match="not supported by RF-Track"):
            obj = translated.to_rftrack()
        assert obj.cls_name == "Drift"

    def test_aperture_applied(self, fake_rftrack):
        elem = Aperture(
            name="AP1",
            machine_area="SEC",
            aperture={"shape": "circular", "radius": 0.02},
            physical={"length": 0.0, "middle": {"x": 0, "y": 0, "z": 0}},
        )
        translated = translate_elements([elem])["AP1"]
        obj = translated.to_rftrack()
        assert obj.cls_name == "Drift"
        assert obj.aperture == (0.02, 0.02, "circular")


# ---------------------------------------------------------------------------
# Section-level to_rftrack()
# ---------------------------------------------------------------------------

class TestSectionToRFTrack:
    def test_builds_lattice_with_all_elements(
        self, sample_drift, sample_quad, sample_dipole, fake_rftrack
    ):
        section = SectionLattice(
            name="SEC",
            order=["DR1", "Q1", "D1"],
            elements=ElementList(
                elements={"DR1": sample_drift, "Q1": sample_quad, "D1": sample_dipole}
            ),
        )
        lattice = SectionLatticeTranslator.from_section(section).to_rftrack(P_Q=-100.0)
        assert isinstance(lattice, _FakeLattice)
        cls_names = [e.cls_name for e in lattice.elements]
        assert "Quadrupole" in cls_names
        assert "SBend" in cls_names
        sbend = next(e for e in lattice.elements if e.cls_name == "SBend")
        assert sbend.args[2] == pytest.approx(-100.0)


# ---------------------------------------------------------------------------
# Real RF_Track integration (skipped unless installed)
# ---------------------------------------------------------------------------

class TestRealRFTrack:
    def test_quadrupole_real(self, sample_quad):
        pytest.importorskip("RF_Track")
        translated = translate_elements([sample_quad])["Q1"]
        obj = translated.to_rftrack()
        assert obj.get_name() == "Q1"

    @staticmethod
    def _track_dipole(rft, sbend, Pref=100.0, Q=-1):
        lattice = rft.Lattice()
        lattice.append(sbend)
        twiss = rft.Bunch6d_twiss()
        twiss.beta_x = twiss.beta_y = 1.0
        twiss.alpha_x = twiss.alpha_y = 0.0
        twiss.emitt_x = twiss.emitt_y = 1.0
        bunch = rft.Bunch6d(rft.electronmass, 1e9, Q, Pref, twiss, 100)
        return lattice.track(bunch)

    def test_dipole_without_p_q_gives_wrong_trajectory_but_no_loss(self, sample_dipole):
        """Regression test for a real, verified finding: passing a raw NaN
        P_Q to RF-Track's SBend (unlike Quadrupole/Multipole, which support
        deferring to autophase()) silently produces zero transmission. Our
        placeholder-of-1.0 fallback (with a warning) avoids that total loss,
        but still gives the WRONG bend trajectory for a real ~100 MeV/c beam
        -- confirming P_Q genuinely affects the physics, not just reporting."""
        rft = pytest.importorskip("RF_Track")
        translated = translate_elements([sample_dipole])["D1"]
        with pytest.warns(UserWarning, match="No P_Q"):
            sbend_no_p_q = translated.to_rftrack()
        tracked_wrong = self._track_dipole(rft, sbend_no_p_q)
        assert tracked_wrong.get_info().transmission == pytest.approx(1e9)

        sbend_correct = translated.to_rftrack(P_Q=100.0 / -1)
        tracked_correct = self._track_dipole(rft, sbend_correct)
        assert tracked_correct.get_info().transmission == pytest.approx(1e9)

        # Same beam, same dipole geometry, different P_Q -> different bend.
        assert tracked_wrong.get_info().mean_x != pytest.approx(
            tracked_correct.get_info().mean_x
        )

    def test_dipole_with_p_q_preserves_transmission(self, sample_dipole):
        rft = pytest.importorskip("RF_Track")
        translated = translate_elements([sample_dipole])["D1"]
        Pref = 100.0
        Q = -1
        sbend = translated.to_rftrack(P_Q=Pref / Q)
        tracked = self._track_dipole(rft, sbend, Pref=Pref, Q=Q)
        assert tracked.get_info().transmission == pytest.approx(1e9)
