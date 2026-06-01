import sys
import os

sys.path.append(r"C:\Users\jkj62.CLRC\Documents\GitHub\laura")
from laura.laura import LAURA
import laura
laura.set_log_level("DEBUG")

lattice = LAURA(
    layout="../../laura-lattices/CLARA/layouts.yaml", 
    section="../../laura-lattices/CLARA/sections.yaml",
    element_list="../../laura-lattices/CLARA/YAML/summary.yaml",
)
print(lattice.all_dipoles)