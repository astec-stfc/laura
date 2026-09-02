import logging
import os
from copy import copy
from typing import Any, Union
import yaml
from IPython.core.magic import Bunch
from pydantic import BaseModel, field_validator, ValidationInfo, Field

_log = logging.getLogger("laura.loader.simframe")

from .magnet_table import add_magnet_table_parameters
from ..models.element import (
    Quadrupole,
    Dipole,
    Sextupole,
    Solenoid,
    Marker,
    Aperture,
    Collimator,
    BeamPositionMonitor,
    BeamArrivalMonitor,
    BunchLengthMonitor,
    WallCurrentMonitor,
    FaradayCupMonitor,
    IntegratedCurrentTransformer,
    Screen,
    CombinedCorrector,
    HorizontalCorrector,
    VerticalCorrector,
    Wakefield,
    RFCavity,
    RFDeflectingCavity,
    Shutter,
    Camera,
)
from ..models.diagnostic import camera_diagnostic_type

with open(
    os.path.dirname(os.path.abspath(__file__)) + "/camera_assignments.yaml", "r"
) as stream:
    camera_assignments = yaml.load(stream, Loader=yaml.Loader)
    camera_types = {}
    for k, v in camera_assignments.items():
        for s in v:
            camera_types[s] = k


class SimFrameConversion(BaseModel):
    typeclass: Any
    hardware_class: str
    hardware_type: Union[str, None] = Field(validate_default=True, default=None)

    @field_validator("hardware_type", mode="before")
    def check_type(cls, value: Any, info: ValidationInfo) -> str:
        if value is None:
            value = info.data["typeclass"].model_fields["hardware_type"].default
        return value or None


SimFrame_Elements = {
    "quadrupole": SimFrameConversion(typeclass=Quadrupole, hardware_class="Magnet"),
    "dipole": SimFrameConversion(typeclass=Dipole, hardware_class="Magnet"),
    "sextupole": SimFrameConversion(typeclass=Sextupole, hardware_class="Magnet"),
    "solenoid": SimFrameConversion(typeclass=Solenoid, hardware_class="Magnet"),
    "marker": SimFrameConversion(typeclass=Marker, hardware_class="Simulation"),
    "aperture": SimFrameConversion(typeclass=Aperture, hardware_class="Simulation"),
    "collimator": SimFrameConversion(typeclass=Collimator, hardware_class="Simulation"),
    "beam_position_monitor": SimFrameConversion(
        typeclass=BeamPositionMonitor, hardware_class="Diagnostic"
    ),
    "beam_arrival_monitor": SimFrameConversion(
        typeclass=BeamArrivalMonitor, hardware_class="Diagnostic"
    ),
    "bunch_length_monitor": SimFrameConversion(
        typeclass=BunchLengthMonitor, hardware_class="Diagnostic"
    ),
    "wall_current_monitor": SimFrameConversion(
        typeclass=WallCurrentMonitor, hardware_class="Diagnostic"
    ),
    "faraday_cup": SimFrameConversion(
        typeclass=FaradayCupMonitor, hardware_class="Diagnostic"
    ),
    "integrated_current_transformer": SimFrameConversion(
        typeclass=IntegratedCurrentTransformer, hardware_class="Diagnostic"
    ),
    "screen": SimFrameConversion(typeclass=Screen, hardware_class="Diagnostic"),
    # 'rf_deflecting_cavity': SimFrame_Conversion(typeclass=Sextupole, PV_class='Magnet'),
    "kicker": SimFrameConversion(typeclass=CombinedCorrector, hardware_class="Magnet"),
    "hkicker": SimFrameConversion(
        typeclass=HorizontalCorrector, hardware_class="Magnet"
    ),
    "vkicker": SimFrameConversion(typeclass=VerticalCorrector, hardware_class="Magnet"),
    # 'monitor': SimFrame_Conversion(typeclass=Sextupole, PV_class='Magnet'),
    "longitudinal_wakefield": SimFrameConversion(
        typeclass=Wakefield, hardware_class="Simulation"
    ),
    "cavity": SimFrameConversion(typeclass=RFCavity, hardware_class="RF"),
    "rf_deflecting_cavity": SimFrameConversion(
        typeclass=RFDeflectingCavity, hardware_class="RF"
    ),
    "shutter": SimFrameConversion(typeclass=Shutter, hardware_class="Vacuum"),
}


def get_simframe_yaml_filename(original, replacement):
    splitstr = original.replace("\\", "/").split("/")
    idx = splitstr.index("YAML")
    return "/".join(splitstr[:idx]) + "/" + replacement


def get_simframe_machine_area(name):
    return name.split("-")[1]


def get_simframe_pv(name):
    return name


