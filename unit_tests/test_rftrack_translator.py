"""RF-Track tests; RF_Track is optional, so most use a fake module."""

import pytest

from laura.models.element import Quadrupole, Dipole, Drift, Marker, Aperture
from laura.models.element_list import SectionLattice, ElementList
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.section import SectionLatticeTranslator
from laura.translator.conversion_rules.codes import rftrack_conversion


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

    def append(self, element, *placement):
        element.placement = placement
        self.elements.append(element)

    def set_name(self, name):
        self.name = name

    def set_aperture(self, rx, ry, shape):
        self.aperture = (rx, ry, shape)


class _FakeRFTrack:
    def __getattr__(self, cls_name):
        if cls_name.startswith("_"):
            raise AttributeError(cls_name)
        return lambda *args: _FakeElement(cls_name, *args)

    def Lattice(self):
        return _FakeLattice()


@pytest.fixture
def fake_rftrack(monkeypatch):
    fake = _FakeRFTrack()
    monkeypatch.setattr(rftrack_conversion, "_rft", fake)
    monkeypatch.setattr(rftrack_conversion, "_RFTRACK_AVAILABLE", True)
    return fake


@pytest.fixture
def rft():
    """The real RF_Track package; skips the test when it is not installed."""
    return pytest.importorskip("RF_Track")


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


class TestElementToRFTrack:
    def test_quadrupole(self, sample_quad, fake_rftrack):
        translated = translate_elements([sample_quad])["Q1"]
        obj = translated.to_rftrack()
        assert obj.cls_name == "Quadrupole"
        length, p_q, k1 = obj.args
        assert length == pytest.approx(0.3)
        assert p_q != p_q  # NaN: P_Q deferred to autophase
        assert k1 == pytest.approx(-1.5 / 0.3)
        assert obj.name == "Q1"

    def test_dipole_uses_sbend_with_edge_angles(self, sample_dipole, fake_rftrack):
        translated = translate_elements([sample_dipole])["D1"]
        obj = translated.to_rftrack()
        assert obj.cls_name == "SBend"
        # RF_Track_reference_manual.pdf SS4.2.3: SBend(L, angle, P_Q, E1, E2).
        length, angle, p_q, e1, e2 = obj.args
        assert length == pytest.approx(0.5)
        assert angle == pytest.approx(0.1)
        assert p_q != p_q  # NaN: P_Q left to the bunch / autophase
        assert e1 == pytest.approx(0.05)
        assert e2 == pytest.approx(0.05)

    def test_dipole_with_p_q_uses_supplied_value(self, sample_dipole, fake_rftrack):
        translated = translate_elements([sample_dipole])["D1"]
        obj = translated.to_rftrack(P_Q=-100.0)
        assert obj.args[2] == pytest.approx(-100.0)

    def test_quadrupole_p_q_always_nan_regardless_of_caller(self, sample_quad, fake_rftrack):
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


