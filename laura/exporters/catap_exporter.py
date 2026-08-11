import logging
import os
import yaml
from ..laura import MachineModel

_log = logging.getLogger("laura.exporter.catap")


def element_to_catap(elem):
    catap_dict = {}
    catap_dict["controls_information"] = {}
    catap_dict["controls_information"]["PV"] = True
    catap_dict["controls_information"]["pv_record_map"] = {}
    _log.debug("element_to_CATAP: controls = %s", elem.controls)
    for k, v in dict(elem.controls).items():
        catap_dict["controls_information"]["pv_record_map"][k] = str(v)
    catap_dict["controls_information"]["records"] = ",".join(dict(elem.controls).keys())
    catap_dict["properties"] = elem.to_CATAP()
    return catap_dict


def save_catap_file(n, e):
    subdir = e.hardware_type
    if not os.path.isdir("to_CATAP/MasterLattice/" + subdir):
        os.mkdir("to_CATAP/MasterLattice/" + subdir)
    with open("to_CATAP/MasterLattice/" + subdir + "/" + n + ".yml", "w") as outfile:
        yaml.dump(element_to_catap(e), outfile, default_flow_style=False)

    # print(element_to_CATAP(e))


def export_machine(path: str, machine: MachineModel, overwrite: bool = False) -> None:
    for name, elem in machine.elements.items():
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        if overwrite or not os.path.isfile(filename):
            _log.debug("Exporting element '%s' to file '%s'", name, filename)
            save_catap_file(filename, elem)


def export_machine_dict(machine: MachineModel) -> list:
    for name, elem in machine.elements.items():
        if hasattr(elem, "controls"):
            _log.debug("Exporting element '%s'", name)
            yield element_to_catap(elem)

# ---------------------------------------------------------------------------
# Backwards compatibility: names renamed for PEP 8. Served lazily with a
# FutureWarning so downstream consumers (astec-stfc/simba) keep working.
# ---------------------------------------------------------------------------
from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "element_to_CATAP": "element_to_catap",
        "save_CATAP_file": "save_catap_file",
    },
)
