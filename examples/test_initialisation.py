import sys
import os

sys.path.append(r"C:\Users\jkj62.CLRC\Documents\GitHub\laura")
from laura.laura import LAURA
import laura
laura.set_log_level("DEBUG")
from laura.exporters.yaml_exporter import export_machine

lattice = LAURA(
    layout="../../laura-lattices/CLARA/layouts.yaml", 
    section="../../laura-lattices/CLARA/sections.yaml",
    element_list="../../laura-lattices/CLARA/YAML/summary.yaml",
)
print(lattice.lattices['CLARAFEBE'])

export_machine('examples/output', lattice, position_mode="reference")