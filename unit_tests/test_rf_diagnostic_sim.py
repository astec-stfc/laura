"""Tests for RF, diagnostic, simulation, and other specialised models."""

import pytest
import numpy as np

from laura.models.RF import (
    RFCavityElement,
    WakefieldElement,
    RFDeflectingCavityElement,
    PIDElement,
    Low_Level_RF_Element,
    RFModulatorElement,
    RFProtectionElement,
    RFHeartbeatElement,
)
from laura.models.diagnostic import (
    DiagnosticElement,
    Beam_Position_Monitor_Diagnostic,
    Beam_Arrival_Monitor_Diagnostic,
    Bunch_Length_Monitor_Diagnostic,
    Camera_Mask,
    Camera_Pixel_Results_Indices,
    Camera_Pixel_Results_Names,
    Charge_Diagnostic,
)
from laura.models.simulation import (
    SimulationElement,
    MagnetSimulationElement,
    DriftSimulationElement,
    DiagnosticSimulationElement,
    RFCavitySimulationElement,
    ApertureElement,
    TwissMatchSimulationElement,
)
from laura.models.electrical import ElectricalElement
from laura.models.laser import LaserElement
from laura.models.plasma import PlasmaElement
from laura.models.control import ControlVariable, ControlsInformation
from laura.models.baseModels import set_functional_definitions


# ---------------------------------------------------------------------------
# Functional parameters (RF / simulation)
# ---------------------------------------------------------------------------

class TestFunctionalParametersRF:
    @pytest.fixture(autouse=True)
    def _defs(self):
        set_functional_definitions(
            {"cav1_phase": 90.0, "famp": 5e6}, merge=False
        )
        yield
        set_functional_definitions({}, merge=False)

    def test_cavity_phase_string(self):
        cav = RFCavityElement(phase="cav1_phase")
        assert cav.phase == "cav1_phase"
        assert cav.resolved("phase") == pytest.approx(90.0)

    def test_cavity_phase_float_still_works(self):
        cav = RFCavityElement(phase=12.5)
        assert cav.resolved("phase") == pytest.approx(12.5)

    def test_deflecting_cavity_phase_string(self):
        cav = RFDeflectingCavityElement(phase="cav1_phase")
        assert cav.phase == "cav1_phase"
        assert cav.resolved("phase") == pytest.approx(90.0)

    def test_sim_field_amplitude_string(self):
        sim = RFCavitySimulationElement(field_amplitude="famp")
        assert sim.field_amplitude == "famp"
        assert sim.resolved("field_amplitude") == pytest.approx(5e6)

    def test_undefined_raises(self):
        cav = RFCavityElement(phase="missing")
        with pytest.raises(KeyError):
            cav.resolved("phase")


# ---------------------------------------------------------------------------
# RF Models
# ---------------------------------------------------------------------------

class TestRFCavityElement:
    def test_defaults(self):
        cav = RFCavityElement()
        assert cav.structure_type == "StandingWave"
        assert cav.frequency == pytest.approx(2998500000.0)
        assert cav.phase == pytest.approx(0.0)
        assert cav.n_cells == 1

    def test_custom_values(self):
        cav = RFCavityElement(
            frequency=1.3e9,
            phase=15.0,
            n_cells=9,
            cell_length=0.1,
        )
        assert cav.frequency == pytest.approx(1.3e9)
        assert cav.n_cells == 9

    def test_crest_default(self):
        cav = RFCavityElement()
        assert cav.crest == 0

    def test_design_power(self):
        cav = RFCavityElement(design_power=1e7)
        assert cav.design_power == pytest.approx(1e7)


class TestWakefieldElement:
    def test_defaults(self):
        wf = WakefieldElement()
        assert wf.n_cells == 1
        assert wf.coupling_cell_length == 0.0


class TestRFDeflectingCavityElement:
    def test_defaults(self):
        rfd = RFDeflectingCavityElement()
        assert rfd.coupling_cell_length == 0.0


