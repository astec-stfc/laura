from typing import Optional

from laura.models.physical import DriftPhysicalElement
from laura.models.simulation import DriftSimulationElement

from ..converters import keyword_conversion_rules_elegant
from .base import BaseElementTranslator


class DriftTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.Drift` element instance into a string or
    object that can be understood by various simulation codes.
    """

    physical: Optional[DriftPhysicalElement] = None
    """Drift physical attributes; the length may be negative."""

    simulation: DriftSimulationElement
    """Drift simulation attributes."""

    def to_elegant(self) -> str:
        """
        Generates a string representation of the object's properties in the Elegant format.
        If `element.simulation.csr_enable`, a `CSRDRIFT` is written;
        if `element.simulation.lsc_enable`, a `LSCDRIFT` is written;
        else a `DRIFT` is written.

        See `Elegant manual LSC drift`_ and `Elegant manual CSR drift`_

        .. _Elegant manual CSR drift: https://ops.aps.anl.gov/manuals/elegant_latest/elegantsu133.html#x144-14300010.23
        .. _Elegant manual LSC drift: https://ops.aps.anl.gov/manuals/elegant_latest/elegantsu134.html

        Returns
        -------
        str
            A formatted string representing the object's properties in Elegant format.
        """
        self.start_write()
        if self.simulation.csr_enable:
            self.hardware_type = "csrdrift"
            if not self.simulation.lsc_enable:
                self.simulation.lsc_bins = 0
        elif self.simulation.lsc_enable:
            self.hardware_type = "lscdrift"
        else:
            self.hardware_type = "drift"
        self.conversion_rules["elegant"] = (
            keyword_conversion_rules_elegant.get(self.hardware_type, {})
            | keyword_conversion_rules_elegant["general"]
        )
        return super().to_elegant()
