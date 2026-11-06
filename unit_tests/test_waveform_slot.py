"""Kicker pulse shapes: ``waveform`` holds sparse ``(time, factor)`` knots and an
interpolation rule. Firing time and absolute strength are study settings, not here.
"""

import pytest
from pydantic import ValidationError

from laura.models._generated import WaveformInterpolationEnum
from laura.models.element import HorizontalACDipole
from laura.models.simulation import SampledWaveform
from unit_tests.helpers import quiet

PULSE = {"time": [0.0, 1.0e-6, 1.2e-6], "factor": [0.0, 1.0, 0.0]}


def kicker(**waveform):
    return HorizontalACDipole(
        name="KICK1",
        machine_area="INJ",
        simulation={"field_amplitude": 1e6, "waveform": {**PULSE, **waveform}},
    )


def test_an_ac_dipole_carries_no_waveform_unless_one_is_authored():
    plain = HorizontalACDipole(
        name="HAC1", machine_area="S", simulation={"frequency": 1e5},
    )
    assert plain.simulation.waveform is None


def test_an_authored_waveform_keeps_its_knots():
    """``baseElement`` is ``extra="ignore"``: only parsed values prove it landed."""
    waveform = kicker().simulation.waveform
    assert waveform.time == pytest.approx(PULSE["time"])
    assert waveform.factor == pytest.approx(PULSE["factor"])


def test_an_authored_waveform_validates_into_the_handwritten_model():
    """Not the generated ``_SampledWaveformBase``, which has no validator."""
    assert type(kicker().simulation.waveform) is SampledWaveform


def test_interpolation_defaults_to_linear():
    """Every tracking code interpolates linearly by default. Compared by value because
    the config is ``use_enum_values``.
    """
    assert kicker().simulation.waveform.interpolation == (
        WaveformInterpolationEnum.linear
    )


@pytest.mark.parametrize("rule", ["linear", "hold", "spline"])
def test_each_interpolation_rule_is_accepted(rule):
    assert kicker(interpolation=rule).simulation.waveform.interpolation == rule


def test_an_unknown_interpolation_rule_is_refused():
    """``step`` and ``constant`` are both plausible spellings of ``hold``."""
    with pytest.raises(ValidationError):
        kicker(interpolation="step")


def test_the_two_columns_must_be_the_same_length():
    with pytest.raises(ValidationError, match="same length"):
        kicker(factor=[0.0, 1.0])


def test_time_must_not_run_backwards():
    """Every code's reader assumes ordered knots rather than checking."""
    with pytest.raises(ValidationError, match="non-decreasing"):
        kicker(time=[0.0, 1.2e-6, 1.0e-6])


def test_a_flat_top_may_repeat_a_time():
    """A repeated time is how a ``hold`` waveform expresses an instantaneous step."""
    stepped = kicker(
        time=[0.0, 1.0e-6, 1.0e-6, 2.0e-6],
        factor=[0.0, 0.0, 1.0, 1.0],
        interpolation="hold",
    )
    assert len(stepped.simulation.waveform.time) == 4


