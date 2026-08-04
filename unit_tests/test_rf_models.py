"""Tests for laura.models.RF: PID range coercion, RFCavityElement validation,
PIDPhaseRange dunder methods, and Low_Level_RF_Element channel-model builder."""

import pytest
from pydantic import ValidationError

from laura.models.RF import (
    RFCavityElement,
    PIDPhaseRange,
    PIDElement,
    Low_Level_RF_Element,
    LLRFChannelsBase,
)


class TestRFCavityElementValidation:
    def test_standing_wave_default_ok(self):
        cav = RFCavityElement()
        assert cav.structure_type == "StandingWave"

    def test_travelling_wave_requires_mode_numbers(self):
        with pytest.raises(ValueError, match="mode_numerator"):
            RFCavityElement(structure_type="TravellingWave")

    def test_travelling_wave_with_modes_ok(self):
        cav = RFCavityElement(
            structure_type="TravellingWave", mode_numerator=2, mode_denominator=3
        )
        assert cav.mode_numerator == 2


class TestPIDPhaseRangeCoercion:
    def test_from_csv_string(self):
        pid = PIDElement(phase_range="1.0, 2.0")
        assert pid.phase_range.min == 1.0
        assert pid.phase_range.max == 2.0

    def test_from_list(self):
        pid = PIDElement(phase_range=[1.0, 2.0])
        assert pid.phase_range == PIDPhaseRange(min=1.0, max=2.0)

    def test_from_existing_instance(self):
        rng = PIDPhaseRange(min=1.0, max=2.0)
        pid = PIDElement(phase_range=rng)
        assert pid.phase_range is rng

    def test_none_stays_none(self):
        pid = PIDElement(phase_range=None)
        assert pid.phase_range is None

    def test_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            PIDElement(phase_range=5)


class TestPIDPhaseRangeDunders:
    def test_str(self):
        rng = PIDPhaseRange(min=1.0, max=2.0)
        assert str(rng) == str([1.0, 2.0])

    def test_repr(self):
        rng = PIDPhaseRange(min=1.0, max=2.0)
        assert repr(rng) == str(rng)

    def test_iter(self):
        rng = PIDPhaseRange(min=1.0, max=2.0)
        assert list(rng) == [1.0, 2.0]


class TestLowLevelRFChannelsModel:
    def test_create_llrf_channels_model_with_generic_fields(self):
        elem = Low_Level_RF_Element(one_record=LLRFChannelsBase())
        fields = {
            "ONE_RECORD_KLYSTRON_FORWARD_POWER": 1,
            "ONE_RECORD_KLYSTRON_FORWARD_PHASE": 2,
        }
        model_cls = elem._create_LLRFChannels_Model(fields)
        instance = model_cls(**{"KLYSTRON_FORWARD": {"power": 1, "phase": 2}})
        assert instance.KLYSTRON_FORWARD.power == 1
        assert fields["labels"] == ["KLYSTRON_FORWARD"]

    def test_create_llrf_channels_model_with_cavity_specific_fields(self):
        elem = Low_Level_RF_Element(one_record=LLRFChannelsBase())
        fields = {
            "ONE_RECORD_LRRG_CAVITY_PROBE_POWER": 3,
            "ONE_RECORD_LRRG_CAVITY_PROBE_PHASE": 4,
        }
        elem._create_LLRFChannels_Model(fields)
        assert "LRRG_CAVITY_PROBE" in fields["labels"]
