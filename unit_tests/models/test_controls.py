import unittest
from dataclasses import dataclass
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
    """A signal defined outside `laura.utils.signals`."""

    gain: float

    def __call__(self, value: float = 0.0):
        return value * self.gain


@dataclass
class NotCallableSignal:
    """A dataclass that cannot be used as an update function."""

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


class TestControlVariableUpdate(unittest.TestCase):
    def make(self, **kwargs):
        return ControlVariable(identifier="var1", protocol="CA", **kwargs)

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

    def test_update_from_class_without_required_fields_warns(self):
        # RandomWalk requires `noise`, so the bare class is not enough.
        with self.assertWarns(UserWarning):
            cv = self.make(update=RandomWalk)
        self.assertIsNone(cv.update)

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

    def test_external_signal_attributes_are_validated(self):
        with self.assertWarns(UserWarning):
            cv = self.make(update={"function": EXTERNAL_PATH})
        self.assertIsNone(cv.update)

    def test_update_with_unknown_signal_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(update={"function": "NotASignal"})
        self.assertIsNone(cv.update)

    def test_update_with_unimportable_module_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(update={"function": "no.such.module.Signal"})
        self.assertIsNone(cv.update)

    def test_update_with_missing_module_attribute_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(update={"function": "laura.utils.signals.NotASignal"})
        self.assertIsNone(cv.update)

    def test_update_with_non_dataclass_target_warns(self):
        # `np` is importable from laura.utils.signals but is not a signal.
        with self.assertWarns(UserWarning):
            cv = self.make(update={"function": "laura.utils.signals.np"})
        self.assertIsNone(cv.update)

    def test_update_with_non_callable_signal_warns(self):
        with self.assertWarns(UserWarning) as ctx:
            cv = self.make(
                update={"function": f"{__name__}.NotCallableSignal", "gain": 1.0}
            )
        self.assertIsNone(cv.update)
        self.assertIn("__call__", str(ctx.warning))

    def test_update_without_function_key_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(update={"period": 1.0})
        self.assertIsNone(cv.update)

    def test_update_with_missing_required_attribute_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(update={"function": SINUSOID_PATH, "period": 1.0})
        self.assertIsNone(cv.update)

    def test_update_with_unknown_attribute_warns(self):
        with self.assertWarns(UserWarning) as ctx:
            cv = self.make(
                update={
                    "function": SINUSOID_PATH,
                    "period": 1.0,
                    "amplitude": 2.0,
                    "amplitud": 3.0,
                }
            )
        self.assertIsNone(cv.update)
        self.assertIn("amplitud", str(ctx.warning))

    def test_update_with_wrong_attribute_type_warns(self):
        with self.assertWarns(UserWarning) as ctx:
            cv = self.make(
                update={"function": SINUSOID_PATH, "period": "slow", "amplitude": 2.0}
            )
        self.assertIsNone(cv.update)
        self.assertIn("period", str(ctx.warning))

    def test_update_accepts_int_where_float_expected(self):
        cv = self.make(update={"function": SINUSOID_PATH, "period": 1, "amplitude": 2})
        self.assertEqual(cv.build_update()(0.25), 2.0)

    def test_update_with_invalid_type_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(update=5)
        self.assertIsNone(cv.update)

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
    def make(self, **kwargs):
        return ControlVariable(
            identifier="LINAC:QUAD01:K1:MEAS",
            protocol="CA",
            setpoint="LINAC:QUAD01:K1:CMD",
            **kwargs,
        )

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

    def test_dynamics_from_class_without_required_fields_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(dynamics=FirstOrderResponse)
        self.assertIsNone(cv.dynamics)

    def test_dynamics_without_model_key_warns(self):
        with self.assertWarns(UserWarning) as ctx:
            cv = self.make(dynamics={"tau": 0.5})
        self.assertIsNone(cv.dynamics)
        self.assertIn("'model'", str(ctx.warning))

    def test_dynamics_with_unknown_model_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(dynamics={"model": "second_order", "tau": 0.5})
        self.assertIsNone(cv.dynamics)

    def test_dynamics_with_missing_required_attribute_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(dynamics={"model": "first_order"})
        self.assertIsNone(cv.dynamics)

    def test_runtime_state_is_not_configurable(self):
        # `value` holds runtime state (init=False), so it is not accepted as config.
        with self.assertWarns(UserWarning) as ctx:
            cv = self.make(dynamics={"model": "first_order", "tau": 0.5, "value": 2.0})
        self.assertIsNone(cv.dynamics)
        self.assertIn("value", str(ctx.warning))

    def test_dynamics_with_wrong_attribute_type_warns(self):
        with self.assertWarns(UserWarning) as ctx:
            cv = self.make(dynamics={"model": "first_order", "tau": "slow"})
        self.assertIsNone(cv.dynamics)
        self.assertIn("tau", str(ctx.warning))

    def test_dynamics_with_invalid_domain_warns(self):
        # tau <= 0 raises ValueError from __post_init__, which the validator
        # catches like any other construction failure.
        with self.assertWarns(UserWarning):
            cv = self.make(dynamics={"model": "first_order", "tau": -1.0})
        self.assertIsNone(cv.dynamics)

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
    """Signals declare only the inputs they need; a generic driver supplies all of
    them and `call_signal` passes on the subset each one accepts."""

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
    """`type_checked` makes a dataclass validate its own argument types on
    construction, so the callable-spec validator can lean on the constructor."""

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
        # FirstOrderResponse validates tau > 0 in its own __post_init__, which
        # type_checked must not displace.
        with self.assertRaises(ValueError):
            FirstOrderResponse(tau=-1.0)

    def test_type_check_precedes_own_post_init(self):
        # A non-numeric tau is a TypeError (from the type check), not whatever
        # the `tau <= 0` comparison would raise.
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


