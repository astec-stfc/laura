import unittest
from dataclasses import dataclass

import pytest

from laura.models.control import ControlVariable, ControlsInformation
from laura.utils.dynamics import (
    DelayedResponse,
    FirstOrderResponse,
    ImmediateResponse,
)
from laura.utils.signals import call_signal, RandomWalk, Sinusoid

SINUSOID_PATH = "laura.utils.signals.Sinusoid"
FIRST_ORDER_PATH = "laura.utils.dynamics.FirstOrderResponse"


@dataclass
class ExternalSignal:
    gain: float

    def __call__(self, value: float = 0.0):
        return value * self.gain


@dataclass
class NotCallableSignal:
    gain: float


EXTERNAL_PATH = f"{__name__}.ExternalSignal"


class TestControlVariable(unittest.TestCase):
    def test_control_variable_creation(self):
        cv = ControlVariable(
            identifier="var1",
            dtype="float",
            protocol="CA",
            units="V",
            description="A float variable for voltage",
        )
        self.assertEqual(cv.identifier, "var1")
        self.assertEqual(cv.dtype, float)
        self.assertEqual(cv.protocol, "CA")
        self.assertEqual(cv.units, "V")
        self.assertEqual(cv.description, "A float variable for voltage")

    def test_dtype_as_type(self):
        cv = ControlVariable(
            identifier="var1",
            dtype=float,
            protocol="CA",
        )
        self.assertEqual(cv.dtype, float)

    def test_validation_for_missing_identifier(self):
        with self.assertRaises(ValueError):
            ControlVariable(
                dtype="float",
                protocol="CA",
            )

    def test_validation_for_missing_protocol(self):
        with self.assertRaises(ValueError):
            ControlVariable(
                identifier="var1",
                dtype="float",
            )

    def test_invalid_dtype(self):
        with self.assertRaises(ValueError):
            ControlVariable(
                identifier="var2",
                dtype="unknown_type",
                protocol="PVA",
            )


def _update_cv(**kwargs):
    return ControlVariable(identifier="var1", protocol="CA", **kwargs)


def _dynamics_cv(**kwargs):
    return ControlVariable(
        identifier="LINAC:QUAD01:K1:MEAS",
        protocol="CA",
        setpoint="LINAC:QUAD01:K1:CMD",
        **kwargs,
    )


@pytest.mark.parametrize(
    "update, match",
    [
        # RandomWalk requires `noise`, so the bare class is not enough.
        (RandomWalk, None),
        ({"function": EXTERNAL_PATH}, None),
        ({"function": "NotASignal"}, None),
        ({"function": "no.such.module.Signal"}, None),
        ({"function": "laura.utils.signals.NotASignal"}, None),
        # `np` is importable from laura.utils.signals but is not a signal.
        ({"function": "laura.utils.signals.np"}, None),
        ({"function": f"{__name__}.NotCallableSignal", "gain": 1.0}, "__call__"),
        ({"period": 1.0}, None),
        ({"function": SINUSOID_PATH, "period": 1.0}, None),
        ({"function": SINUSOID_PATH, "period": 1.0, "amplitude": 2.0, "amplitud": 3.0}, "amplitud"),
        ({"function": SINUSOID_PATH, "period": "slow", "amplitude": 2.0}, "period"),
        (5, None),
    ],
    ids=[
        "class_without_required_fields",
        "external_signal_attributes_validated",
        "unknown_signal",
        "unimportable_module",
        "missing_module_attribute",
        "non_dataclass_target",
        "non_callable_signal",
        "no_function_key",
        "missing_required_attribute",
        "unknown_attribute",
        "wrong_attribute_type",
        "invalid_type",
    ],
)
def test_invalid_update_warns_and_is_dropped(update, match):
    with pytest.warns(UserWarning, match=match):
        cv = _update_cv(update=update)
    assert cv.update is None