def interpret_simframe_element(name, elem):
    if "type" in elem and elem["type"] in SimFrame_Elements:
        # try:
        # print('type',elem['type'],'found')
        felem = SimFrame_Elements[elem["type"]].typeclass

        elem.update(dict(SimFrame_Elements[elem["type"]]))
        elem.update(
            {
                "name": name,
                "machine_area": get_simframe_machine_area(name),
                "hardware_class": SimFrame_Elements[elem["type"]].hardware_class,
            }
        )

        fields = elem
        elemmodel = felem(**fields)
        return elemmodel
    # except Exception as e:
    #     print('Error', name, e)


def read_simframe_yaml(filename):
    # print('File:',filename)
    elemlist = {}
    with open(filename, "r") as stream:
        data = yaml.load(stream, Loader=yaml.Loader)
    for name, elem in data["elements"].items():
        if name == "filename":  # and isinstance(elem, str):
            if isinstance(elem, str):
                newfilename = get_simframe_yaml_filename(filename, elem)
                elemlist.update(read_simframe_yaml(newfilename))
            elif isinstance(elem, list):
                for e in elem:
                    newfilename = get_simframe_yaml_filename(filename, e)
                    elemlist.update(read_simframe_yaml(newfilename))
        elif "type" in elem and elem["type"] in SimFrame_Elements:
            if elem["type"] == "kicker":
                helem = copy(elem)
                helem["type"] = "hkicker"
                helem["mag_type"] = "HORIZONTAL_CORRECTOR"
                hname = name.replace("HVCOR", "HCOR")
                velem = copy(elem)
                velem["type"] = "vkicker"
                velem["mag_type"] = "VERTICAL_CORRECTOR"
                vname = name.replace("HVCOR", "VCOR")
                elemmodel = interpret_simframe_element(hname, helem)
                elemlist.update({hname: elemmodel})
                elemmodel = interpret_simframe_element(vname, velem)
                elemlist.update({vname: elemmodel})
                elem["Horizontal_Corrector"] = hname
                elem["Vertical_Corrector"] = vname
            if elem["type"] == "screen":
                elemmodel = interpret_simframe_element(name, elem)
                elemlist.update({name: elemmodel})
                camtype = (
                    camera_types[elemmodel.name]
                    if elemmodel.name in camera_types
                    else "PCO"
                )
                _log.debug(
                    "Screen '%s': camera '%s' type='%s'",
                    elemmodel.name,
                    elemmodel.diagnostic.camera_name,
                    camtype,
                )
                elemmodelcam = Camera(
                    name=elemmodel.diagnostic.camera_name,
                    hardware_model=camtype,
                    machine_area=elemmodel.machine_area,
                    physical=elemmodel.physical,
                    diagnostic=camera_diagnostic_type(type=camtype),
                    controls=None,
                )
                elemlist.update({elemmodel.diagnostic.camera_name: elemmodelcam})
            else:
                elemmodel = interpret_simframe_element(name, elem)
                elemlist.update({name: elemmodel})
        else:
            # pass
            _log.warning(
                "Skipping SimFrame element '%s': unrecognised type '%s'",
                name,
                elem["type"],
            )
        if "sub_elements" in elem:
            for subname, subelem in elem["sub_elements"].items():
                if "type" in subelem and subelem["type"] in SimFrame_Elements:
                    # print('Subelement:', subelem)
                    subelem["subelement"] = True
                    elemmodel = interpret_simframe_element(subname, subelem)
                    # print(subname, elemmodel)
                    elemlist.update({subname: elemmodel})
    # print('simframe',elemlist)
    return elemlist


SF_files = [
    r"../../masterlattice/MasterLattice/YAML/CLA_Gun400.yaml",
    r"../../masterlattice/MasterLattice/YAML/CLA_SP2.yaml",
    r"../../masterlattice/MasterLattice/YAML/CLA_SP3.yaml",
    r"../../masterlattice/MasterLattice/YAML/CLA_FEBE.yaml",
    r"../../masterlattice/MasterLattice/YAML/CLA_SP1.yaml",
]

# ---------------------------------------------------------------------------
# Backwards compatibility: names renamed for PEP 8. Served lazily with a
# FutureWarning so downstream consumers (astec-stfc/simba) keep working.
# ---------------------------------------------------------------------------
from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "SimFrame_Conversion": "SimFrameConversion",
        "get_SimFrame_MachineArea": "get_simframe_machine_area",
        "get_SimFrame_PV": "get_simframe_pv",
        "get_SimFrame_YAML_filename": "get_simframe_yaml_filename",
        "interpret_SimFrame_Element": "interpret_simframe_element",
        "read_SimFrame_YAML": "read_simframe_yaml",
    },
)
