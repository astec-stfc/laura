from typing import NamedTuple, Dict
from laura.models.simulation import TwissMatchSimulationElement

class BmadBody(NamedTuple):
    """One section's contribution to a Bmad lattice file, minus the header."""

    definitions: str
    """Leading drift, patches and element definitions."""

    line: str
    """The section's ``line`` (or ``line[multipass]``) definition."""

    superpositions: str
    """``superimpose`` statements, which must follow every definition."""

    beginning: str
    """Floor-position datum for the section's first element."""

    origin: TwissMatchSimulationElement | None
    """Twiss seed taken from a leading ``TwissMatch``, if the section has one."""

    name: str
    """Sanitised line name, for the ``use`` statement."""

    renames: Dict[str, str]
    """Elements Bmad would not accept under their LAURA name, and what they are
    written out as. Anything addressing the export by name must follow it."""

