"""
LAURA utilities package.

Provides utilities for model calculations, conversions, and transformations.

Modules:
    cascading_access: Transparent nested attribute access
    rotation_matrix: Rotation and geometric transformations
    magnet_conversions: K↔Current conversions and field physics
    dict_utils: Dictionary flattening and YAML helpers
    vector_math: Vector operations and geometry
"""

from .cascading_access import CascadingAccessMixin
from .rotation_matrix import (
    euler_angles_to_rotation_matrix,
    position_rotated,
    element_start_position,
    element_end_position,
)
from .magnet_conversions import k_to_current, current_to_k, scale_order
from .dict_utils import flatten_dict, StringWithQuotes, FlowList
from .vector_math import (
    vector_length,
    vector_angle,
    normalized_vector,
    dot_product,
    cross_product,
)

__all__ = [
    # Cascading access
    "CascadingAccessMixin",
    # Rotation and geometry
    "euler_angles_to_rotation_matrix",
    "position_rotated",
    "element_start_position",
    "element_end_position",
    # Magnet conversions
    "k_to_current",
    "current_to_k",
    "scale_order",
    # Dict utilities
    "flatten_dict",
    "StringWithQuotes",
    "FlowList",
    # Vector math
    "vector_length",
    "vector_angle",
    "normalized_vector",
    "dot_product",
    "cross_product",
]
