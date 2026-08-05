"""Tests for laura.models.control expression evaluation / apply machinery
(resolve_path, eval_expr, set_attr_by_path, ControlVariable.apply,
ControlsInformation.build_context/apply/__getattr__), which the docstring
in control.py demonstrates but which had no direct test coverage."""

import pytest

from laura.models.control import (
    ControlVariable,
    ControlsInformation,
    resolve_path,
    eval_expr,
    set_attr_by_path,
)
from laura.models.element import Quadrupole


def make_quad(**controls_kwargs):
    cv = ControlVariable(
        identifier="k1l_control",
        dtype=float,
        protocol="CA",
        value=0.1,
        target="magnetic.k1l",
        expression={"op": "mul", "args": ["k1l_control", "magnetic.length"]},
        **controls_kwargs,
    )
    controls_info = ControlsInformation(variables={"k1l_control": cv})
    element = Quadrupole(
        name="Quad1",
        machine_area="AREA",
        magnetic={"k1l": 0.0, "length": 2.0},
        controls=controls_info,
    )
    return element, controls_info, cv


class TestResolvePath:
    def test_resolves_top_level_symbol(self):
        assert resolve_path({"x": 5}, "x") == 5

    def test_resolves_nested_attribute(self):
        element, *_ = make_quad()
        ctx = {"magnetic": element.magnetic}
        assert resolve_path(ctx, "magnetic.length") == 2.0

    def test_unknown_symbol_raises_keyerror(self):
        with pytest.raises(KeyError, match="Unknown symbol"):
            resolve_path({}, "nope")


class TestEvalExpr:
    def test_number_passthrough(self):
        assert eval_expr(5, {}) == 5
        assert eval_expr(2.5, {}) == 2.5

    def test_string_resolves_from_context(self):
        assert eval_expr("x", {"x": 3.0}) == 3.0

    def test_op_expression(self):
        expr = {"op": "mul", "args": [2, 3]}
        assert eval_expr(expr, {}) == 6

    def test_nested_op_expression(self):
        expr = {"op": "add", "args": [{"op": "mul", "args": [2, 3]}, 1]}
        assert eval_expr(expr, {}) == 7


class TestSetAttrByPath:
    def test_sets_nested_attribute(self):
        element, *_ = make_quad()
        set_attr_by_path(element, "magnetic.k1l", 9.0)
        assert element.magnetic.k1l == 9.0


class TestControlVariableApply:
    def test_apply_updates_target(self):
        element, controls_info, cv = make_quad()
        controls_info.apply(element)
        assert element.magnetic.k1l == pytest.approx(0.2)  # 0.1 * length(2.0)

    def test_apply_noop_without_target_or_expression(self):
        cv = ControlVariable(identifier="v", protocol="CA", value=1.0)
        element, *_ = make_quad()
        before = element.magnetic.k1l
        cv.apply(element, {})
        assert element.magnetic.k1l == before

    def test_str_returns_identifier(self):
        cv = ControlVariable(identifier="my_var", protocol="CA")
        assert str(cv) == "my_var"


class TestControlsInformationGetattr:
    def test_getattr_returns_variable(self):
        element, controls_info, cv = make_quad()
        assert controls_info.k1l_control is cv

    def test_getattr_unknown_raises(self):
        element, controls_info, cv = make_quad()
        with pytest.raises(AttributeError):
            controls_info.does_not_exist

    def test_build_context_includes_variables_and_subsystems(self):
        element, controls_info, cv = make_quad()
        ctx = ControlsInformation.build_context(element)
        assert ctx["k1l_control"] == 0.1
        assert ctx["magnetic"] is element.magnetic

    def test_variables_value_must_be_dict_or_controlvariable(self):
        with pytest.raises(TypeError):
            ControlsInformation(variables={"var1": 123})


class TestValidateDtype:
    def test_dtype_invalid_object_raises_typeerror(self):
        with pytest.raises(TypeError):
            ControlVariable(identifier="v", protocol="CA", dtype=[1, 2])


class TestSerializeExtras:
    def test_extra_fields_survive_serialization(self):
        cv = ControlVariable(
            identifier="v", protocol="CA", auto_buffer=True, buffer_size=10
        )
        dumped = cv.model_dump()
        assert dumped["auto_buffer"] is True
        assert dumped["buffer_size"] == 10
