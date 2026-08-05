"""
Vector and geometry utilities for LAURA elements.

Provides vector operations, geometric calculations, and angle computations.
"""

import numpy as np
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..models.physical import Position, Rotation


def vector_length(x: float, y: float, z: float = 0.0) -> float:
    """
    Calculate the length (magnitude) of a 2D or 3D vector.

    Args:
        x: X component
        y: Y component
        z: Z component (default 0 for 2D)

    Returns:
        Vector magnitude
    """
    return float(np.sqrt(x**2 + y**2 + z**2))


def vector_angle(
    x1: float, y1: float, x2: float, y2: float, z1: float = 0.0, z2: float = 0.0
) -> float:
    """
    Calculate angle between two vectors.

    Args:
        x1, y1, z1: First vector components
        x2, y2, z2: Second vector components

    Returns:
        Angle in radians
    """
    v1 = np.array([x1, y1, z1])
    v2 = np.array([x2, y2, z2])

    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
    # Clamp to [-1, 1] to avoid numerical errors in arccos
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    return float(np.arccos(cos_angle))


def normalized_vector(x: float, y: float, z: float = 0.0) -> tuple:
    """
    Normalize a vector to unit length.

    Args:
        x, y, z: Vector components

    Returns:
        Tuple of (x_norm, y_norm, z_norm)
    """
    length = vector_length(x, y, z)
    if length < 1e-10:
        return (0.0, 0.0, 0.0)
    return (x / length, y / length, z / length)


def dot_product(
    x1: float, y1: float, x2: float, y2: float, z1: float = 0.0, z2: float = 0.0
) -> float:
    """
    Calculate dot product of two vectors.

    Args:
        x1, y1, z1: First vector
        x2, y2, z2: Second vector

    Returns:
        Scalar dot product
    """
    return float(x1 * x2 + y1 * y2 + z1 * z2)


def cross_product(
    x1: float, y1: float, z1: float,
    x2: float, y2: float, z2: float,
) -> tuple:
    """
    Calculate cross product of two 3D vectors.

    Args:
        x1, y1, z1: First vector
        x2, y2, z2: Second vector

    Returns:
        Tuple of (x, y, z) components of cross product
    """
    v1 = np.array([x1, y1, z1])
    v2 = np.array([x2, y2, z2])
    result = np.cross(v1, v2)
    return tuple(float(c) for c in result)
