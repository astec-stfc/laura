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
from laura.models.element_list import SectionLattice, ElementList
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
        self.name = None
        self.aperture = None

    def append(self, element):
        self.elements.append(element)

    def set_name(self, name):
        self.name = name

    def set_aperture(self, rx, ry, shape):
        self.aperture = (rx, ry, shape)


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

    def TW_Structure(self, *args):
        return _FakeElement("TW_Structure", *args)

    def RF_FieldMap_1d(self, *args):
        return _FakeElement("RF_FieldMap_1d", *args)

    def Static_Magnetic_FieldMap_1d(self, *args):
        return _FakeElement("Static_Magnetic_FieldMap_1d", *args)

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


# ---------------------------------------------------------------------------
# Field maps (laura.translator.utils.fields.rftrack) -- pure arg-building,
# no RF_Track import required.
# ---------------------------------------------------------------------------

from types import SimpleNamespace  # noqa: E402
import numpy as np  # noqa: E402
from laura.translator.utils.fields import rftrack as fields_rftrack  # noqa: E402


def _fake_val(arr):
    return SimpleNamespace(val=np.asarray(arr, dtype=float))


def _fake_field(field_type, cavity_type=None, z=None, Ez=None, Bz=None, **tw_kwargs):
    return SimpleNamespace(
        field_type=field_type,
        cavity_type=cavity_type,
        z_values=np.asarray(z, dtype=float) if z is not None else None,
        Ez=SimpleNamespace(value=_fake_val(Ez)) if Ez is not None else None,
        Bz=SimpleNamespace(value=_fake_val(Bz)) if Bz is not None else None,
        start_cell_z=tw_kwargs.get("start_cell_z"),
        end_cell_z=tw_kwargs.get("end_cell_z"),
        mode_numerator=tw_kwargs.get("mode_numerator"),
        mode_denominator=tw_kwargs.get("mode_denominator"),
    )


def _make_tws_field(
    n_points_per_cell=21, in_points=10, out_points=10,
    mode_numerator=1, mode_denominator=3,
):
    """
    Build a fake ASTRA-TWS-style field: an input coupler, one periodic
    repeat block spanning ``mode_denominator`` physical cells between
    z1=1.0/z2=1.3, and an output coupler -- mirrors the structure
    ``astra.read_astra_field_file``'s ``TravellingWave`` branch parses from
    a real TWS file. The core genuinely oscillates in sign (phase advance
    ``mode_numerator*2*pi/mode_denominator`` per cell, i.e. exactly
    ``mode_numerator`` full periods across the whole block) -- matching real
    ASTRA/CLARA field-map data, unlike a smooth single-hump envelope.
    """
    z1, z2 = 1.0, 1.3
    z_in = np.linspace(z1 - 0.1, z1, in_points, endpoint=False)
    z_core = np.linspace(z1, z2, n_points_per_cell * mode_denominator)
    z_out = np.linspace(z2, z2 + 0.1, out_points + 1)[1:]
    z = np.concatenate([z_in, z_core, z_out])
    ez_core = np.cos(2 * np.pi * mode_numerator * (z_core - z1) / (z2 - z1))
    ez_in = np.zeros_like(z_in)
    ez_out = np.zeros_like(z_out)
    ez = np.concatenate([ez_in, ez_core, ez_out])
    field_obj = _fake_field(
        "1DElectroDynamic", cavity_type="TravellingWave", z=z, Ez=ez,
        start_cell_z=z1, end_cell_z=z2,
        mode_numerator=mode_numerator, mode_denominator=mode_denominator,
    )
    field_obj.read = True
    return field_obj