@pytest.mark.parametrize(
    "dynamics, match",
    [
        (FirstOrderResponse, None),
        ({"tau": 0.5}, "'model'"),
        ({"model": "second_order", "tau": 0.5}, None),
        ({"model": "first_order"}, None),
        # `value` holds runtime state (init=False), so it is not accepted as config.
        ({"model": "first_order", "tau": 0.5, "value": 2.0}, "value"),
        ({"model": "first_order", "tau": "slow"}, "tau"),
        # tau <= 0 fails in __post_init__, caught like any construction failure.
        ({"model": "first_order", "tau": -1.0}, None),
    ],
    ids=[
        "class_without_required_fields",
        "no_model_key",
        "unknown_model",
        "missing_required_attribute",
        "runtime_state_not_configurable",
        "wrong_attribute_type",
        "invalid_domain",
    ],
)
def test_invalid_dynamics_warns_and_is_dropped(dynamics, match):
    with pytest.warns(UserWarning, match=match):
        cv = _dynamics_cv(dynamics=dynamics)
    assert cv.dynamics is None


class TestControlVariableUpdate(unittest.TestCase):
    make = staticmethod(_update_cv)

    def test_update_defaults_to_none(self):
        self.assertIsNone(self.make().update)

    def test_update_from_dict(self):
        cv = self.make(
            update={"function": SINUSOID_PATH, "period": 1.0, "amplitude": 2.0}
        )
        self.assertEqual(
            cv.update, {"function": SINUSOID_PATH, "period": 1.0, "amplitude": 2.0}
        )

    def test_update_from_instance_flattens_fields(self):
        cv = self.make(update=Sinusoid(period=1.0, amplitude=2.0))
        self.assertEqual(
            cv.update,
            {
                "function": SINUSOID_PATH,
                "period": 1.0,
                "amplitude": 2.0,
                "noise": 0.0,
                "phase": 0.0,
            },
        )

    def test_bare_name_is_upgraded_to_full_path(self):
        cv = self.make(
            update={"function": "Sinusoid", "period": 1.0, "amplitude": 2.0}
        )
        self.assertEqual(cv.update["function"], SINUSOID_PATH)

    def test_update_from_external_signal_by_path(self):
        cv = self.make(update={"function": EXTERNAL_PATH, "gain": 3.0})
        self.assertEqual(cv.update, {"function": EXTERNAL_PATH, "gain": 3.0})
        self.assertAlmostEqual(cv.build_update()(2.0), 6.0)

    def test_update_from_external_signal_instance(self):
        cv = self.make(update=ExternalSignal(gain=3.0))
        self.assertEqual(cv.update["function"], EXTERNAL_PATH)

    def test_update_accepts_int_where_float_expected(self):
        cv = self.make(update={"function": SINUSOID_PATH, "period": 1, "amplitude": 2})
        self.assertEqual(cv.build_update()(0.25), 2.0)

    def test_warning_names_the_variable(self):
        with self.assertWarns(UserWarning) as ctx:
            ControlVariable(
                identifier="k1l_control",
                protocol="CA",
                update={"function": "NotASignal"},
            )
        self.assertIn("k1l_control", str(ctx.warning))

    def test_build_update_returns_none_when_unset(self):
        self.assertIsNone(self.make().build_update())

    def test_build_update_instantiates_signal(self):
        cv = self.make(
            update={"function": SINUSOID_PATH, "period": 4.0, "amplitude": 2.0}
        )
        signal = cv.build_update()
        self.assertIsInstance(signal, Sinusoid)
        self.assertAlmostEqual(signal(1.0), 2.0)  # quarter period -> peak

    def test_build_update_from_instance(self):
        cv = self.make(update=RandomWalk(noise=0.0))
        signal = cv.build_update()
        self.assertIsInstance(signal, RandomWalk)
        self.assertAlmostEqual(signal(3.0), 3.0)  # no noise -> value unchanged

    def test_update_survives_round_trip(self):
        cv = self.make(
            update={"function": SINUSOID_PATH, "period": 1.0, "amplitude": 2.0}
        )
        restored = ControlVariable(**cv.model_dump())
        self.assertEqual(restored.update, cv.update)


