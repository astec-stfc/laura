"""
Magnet physics: K↔Current conversions and field integral calculations.

Provides standardized formulas for converting between integrated field strengths (KL)
and magnet currents, accounting for magnet rigidity and magnet type.
"""

from typing import Union


def k_to_current(
    k_value: float,
    magnet_type: str,
    momentum: float,
    magnet_rigidity: float = 1.0,
) -> float:
    """
    Convert integrated field strength K [m^-1] to magnet current [A].

    Formula:
        I [A] = K [m^-1] * momentum [GeV/c] / (brho_coeff * magnet_rigidity)

    Args:
        k_value: Integrated field strength K [m^-1]
        magnet_type: Type of magnet ('Dipole', 'Quadrupole', 'Sextupole', etc.)
        momentum: Beam momentum [GeV/c]
        magnet_rigidity: Magnet rigidity coefficient (from calibration)

    Returns:
        Current [A]

    Raises:
        ValueError if magnet_type unknown or momentum <= 0
    """
    if momentum <= 0:
        raise ValueError(f"Momentum must be positive, got {momentum}")

    # Brho coefficient: converts momentum to magnetic rigidity
    # brho [T*m] = momentum [GeV/c] * (10^9 / c) / (e/c)
    # brho = momentum * 3.336 (T*m per GeV/c)
    brho_coeff = 3.336  # T*m per GeV/c

    brho = momentum * brho_coeff  # [T*m]

    # Type-specific scaling (from magnet calibrations)
    if magnet_type in ("Dipole", "Dipole_Magnet", "Bending"):
        # Dipole: I = K * brho / rigidity_coeff (in thousands)
        i = k_value * brho / (magnet_rigidity * 1000)
    elif magnet_type in ("Quadrupole", "Quadrupole_Magnet"):
        # Quadrupole: I = K * brho / (rigidity_coeff * 1e6)
        i = k_value * brho / (magnet_rigidity * 1e6)
    elif magnet_type in ("Sextupole", "Sextupole_Magnet"):
        # Sextupole: Similar to quadrupole
        i = k_value * brho / (magnet_rigidity * 1e6)
    elif magnet_type in ("Octupole", "Octupole_Magnet"):
        # Octupole: Similar to quadrupole
        i = k_value * brho / (magnet_rigidity * 1e6)
    elif magnet_type in ("Solenoid", "Solenoid_Magnet"):
        # Solenoid: I = K * brho / rigidity_coeff
        i = k_value * brho / (magnet_rigidity * 1000)
    else:
        raise ValueError(
            f"Unknown magnet type '{magnet_type}'. "
            f"Supported: Dipole, Quadrupole, Sextupole, Octupole, Solenoid"
        )

    return i


def current_to_k(
    current: float,
    magnet_type: str,
    momentum: float,
    magnet_rigidity: float = 1.0,
) -> float:
    """
    Convert magnet current [A] to integrated field strength K [m^-1].

    Inverse of k_to_current().

    Args:
        current: Magnet current [A]
        magnet_type: Type of magnet ('Dipole', 'Quadrupole', 'Sextupole', etc.)
        momentum: Beam momentum [GeV/c]
        magnet_rigidity: Magnet rigidity coefficient (from calibration)

    Returns:
        Integrated field strength K [m^-1]

    Raises:
        ValueError if magnet_type unknown or momentum <= 0
    """
    if momentum <= 0:
        raise ValueError(f"Momentum must be positive, got {momentum}")

    brho_coeff = 3.336  # T*m per GeV/c
    brho = momentum * brho_coeff  # [T*m]

    # Type-specific inverse scaling
    if magnet_type in ("Dipole", "Dipole_Magnet", "Bending"):
        k = current * magnet_rigidity * 1000 / brho
    elif magnet_type in ("Quadrupole", "Quadrupole_Magnet"):
        k = current * magnet_rigidity * 1e6 / brho
    elif magnet_type in ("Sextupole", "Sextupole_Magnet"):
        k = current * magnet_rigidity * 1e6 / brho
    elif magnet_type in ("Octupole", "Octupole_Magnet"):
        k = current * magnet_rigidity * 1e6 / brho
    elif magnet_type in ("Solenoid", "Solenoid_Magnet"):
        k = current * magnet_rigidity * 1000 / brho
    else:
        raise ValueError(
            f"Unknown magnet type '{magnet_type}'. "
            f"Supported: Dipole, Quadrupole, Sextupole, Octupole, Solenoid"
        )

    return k


def scale_order(order: int, value: float, direction: str = "to_canonical") -> float:
    """
    Scale multipole coefficient by order (convert between storage and canonical forms).

    Multipoles can be stored in different scaling conventions:
    - Canonical: raw multipole strength
    - Scaled: adjusted for hardware representation

    Args:
        order: Multipole order (0=dipole, 1=quadrupole, 2=sextupole, etc.)
        value: Coefficient value
        direction: "to_canonical" or "from_canonical"

    Returns:
        Scaled value
    """
    # For now, this is a pass-through. Different magnets may need different scaling.
    # Currently handled in Dipole_Magnet.k0l and Quadrupole_Magnet.k1l with inconsistent logic
    return value