class TestFieldMapUtils:
    def test_uniform_mesh_regular_grid_passthrough(self):
        z = np.array([0.0, 0.1, 0.2, 0.3])
        values = np.array([0.0, 1.0, 0.5, 0.0])
        hz, out = fields_rftrack._uniform_mesh(z, values)
        assert hz == pytest.approx(0.1)
        assert out == pytest.approx(values)

    def test_uniform_mesh_resamples_irregular_grid(self):
        z = np.array([0.0, 0.1, 0.25, 0.3])  # irregular spacing
        values = np.array([0.0, 1.0, 0.5, 0.0])
        hz, out = fields_rftrack._uniform_mesh(z, values)
        assert hz == pytest.approx(0.1)
        assert len(out) == len(z)

    def test_rf_fieldmap_1d_args_scales_by_amplitude(self):
        z = np.linspace(0, 1, 11)
        ez_norm = np.sin(np.pi * z)  # peak-normalized to 1.0
        field_obj = _fake_field("1DElectroDynamic", cavity_type="StandingWave", z=z, Ez=ez_norm)
        args = fields_rftrack.rf_fieldmap_1d_args(field_obj, amplitude=2e6, frequency=3e9)
        ez, hz, length, freq, direction, p_map, p_actual = args
        assert ez.max() == pytest.approx(2e6)
        assert hz == pytest.approx(0.1)
        assert length == -1
        assert freq == pytest.approx(3e9)
        assert direction == 1

    def test_rf_fieldmap_1d_args_wrong_field_type_raises(self):
        field_obj = _fake_field("1DMagnetoStatic", z=[0, 1], Bz=[0, 1])
        with pytest.raises(ValueError, match="1DElectroDynamic"):
            fields_rftrack.rf_fieldmap_1d_args(field_obj, amplitude=1.0, frequency=1e9)

    def test_rf_fieldmap_1d_args_wrong_cavity_type_raises(self):
        field_obj = _fake_field("1DElectroDynamic", cavity_type="TravellingWave", z=[0, 1], Ez=[0, 1])
        with pytest.raises(ValueError, match="StandingWave"):
            fields_rftrack.rf_fieldmap_1d_args(field_obj, amplitude=1.0, frequency=1e9)

    def test_static_magnetic_fieldmap_1d_args_scales_by_amplitude(self):
        z = np.linspace(-0.1, 0.1, 21)
        bz_norm = np.exp(-(z / 0.03) ** 2)  # peak-normalized to 1.0
        field_obj = _fake_field("1DMagnetoStatic", z=z, Bz=bz_norm)
        args = fields_rftrack.static_magnetic_fieldmap_1d_args(field_obj, amplitude=0.5)
        bz, hz, length = args
        assert bz.max() == pytest.approx(0.5)
        assert length == -1

    def test_static_magnetic_fieldmap_1d_args_wrong_field_type_raises(self):
        field_obj = _fake_field("1DElectroDynamic", cavity_type="StandingWave", z=[0, 1], Ez=[0, 1])
        with pytest.raises(ValueError, match="1DMagnetoStatic"):
            fields_rftrack.static_magnetic_fieldmap_1d_args(field_obj, amplitude=1.0)