class TestRealRFTrack:
    def test_quadrupole_real(self, sample_quad, rft):
        translated = translate_elements([sample_quad])["Q1"]
        obj = translated.to_rftrack()
        assert obj.get_name() == "Q1"

    def test_dipole_without_p_q_bends_with_the_bunch(self, sample_dipole, rft):
        """A NaN P_Q takes the bunch's own: the same as passing it."""
        translated = translate_elements([sample_dipole])["D1"]
        bunch = np.array([[1.0, 0.5, 0.5, 0.2, 0, 100.0, rft.electronmass, -1, 1, 0]])

        def track(sbend):
            lattice = rft.Lattice()
            lattice.append(sbend)
            return lattice.track(rft.Bunch6d(bunch)).get_phase_space("%x %xp %y %yp")

        unset = track(translated.to_rftrack())
        assert unset.shape == (1, 4)
        assert unset == pytest.approx(track(translated.to_rftrack(P_Q=100.0 / -1)), rel=1e-12)

    def test_dipole_without_p_q_follows_acceleration(self, sample_dipole, rft):
        """After a cavity, autophase gives the bend the accelerated P/Q; the
        incoming one would leave the bunch off axis."""
        translated = translate_elements([sample_dipole])["D1"]

        def mean_x(sbend):
            cavity = rft.Pillbox_Cavity(np.array([20e6]), 3e9, 0.05, 1)
            lattice = rft.Lattice()
            lattice.append(cavity)
            lattice.append(sbend)
            bunch = rft.Bunch6d(np.array([[0, 0, 0, 0, 0, 100.0, rft.electronmass, -1, 1, 0]]))
            lattice.autophase(bunch)
            return lattice.track(bunch).get_info().mean_x

        assert mean_x(translated.to_rftrack()) == pytest.approx(0.0, abs=1e-9)
        assert abs(mean_x(translated.to_rftrack(P_Q=-100.0))) > 1e-3

    def test_dipole_fringe_field_focuses_vertically_as_in_mad(self, rft):
        """fint/hgap reach the SBend: its vertical map is MAD's edge . drift . edge."""
        length, angle, edge, fint, hgap = 0.2, -0.3, -0.15, 0.45, 0.015
        dipole = Dipole(
            name="D1",
            machine_area="SEC",
            magnetic={
                "length": length, "angle": angle, "entrance_edge_angle": edge,
                "exit_edge_angle": edge, "gap": 2 * hgap,
                "edge_field_integral_entrance": fint, "edge_field_integral_exit": fint,
            },
            physical={"length": length, "middle": {"x": 0.0, "y": 0.0, "z": 2.0}},
        )
        lattice = rft.Lattice()
        lattice.append(translate_elements([dipole])["D1"].to_rftrack())
        d = 1e-4
        start = np.zeros((3, 10))
        start[:, 5:9] = [100.0, rft.electronmass, -1, 1]
        start[1, 2], start[2, 3] = d, d
        out = lattice.track(rft.Bunch6d(start)).get_phase_space("%y %yp")
        got = ((out[1:] - out[0]) / d).T

        h = angle / length
        psi = 2 * hgap * h * fint * (1 + np.sin(edge) ** 2) / np.cos(edge)
        kick = np.array([[1, 0], [-h * np.tan(edge - psi), 1]])
        expected = kick @ np.array([[1, length], [0, 1]]) @ kick
        assert got == pytest.approx(expected, abs=1e-8)

    def test_tilted_dipole_bends_vertically(self, rft):
        """A tilt of pi/2 rolls the bend into y, with MAD's sign (as Xsuite's rot_s_rad)."""
        dipole = Dipole(
            name="BY1",
            machine_area="SEC",
            magnetic={"length": 1.0, "angle": 0.01, "tilt": np.pi / 2},
            physical={"length": 1.0, "middle": {"x": 0.0, "y": 0.0, "z": 0.5}},
        )
        section = SectionLattice(
            name="SEC", order=["BY1"], elements=ElementList(elements={"BY1": dipole})
        )
        lattice = SectionLatticeTranslator.from_section(section).to_rftrack()
        off_momentum = np.array([[0, 0, 0, 0, 0, 1010.0, rft.electronmass, -1, 1, 0]])
        lattice.autophase(rft.Bunch6d(off_momentum * [1, 1, 1, 1, 1, 1000 / 1010, 1, 1, 1, 1]))
        x, xp, y, yp = lattice.track(rft.Bunch6d(off_momentum)).get_phase_space("%x %xp %y %yp")[0]
        assert (x, xp) == pytest.approx((0.0, 0.0), abs=1e-12)
        assert y == pytest.approx(0.0495, rel=1e-2)  # rho * angle^2 / 2 * delta / (1 + delta), in mm
        assert yp > 0

    def test_tw_structure_spans_the_element_and_gains_the_bmad_voltage(self, rft):
        """An LCLS 10-ft structure: as long as the element, and on crest it gains
        Elegant/Bmad's field_amplitude * (cells + 3.8) * cell_length / sqrt(2)."""
        from laura.models.element import RFCavity

        cell_length, amplitude = 0.03498978267973856, 2e7
        cavity = RFCavity(
            name="K1",
            machine_area="SEC",
            cavity={
                "frequency": 2856e6, "n_cells": 86, "cell_length": cell_length,
                "structure_type": "TravelingWave", "phase": 0.0,
                "mode_numerator": 1, "mode_denominator": 3,
            },
            simulation={"field_amplitude": amplitude},
            physical={"length": 3.0441, "middle": {"x": 0.0, "y": 0.0, "z": 2.0}},
        )
        structure = translate_elements([cavity])["K1"].to_rftrack()
        assert structure.get_length() == pytest.approx(3.0441)
        lattice = rft.Lattice()
        lattice.append(structure)
        bunch = rft.Bunch6d(np.array([[0, 0, 0, 0, 0, 1000.0, rft.electronmass, -1, 1, 0]]))
        lattice.autophase(bunch)
        gain = lattice.track(bunch).get_phase_space("%Pc")[0, 0] - 1000.0
        assert gain == pytest.approx(amplitude * (84 + 3.8) * cell_length / np.sqrt(2) / 1e6, rel=1e-3)


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
        read=True,
    )