class TestControlVariableDynamics(unittest.TestCase):
    make = staticmethod(_dynamics_cv)

    def test_dynamics_defaults_to_none(self):
        self.assertIsNone(self.make().dynamics)
        self.assertIsNone(self.make().build_dynamics())

    def test_short_name_is_upgraded_to_full_path(self):
        cv = self.make(dynamics={"model": "first_order", "tau": 0.5})
        self.assertEqual(cv.dynamics, {"model": FIRST_ORDER_PATH, "tau": 0.5})

    def test_dynamics_from_instance(self):
        cv = self.make(dynamics=FirstOrderResponse(tau=0.5))
        self.assertEqual(
            cv.dynamics, {"model": FIRST_ORDER_PATH, "tau": 0.5, "initial": 0.0}
        )

    def test_dynamics_survives_round_trip(self):
        cv = self.make(dynamics={"model": "first_order", "tau": 0.5})
        restored = ControlVariable(**cv.model_dump())
        self.assertEqual(restored.dynamics, cv.dynamics)

    def test_build_dynamics_instantiates_response(self):
        cv = self.make(dynamics={"model": "first_order", "tau": 0.5})
        response = cv.build_dynamics()
        self.assertIsInstance(response, FirstOrderResponse)
        self.assertAlmostEqual(response(1.0, 0.5), 1.0)  # dt == tau -> settled

    def test_build_dynamics_returns_independent_instances(self):
        cv = self.make(dynamics={"model": "first_order", "tau": 1.0})
        first, second = cv.build_dynamics(), cv.build_dynamics()
        first(1.0, 0.5)
        self.assertAlmostEqual(second.value, 0.0)


class TestCallSignal(unittest.TestCase):
    """Signals take only the inputs they need; `call_signal` passes each its subset."""

    def test_passes_only_declared_arguments(self):
        signal = Sinusoid(period=4.0, amplitude=2.0)  # takes t
        value = call_signal(signal, t=1.0, value=99.0, dt=0.1)
        self.assertAlmostEqual(value, 2.0)

    def test_passes_value_to_signals_that_take_it(self):
        signal = RandomWalk(noise=0.0)  # takes value
        self.assertAlmostEqual(call_signal(signal, t=1.0, value=3.0, dt=0.1), 3.0)

    def test_signal_taking_no_arguments(self):
        self.assertEqual(call_signal(lambda: 7.0, t=1.0, value=2.0), 7.0)

    def test_signal_taking_kwargs_receives_everything(self):
        captured = {}

        def signal(**kwargs):
            captured.update(kwargs)
            return 0.0

        call_signal(signal, t=1.0, value=2.0, dt=0.1)
        self.assertEqual(captured, {"t": 1.0, "value": 2.0, "dt": 0.1})

    def test_missing_required_argument_still_raises(self):
        with self.assertRaises(TypeError):
            call_signal(Sinusoid(period=1.0, amplitude=1.0), value=3.0)


class TestTypeChecked(unittest.TestCase):
    """`type_checked` validates argument types on construction."""

    def test_wrong_type_raises_type_error(self):
        with self.assertRaises(TypeError) as ctx:
            Sinusoid(period="slow", amplitude=1.0)
        self.assertIn("period", str(ctx.exception))

    def test_int_accepted_where_float_expected(self):
        signal = Sinusoid(period=2, amplitude=1)
        self.assertAlmostEqual(signal(0.5), 1.0)  # quarter period -> peak

    def test_bool_rejected_where_float_expected(self):
        with self.assertRaises(TypeError):
            FirstOrderResponse(tau=True)

    def test_own_post_init_still_runs(self):
        # type_checked must not displace FirstOrderResponse's own __post_init__ check.
        with self.assertRaises(ValueError):
            FirstOrderResponse(tau=-1.0)

    def test_type_check_precedes_own_post_init(self):
        # A non-numeric tau fails the type check before the `tau <= 0` comparison.
        with self.assertRaises(TypeError):
            FirstOrderResponse(tau="oops")