class TestTravellingWaveFieldMapArgs:
    """Tests for :func:`rf_fieldmap_1d_travelling_wave_args_list`, which
    returns a list of 1-3 ``RF_FieldMap_1d`` arg-tuples: real input coupler,
    complex core, real output coupler (in that order, omitting an empty
    coupler region) -- ``_make_tws_field``'s fixture always has both
    couplers, so the list is always length 3 here, with the core at
    index 1."""

    def test_stitches_n_cells_with_no_gap(self):
        field_obj = _make_tws_field()
        args_list = fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
            field_obj, amplitude=1e6, frequency=3e9, n_cells=6
        )
        assert len(args_list) == 3
        ez, hz, length, freq, direction, p_map, p_actual = args_list[1]
        assert length == -1
        assert freq == pytest.approx(3e9)
        assert direction == 1
        assert np.iscomplexobj(ez)
        assert hz > 0

    def test_amplitude_scales_peak(self):
        field_obj = _make_tws_field()
        args_small = fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
            field_obj, amplitude=1e6, frequency=3e9, n_cells=3
        )
        args_big = fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
            field_obj, amplitude=2e6, frequency=3e9, n_cells=3
        )
        ez_small = args_small[1][0]
        ez_big = args_big[1][0]
        assert np.abs(ez_big).max() == pytest.approx(2 * np.abs(ez_small).max())

    def test_core_tiles_without_extra_rotation(self):
        """Every tile of the periodic block is identical (see module
        docstring -- an earlier version rotated per tile by
        ``exp(i*i*dphi)``, which summed to exactly zero every
        ``mode_denominator`` replicas); tiling 2 periods vs 1 period should
        therefore give the same peak envelope magnitude, just over double
        the length."""
        field_obj = _make_tws_field()
        args_1 = fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
            field_obj, amplitude=1.0, frequency=3e9, n_cells=3
        )
        args_2 = fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
            field_obj, amplitude=1.0, frequency=3e9, n_cells=6
        )
        ez_1, hz_1 = args_1[1][0], args_1[1][1]
        ez_2, hz_2 = args_2[1][0], args_2[1][1]
        assert np.abs(ez_2).max() == pytest.approx(np.abs(ez_1).max(), rel=0.05)
        assert len(ez_2) * hz_2 == pytest.approx(2 * len(ez_1) * hz_1, rel=0.05)

    def test_missing_preamble_raises(self):
        field_obj = _fake_field(
            "1DElectroDynamic", cavity_type="TravellingWave", z=[0, 1], Ez=[0, 1]
        )
        with pytest.raises(ValueError, match="start_cell_z"):
            fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
                field_obj, amplitude=1.0, frequency=3e9, n_cells=3
            )

    def test_wrong_cavity_type_raises(self):
        field_obj = _make_tws_field()
        field_obj.cavity_type = "StandingWave"
        with pytest.raises(ValueError, match="TravellingWave"):
            fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
                field_obj, amplitude=1.0, frequency=3e9, n_cells=3
            )


# ---------------------------------------------------------------------------
# Cavity/solenoid field-map dispatch (rftrack_conversion.py)
# ---------------------------------------------------------------------------

def _fake_translator(simulation, cavity=None, magnetic=None):
    return SimpleNamespace(simulation=simulation, cavity=cavity, magnetic=magnetic)


class TestCavityFieldMapDispatch:
    def _resolved_field(self):
        z = np.linspace(0, 0.5, 26)
        ez_norm = np.sin(np.pi * z / 0.5)
        field_obj = _fake_field("1DElectroDynamic", cavity_type="StandingWave", z=z, Ez=ez_norm)
        field_obj.read = True
        return field_obj

    def test_available_when_resolved_standing_wave_field(self):
        field_obj = self._resolved_field()
        t = _fake_translator(simulation=SimpleNamespace(field_definition=field_obj))
        assert rftrack_conversion._cavity_fieldmap_available(t) is True

    def test_unavailable_when_no_field_definition(self):
        t = _fake_translator(simulation=SimpleNamespace(field_definition=None))
        assert rftrack_conversion._cavity_fieldmap_available(t) is False

    def test_unavailable_when_travelling_wave(self):
        field_obj = _fake_field("1DElectroDynamic", cavity_type="TravellingWave", z=[0, 1], Ez=[0, 1])
        field_obj.read = True
        t = _fake_translator(simulation=SimpleNamespace(field_definition=field_obj))
        assert rftrack_conversion._cavity_fieldmap_available(t) is False

    def test_build_cavity_fieldmap(self, fake_rftrack):
        field_obj = self._resolved_field()
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=field_obj, field_amplitude=1e6),
            cavity=SimpleNamespace(frequency=3e9, phase=30.0, n_cells=1),
        )
        obj = rftrack_conversion.build_cavity_fieldmap(t)
        assert obj.cls_name == "RF_FieldMap_1d"
        ez, hz, length, freq, direction, p_map, p_actual = obj.args
        # Discrete peak of a 26-point sine sampling isn't exactly the
        # continuous peak, so compare against the source shape's own max
        # (self-consistent) rather than assuming amplitude is hit exactly.
        assert ez.max() == pytest.approx(field_obj.Ez.value.val.max() * 1e6)
        assert freq == pytest.approx(3e9)
        assert obj.phid == pytest.approx(30.0)

    def test_build_rf_cavity_dispatches_to_fieldmap(self, fake_rftrack):
        field_obj = self._resolved_field()
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=field_obj, field_amplitude=1e6),
            cavity=SimpleNamespace(
                frequency=3e9, phase=30.0, n_cells=1, structure_type="StandingWave"
            ),
        )
        obj = rftrack_conversion.build_rf_cavity(t)
        assert obj.cls_name == "RF_FieldMap_1d"

    def test_build_rf_cavity_falls_back_to_pillbox_without_field_map(self, fake_rftrack):
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=None, field_amplitude=1e6),
            cavity=SimpleNamespace(
                frequency=3e9, phase=30.0, n_cells=1, structure_type="StandingWave",
                cell_length=0.5,
            ),
        )
        t.physical = SimpleNamespace(length=0.5)
        obj = rftrack_conversion.build_rf_cavity(t)
        assert obj.cls_name == "Pillbox_Cavity"


