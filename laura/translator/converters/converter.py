from typing import List, Dict

from laura.models.element import (
    Element,
    Magnet,
    Solenoid,
    Dipole,
    RFCavity,
    RFDeflectingCavity,
    CrabCavity,
    Drift,
    Aperture,
    Diagnostic,
    Marker,
    Plasma,
    Laser,
    Wiggler,
    Combined_Corrector,
    Horizontal_Corrector,
    Vertical_Corrector,
    NonLinearLens,
    TwissMatch,
    Screen,
    MatrixTransform,
    ElectrostaticSeparator,
    ACDipole,
    Wire,
    BeamBeam,
    RFMultipole,
)

from .base import BaseElementTranslator
from .magnet import (
    MagnetTranslator,
    SolenoidTranslator,
    DipoleTranslator,
    WigglerTranslator,
    NonLinearLensTranslator,
    CorrectorTranslator,
)
from .cavity import RFCavityTranslator
from .drift import DriftTranslator
from .diagnostic import DiagnosticTranslator
from .aperture import ApertureTranslator
from .plasma import PlasmaTranslator
from .laser import LaserTranslator
from .twiss import TwissMatchTranslator
from .matrix import MatrixTransformTranslator
from .electrostatic_separator import ElectrostaticSeparatorTranslator
from .ac_dipole import ACDipoleTranslator
from .wire import WireTranslator
from .beam_beam import BeamBeamTranslator
from .rf_multipole import RFMultipoleTranslator


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
                Combined_Corrector,
                Horizontal_Corrector,
                Vertical_Corrector,
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
        elif isinstance(elem, Diagnostic) or isinstance(elem, Marker) or isinstance(elem, Screen):
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
        try:
            elem_dict.update({elem.name: translator.model_validate(elem.model_dump(by_alias=False))})
        except Exception as exc:
            raise Exception(f"Element {elem.name} failed validation: {elem.model_dump().keys()}")
        elem_dict[elem.name].master_lattice = master_lattice
        elem_dict[elem.name].directory = directory
    return elem_dict