def _tw_without_preamble():
    """A travelling-wave field with no start/end cell markers."""
    return _fake_field("1DElectroDynamic", cavity_type="TravellingWave", z=[0, 1], Ez=[0, 1])


def _make_tws_field(
    n_points_per_cell=21, in_points=10, out_points=10,
    mode_numerator=1, mode_denominator=3, coupler_field=False,
):
    """Fake ASTRA TWS field: coupler, a ``mode_denominator``-cell block (z 1.0-1.3)
    oscillating ``mode_numerator`` periods, coupler. The couplers have no field,
    or with ``coupler_field`` carry the core's wave on.
    """
    z1, z2 = 1.0, 1.3
    z_in = np.linspace(z1 - 0.1, z1, in_points, endpoint=False)
    z_core = np.linspace(z1, z2, n_points_per_cell * mode_denominator)
    z_out = np.linspace(z2, z2 + 0.1, out_points + 1)[1:]
    z = np.concatenate([z_in, z_core, z_out])
    ez = np.cos(2 * np.pi * mode_numerator * (z - z1) / (z2 - z1))
    if not coupler_field:
        ez[(z < z1) | (z > z2)] = 0.0
    field_obj = _fake_field(
        "1DElectroDynamic", cavity_type="TravellingWave", z=z, Ez=ez,
        start_cell_z=z1, end_cell_z=z2,
        mode_numerator=mode_numerator, mode_denominator=mode_denominator,
    )
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
    """One complex map over input coupler, tiled core and output coupler."""

    @staticmethod
    def _map(n_cells, amplitude=1.0, **kw):
        (args,) = fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
            _make_tws_field(**kw), amplitude=amplitude, frequency=3e9, n_cells=n_cells
        )
        return args

    def test_one_map_spans_couplers_and_tiled_core(self):
        ez, hz, length, freq, direction, p_map, p_actual = self._map(6)
        assert (length, freq, direction) == (-1, pytest.approx(3e9), 1)
        assert np.iscomplexobj(ez)
        # 0.1 m couplers either side of two 0.3 m blocks
        assert (len(ez) - 1) * hz == pytest.approx(0.8, abs=hz)

    def test_real_part_is_the_source_field(self):
        ez, hz, *_ = self._map(6, amplitude=2e6, coupler_field=True)
        z = np.arange(len(ez)) * hz - 0.1  # from the core's start
        # 1%: the couplers' coarser samples are resampled linearly
        assert np.real(ez) == pytest.approx(2e6 * np.cos(2 * np.pi * z / 0.3), abs=2e6 * 1e-2)

    def test_quadrature_field_does_not_jump_at_the_couplers(self):
        """Real couplers joined to a complex core would step by the full amplitude."""
        ez, hz, *_ = self._map(6, coupler_field=True)
        step = 2 * np.pi / 0.3 * hz  # largest sample-to-sample change of a unit wave
        assert np.abs(np.diff(ez)).max() < 3 * step

    def test_amplitude_scales_peak(self):
        small, big = self._map(3, amplitude=1e6)[0], self._map(3, amplitude=2e6)[0]
        assert np.abs(big).max() == pytest.approx(2 * np.abs(small).max())

    def test_core_tiles_without_extra_rotation(self):
        """Identical tiles: 2 periods give 1 period's peak over one block more."""
        ez_1, hz_1, *_ = self._map(3)
        ez_2, hz_2, *_ = self._map(6)
        assert np.abs(ez_2).max() == pytest.approx(np.abs(ez_1).max(), rel=0.05)
        assert (len(ez_2) - len(ez_1)) * hz_1 == pytest.approx(0.3, abs=hz_1)

    def test_missing_preamble_raises(self):
        field_obj = _tw_without_preamble()
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


def _fake_translator(simulation, cavity=None, magnetic=None):
    # RFCavityTranslator.structure_type, which also accepts Bmad's "TravelingWave"
    structure = str(getattr(cavity, "structure_type", "StandingWave"))
    structure = "TravellingWave" if structure.lower() in ("travellingwave", "travelingwave") else structure
    return SimpleNamespace(
        simulation=simulation, cavity=cavity, magnetic=magnetic, structure_type=structure
    )


@pytest.mark.parametrize(
    "available",
    ["_cavity_fieldmap_available", "_tw_fieldmap_available", "_magnetic_fieldmap_available"],
)
def test_fieldmap_unavailable_without_field_definition(available):
    t = _fake_translator(simulation=SimpleNamespace(field_definition=None))
    assert getattr(rftrack_conversion, available)(t) is False


