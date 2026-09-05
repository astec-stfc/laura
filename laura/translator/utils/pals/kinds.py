"""The correspondence between PALS element kinds and LAURA hardware types."""

from typing import Dict, Optional

from ...converters import type_conversion_rules_Pals

__all__ = [
    "LAURA_TYPE_EXTENSION",
    "laura_type_to_pals_kind",
    "pals_kind_round_trips",
    "pals_kind_to_laura_type",
]

LAURA_TYPE_EXTENSION = "LauraP"
"""Extension group carrying the LAURA hardware type a kind cannot express.

LAURA gets its own extension group, declared in the document's 
``extension_labels``.
"""

_PINNED = {
    "solenoid": "Solenoid",
    "instrument": "Diagnostic",
    "kicker": "Combined_Corrector",
    "mask": "Collimator",
    "crabcavity": "CrabCavity",
    "ackicker": "Horizontal_AC_Dipole",
    "match": "TwissMatch",
    "taylor": "MatrixTransform",
    "egun": "RFCavity",
    "foil": "Collimator",
    "fiducial": "Marker",
    "floorshift": "Marker",
    "fork": "Marker",
    "patch": "Marker",
    "referencechange": "Marker",
}


def pals_kind_to_laura_type() -> Dict[str, str]:
    """PALS element kind (lowercased) -> LAURA hardware type."""
    switch = {
        native_kind.lower(): laura_type
        for laura_type, native_kind in type_conversion_rules_Pals.items()
        if native_kind.lower() != "drift"
    }
    switch.update(_PINNED)
    return switch


def laura_type_to_pals_kind(hardware_type: str) -> Optional[str]:
    """PALS kind for a LAURA hardware type, or ``None`` if it has no kind."""
    return type_conversion_rules_Pals.get(hardware_type)


def pals_kind_round_trips(hardware_type: str) -> bool:
    """True if reading the exported kind back gives ``hardware_type`` again."""
    kind = laura_type_to_pals_kind(hardware_type)
    if kind is None:
        return False
    if kind.lower() == "drift":
        return hardware_type == "Drift"
    return pals_kind_to_laura_type().get(kind.lower()) == hardware_type
