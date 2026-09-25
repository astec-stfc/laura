"""Element names Bmad will not accept, and what to call them instead."""

from typing import Dict, Iterable, List
from warnings import warn

__all__ = [
    "BMAD_RESERVED_NAMES",
    "BMAD_RENAME_SUFFIX",
    "bmad_safe_names",
]

BMAD_RESERVED_NAMES = frozenset(
    {
        "AB_MULTIPOLE",
        "AC_KICKER",
        "BEAM",
        "BEAMBEAM",
        "BEGINNING",
        "BEGINNING_ELE",
        "BMAD_COM",
        "CALL",
        "CAPILLARY",
        "COMBINE_CONSECUTIVE_ELEMENTS",
        "CONVERTER",
        "CRAB_CAVITY",
        "CRYSTAL",
        "CUSTOM",
        "DETECTOR",
        "DIFFRACTION_PLATE",
        "DRIFT",
        "ECOLLIMATOR",
        "ELSEPARATOR",
        "EM_FIELD",
        "END",
        "END_FILE",
        "EXPAND_LATTICE",
        "E_GUN",
        "FEEDBACK",
        "FIDUCIAL",
        "FIXER",
        "FLOOR_SHIFT",
        "FOIL",
        "FORK",
        "GIRDER",
        "GKICKER",
        "GROUP",
        "HKICKER",
        "HYBRID",
        "INSTRUMENT",
        "KICKER",
        "LCAVITY",
        "LENS",
        "MARKER",
        "MASK",
        "MATCH",
        "MERGE_ELEMENTS",
        "MIRROR",
        "MONITOR",
        "MULTILAYER_MIRROR",
        "MULTIPOLE",
        "NO_DIGESTED",
        "NULL_ELE",
        "OCTUPOLE",
        "OVERLAY",
        "PARAMETER",
        "PARSER_DEBUG",
        "PARTICLE_START",
        "PATCH",
        "PHOTON_FORK",
        "PHOTON_INIT",
        "PICKUP",
        "PIPE",
        "PRINT",
        "PTC_COM",
        "QUADRUPOLE",
        "RAMPER",
        "RBEND",
        "RCOLLIMATOR",
        "REDEF",
        "REMOVE_ELEMENTS",
        "RETURN",
        "RFCAVITY",
        "RF_BEND",
        "SAD_MULT",
        "SAMPLE",
        "SBEND",
        "SEXTUPOLE",
        "SLICE_LATTICE",
        "SOLENOID",
        "SOL_QUAD",
        "SPACE_CHARGE_COM",
        "SUPERIMPOSE",
        "TAYLOR",
        "THICK_MULTIPOLE",
        "TITLE",
        "UNDULATOR",
        "USE",
        "VKICKER",
        "WIGGLER",
        "WRITE_DIGESTED",
    }
)
"""Names an element cannot carry in a Bmad lattice"""

BMAD_RENAME_SUFFIX = "_ELEMENT"
"""Appended to a reserved name; a further ``_2``, ``_3`` ... breaks a tie."""


def bmad_safe_names(names: Iterable[str]) -> Dict[str, str]:
    """
    Map each name Bmad would reject to one it accepts.

    Only the names that have to change appear in the result, so a lattice with
    nothing reserved in it is written exactly as it was.

    Parameters
    ----------
    names: Iterable[str]
        Every name that will be written into the lattice.

    Returns
    -------
    dict
        Original name -> replacement, for the reserved names only.
    """
    names = list(names)
    seen = {name.upper() for name in names}
    renames: Dict[str, str] = {}
    reserved: List[str] = list(
        dict.fromkeys(name for name in names if name.upper() in BMAD_RESERVED_NAMES)
    )
    for name in reserved:
        candidate = name + BMAD_RENAME_SUFFIX
        count = 1
        while candidate.upper() in seen or candidate.upper() in BMAD_RESERVED_NAMES:
            count += 1
            candidate = f"{name}{BMAD_RENAME_SUFFIX}_{count}"
        seen.add(candidate.upper())
        renames[name] = candidate
    if renames:
        listed = ", ".join(f"{old} -> {new}" for old, new in sorted(renames.items()))
        warn(
            "Bmad reserves these element names, so they are written out under "
            f"different ones: {listed}. Anything matching the exported lattice "
            "back to this one by name has to follow the same mapping."
        )
    return renames
