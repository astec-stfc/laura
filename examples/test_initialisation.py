import sys
import os

sys.path.append(r"C:\Users\jkj62.CLRC\Documents\GitHub\laura")
from laura.laura import LAURA

lattice = LAURA(
    layout="../../laura-lattices/CLARA/layouts.yaml",
    section="../../laura-lattices/CLARA/sections.yaml",
    element_list="../../laura-lattices/CLARA/YAML/summary.json",
)
print(lattice)
