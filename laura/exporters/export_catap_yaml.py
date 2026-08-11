import os

from ..models.element_list import MachineModel
from laura.importers.catap_loader import catap_files, read_catap_yaml

if __name__ == "__main__":
    CATAPmachine = MachineModel(layout_file=os.path.abspath("./layouts.yaml"))

    for f in catap_files:
        elem = read_catap_yaml(f)
        CATAPmachine.update({n: e for n, e in elem.items()})
