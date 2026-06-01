import logging
import os
import yaml
from typing import Union
from ..models.elementList import MachineModel
from ..models.element import PhysicalElement
from ..models.magnetic import MagneticElement

_log = logging.getLogger("laura.exporter.yaml")


def represent_tuple(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data)


yaml.add_representer(tuple, represent_tuple)


def _clean_export_data(data: dict, ele: PhysicalElement) -> dict:
    """Remove computed / internal fields and restore essential identification fields
    that may have been stripped by exclude_defaults."""
    # --- Essential identification fields (have subclass-level defaults) ---
    data["hardware_type"] = ele.hardware_type
    data["hardware_class"] = ele.hardware_class

    # --- Computed fields on PhysicalElement ---
    if "physical" in data and isinstance(data["physical"], dict):
        data["physical"].pop("_physical_angle", None)

    # --- Computed fields on MagneticElement / Dipole_Magnet ---
    if "magnetic" in data and isinstance(data["magnetic"], dict):
        data["magnetic"].pop("half_gap", None)
        data["magnetic"].pop("rho", None)
        # Restore order (subclass default matches actual value, but useful in YAML)
        if hasattr(ele, "magnetic") and isinstance(ele.magnetic, MagneticElement):
            data["magnetic"]["order"] = ele.magnetic.order

    # --- Empty alias (Aliases([]) serialises as {} or []) ---
    alias = data.get("alias")
    if isinstance(alias, (dict, list)) and not alias:
        data.pop("alias", None)

    return data


def export_as_yaml(
    filename: Union[str, None], ele: PhysicalElement = PhysicalElement
) -> None:
    # exclude_defaults strips default values for a cleaner export, but may fail
    # if nested models have required fields without defaults; fall back gracefully.
    try:
        dump = ele.base_model_dump(exclude_defaults=True)
    except Exception:
        dump = ele.base_model_dump()
    dump.pop("CASCADING_RULES", None)
    dump = _clean_export_data(dump, ele)
    if filename is not None:
        with open(filename, "w") as yaml_file:
            yaml.default_flow_style = False
            yaml.dump(dump, yaml_file)
    else:
        return dump


def export_machine_combined_file(path: str, machine: MachineModel) -> None:
    filename = os.path.join(path, "summary.yaml")
    os.makedirs(path, exist_ok=True)
    combined_yaml = {}
    for name, elem in machine.elements.items():
        if elem is None:
            continue
        combined_yaml[name] = export_as_yaml(None, elem)
    with open(filename, "w") as yaml_file:
        yaml.default_flow_style = True
        yaml.dump(combined_yaml, yaml_file)


def export_machine(
    path: str, machine: MachineModel, overwrite: bool = False, verbose: bool = False
) -> None:
    os.makedirs(path, exist_ok=True)
    for name, elem in machine.elements.items():
        if elem is None:
            continue
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        if overwrite or not os.path.isfile(filename):
            if verbose:
                _log.debug("Exporting element '%s' to file '%s'", name, filename)
            export_as_yaml(filename, elem)


def export_elements(path: str, elements: list[PhysicalElement]) -> None:
    for elem in elements:
        if elem is None:
            continue
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        export_as_yaml(filename, elem)
