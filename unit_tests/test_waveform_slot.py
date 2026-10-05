"""A kicker's pulse shape is part of the machine description.

``ACDipoleSimulationElement`` could describe a sinusoidal exciter
(``frequency``, ``phase``) with a four-point ``ramp`` envelope, and nothing
else. That is MAD-X's ``HACDIPOLE`` and no more: an injection kicker or an
extraction septum, whose strength is a *sampled pulse* rather than a sinusoid,
had nowhere to live. Bmad's importer said so out loud -- it dropped
``amp_vs_time`` from every ``AC_Kicker`` it read, with a warning that LAURA had
no equivalent.

``waveform`` is that equivalent: sparse ``(time, factor)`` knots plus a rule
for what happens between them, which is the shape MAD-X ``ramp1``-``ramp4``,
Bmad ``x_knot``/``y_knot``, elegant's SDDS ``WAVEFORM`` file and Xsuite's
``FunctionPieceWiseLinear`` all agree on.

What it deliberately does *not* hold is when the device fires or how hard. The
waveform is the device's own shape, the same in every study; the firing turn
and the absolute strength are study settings and belong to the tracking code's
run configuration.

Two things here are asserted rather than assumed, both from
``patterns/add-schema-slot.md``: that the parsed *value* survives (``extra =
"ignore"`` means an unknown key is dropped in silence, so "it loaded" proves
nothing), and that an authored mapping lands in the handwritten
``SampledWaveform`` and not in the generated base, which is how the cavity
models went wrong.
"""

import pytest
from pydantic import ValidationError

from laura.models._generated import WaveformInterpolationEnum
from laura.models.element import HorizontalACDipole
from laura.models.simulation import SampledWaveform

PULSE = {"time": [0.0, 1.0e-6, 1.2e-6], "factor": [0.0, 1.0, 0.0]}


def kicker(**waveform):
    return HorizontalACDipole(
        name="KICK1",
        machine_area="INJ",
        simulation={"field_amplitude": 1e6, "waveform": {**PULSE, **waveform}},
    )


def test_an_ac_dipole_carries_no_waveform_unless_one_is_authored():
    """A tune exciter is still described by frequency and phase alone."""
    plain = HorizontalACDipole(
        name="HAC1", machine_area="S", simulation={"frequency": 1e5},
    )
    assert plain.simulation.waveform is None


def test_an_authored_waveform_keeps_its_knots():
    """``baseElement`` is ``extra="ignore"``, so a slot that never landed would
    be dropped without complaint and the model would construct just the same.
    Only the parsed values show the difference."""
    waveform = kicker().simulation.waveform
    assert waveform.time == pytest.approx(PULSE["time"])
    assert waveform.factor == pytest.approx(PULSE["factor"])


def test_an_authored_waveform_validates_into_the_handwritten_model():
    """Not the generated ``_SampledWaveformBase``, which carries no validator
    -- the same trap the cavity models fell into."""
    assert type(kicker().simulation.waveform) is SampledWaveform


def test_interpolation_defaults_to_linear():
    """Every tracking code interpolates its knots linearly unless told
    otherwise, so an unstated rule has to mean what the codes already do.

    Compared by value, not identity: the base model config is
    ``use_enum_values``, so what is stored is the string the enum stands for."""
    assert kicker().simulation.waveform.interpolation == (
        WaveformInterpolationEnum.linear
    )


@pytest.mark.parametrize("rule", ["linear", "hold", "spline"])
def test_each_interpolation_rule_is_accepted(rule):
    assert kicker(interpolation=rule).simulation.waveform.interpolation == rule


def test_an_unknown_interpolation_rule_is_refused():
    """The enum is the point: ``step`` and ``constant`` are both plausible
    spellings of ``hold``, and a free string would let all three coexist."""
    with pytest.raises(ValidationError):
        kicker(interpolation="step")


def test_the_two_columns_must_be_the_same_length():
    """``time`` and ``factor`` are one trace, not two independent lists. A
    trailing knot dropped from one of them is the easy way to author a pulse
    that silently ends early."""
    with pytest.raises(ValidationError, match="same length"):
        kicker(factor=[0.0, 1.0])


def test_time_must_not_run_backwards():
    """There is no interpolation through a trace that doubles back, and every
    code's reader assumes ordered knots rather than checking."""
    with pytest.raises(ValidationError, match="non-decreasing"):
        kicker(time=[0.0, 1.2e-6, 1.0e-6])


def test_a_flat_top_may_repeat_a_time():
    """Non-decreasing, not strictly increasing: a repeated time is how a
    ``hold`` waveform expresses an instantaneous step."""
    stepped = kicker(
        time=[0.0, 1.0e-6, 1.0e-6, 2.0e-6],
        factor=[0.0, 0.0, 1.0, 1.0],
        interpolation="hold",
    )
    assert len(stepped.simulation.waveform.time) == 4


