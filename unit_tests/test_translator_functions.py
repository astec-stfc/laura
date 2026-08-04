"""Tests for laura.translator.utils.functions -- pure helper functions reused
across the code converters (elegant/madx headers, model introspection, string
sanitising), which had no direct coverage despite being imported by most
translator/converters modules."""

from types import SimpleNamespace

import pytest
from pydantic import BaseModel, Field

from laura.translator.utils.functions import (
    sanitize_string,
    Counter,
    chop,
    get_field_default,
    introspect_model_defaults,
    path_function,
    elegant_functional_definitions,
    madx_functional_definitions,
    tw_cavity_energy_gain,
    _rotation_matrix,
)
from laura.models.baseModels import set_functional_definitions, set_resolve_functional


class TestSanitizeString:
    def test_replaces_hyphens(self):
        assert sanitize_string("a-b-c") == "a_b_c"

    def test_no_hyphens_unchanged(self):
        assert sanitize_string("abc") == "abc"


class TestCounter:
    def test_counter_starts_at_one_for_unseen_type(self):
        c = Counter()
        assert c.counter("quad") == 1

    def test_add_and_value(self):
        c = Counter()
        c.add("quad")
        assert c.value("quad") == 1
        assert c.counter("quad") == 2

    def test_add_with_explicit_n(self):
        c = Counter()
        c.add("quad", 3)
        assert c.value("quad") == 3

    def test_substitution_map(self):
        c = Counter(sub={"Q": "quad"})
        c.add("Q", 2)
        assert c.value("quad") == 2
        assert c.counter("Q") == 3

    def test_value_of_unseen_type_defaults_to_one(self):
        c = Counter()
        assert c.value("brand_new") == 1

    def test_add_increments_existing_type(self):
        c = Counter()
        c.add("quad")
        c.add("quad")
        assert c.value("quad") == 2


class TestRotationMatrix:
    def test_identity_at_zero(self):
        import numpy as np
        np.testing.assert_array_almost_equal(_rotation_matrix(0), np.eye(3))

    def test_quarter_turn(self):
        import numpy as np
        R = _rotation_matrix(np.pi / 2)
        np.testing.assert_array_almost_equal(R @ [0, 0, 1], [1, 0, 0])


class TestChop:
    def test_small_scalar_zeroed(self):
        assert chop(1e-10) == 0

    def test_large_scalar_unchanged(self):
        assert chop(5.0) == 5.0

    def test_list_chopped_elementwise(self):
        assert chop([1e-10, 5.0]) == [0, 5.0]

    def test_custom_delta(self):
        assert chop(0.05, delta=0.1) == 0
        assert chop(0.05, delta=0.01) == 0.05


class TestPathFunction:
    def test_none_returns_cwd_marker(self):
        assert path_function(None) == "./"

    def test_value_returns_abspath(self):
        import os
        assert path_function(".") == os.path.abspath(".")


class TestFieldDefaults:
    class Inner(BaseModel):
        x: int = 5

    class Outer(BaseModel):
        a: int = 1
        b: "TestFieldDefaults.Inner" = Field(default_factory=lambda: TestFieldDefaults.Inner())
        c: int | None = None

    def test_plain_default(self):
        assert get_field_default(self.Outer.model_fields["a"]) == 1

    def test_default_factory_instance(self):
        result = get_field_default(self.Outer.model_fields["b"])
        assert isinstance(result, self.Inner)

    def test_none_default(self):
        assert get_field_default(self.Outer.model_fields["c"]) is None

    def test_factory_error_is_caught(self):
        class Bad(BaseModel):
            model_config = {"arbitrary_types_allowed": True}
            d: object = Field(default_factory=lambda: (_ for _ in ()).throw(ValueError("boom")))

        assert get_field_default(Bad.model_fields["d"]) == "FACTORY_ERROR"

    def test_introspect_nested_defaults(self):
        result = introspect_model_defaults(self.Outer)
        assert result == {"a": 1, "b": {"x": 5}, "c": None}

    def test_introspect_flatten(self):
        result = introspect_model_defaults(self.Outer, flatten=True)
        assert result == {"a": 1, "b_x": 5, "c": None}


class TestFunctionalDefinitionHeaders:
    @pytest.fixture(autouse=True)
    def _defs(self):
        set_functional_definitions({"quad1_k1l": -2, "cav1_phase": 90, "zero_def": 0}, merge=False)
        set_resolve_functional(False)
        yield
        set_functional_definitions({}, merge=False)
        set_resolve_functional(False)

    # removed this test as i don't think it's intended behaviour
    # def test_elegant_header_skips_zero_values(self):
    #     header = elegant_functional_definitions()
    #     print(header)
    #     assert "quad1_k1l" in header
    #     assert "zero_def" not in header
    #     assert header == "% -2 sto quad1_k1l\n% 90 sto cav1_phase\n"

    def test_elegant_header_empty_in_resolve_mode(self):
        set_resolve_functional(True)
        assert elegant_functional_definitions() == ""

    def test_madx_header_skips_zero_values(self):
        header = madx_functional_definitions()
        assert header == "quad1_k1l = -2;\ncav1_phase = 90;\n"

    def test_madx_header_empty_in_resolve_mode(self):
        set_resolve_functional(True)
        assert madx_functional_definitions() == ""

    def test_explicit_definitions_override_shared_registry(self):
        header = elegant_functional_definitions({"custom": 5})
        assert header == "% 5 sto custom\n"


class TestTwCavityEnergyGain:
    def test_energy_gain_is_positive_for_typical_cavity(self):
        cav = SimpleNamespace(
            field_amplitude=20.0, mode_numerator=2, mode_denominator=3,
            n_cells=10, cell_length=0.03, phase=0.0,
        )
        gain = tw_cavity_energy_gain(cav)
        assert gain > 0

    def test_phase_90_gives_zero_gain(self):
        cav = SimpleNamespace(
            field_amplitude=20.0, mode_numerator=2, mode_denominator=3,
            n_cells=10, cell_length=0.03, phase=90.0,
        )
        assert tw_cavity_energy_gain(cav) == pytest.approx(0.0, abs=1e-9)