class TestControlsInformation(unittest.TestCase):
    def test_controls_information_creation(self):
        controls_info = ControlsInformation(
            variables={
                "var1": ControlVariable(
                    identifier="var1",
                    dtype="float",
                    protocol="CA",
                    units="V",
                    description="A float variable for voltage",
                ),
                "var2": ControlVariable(
                    identifier="var2",
                    dtype="int",
                    protocol="PVA",
                ),
            }
        )
        self.assertIn("var1", controls_info.variables)
        self.assertIn("var2", controls_info.variables)
        self.assertEqual(controls_info.variables["var1"].dtype, float)
        self.assertEqual(controls_info.variables["var2"].dtype, int)

    def test_controls_information_with_dicts(self):
        controls_info = ControlsInformation(
            variables={
                "var1": {
                    "identifier": "var1",
                    "dtype": "float",
                    "protocol": "CA",
                    "units": "V",
                    "description": "A float variable for voltage",
                },
                "var2": {
                    "identifier": "var2",
                    "dtype": "int",
                    "protocol": "PVA",
                },
            }
        )
        self.assertIn("var1", controls_info.variables)
        self.assertIn("var2", controls_info.variables)
        self.assertEqual(controls_info.variables["var1"].dtype, float)
        self.assertEqual(controls_info.variables["var2"].dtype, int)

    def test_controls_information_with_mixed_types(self):
        controls_info = ControlsInformation(
            variables={
                "var1": ControlVariable(
                    identifier="var1",
                    dtype="float",
                    protocol="CA",
                    units="V",
                    description="A float variable for voltage",
                ),
                "var2": {
                    "identifier": "var2",
                    "dtype": "int",
                    "protocol": "PVA",
                },
            }
        )
        self.assertIn("var1", controls_info.variables)
        self.assertIn("var2", controls_info.variables)
        self.assertEqual(controls_info.variables["var1"].dtype, float)
        self.assertEqual(controls_info.variables["var2"].dtype, int)

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
    """`_SERIALIZE_DEFAULTS` keys must match the field names `serialize` reads
    from `self`, not their YAML aliases -- ``control_type`` is the field,
    ``type`` is only the alias it is populated from."""

    def test_default_control_type_is_omitted(self):
        cv = ControlVariable(identifier="var1", protocol="CA")
        self.assertNotIn("control_type", cv.model_dump())

    def test_non_default_control_type_is_kept(self):
        cv = ControlVariable(identifier="var1", protocol="CA", type="waveform")
        print(cv.model_dump())
        self.assertEqual(cv.model_dump()["type"], "waveform")

    def test_default_control_type_omitted_via_alias(self):
        cv = ControlVariable(identifier="var1", protocol="CA", type="statistical")
        self.assertNotIn("control_type", cv.model_dump())