class TestTravellingWaveFieldMapDispatch:
    def test_available_when_resolved_tws_field(self):
        field_obj = _make_tws_field()
        t = _fake_translator(simulation=SimpleNamespace(field_definition=field_obj))
        assert rftrack_conversion._tw_fieldmap_available(t) is True

    def test_unavailable_when_no_field_definition(self):
        t = _fake_translator(simulation=SimpleNamespace(field_definition=None))
        assert rftrack_conversion._tw_fieldmap_available(t) is False

    def test_unavailable_when_preamble_missing(self):
        field_obj = _fake_field(
            "1DElectroDynamic", cavity_type="TravellingWave", z=[0, 1], Ez=[0, 1]
        )
        field_obj.read = True
        t = _fake_translator(simulation=SimpleNamespace(field_definition=field_obj))
        assert rftrack_conversion._tw_fieldmap_available(t) is False

    def test_build_tw_fieldmap(self, fake_rftrack):
        """``build_tw_fieldmap`` returns a **list** of a real input coupler,
        complex core, and real output coupler (mirrors manual §4.3.6's own
        SW+TW+SW chaining) -- a flat list, not wrapped in their own
        sub-``Lattice``, so ``SectionLatticeTranslator.to_rftrack`` can
        append each as a direct sibling of the section's own top-level
        Lattice (verified against the real package: a nested Lattice-in-
        Lattice-in-Volume breaks ``Volume.autophase()`` for the inner
        elements, see :func:`build_tw_fieldmap` docstring); every element
        gets the same ``set_phid``."""
        field_obj = _make_tws_field()
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=field_obj, field_amplitude=1e6),
            cavity=SimpleNamespace(frequency=3e9, phase=45.0),
        )
        t.get_cells = lambda: 3
        elems = rftrack_conversion.build_tw_fieldmap(t)
        assert len(elems) == 3
        assert [e.cls_name for e in elems] == ["RF_FieldMap_1d"] * 3
        core_ez, *_ = elems[1].args
        assert np.iscomplexobj(core_ez)
        assert all(e.phid == pytest.approx(45.0) for e in elems)

    def test_build_rf_cavity_dispatches_to_tw_fieldmap(self, fake_rftrack):
        field_obj = _make_tws_field()
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=field_obj, field_amplitude=1e6),
            cavity=SimpleNamespace(
                frequency=3e9, phase=45.0, structure_type="TravellingWave"
            ),
        )
        t.get_cells = lambda: 3
        elems = rftrack_conversion.build_rf_cavity(t)
        assert len(elems) == 3
        assert elems[1].cls_name == "RF_FieldMap_1d"

    def test_build_rf_cavity_falls_back_to_tw_structure_without_preamble(self, fake_rftrack):
        field_obj = _fake_field(
            "1DElectroDynamic", cavity_type="TravellingWave", z=[0, 1], Ez=[0, 1]
        )
        field_obj.read = True
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=field_obj, field_amplitude=1e6),
            cavity=SimpleNamespace(
                frequency=3e9, phase=45.0, n_cells=3, structure_type="TravellingWave",
                mode_numerator=None, mode_denominator=None,
            ),
        )
        t.name = "TW1"
        with pytest.warns(UserWarning, match="mode_numerator"):
            obj = rftrack_conversion.build_rf_cavity(t)
        assert obj.cls_name == "TW_Structure"