class TestBmadImport:
    """The gap the slot was added to close.

    ``_build_ac_kicker`` is called without an importer instance: it never
    touches ``self``, and building a real one needs Tao, which this has no
    other use for.
    """

    @staticmethod
    def build(amp_vs_time, **parameters):
        from laura.translator.converters.codes.bmad import (
            BmadLatticeImporter,
            _NativeElement,
        )

        element = _NativeElement(
            universe=1, branch="0", name="KICK1", etype="AC_Kicker",
            hardware_type="Horizontal_AC_Dipole", length=0.3,
            parameters={
                "BL_HKICK": 1.0,
                "_AC_KICKER": {"frequencies": [], "amp_vs_time": amp_vs_time},
                **parameters,
            },
            physical={},
        )
        return BmadLatticeImporter._build_ac_kicker(None, element)

    # Tao writes `index;amp;time`, amplitude first -- the reverse of the
    # `{(time, amp), ...}` order the lattice file itself is written in.
    PULSE = [(0.0, 0.0), (1.0, 1.0e-6), (0.0, 1.2e-6)]

    def test_amp_vs_time_is_imported(self):
        """It used to be dropped with a warning saying LAURA had nowhere to
        put it."""
        waveform = self.build(self.PULSE)["simulation"]["waveform"]
        assert waveform["time"] == pytest.approx([0.0, 1.0e-6, 1.2e-6])
        assert waveform["factor"] == pytest.approx([0.0, 1.0, 0.0])

    def test_the_columns_are_not_transposed(self):
        """The one way this import can go wrong silently: times and amplitudes
        are both small floats, so a swap produces a valid waveform that is the
        pulse reflected about the diagonal."""
        waveform = self.build(self.PULSE)["simulation"]["waveform"]
        assert max(waveform["time"]) < 1e-3
        assert max(waveform["factor"]) == pytest.approx(1.0)

    def test_an_unstated_interpolation_is_recorded_as_spline(self):
        """Bmad's default is cubic where every other code's is linear, so
        importing the knots without the rule would quietly change the pulse."""
        assert self.build(self.PULSE)["simulation"]["waveform"][
            "interpolation"
        ] == "spline"

    def test_an_explicit_linear_interpolation_is_kept(self):
        waveform = self.build(self.PULSE, INTERPOLATION="Linear")["simulation"][
            "waveform"
        ]
        assert waveform["interpolation"] == "linear"

    def test_a_t_offset_is_reported_rather_than_imported(self):
        """When the kicker fires is a study setting under the agreed split, so
        LAURA drops it -- but says so, rather than losing it in silence."""
        with pytest.warns(UserWarning, match="t_offset"):
            self.build(self.PULSE, T_OFFSET=3.6e-8)

    def test_the_imported_waveform_validates(self):
        """What the importer builds has to satisfy the model it is built for,
        including the paired-column and ordering checks."""
        from laura.models.element import HorizontalACDipole

        built = self.build(self.PULSE)
        element = HorizontalACDipole(
            name="KICK1", machine_area="INJ", simulation=built["simulation"],
        )
        assert type(element.simulation.waveform) is SampledWaveform

    def test_a_frequency_driven_kicker_carries_no_waveform(self):
        """Tao reports one or the other, never both."""
        from laura.translator.converters.codes.bmad import (
            BmadLatticeImporter,
            _NativeElement,
        )

        element = _NativeElement(
            universe=1, branch="0", name="HAC1", etype="AC_Kicker",
            hardware_type="Horizontal_AC_Dipole", length=0.3,
            parameters={
                "BL_HKICK": 1.0,
                "_AC_KICKER": {
                    "frequencies": [(1e5, 0.5, 0.25)], "amp_vs_time": [],
                },
            },
            physical={},
        )
        built = BmadLatticeImporter._build_ac_kicker(None, element)
        assert "waveform" not in built["simulation"]
        assert built["simulation"]["frequency"] == pytest.approx(1e5)


class TestExportSaysWhatItCannotWrite:
    """MAD-X and Xsuite cannot carry a sampled waveform on the element.

    MAD-X's HACDIPOLE has only the four-point ramp, and xtrack's ACDipole only
    a frequency; Xsuite does sampled pulses, but as a line-level
    ``FunctionPieceWiseLinear`` rather than an element attribute. Dropping the
    waveform is therefore correct here -- doing it quietly is not, because the
    exported lattice tracks happily and kicks for the whole run.

    Bmad and ELEGANT *do* have element syntax for it, and write it out; see
    ``test_ac_dipole_export.py``.
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
        """The warning has to be about the waveform, not about AC dipoles."""
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
    """The slot has to survive export and re-import, which is where a field
    present on the model but missing from the schema comes apart."""
    import warnings

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
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
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
