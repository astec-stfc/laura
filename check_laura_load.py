import sys
import time

# List of modules to check
modules_to_check = ['scipy', 'scipy.constants', 'scipy.stats', 'scipy.spatial']

# Set sys.path to include laura
sys.path.append(r'C:\Users\jkj62.CLRC\Documents\GitHub\laura')

start_time = time.time()
from laura.laura import LAURA
end_time = time.time()

print(f"Importing laura.LAURA took {end_time - start_time:.4f} seconds.")

for mod in modules_to_check:
    if mod in sys.modules:
        print(f"{mod} was loaded!")
    else:
        print(f"{mod} was NOT loaded.")

# Check how many laura modules were loaded
laura_modules = [m for m in sys.modules if m.startswith('laura')]
print(f"Loaded laura modules: {len(laura_modules)}")
