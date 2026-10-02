"""Name helpers shared by the model layer and the importers.

The reverse-direction importers when a source
lattice reuses an element name, and sequential (drift-based) placement when a
hand-written section order does the same.
"""

from collections import Counter as OccurrenceCounter


def number_repeated_names(names: list[str]) -> list[str]:
    """Append ``.n`` only to names that occur more than once."""
    keys = [name.lower() for name in names]
    totals = OccurrenceCounter(keys)
    seen = OccurrenceCounter()
    numbered = []
    for name, key in zip(names, keys):
        seen[key] += 1
        numbered.append(f"{name}.{seen[key]}" if totals[key] > 1 else name)
    return numbered
