"""A bend's edge order reaches every code the same way: second order unless
the lattice asks for first, so no code falls back on its own default."""

import pytest

from laura.models.element import Dipole
from laura.translator.converters.converter import translate_elements


def bend(edge_order=None):
    element = Dipole(
        name="B1", machine_area="A", physical={"length": 1.3},
        magnetic={"magnetic_length": 1.3, "k0l": 0.11, "k1l": -0.9,
                  "entrance_edge_angle": 0.055, "exit_edge_angle": 0.055},
        simulation={"edge_order": edge_order},
    )
    return translate_elements([element])["B1"]


@pytest.mark.parametrize("edge_order, order, xsuite, bmad", [
    (None, 2, "full", None),  # unset: second order, Bmad's own basic_bend
    (2, 2, "full", None),
    (1, 1, "linear", "fringe_type = linear_edge"),
])
def test_every_code_gets_the_same_edge_order(edge_order, order, xsuite, bmad):
    elegant = bend(edge_order).to_elegant()
    assert f"edge_order = {order}" in elegant
    # second order through ELEGANT's symplectic edge method
    assert ("edge1_effects = 3" in elegant and "edge2_effects = 3" in elegant) is (order == 2)
    _, _, properties = bend(edge_order).to_xsuite(beam_length=1)
    assert properties["edge_entry_model"] == properties["edge_exit_model"] == xsuite
    written = bend(edge_order).to_bmad().lower()
    assert ("fringe_type" in written) is (bmad is not None)
    if bmad:
        assert bmad in written


def test_codes_that_cannot_drop_the_second_order_terms_say_so():
    with pytest.warns(UserWarning, match="MAD-X always models"):
        bend(1).to_madx()
