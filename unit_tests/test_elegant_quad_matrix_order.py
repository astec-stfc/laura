"""A quadrupole's multipole order is not elegant's matrix order.

LAURA's ``magnetic.order`` is the multipole order -- 1 for a quadrupole --
and elegant's ``QUAD`` has an ``ORDER`` keyword too, meaning the order of
its transfer matrix. The names matched, so every quadrupole went out as
``ORDER=1``: a first-order matrix, which has no chromatic terms at all. A
FODO cell then had dnux/dp = 0 in elegant instead of -0.526 (measured), and
any off-momentum particle was focused as if it were on momentum.
"""

import shutil
import subprocess

import pytest

from laura.models.element import Quadrupole
from laura.translator.converters.converter import translate_elements

ELEGANT = shutil.which("elegant")
SDDSPRINTOUT = shutil.which("sddsprintout")


def _quad(name, k1l, middle):
    return Quadrupole(
        name=name, machine_area="A",
        magnetic={"length": 1.0, "k1l": k1l},
        physical={"length": 1.0, "middle": {"x": 0.0, "y": 0.0, "z": middle}},
    )


def _exported_cell():
    """A FODO cell whose quadrupoles are LAURA's own elegant export."""
    quads = translate_elements([_quad("QF", -1.0, 0.75), _quad("QD", 1.0, 3.25)])
    return "\n".join(
        [
            quads["QF"].to_elegant().strip(),
            quads["QD"].to_elegant().strip(),
            "D1: DRIFT, L=0.25",
            "D2: DRIFT, L=1.5",
            "D3: DRIFT, L=0.5",
            "CELL: LINE=(D1,QF,D2,QD,D3)",
            "",
        ]
    )


def test_the_multipole_order_is_not_written_as_a_matrix_order():
    """No ``ORDER`` on the QUAD, so the run's ``default_order`` applies."""
    for line in _exported_cell().splitlines()[:2]:
        keywords = {
            term.split("=")[0].strip().lower()
            for term in line.replace("&", "").split(",")[1:]
        }
        assert "order" not in keywords, line


@pytest.mark.skipif(
    ELEGANT is None or SDDSPRINTOUT is None, reason="elegant is not installed"
)
def test_an_exported_fodo_cell_has_its_chromaticity(tmp_path):
    """The property that was lost: elegant's own chromaticity for the cell."""
    (tmp_path / "cell.lte").write_text(_exported_cell())
    (tmp_path / "cell.ele").write_text(
        '&run_setup lattice="cell.lte", use_beamline="CELL", '
        "p_central_mev=5.0, default_order=3 &end\n"
        '&twiss_output filename="%s.twi", matched=1 &end\n'
        "&run_control &end\n&bunched_beam &end\n&track &end\n"
    )
    subprocess.run(
        [ELEGANT, "cell.ele"], cwd=tmp_path, check=True, capture_output=True
    )
    values = {}
    for parameter in ("nux", "dnux/dp"):
        out = subprocess.run(
            [SDDSPRINTOUT, "cell.twi", f"-parameter={parameter}", "-noTitle"],
            cwd=tmp_path, check=True, capture_output=True, text=True,
        ).stdout
        values[parameter] = float(out.split("=")[-1])
    # guards the comparison: an unstable cell would have no tune to talk about
    assert values["nux"] == pytest.approx(0.3277, abs=1e-3)
    assert values["dnux/dp"] == pytest.approx(-0.5257, abs=1e-3)
