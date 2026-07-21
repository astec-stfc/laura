import unittest
from laura.models.control import ControlVariable, ControlsInformation
from laura.utils.signals import RandomWalk, Sinusoid


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
            update={"function": "Sinusoid", "period": 1.0, "amplitude": 2.0}
        )
        self.assertEqual(
            cv.update, {"function": "Sinusoid", "period": 1.0, "amplitude": 2.0}
        )

    def test_update_from_instance_flattens_fields(self):
        cv = self.make(update=Sinusoid(period=1.0, amplitude=2.0))
        self.assertEqual(
            cv.update,
            {
                "function": "Sinusoid",
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

    def test_update_with_unknown_signal_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(update={"function": "NotASignal"})
        self.assertIsNone(cv.update)

    def test_update_with_non_dataclass_module_member_warns(self):
        # `np` is importable from laura.utils.signals but is not a signal.
        with self.assertWarns(UserWarning):
            cv = self.make(update={"function": "np"})
        self.assertIsNone(cv.update)

    def test_update_without_function_key_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(update={"period": 1.0})
        self.assertIsNone(cv.update)

    def test_update_with_missing_required_attribute_warns(self):
        with self.assertWarns(UserWarning):
            cv = self.make(update={"function": "Sinusoid", "period": 1.0})
        self.assertIsNone(cv.update)

    def test_update_with_unknown_attribute_warns(self):
        with self.assertWarns(UserWarning) as ctx:
            cv = self.make(
                update={
                    "function": "Sinusoid",
                    "period": 1.0,
                    "amplitude": 2.0,
                    "amplitud": 3.0,
                }
            )
        self.assertIsNone(cv.update)
        self.assertIn("amplitud", str(ctx.warning))

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
            update={"function": "Sinusoid", "period": 4.0, "amplitude": 2.0}
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
            update={"function": "Sinusoid", "period": 1.0, "amplitude": 2.0}
        )
        restored = ControlVariable(**cv.model_dump())
        self.assertEqual(restored.update, cv.update)


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
