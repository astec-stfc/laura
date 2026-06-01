"""
Rotation matrix calculations and geometric transformations.

Provides efficient computation of rotation matrices from Euler angles and
lattice geometry calculations based on Position and Rotation.
"""

import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.physical import Position, Rotation


def euler_angles_to_rotation_matrix(
    yaw: float, pitch: float, roll: float
) -> np.ndarray:
    """
    Convert Euler angles (in radians) to a 3x3 rotation matrix.

    Uses YXZ convention matching LAURA's physical model:
    R = Rz(roll) @ Rx(pitch) @ Ry(yaw)

    This convention matches historical LAURA geometry calculations where:
    - yaw (theta): rotation around Z (Ry)
    - pitch (phi): rotation around X (Rx)
    - roll (psi): rotation around Z (Rz)

    Args:
        yaw: Rotation angle theta (radians), applied around Y via Ry
        pitch: Rotation angle phi (radians), applied around X via Rx
        roll: Rotation angle psi (radians), applied around Z via Rz

    Returns:
        3x3 numpy array rotation matrix: Rz(roll) @ Rx(pitch) @ Ry(yaw)
    """
    cy = np.cos(yaw)
    sy = np.sin(yaw)
    cp = np.cos(pitch)
    sp = np.sin(pitch)
    cr = np.cos(roll)
    sr = np.sin(roll)

    # Rotation matrices
    Ry = np.array([
        [cy, 0, -sy],
        [0, 1, 0],
        [sy, 0, cy],
    ])
    
    Rx = np.array([
        [1, 0, 0],
        [0, cp, -sp],
        [0, sp, cp],
    ])
    
    Rz = np.array([
        [cr, -sr, 0],
        [sr, cr, 0],
        [0, 0, 1],
    ])

    # Apply in order: Rz @ Rx @ Ry (rightmost is applied first to column vectors)
    return np.dot(Rz, np.dot(Rx, Ry))


def position_rotated(
    position: "Position", rotation: "Rotation"
) -> "Position":
    """
    Apply rotation to a position vector.

    Args:
        position: Position to rotate (x, y, z)
        rotation: Rotation (alpha, beta, gamma) in radians

    Returns:
        Rotated position
    """
    from ..models.physical import Position  # Avoid circular import
    
    matrix = rotation.rotation_matrix
    original_vec = np.array([position.x, position.y, position.z])
    rotated_vec = matrix @ original_vec

    return Position(x=rotated_vec[0], y=rotated_vec[1], z=rotated_vec[2])


def element_start_position(
    middle: "Position", rotation: "Rotation", length: float
) -> "Position":
    """
    Calculate element entrance position from middle position and rotation.

    The entrance is length/2 upstream along the element's s-axis.

    Args:
        middle: Element center position
        rotation: Element orientation
        length: Element length

    Returns:
        Entrance position
    """
    from ..models.physical import Position  # Avoid circular import
    
    # Vector pointing upstream (negative s)
    upstream = np.array([0.0, 0.0, -length / 2.0])
    
    # Rotate to element frame
    matrix = rotation.rotation_matrix
    offset = matrix @ upstream
    
    return Position(
        x=middle.x + offset[0],
        y=middle.y + offset[1],
        z=middle.z + offset[2],
    )


def rotation_matrix_to_euler(R: np.ndarray) -> tuple:
    """
    Extract (yaw, pitch, roll) Euler angles from a 3x3 rotation matrix.

    Inverse of euler_angles_to_rotation_matrix.  Uses the same YXZ convention:
        R = Rz(roll) @ Rx(pitch) @ Ry(yaw)

    For the expanded matrix:
        R[2,1] = sin(pitch)
        R[2,0] = cos(pitch)*sin(yaw),  R[2,2] = cos(pitch)*cos(yaw)
        R[0,1] = -sin(roll)*cos(pitch), R[1,1] = cos(roll)*cos(pitch)

    Returns
    -------
    (yaw, pitch, roll) in radians
    """
    pitch = float(np.arcsin(np.clip(R[2, 1], -1.0, 1.0)))
    cp = np.cos(pitch)
    if abs(cp) > 1e-9:
        yaw = float(np.arctan2(R[2, 0], R[2, 2]))
        roll = float(np.arctan2(-R[0, 1], R[1, 1]))
    else:
        # Gimbal lock (pitch = ±90°): assign all rotation to yaw, zero roll
        yaw = float(np.arctan2(-R[0, 2], R[0, 0]))
        roll = 0.0
    return yaw, pitch, roll


def element_end_position(
    middle: "Position", rotation: "Rotation", length: float
) -> "Position":
    """
    Calculate element exit position from middle position and rotation.

    The exit is length/2 downstream along the element's s-axis.

    Args:
        middle: Element center position
        rotation: Element orientation
        length: Element length

    Returns:
        Exit position
    """
    from ..models.physical import Position  # Avoid circular import
    
    # Vector pointing downstream (positive s)
    downstream = np.array([0.0, 0.0, length / 2.0])
    
    # Rotate to element frame
    matrix = rotation.rotation_matrix
    offset = matrix @ downstream
    
    return Position(
        x=middle.x + offset[0],
        y=middle.y + offset[1],
        z=middle.z + offset[2],
    )
