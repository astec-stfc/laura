from pydantic import Field, field_validator, create_model
from typing import List, Type, Union

from .baseModels import IgnoreExtra, T, ModelBase, FunctionalMixin
from ._generated import (
    _RFCavityElementBase,
    _WakefieldElementBase,
    _RFDeflectingCavityElementBase,
    _PIDElementBase,
    _PIDPhaseRangeBase,
    _TraceBase,
    _ChannelNamesBase,
    _LLRFTimingBase,
    _LLRFTimingsBase,
    _LowLevelRFElementBase,
    _RFModulatorElementBase,
    _RFProtectionElementBase,
    _RFHeartbeatElementBase,
)


def _coerce_pid_range(v: Union[str, List, None], range_type):
    if v is None:
        return None
    if isinstance(v, str):
        splitlist = list(map(str.strip, v.split(",")))
        assert len(splitlist) == 2
        min_value, max_value = splitlist
        return range_type(min=min_value, max=max_value)
    if isinstance(v, (list, tuple)):
        assert len(v) == 2
        return range_type(min=v[0], max=v[1])
    if isinstance(v, range_type):
        return v
    raise ValueError("range should be a string or a list of numbers")


class RFCavityElement(_RFCavityElementBase, FunctionalMixin):
    """
    RF Cavity model.
    """

    def model_post_init(self, __context):
        if self.structure_type.lower() == "travellingwave" and any(
            [self.mode_numerator is None and self.mode_denominator is None]
        ):
            raise ValueError(
                "mode_numerator and mode_denominator must be defined for TravellingWave structure type"
            )


class WakefieldElement(_WakefieldElementBase):
    """
    Wakefield element model.
    """

    pass


class RFDeflectingCavityElement(_RFDeflectingCavityElementBase, FunctionalMixin):
    """
    RF deflecting cavity model.
    """


class PIDPhaseRange(_PIDPhaseRangeBase):

    def __str__(self) -> str:
        return str([self.min, self.max])

    def __repr__(self) -> repr:
        return self.__str__()

    def __iter__(self) -> iter:
        cls = self.__class__
        return iter([getattr(self, k) for k in cls.model_fields.keys()])


class PIDWeightRange(PIDPhaseRange):
    pass


class PIDElement(_PIDElementBase):
    """LLRF info model."""

    @field_validator("phase_range", mode="before")
    @classmethod
    def validate_phase_range(cls, v: Union[str, List, None]) -> PIDPhaseRange | None:
        return _coerce_pid_range(v, PIDPhaseRange)

    @field_validator("phase_weight_range", mode="before")
    @classmethod
    def validate_phase_weight_range(cls, v: Union[str, List, None]) -> PIDWeightRange | None:
        return _coerce_pid_range(v, PIDWeightRange)


class Trace(_TraceBase):
    pass


class ChannelNames(_ChannelNamesBase):
    pass


llrffieldnames = [
    "klystron_forward",
    "klystron_reverse",
    "cavity_forward",
    "cavity_reverse",
    "cavity_probe",
]
llrftimingsCATAPnames = ["kf", "kr", "cf", "cr", "cp"]
cavitynames = ["LRRG", "HRRG", "L01", "CALIBRATION"]


class LLRFChannelIndex(ModelBase):
    power: int
    phase: int


class LLRFChannelsBase(ModelBase):
    labels: List[str] = []


class LLRFTiming(_LLRFTimingBase):
    pass


class LLRFTimings(_LLRFTimingsBase):
    pass


class Low_Level_RF_Element(_LowLevelRFElementBase, IgnoreExtra):
    # one_record remains dynamic because CATAP payload keys depend on
    # available cavity/channel combinations at runtime.
    one_record: LLRFChannelsBase

    def _create_LLRFChannels_Model(self, fields: dict):
        inputs = {}
        for name in llrffieldnames:
            if "ONE_RECORD_" + str.upper(name) + "_POWER" in fields:
                substr = "ONE_RECORD_" + str.upper(name)
                inputs[str.upper(name)] = LLRFChannelIndex(
                    power=fields[substr + "_POWER"], phase=fields[substr + "_PHASE"]
                )
            for cav in cavitynames:
                if (
                    "ONE_RECORD_" + str.upper(cav) + "_" + str.upper(name) + "_POWER"
                    in fields
                ):
                    subname = str.upper(cav) + "_" + str.upper(name)
                    substr = "ONE_RECORD_" + subname
                    inputs[subname] = LLRFChannelIndex(
                        power=fields[substr + "_POWER"], phase=fields[substr + "_PHASE"]
                    )
        model_fields = {i: (LLRFChannelIndex, Field()) for i in inputs.keys()}
        LLRFChannels = create_model(
            "LLRFChannels", **model_fields, __base__=LLRFChannelsBase
        )
        fields["labels"] = list(model_fields.keys())
        return LLRFChannels


class RFModulatorElement(_RFModulatorElementBase):
    pass


class RFProtectionElement(_RFProtectionElementBase):
    pass


class RFHeartbeatElement(_RFHeartbeatElementBase):
    pass