class TestBmadImport:
    """``_build_ac_kicker`` never touches ``self``: no importer or Tao needed."""

    @staticmethod
    def build(amp_vs_time, frequencies=(), **parameters):
        from laura.translator.converters.codes.bmad import (
            BmadLatticeImporter,
            _NativeElement,
        )

        element = _NativeElement(
            universe=1, branch="0", name="KICK1", etype="AC_Kicker",
            hardware_type="Horizontal_AC_Dipole", length=0.3,
            parameters={
                "BL_HKICK": 1.0,
                "_AC_KICKER": {"frequencies": list(frequencies), "amp_vs_time": amp_vs_time},
                **parameters,
            },
            physical={},
        )
        return BmadLatticeImporter._build_ac_kicker(None, element)

    # Tao writes `index;amp;time`, amplitude first, unlike the lattice file's
    # `{(time, amp), ...}`.
    PULSE = [(0.0, 0.0), (1.0, 1.0e-6), (0.0, 1.2e-6)]

    def test_amp_vs_time_is_imported(self):
        waveform = self.build(self.PULSE)["simulation"]["waveform"]
        assert waveform["time"] == pytest.approx([0.0, 1.0e-6, 1.2e-6])
        assert waveform["factor"] == pytest.approx([0.0, 1.0, 0.0])

    def test_the_columns_are_not_transposed(self):
        """Times and amplitudes are both small floats, so a swap still validates."""
        waveform = self.build(self.PULSE)["simulation"]["waveform"]
        assert max(waveform["time"]) < 1e-3
        assert max(waveform["factor"]) == pytest.approx(1.0)

    def test_an_unstated_interpolation_is_recorded_as_spline(self):
        """Bmad's default is cubic where every other code's is linear."""
        assert self.build(self.PULSE)["simulation"]["waveform"][
            "interpolation"
        ] == "spline"

    def test_an_explicit_linear_interpolation_is_kept(self):
        waveform = self.build(self.PULSE, INTERPOLATION="Linear")["simulation"][
            "waveform"
        ]
        assert waveform["interpolation"] == "linear"

    def test_a_t_offset_is_reported_rather_than_imported(self):
        """Firing time is a study setting, so it is dropped, with a warning."""
        with pytest.warns(UserWarning, match="t_offset"):
            self.build(self.PULSE, T_OFFSET=3.6e-8)

    def test_the_imported_waveform_validates(self):
        built = self.build(self.PULSE)
        element = HorizontalACDipole(
            name="KICK1", machine_area="INJ", simulation=built["simulation"],
        )
        assert type(element.simulation.waveform) is SampledWaveform

    def test_a_frequency_driven_kicker_carries_no_waveform(self):
        """Tao reports one or the other, never both."""
        built = self.build([], frequencies=[(1e5, 0.5, 0.25)])
        assert "waveform" not in built["simulation"]
        assert built["simulation"]["frequency"] == pytest.approx(1e5)


class TestExportSaysWhatItCannotWrite:
    """MAD-X's HACDIPOLE has only a four-point ramp and xtrack's ACDipole only a
    frequency, so the waveform is dropped, with a warning.
    """

    @staticmethod
    def translated():
        from laura.translator.converters.converter import translate_elements

        return translate_elements([kicker()])["KICK1"]

    def test_madx_export_warns(self):
        with pytest.warns(UserWarning, match="HACDIPOLE"):
            self.translated().to_madx()

    def test_xsuite_export_warns(self):
        pytest.importorskip("xtrack")
        with pytest.warns(UserWarning, match="FunctionPieceWiseLinear"):
            self.translated().to_xsuite(1)

    def test_a_plain_exciter_exports_without_a_warning(self):
        import warnings

        from laura.translator.converters.converter import translate_elements

        exciter = HorizontalACDipole(
            name="HAC1", machine_area="S",
            simulation={"field_amplitude": 1e6, "frequency": 1e5},
        )
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            assert "hacdipole" in translate_elements([exciter])["HAC1"].to_madx()


def test_a_waveform_round_trips_through_yaml(tmp_path):
    import yaml

    from laura import LAURA
    from laura.exporters.yaml_exporter import export_as_yaml

    element = kicker(interpolation="hold")
    (tmp_path / "elements.yaml").write_text(
        yaml.dump({element.name: export_as_yaml(None, element, "global")})
    )
    (tmp_path / "sections.yaml").write_text(
        yaml.dump({"sections": {"INJ": [element.name]}})
    )
    (tmp_path / "layouts.yaml").write_text(
        yaml.dump({"default_layout": "beam", "layouts": {"beam": ["INJ"]}})
    )
    with quiet():
        machine = LAURA(
            element_list=str(tmp_path / "elements.yaml"),
            section=str(tmp_path / "sections.yaml"),
            layout=str(tmp_path / "layouts.yaml"),
            master_lattice=str(tmp_path),
        )

    waveform = machine[element.name].simulation.waveform
    assert waveform.time == pytest.approx(PULSE["time"])
    assert waveform.factor == pytest.approx(PULSE["factor"])
    assert waveform.interpolation == "hold"
