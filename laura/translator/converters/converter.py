from typing import Dict, List

from laura.models._generated import HardwareClassEnum
from laura.models.element import (
    ACDipole,
    Aperture,
    BeamBeam,
    CombinedCorrector,
    CrabCavity,
    Diagnostic,
    Dipole,
    Drift,
    ElectrostaticSeparator,
    Element,
    HorizontalCorrector,
    Laser,
    Magnet,
    Marker,
    MatrixTransform,
    NonLinearLens,
    Plasma,
    RFCavity,
    RFDeflectingCavity,
    RFMultipole,
    Screen,
    Solenoid,
    TwissMatch,
    VerticalCorrector,
    Wiggler,
    Wire,
)

from .ac_dipole import ACDipoleTranslator
from .aperture import ApertureTranslator
from .base import BaseElementTranslator
from .beam_beam import BeamBeamTranslator
from .cavity import RFCavityTranslator
from .diagnostic import DiagnosticTranslator
from .drift import DriftTranslator
from .electrostatic_separator import ElectrostaticSeparatorTranslator
from .laser import LaserTranslator
from .magnet import (
    CorrectorTranslator,
    DipoleTranslator,
    MagnetTranslator,
    NonLinearLensTranslator,
    SolenoidTranslator,
    WigglerTranslator,
)
from .matrix import MatrixTransformTranslator
from .plasma import PlasmaTranslator
from .rf_multipole import RFMultipoleTranslator
from .twiss import TwissMatchTranslator
from .wire import WireTranslator


def translate_elements(
    elements: List[Element],
    master_lattice: str = None,
    directory: str = ".",
) -> Dict[str, BaseElementTranslator]:
    """
    Function for translating a list of elements into their respective Translator classes.

    Parameters
    ----------
    elements: List[Element]
        List of :class:`~laura.models.element.Element` objects.
    master_lattice: str
        Directory containing lattice/data files including field/wakefield files.
    directory:
        Directory to which files will be written.

    Returns
    -------
    Dict[str, BaseElementTranslator]
        Dictionary of :class:`~laura.translator.converters.base.BaseElementTranslator` objects, keyed
        by their original name.
    """
    elem_dict = {}
    for elem in elements:
        if isinstance(elem, Magnet):
            if isinstance(elem, Solenoid):
                translator = SolenoidTranslator
            elif type(elem) in [
                CombinedCorrector,
                HorizontalCorrector,
                VerticalCorrector,
            ]:
                translator = CorrectorTranslator
            elif isinstance(elem, Dipole):
                translator = DipoleTranslator
            elif isinstance(elem, Wiggler):
                translator = WigglerTranslator
            elif isinstance(elem, NonLinearLens):
                translator = NonLinearLensTranslator
            else:
                translator = MagnetTranslator
        elif type(elem) in [RFCavity, RFDeflectingCavity, CrabCavity]:
            translator = RFCavityTranslator
        elif isinstance(elem, Drift):
            translator = DriftTranslator
        elif (
            isinstance(elem, Diagnostic)
            or isinstance(elem, Marker)
            or isinstance(elem, Screen)
        ):
            translator = DiagnosticTranslator
        elif isinstance(elem, Aperture):
            translator = ApertureTranslator
        elif isinstance(elem, Plasma):
            translator = PlasmaTranslator
        elif isinstance(elem, Laser):
            translator = LaserTranslator
        elif isinstance(elem, TwissMatch):
            translator = TwissMatchTranslator
        elif isinstance(elem, MatrixTransform):
            translator = MatrixTransformTranslator
        elif isinstance(elem, ElectrostaticSeparator):
            translator = ElectrostaticSeparatorTranslator
        elif isinstance(elem, ACDipole):
            translator = ACDipoleTranslator
        elif isinstance(elem, Wire):
            translator = WireTranslator
        elif isinstance(elem, BeamBeam):
            translator = BeamBeamTranslator
        elif isinstance(elem, RFMultipole):
            translator = RFMultipoleTranslator
        else:
            translator = BaseElementTranslator
        dump = elem.model_dump(by_alias=False)
        if dump.get("hardware_class") not in set(HardwareClassEnum):
            # Legacy/incorrectly-authored lattice data (seen in FERMI/ISIS/
            # UKXFEL, not CLARA): hardware_class was set to the specific
            # hardware_type instead of its coarse category (e.g. "RFCavity"
            # instead of "RF"), which fails the stricter Translator schema's
            # enum below even though the looser Element model accepted it at
            # load time (hardware_class is a plain, unconstrained `str`
            # there -- `frozen=True` on some subclasses only blocks a LATER
            # reassignment, not an explicit constructor override, which is
            # how the bad value got in to begin with). The owning Element
            # subclass's own declared default is the correct category
            # regardless of what literal value the YAML explicitly overrode
            # it with.
            dump["hardware_class"] = type(elem).model_fields["hardware_class"].default
        try:
            elem_dict.update({elem.name: translator.model_validate(dump)})
        except Exception as exc:
            raise Exception(
                f"Element {elem.name} failed validation: {dump.keys()}"
            ) from exc
        elem_dict[elem.name].master_lattice = master_lattice
        elem_dict[elem.name].directory = directory
    return elem_dict