class TestResponseModels(unittest.TestCase):
    def test_first_order_approaches_target(self):
        response = FirstOrderResponse(tau=1.0)
        values = [response(1.0, 0.1) for _ in range(5)]
        self.assertTrue(all(b > a for a, b in zip(values, values[1:])))
        self.assertLess(values[-1], 1.0)

    def test_first_order_respects_initial_value(self):
        response = FirstOrderResponse(tau=1.0, initial=5.0)
        self.assertAlmostEqual(response.value, 5.0)
        self.assertLess(response(0.0, 0.1), 5.0)

    def test_first_order_does_not_overshoot_for_large_timestep(self):
        response = FirstOrderResponse(tau=0.1)
        self.assertAlmostEqual(response(1.0, 10.0), 1.0)

    def test_first_order_rejects_non_positive_tau(self):
        with self.assertRaises(ValueError):
            FirstOrderResponse(tau=0.0)

    def test_immediate_response_tracks_setpoint(self):
        response = ImmediateResponse()
        self.assertAlmostEqual(response(2.5, 0.1), 2.5)

    def test_delayed_response_waits_for_dead_time(self):
        response = DelayedResponse(delay=0.3)
        self.assertAlmostEqual(response(1.0, 0.1), 0.0)
        self.assertAlmostEqual(response(1.0, 0.1), 0.0)
        self.assertAlmostEqual(response(1.0, 0.1), 1.0)

    def test_delayed_response_rejects_negative_delay(self):
        with self.assertRaises(ValueError):
            DelayedResponse(delay=-1.0)


_VAR1 = {
    "identifier": "var1",
    "dtype": "float",
    "protocol": "CA",
    "units": "V",
    "description": "A float variable for voltage",
}
_VAR2 = {"identifier": "var2", "dtype": "int", "protocol": "PVA"}


@pytest.mark.parametrize(
    "variables",
    [
        {"var1": ControlVariable(**_VAR1), "var2": ControlVariable(**_VAR2)},
        {"var1": _VAR1, "var2": _VAR2},
        {"var1": ControlVariable(**_VAR1), "var2": _VAR2},
    ],
    ids=["instances", "dicts", "mixed"],
)
def test_controls_information_creation(variables):
    controls_info = ControlsInformation(variables=variables)
    assert "var1" in controls_info.variables
    assert "var2" in controls_info.variables
    assert controls_info.variables["var1"].dtype is float
    assert controls_info.variables["var2"].dtype is int


class TestControlsInformation(unittest.TestCase):
    def test_controls_information_without_variables(self):
        # The exporter prunes an empty variables map.
        controls_info = ControlsInformation(identifier_pattern="QUAD:LI21:201")
        self.assertEqual(controls_info.variables, {})

    def test_controls_information_with_invalid_dict(self):
        with self.assertRaises(ValueError):
            ControlsInformation(
                variables={
                    "var1": {
                        "identifier": "var1",
                        "dtype": "float",
                        # Missing protocol
                    },
                }
            )

    def test_controls_information_with_invalid_type(self):
        with self.assertRaises(TypeError):
            ControlsInformation(variables=["not", "a", "dict"])

    def test_controls_information_model_dump_serialises_dtypes(self):
        controls_info = ControlsInformation(
            variables={
                "var1": ControlVariable(
                    identifier="var1",
                    dtype=float,
                    protocol="CA",
                    units="V",
                    description="A float variable for voltage",
                ),
                "var2": ControlVariable(
                    identifier="var2",
                    dtype=int,
                    protocol="PVA",
                ),
            }
        )
        dumped = controls_info.model_dump()
        self.assertEqual(dumped["variables"]["var1"]["dtype"], "float")
        self.assertEqual(dumped["variables"]["var2"]["dtype"], "int")


class TestControlVariableSerializeDefaults(unittest.TestCase):
    """`_SERIALIZE_DEFAULTS` keys are field names (``control_type``), not aliases."""

    def test_default_control_type_is_omitted(self):
        cv = ControlVariable(identifier="var1", protocol="CA")
        self.assertNotIn("control_type", cv.model_dump())

    def test_non_default_control_type_is_kept(self):
        cv = ControlVariable(identifier="var1", protocol="CA", type="waveform")
        self.assertEqual(cv.model_dump()["type"], "waveform")

    def test_default_control_type_omitted_via_alias(self):
        cv = ControlVariable(identifier="var1", protocol="CA", type="statistical")
        self.assertNotIn("control_type", cv.model_dump())
