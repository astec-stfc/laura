import numpy as np
import pytest

from laura.models.simulation import MatrixTransformSimulationElement


def _with(base, entries):
    for idx, val in entries.items():
        base[idx] = val
    return base


@pytest.mark.parametrize(
    "field, value, expected",
    [
        pytest.param("c_matrix", [1, 2, 3, 4, 5, 6], np.array([1, 2, 3, 4, 5, 6], dtype=float), id="c-vector"),
        pytest.param("c_matrix", {"c1": 1.5, "c6": -2.0}, _with(np.zeros(6), {0: 1.5, 5: -2.0}), id="c-dict"),
        pytest.param("c_matrix", {"C1": 1.5, "c6": -2.0}, _with(np.zeros(6), {0: 1.5, 5: -2.0}), id="c-case-insensitive"),
        pytest.param("r_matrix", np.arange(36).reshape(6, 6), np.arange(36).reshape(6, 6), id="r-dense"),
        pytest.param(
            "r_matrix", {"r21": 0.3, "R34": 1.5},
            _with(np.eye(6), {(1, 0): 0.3, (2, 3): 1.5}), id="r-dict",
        ),
        pytest.param("t_matrix", np.ones((6, 6, 6)), np.ones((6, 6, 6)), id="t-dense"),
        pytest.param(
            "t_matrix", {"t513": 0.1, "T122": 0.5},
            _with(np.zeros((6, 6, 6)), {(4, 0, 2): 0.1, (0, 1, 1): 0.5}), id="t-dict",
        ),
    ],
)
def test_matrix_input(field, value, expected):
    obj = MatrixTransformSimulationElement(**{field: value})
    np.testing.assert_array_equal(getattr(obj, field), expected)


@pytest.mark.parametrize(
    "field, value, match",
    [
        pytest.param("c_matrix", {"c7": 1.0}, "out of range", id="c-index"),
        pytest.param("c_matrix", {"foo": 1.0}, "Invalid C-matrix element", id="c-name"),
        pytest.param("r_matrix", {"foo": 1.0}, None, id="r-name"),
        pytest.param("r_matrix", {"r71": 1.0}, None, id="r-index"),
        pytest.param("t_matrix", {"foo": 1.0}, None, id="t-name"),
        pytest.param("t_matrix", {"t771": 1.0}, None, id="t-index"),
        pytest.param("u_matrix", np.zeros((6, 6, 6)), "u_matrix must have shape", id="u-shape"),
    ],
)
def test_matrix_input_invalid(field, value, match):
    with pytest.raises(ValueError, match=match):
        MatrixTransformSimulationElement(**{field: value})


def test_u_matrix_from_dict():
    obj = MatrixTransformSimulationElement(u_matrix={"u1234": 2.5})

    assert obj.u_matrix.shape == (6, 6, 6, 6)
    assert obj.u_matrix[0, 1, 2, 3] == 2.5


def test_spin_taylor_terms():
    term = {
        "index": 2,
        "coef": -0.5,
        **{f"exp{i}": float(i == 1) for i in range(1, 7)},
    }

    assert MatrixTransformSimulationElement(spin_taylor=[term]).spin_taylor == [term]


def test_spin_taylor_term_requires_all_exponents():
    with pytest.raises(ValueError, match="exp6"):
        MatrixTransformSimulationElement(spin_taylor=[{"index": 0, "coef": 1.0}])