class TestCavityFieldMapDispatch:
    def _resolved_field(self):
        z = np.linspace(0, 0.5, 26)
        ez_norm = np.sin(np.pi * z / 0.5)
        field_obj = _fake_field("1DElectroDynamic", cavity_type="StandingWave", z=z, Ez=ez_norm)
        return field_obj

    def test_available_when_resolved_standing_wave_field(self):
        field_obj = self._resolved_field()
        t = _fake_translator(simulation=SimpleNamespace(field_definition=field_obj))
        assert rftrack_conversion._cavity_fieldmap_available(t) is True

    def test_unavailable_when_travelling_wave(self):
        field_obj = _tw_without_preamble()
        t = _fake_translator(simulation=SimpleNamespace(field_definition=field_obj))
        assert rftrack_conversion._cavity_fieldmap_available(t) is False

    def test_build_cavity_fieldmap(self, fake_rftrack):
        field_obj = self._resolved_field()
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=field_obj, field_amplitude=1e6),
            cavity=SimpleNamespace(frequency=3e9, phase=30.0, n_cells=1.5),
        )
        obj = rftrack_conversion.build_cavity_fieldmap(t)
        assert obj.cls_name == "RF_FieldMap_1d"
        ez, hz, length, freq, direction, p_map, p_actual = obj.args
        # The peak field, as ASTRA's MaxE: not scaled by n_cells (a gun's 1.5).
        # 26 samples miss the continuous peak, so compare against the source's own max.
        assert ez.max() == pytest.approx(field_obj.Ez.value.val.max() * 1e6)
        assert freq == pytest.approx(3e9)
        assert obj.phid == pytest.approx(-30.0)  # ASTRA's sign: Phi = crest - phase

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
        """``field_amplitude`` is the voltage: a half-wavelength cell (transit-time
        factor 2/pi) needs ``V / (L * 2/pi)``."""
        half_wave = 299792458.0 / 3e9 / 2
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=None, field_amplitude=1e6),
            cavity=SimpleNamespace(
                frequency=3e9, phase=30.0, n_cells=1, structure_type="StandingWave",
                cell_length=half_wave,
            ),
        )
        t.physical = SimpleNamespace(length=half_wave)
        obj = rftrack_conversion.build_rf_cavity(t)
        assert obj.cls_name == "Pillbox_Cavity"
        assert obj.args[0][0] == pytest.approx(1e6 / (half_wave * 2 / np.pi))

    def test_build_rf_cavity_without_field_is_a_drift(self, fake_rftrack):
        """RF-Track loses every particle in a zero-field RF element."""
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=None, field_amplitude=0.0),
            cavity=SimpleNamespace(frequency=3e9, phase=0.0, structure_type="StandingWave"),
        )
        t.physical = SimpleNamespace(length=0.5)
        obj = rftrack_conversion.build_rf_cavity(t)
        assert (obj.cls_name, obj.args) == ("Drift", (0.5,))


class TestTravellingWaveFieldMapDispatch:
    def test_available_when_resolved_tws_field(self):
        field_obj = _make_tws_field()
        t = _fake_translator(simulation=SimpleNamespace(field_definition=field_obj))
        assert rftrack_conversion._tw_fieldmap_available(t) is True

    def test_unavailable_when_preamble_missing(self):
        field_obj = _tw_without_preamble()
        t = _fake_translator(simulation=SimpleNamespace(field_definition=field_obj))
        assert rftrack_conversion._tw_fieldmap_available(t) is False

    def test_build_tw_fieldmap(self, fake_rftrack):
        field_obj = _make_tws_field()
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=field_obj, field_amplitude=1e6),
            cavity=SimpleNamespace(frequency=3e9, phase=45.0),
        )
        t.get_cells = lambda: 3
        obj = rftrack_conversion.build_tw_fieldmap(t)
        assert obj.cls_name == "RF_FieldMap_1d"
        assert np.iscomplexobj(obj.args[0])
        assert obj.phid == pytest.approx(-45.0)

    def test_build_rf_cavity_dispatches_to_tw_fieldmap(self, fake_rftrack):
        field_obj = _make_tws_field()
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=field_obj, field_amplitude=1e6),
            cavity=SimpleNamespace(
                frequency=3e9, phase=45.0, structure_type="TravellingWave"
            ),
        )
        t.get_cells = lambda: 3
        assert rftrack_conversion.build_rf_cavity(t).cls_name == "RF_FieldMap_1d"

    def test_build_rf_cavity_falls_back_to_tw_structure_without_preamble(self, fake_rftrack):
        field_obj = _tw_without_preamble()
        t = _fake_translator(
            simulation=SimpleNamespace(field_definition=field_obj, field_amplitude=1e6),
            cavity=SimpleNamespace(
                frequency=3e9, phase=45.0, n_cells=3, structure_type="TravellingWave",
                mode_numerator=None, mode_denominator=None, cell_length=1 / 30,
            ),
        )
        t.name = "TW1"
        t.physical = SimpleNamespace(length=0.1)
        t.get_cells = lambda: 3
        with pytest.warns(UserWarning, match="mode_numerator"):
            obj = rftrack_conversion.build_rf_cavity(t)
        assert obj.cls_name == "TW_Structure"


