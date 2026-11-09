"""One meaning for each collective switch, whichever code it is written for."""

import pytest

from laura.models.element import Dipole, Quadrupole
from laura.models.element_list import ElementList, SectionLattice
from laura.translator.converters.codes.astra import AstraCharge
from laura.translator.converters.codes.gpt import GptSpaceCharge
from laura.translator.converters.codes.opal import OpalFieldSolver
from laura.translator.utils.functions import space_charge_dimension

OFF = [None, False, "", "False", "None", "off", "OFF", "0", "no"]


@pytest.mark.parametrize("mode", OFF)
def test_off_is_off_in_every_code(mode):
    """laura#56: ASTRA took "off" for 3D space charge."""
    assert space_charge_dimension(mode) == ""
    text = mode if isinstance(mode, str) else str(mode)  # the converters' fields are strings
    assert GptSpaceCharge(space_charge_mode=text).write_gpt() == ""
    astra = AstraCharge(space_charge_mode=text).write_astra()
    assert "LSPCH = F" in astra and "LSPCH3D = F" in astra
    assert OpalFieldSolver(npart=32768, space_charge_mode=text).FSTYPE == "NONE"


@pytest.mark.parametrize("mode, lspch3d, grid", [("2D", "F", "nrad"), ("3d", "T", "nxf")])
def test_astra_solver(mode, lspch3d, grid):
    """LSPCH turns space charge on at all; LSPCH3D picks the FFT solver (ASTRA manual)."""
    text = AstraCharge(space_charge_mode=mode).write_astra()
    assert "LSPCH = T" in text
    assert f"LSPCH3D = {lspch3d}" in text
    assert f"{grid} = " in text


@pytest.mark.parametrize("mode", ["3", "cylindrical", True])
def test_an_unknown_mode_is_an_error(mode):
    with pytest.raises(ValueError, match="space_charge_mode"):
        space_charge_dimension(mode)
    with pytest.raises(ValueError, match="space_charge_mode"):
        AstraCharge(space_charge_mode=str(mode)).write_astra()


def _section(csr_on_bend):
    bend = Dipole(name="B1", machine_area="S", physical={"s": 1.0, "length": 0.5})
    bend.simulation.csr_enable = csr_on_bend
    quad = Quadrupole(name="Q1", machine_area="S", physical={"s": 2.0, "length": 0.1})
    registry = {e.name: e for e in (bend, quad)}
    return SectionLattice(name="S", order=list(registry), elements=ElementList(elements=registry))


@pytest.mark.parametrize("csr_on_bend", [True, False])
def test_the_bends_decide_csr_for_synthesised_drifts(csr_on_bend):
    """The quadrupole keeps LAURA's default (on); only the bend's setting counts."""
    assert _section(csr_on_bend)._collective_default("csr_enable") is csr_on_bend