class TestSolenoidFieldMapDispatch:
    def _resolved_field(self):
        z = np.linspace(-0.1, 0.1, 21)
        bz_norm = np.exp(-(z / 0.03) ** 2)
        field_obj = _fake_field("1DMagnetoStatic", z=z, Bz=bz_norm)
        field_obj.read = True
        return field_obj

    def test_available_when_resolved_magnetostatic_field(self):
        t = _fake_translator(simulation=SimpleNamespace(field_definition=self._resolved_field()))
        assert rftrack_conversion._magnetic_fieldmap_available(t) is True

    def test_unavailable_when_no_field_definition(self):
        t = _fake_translator(simulation=SimpleNamespace(field_definition=None))
        assert rftrack_conversion._magnetic_fieldmap_available(t) is False

    def test_build_solenoid_dispatches_to_fieldmap(self, fake_rftrack):
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=self._resolved_field()),
            magnetic=SimpleNamespace(field_amplitude=0.5),
        )
        obj = rftrack_conversion.build_solenoid(t)
        assert obj.cls_name == "Static_Magnetic_FieldMap_1d"
        bz, hz, length = obj.args
        assert bz.max() == pytest.approx(0.5)

    def test_build_solenoid_falls_back_to_analytic_without_field_map(self, fake_rftrack):
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=None),
            magnetic=SimpleNamespace(field_amplitude=0.5),
            cavity=None,
        )
        t.physical = SimpleNamespace(length=0.2)
        obj = rftrack_conversion.build_solenoid(t)
        assert obj.cls_name == "Solenoid"
        assert obj.args == (0.2, 0.5, 0.0)


# ---------------------------------------------------------------------------
# Real RF_Track field-map integration (skipped unless installed)
# ---------------------------------------------------------------------------