class TestSolenoidFieldMapDispatch:
    def _resolved_field(self):
        z = np.linspace(-0.1, 0.1, 21)
        bz_norm = np.exp(-(z / 0.03) ** 2)
        field_obj = _fake_field("1DMagnetoStatic", z=z, Bz=bz_norm)
        return field_obj

    def test_available_when_resolved_magnetostatic_field(self):
        t = _fake_translator(simulation=SimpleNamespace(field_definition=self._resolved_field()))
        assert rftrack_conversion._magnetic_fieldmap_available(t) is True

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
        # the third is the aperture radius: 0 loses every particle
        assert obj.args == (0.2, 0.5, 1.0)


class TestRealRFTrackFieldMap:
    @staticmethod
    def _track_one(rft, element):
        lattice = rft.Lattice()
        lattice.append(element)
        B0 = rft.Bunch6d(rft.electronmass, 0.0, -1, np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 5.0]]))
        return lattice.track(B0)

    def test_rf_fieldmap_1d_tracks(self, rft):
        z = np.linspace(0, 0.2, 41)
        ez_norm = np.sin(np.pi * z / 0.2)
        field_obj = _fake_field("1DElectroDynamic", cavity_type="StandingWave", z=z, Ez=ez_norm)
        args = fields_rftrack.rf_fieldmap_1d_args(field_obj, amplitude=1e6, frequency=3e9)
        B1 = self._track_one(rft, rft.RF_FieldMap_1d(*args))
        assert B1.get_info().transmission >= 0.0

    def test_static_magnetic_fieldmap_1d_tracks(self, rft):
        z = np.linspace(-0.1, 0.1, 41)
        bz_norm = np.exp(-(z / 0.03) ** 2)
        field_obj = _fake_field("1DMagnetoStatic", z=z, Bz=bz_norm)
        args = fields_rftrack.static_magnetic_fieldmap_1d_args(field_obj, amplitude=0.5)
        B1 = self._track_one(rft, rft.Static_Magnetic_FieldMap_1d(*args))
        assert B1.get_info().transmission >= 0.0

    @staticmethod
    def _tws_field_realistic(frequency=2998.5e6, mode_numerator=1, mode_denominator=3):
        """S-band-like TWS block. ``z2 - z1 = mode_numerator * c / frequency`` is the
        v_phase = c synchronism condition; otherwise gain drops ~40x.
        """
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
        return field_obj

    N_CELLS = 21  # whole multiple of mode_denominator=3
    AMPLITUDE = 20e6  # V/m, realistic S-band gradient
    FREQUENCY = 2998.5e6
    START_PZ = 5.0  # MeV/c

    def _track_lattice(self, rft, elements):
        lattice = rft.Lattice()
        for element in elements:
            lattice.append(element)
        B0 = rft.Bunch6d(
            rft.electronmass, 1e9, -1, np.array([[0.0, 0.0, 0.0, 0.0, 0.0, self.START_PZ]])
        )
        return lattice.track(B0).get_info()

    def test_tw_fieldmap_1d_tracks_and_accelerates(self, rft):
        t = _fake_translator(
            simulation=SimpleNamespace(
                field_definition=self._tws_field_realistic(), field_amplitude=self.AMPLITUDE
            ),
            cavity=SimpleNamespace(frequency=self.FREQUENCY, phase=0.0),
        )
        t.get_cells = lambda: self.N_CELLS
        info = self._track_lattice(rft, [rftrack_conversion.build_tw_fieldmap(t)])
        assert info.transmission == pytest.approx(1e9)
        assert info.mean_P - self.START_PZ > 1.0

    def test_tw_core_accelerates_only_forwards(self, rft):
        """Unlike SW, ``direction`` matters for a TW map."""

        def gain(direction):
            (args,) = fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
                self._tws_field_realistic(), amplitude=self.AMPLITUDE,
                frequency=self.FREQUENCY, n_cells=self.N_CELLS, direction=direction,
            )
            info = self._track_lattice(rft, [rft.RF_FieldMap_1d(*args)])
            assert info.transmission == pytest.approx(1e9)
            return info.mean_P - self.START_PZ

        assert gain(1) > 1.0
        assert gain(1) > 5 * gain(-1)
