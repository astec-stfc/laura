import numpy as np
import pytest

from laura.models.simulation import MatrixTransformSimulationElement


def test_c_matrix_from_vector():
    obj = MatrixTransformSimulationElement(
        c_matrix=[1, 2, 3, 4, 5, 6]
    )

    np.testing.assert_array_equal(
        obj.c_matrix,
        np.array([1, 2, 3, 4, 5, 6], dtype=float),
    )


def test_c_matrix_from_dict():
    obj = MatrixTransformSimulationElement(
        c_matrix={
            "c1": 1.5,
            "c6": -2.0,
        }
    )

    expected = np.zeros(6)
    expected[0] = 1.5
    expected[5] = -2.0

    np.testing.assert_array_equal(obj.c_matrix, expected)


def test_c_matrix_case_insensitive():
    obj = MatrixTransformSimulationElement(
        c_matrix={
            "C1": 1.5,
            "c6": -2.0,
        }
    )

    expected = np.zeros(6)
    expected[0] = 1.5
    expected[5] = -2.0

    np.testing.assert_array_equal(obj.c_matrix, expected)


def test_c_matrix_invalid_index():
    with pytest.raises(ValueError, match="out of range"):
        MatrixTransformSimulationElement(
            c_matrix={"c7": 1.0}
        )


def test_c_matrix_invalid_name():
    with pytest.raises(ValueError, match="Invalid C-matrix element"):
        MatrixTransformSimulationElement(
            c_matrix={"foo": 1.0}
        )

def test_r_matrix_from_dense():
    mat = np.arange(36).reshape(6, 6)

    obj = MatrixTransformSimulationElement(r_matrix=mat)

    np.testing.assert_array_equal(obj.r_matrix, mat)


def test_r_matrix_from_dict():
    obj = MatrixTransformSimulationElement(
        r_matrix={
            "r21": 0.3,
            "R34": 1.5,
        }
    )

    expected = np.eye(6)
    expected[1, 0] = 0.3
    expected[2, 3] = 1.5

    np.testing.assert_array_equal(obj.r_matrix, expected)


def test_r_matrix_invalid_name():
    with pytest.raises(ValueError):
        MatrixTransformSimulationElement(
            r_matrix={"foo": 1.0}
        )


def test_r_matrix_invalid_index():
    with pytest.raises(ValueError):
        MatrixTransformSimulationElement(
            r_matrix={"r71": 1.0}
        )

def test_t_matrix_from_dense():
    tensor = np.ones((6, 6, 6))

    obj = MatrixTransformSimulationElement(
        t_matrix=tensor
    )

    np.testing.assert_array_equal(
        obj.t_matrix,
        tensor,
    )


def test_t_matrix_from_dict():
    obj = MatrixTransformSimulationElement(
        t_matrix={
            "t513": 0.1,
            "T122": 0.5,
        }
    )

    expected = np.zeros((6, 6, 6))
    expected[4, 0, 2] = 0.1
    expected[0, 1, 1] = 0.5

    np.testing.assert_array_equal(
        obj.t_matrix,
        expected,
    )


def test_t_matrix_invalid_name():
    with pytest.raises(ValueError):
        MatrixTransformSimulationElement(
            t_matrix={"foo": 1.0}
        )


def test_t_matrix_invalid_index():
    with pytest.raises(ValueError):
        MatrixTransformSimulationElement(
            t_matrix={"t771": 1.0}
        )


def test_u_matrix_from_dict():
    obj = MatrixTransformSimulationElement(u_matrix={"u1234": 2.5})

    assert obj.u_matrix.shape == (6, 6, 6, 6)
    assert obj.u_matrix[0, 1, 2, 3] == 2.5


def test_u_matrix_invalid_shape():
    with pytest.raises(ValueError, match="u_matrix must have shape"):
        MatrixTransformSimulationElement(u_matrix=np.zeros((6, 6, 6)))


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