class TestRealRFTrackFieldMap:
    def test_rf_fieldmap_1d_tracks(self):
        rft = pytest.importorskip("RF_Track")
        z = np.linspace(0, 0.2, 41)
        ez_norm = np.sin(np.pi * z / 0.2)
        field_obj = _fake_field("1DElectroDynamic", cavity_type="StandingWave", z=z, Ez=ez_norm)
        args = fields_rftrack.rf_fieldmap_1d_args(field_obj, amplitude=1e6, frequency=3e9)
        fm = rft.RF_FieldMap_1d(*args)
        lattice = rft.Lattice()
        lattice.append(fm)
        B0 = rft.Bunch6d(rft.electronmass, 0.0, -1, np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 5.0]]))
        B1 = lattice.track(B0)
        assert B1.get_info().transmission >= 0.0

    def test_static_magnetic_fieldmap_1d_tracks(self):
        rft = pytest.importorskip("RF_Track")
        z = np.linspace(-0.1, 0.1, 41)
        bz_norm = np.exp(-(z / 0.03) ** 2)
        field_obj = _fake_field("1DMagnetoStatic", z=z, Bz=bz_norm)
        args = fields_rftrack.static_magnetic_fieldmap_1d_args(field_obj, amplitude=0.5)
        fm = rft.Static_Magnetic_FieldMap_1d(*args)
        lattice = rft.Lattice()
        lattice.append(fm)
        B0 = rft.Bunch6d(rft.electronmass, 0.0, -1, np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 5.0]]))
        B1 = lattice.track(B0)
        assert B1.get_info().transmission >= 0.0

    @staticmethod
    def _tws_field_realistic(frequency=2998.5e6, mode_numerator=1, mode_denominator=3):
        """A realistic S-band-like TWS periodic block (spanning
        ``mode_denominator`` physical cells) with input/output couplers
        either side, for a real end-to-end tracking check -- deliberately
        much finer/larger than ``_make_tws_field()`` (which only needs to
        exercise the arg-building math). The core genuinely oscillates in
        sign (``mode_numerator`` full periods across the whole block,
        matching real ASTRA/CLARA field-map data), unlike a smooth
        single-hump envelope.

        ``z2 - z1 = mode_numerator * c / frequency`` -- the phase-velocity-
        equals-c synchronism condition a real travelling-wave structure
        satisfies (verified: an arbitrary block length gives ~40x less gain,
        since the field's spatial phase advance per cell no longer matches
        how far a relativistic beam travels per RF cycle; real ASTRA/CLARA
        field files satisfy this automatically since they come from an
        actual simulated structure)."""
        c = 299792458.0
        z1 = 0.0
        z2 = mode_numerator * c / frequency
        z_in = np.linspace(z1 - 0.02, z1, 20, endpoint=False)
        z_core = np.linspace(z1, z2, 41)
        z_out = np.linspace(z2, z2 + 0.02, 21)[1:]
        z = np.concatenate([z_in, z_core, z_out])
        ez_core = np.cos(2 * np.pi * mode_numerator * (z_core - z1) / (z2 - z1))
        ez = np.concatenate([np.zeros_like(z_in), ez_core, np.zeros_like(z_out)])
        field_obj = _fake_field(
            "1DElectroDynamic", cavity_type="TravellingWave", z=z, Ez=ez,
            start_cell_z=z1, end_cell_z=z2,
            mode_numerator=mode_numerator, mode_denominator=mode_denominator,
        )
        field_obj.read = True
        return field_obj

    def test_tw_fieldmap_1d_tracks_and_accelerates(self):
        """Regression test for two real, verified findings, using the actual
        three-element (real input coupler + complex core + real output
        coupler) architecture :func:`build_tw_fieldmap` builds:

        1. ``direction`` is NOT cosmetic for the complex core -- unlike the
           standing-wave case (manual §4.4.1's own note that direction is
           interchangeable there), a relativistic forward-moving beam stays
           in phase with a ``direction=1`` (forward) wave over many cells and
           gains substantial energy, but is largely out of phase with a
           ``direction=-1`` (backward) wave and gains much less.
        2. The couplers and core all take the same ``set_phid`` -- verified
           against real CLARA L01 data (this module's ``rf_fieldmap_1d_
           travelling_wave_args_list`` docstring) that this (not the manual's
           own +90 degree core-vs-coupler offset, specific to the analytic
           ``SW_Structure``/``TW_Structure`` pair) is correct for
           ``RF_FieldMap_1d``.
        """
        rft = pytest.importorskip("RF_Track")
        field_obj = self._tws_field_realistic()
        n_cells = 21  # whole multiple of mode_denominator=3
        amplitude = 20e6  # V/m, realistic S-band gradient
        frequency = 2998.5e6
        start_pz = 5.0  # MeV/c
        phase = 0.0

        def _track(direction):
            args_list = fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
                field_obj, amplitude=amplitude, frequency=frequency,
                n_cells=n_cells, direction=direction,
            )
            lattice = rft.Lattice()
            for args in args_list:
                fm = rft.RF_FieldMap_1d(*args)
                fm.set_phid(phase)
                lattice.append(fm)
            B0 = rft.Bunch6d(
                rft.electronmass, 1e9, -1, np.array([[0.0, 0.0, 0.0, 0.0, 0.0, start_pz]])
            )
            return lattice.track(B0).get_info()

        info_fwd = _track(direction=1)
        info_bwd = _track(direction=-1)

        assert info_fwd.transmission == pytest.approx(1e9)
        assert info_bwd.transmission == pytest.approx(1e9)
        gain_fwd = info_fwd.mean_P - start_pz
        gain_bwd = info_bwd.mean_P - start_pz
        assert gain_fwd > 1.0  # substantial acceleration, forward-travelling
        assert gain_fwd > 5 * gain_bwd  # forward wave stays in phase far better