# ---------------------------------------------------------------------------
# Diagnostic Models
# ---------------------------------------------------------------------------

class TestDiagnosticModels:
    def test_bpm_diagnostic(self):
        bpm = Beam_Position_Monitor_Diagnostic()
        assert bpm.type == "Stripline"

    def test_bpm_custom_type(self):
        bpm = Beam_Position_Monitor_Diagnostic(bpm_type="Cavity")
        assert bpm.type == "Cavity"

    def test_bam_diagnostic(self):
        bam = Beam_Arrival_Monitor_Diagnostic()
        assert bam.type == "DESY"

    def test_blm_diagnostic(self):
        blm = Bunch_Length_Monitor_Diagnostic()
        assert blm.type == "CDR"

    def test_camera_mask_defaults(self):
        mask = Camera_Mask()
        assert mask.middle == [1280, 1080]
        assert mask.radius == [1240, 1040]

    def test_camera_pixel_indices(self):
        cpi = Camera_Pixel_Results_Indices()
        assert cpi.x == 0
        assert cpi.y == 1

    def test_camera_pixel_names(self):
        cpn = Camera_Pixel_Results_Names()
        assert cpn.x == "X"
        assert cpn.y == "Y"


# ---------------------------------------------------------------------------
# Simulation Models
# ---------------------------------------------------------------------------

class TestSimulationModels:
    def test_simulation_element_defaults(self):
        se = SimulationElement()
        assert se.field_definition is None
        assert se.scale_field is False

    def test_magnet_simulation(self):
        ms = MagnetSimulationElement()
        assert ms.n_kicks == 4
        assert ms.csr_enable is True
        assert ms.sr_enable is True

    def test_drift_simulation(self):
        ds = DriftSimulationElement()
        assert ds is not None

    def test_aperture_element(self):
        ae = ApertureElement(horizontal_size=0.03, vertical_size=0.02, shape="elliptical")
        assert ae.horizontal_size == pytest.approx(0.03)
        assert ae.shape == "elliptical"


# ---------------------------------------------------------------------------
# Electrical
# ---------------------------------------------------------------------------

class TestElectricalElement:
    def test_defaults(self):
        ee = ElectricalElement()
        assert ee.minI is not None or ee.minI == 0
        assert ee.maxI is not None or ee.maxI == 0


# ---------------------------------------------------------------------------
# Laser
# ---------------------------------------------------------------------------

class TestLaserElement:
    def test_defaults(self):
        # LaserElement requires wavelength, pulse_energy, pulse_duration_fwhm (all gt=0)
        le = LaserElement(wavelength=800e-9, pulse_energy=1e-3, pulse_duration_fwhm=30e-15)
        assert le.wavelength == pytest.approx(800e-9)
        assert le.pulse_energy == pytest.approx(1e-3)
        assert le.pulse_duration_fwhm == pytest.approx(30e-15)


# ---------------------------------------------------------------------------
# Plasma
# ---------------------------------------------------------------------------

class TestPlasmaElement:
    def test_defaults(self):
        # PlasmaElement requires density (gt=0)
        pe = PlasmaElement(density=1e16)
        assert pe.density == pytest.approx(1e16)
        assert pe.species == "electron"


# ---------------------------------------------------------------------------
# Control Variables
# ---------------------------------------------------------------------------

class TestControlVariable:
    def test_basic_creation(self):
        cv = ControlVariable(
            identifier="CURRENT",
            dtype="float",
            protocol="EPICS",
            units="A",
            description="Magnet current",
        )
        assert cv.identifier == "CURRENT"
        assert cv.protocol == "EPICS"
        assert cv.units == "A"

    def test_control_variable_with_value(self):
        cv = ControlVariable(
            identifier="CURRENT",
            dtype="float",
            protocol="EPICS",
            value=10.0,
        )
        assert cv.value == 10.0

    def test_controls_information_creation(self):
        cv1 = ControlVariable(identifier="I", dtype="float", protocol="EPICS")
        ci = ControlsInformation(variables={"I": cv1})
        assert "I" in ci.variables
