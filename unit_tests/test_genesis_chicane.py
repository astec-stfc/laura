"""A Genesis chicane replaces its dipoles and inner drifts, with delay = R56/2, and
the HGHG split lines share the full line's labels."""

from laura.models.element import Dipole, Marker, Wiggler
from laura.models.element_list import ElementList, SectionLattice
from laura.translator.converters.section import SectionLatticeTranslator


def test_chicane_and_split():
    und = {"length": 1.0, "period": 0.1, "num_periods": 10, "strength": 2.0}
    elements = [
        Wiggler(name="MOD", machine_area="S", physical={"s": 0.0, "length": 1.0}, magnetic=und),
        *[
            Dipole(name=f"D{i}", machine_area="S", physical={"s": 1.5 + 0.5 * i, "length": 0.2},
                   magnetic={"length": 0.2, "angle": a})
            for i, a in enumerate([0.01, -0.01, -0.01, 0.01])
        ],
        Marker(name="SPLIT", machine_area="S", hardware_class="Marker", physical={"s": 3.6}),
        Wiggler(name="RAD", machine_area="S", physical={"s": 4.0, "length": 1.0}, magnetic=und),
    ]
    registry = {e.name: e for e in elements}
    lattice = SectionLattice(name="FEL", order=list(registry), elements=ElementList(elements=registry))
    lattice.resolve_positions(lattice.elements.elements)
    chicane = {"start": "D0", "end": "D3", "r56": 1e-4, "dipole_length": 0.2, "drift_length": 0.3, "length": 1.7}
    lat = SectionLatticeTranslator.from_section(lattice).to_genesis(split_element="SPLIT", chicanes={"CH": chicane})
    assert "CHICANE = {l = 1.7, delay = 5e-05, lb = 0.2, ld = 0.3}" in lat
    assert not any(f"D{i}:" in lat for i in (1, 2, 3))
    full, first, second = (line.split("{")[1].rstrip("};").split(", ") for line in lat.splitlines()[-3:])
    assert first + second == full and second[0].endswith("SPLIT")
