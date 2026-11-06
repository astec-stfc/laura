"""A sequentially-placed multipass path, as tracking codes need it placed.

The linac is shared hardware: what follows its second pass starts from its
exit (not from whatever preceded that pass), and s-lookups along the path
take the pass-qualified names (``NAME#N``) the path hands out.
"""

import pytest

from laura import LAURA
from unit_tests.helpers import quad, quiet

SECTIONS = {"INJ": ["INJ_Q"], "LINAC": ["LIN_Q"], "ARC": ["ARC_Q"], "DUMP": ["DMP_Q"]}
ERL = ["INJ", {"LINAC": {"multipass": 1}}, "ARC", {"LINAC": {"multipass": 2}}, "DUMP"]


def machine():
    with quiet():
        return LAURA(
            element_list=[quad(n, 0.4, 1.0, machine_area="A") for n in ("INJ_Q", "LIN_Q", "ARC_Q", "DMP_Q")],
            section={"sections": SECTIONS},
            layout={"layouts": {"ERL": ERL}, "default_layout": "ERL"},
        )


def test_what_follows_a_later_pass_starts_at_the_shared_sections_exit():
    m = machine()
    assert m.elements["DMP_Q"].physical.start.z == pytest.approx(m.elements["LIN_Q"].physical.end.z)


def test_a_pass_copy_carries_that_passs_arc_length():
    m = machine()
    layout = m.lattices["ERL"]
    arc = layout.arc_lengths()
    assert layout.element_on_pass("LIN_Q#2").physical.s == pytest.approx(arc["LIN_Q#2"] + 0.2)
    assert layout.element_on_pass("LIN_Q#1").physical.s == pytest.approx(m.elements["LIN_Q"].physical.s)
    # the device has not moved
    assert layout.element_on_pass("LIN_Q#2").physical.start.z == pytest.approx(m.elements["LIN_Q"].physical.start.z)


def test_s_positions_take_pass_qualified_names():
    s = machine().get_elements_s_pos(end="DMP_Q")
    assert {"LIN_Q#1", "LIN_Q#2", "DMP_Q"} <= set(s)
