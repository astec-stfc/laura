from .base import BaseElementTranslator
from laura.models.simulation import DiagnosticSimulationElement
from laura.models.diagnostic import WireScanner_Diagnostic


class DiagnosticTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.Diagnostic` element instance into a string or
    object that can be understood by various simulation codes.
    """

    simulation: DiagnosticSimulationElement
    """Diagnostic simulation element"""

    directory: str = ""
    """Directory to which files will be written."""

    def to_elegant(self) -> str:
        """
        Generates a string representation of the object's properties in the Elegant format.
        The `element.simulation.output_filename` parameter will be updated to include an `.SDDS` suffix.

        Returns
        -------
        str
            A formatted string representing the object's properties in Elegant format.
        """
        self.start_write()
        if not self.simulation.output_filename:
            self.simulation.output_filename = f'"./{self.name}.SDDS"'
            # self.simulation.output_filename = f'"{self.directory}/{self.name}.SDDS"'
        return super().to_elegant()

    def to_csrtrack(self, n: int) -> str:
        """
        Writes the screen element string for CSRTrack.

        Parameters
        ----------
        n: int
            Modulator index

        Returns
        -------
        str
            String representation of the element for CSRTrack
        """
        z = self.physical.middle.z
        return (
            """quadrupole{\nposition{rho="""
            + str(z)
            + """, psi=0.0, marker=screen"""
            + str(n)
            + """a}\nproperties{strength=0.0, alpha=0, horizontal_offset=0,vertical_offset=0}\nposition{rho="""
            + str(z + 1e-6)
            + """, psi=0.0, marker=screen"""
            + str(n)
            + """b}\n}\n"""
        )


class WireScannerTranslator(DiagnosticTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.WireScanner`
    element instance into a string or object that can be understood by various
    simulation codes.

    Declares the ``diagnostic`` payload explicitly: the generic
    :class:`DiagnosticTranslator` has no such field, so under ``extra="ignore"``
    the wire geometry would be dropped during ``model_validate`` and never reach
    the output. BDSIM's ``wirescanner`` requires it.
    """

    diagnostic: WireScanner_Diagnostic
    """Wire-scanner diagnostic element."""
