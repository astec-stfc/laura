"""A bend left at the default kick count gets enough steps for its angle.

ELEGANT's ``CSBEND`` misses its own reference by ~0.3 θ (θ/N)⁴: at the old
fixed four, a 45-degree bend put a millimetre of closed orbit round a ring.
"""

import re
import shutil
import subprocess

import pytest

from laura.models.element import Dipole
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.magnet import BEND_ANGLE_PER_KICK

ELEGANT = shutil.which("elegant")


def bend(angle, **simulation):
    element = Dipole(
        name="B1", machine_area="A", physical={"length": 1.0},
        magnetic={"length": 1.0, "k0l": angle},
        simulation={"csr_enable": False, "sr_enable": False,
                    "isr_enable": False, **simulation},
    )
    return translate_elements([element])["B1"]


def slices(angle, **simulation):
    written = bend(angle, **simulation).to_elegant()
    return int(re.search(r"n_slices = (\d+)", written).group(1))


@pytest.mark.parametrize("angle, expected", [
    (0.0, 4),
    (0.02, 4),  # small bends keep the schema default
    (0.17, 17),
    (0.785, 79),
    (-0.785, 79),  # the sign bends the other way, not less
])
def test_an_unset_count_scales_with_the_angle(angle, expected):
    assert slices(angle) == expected


@pytest.mark.parametrize("n_kicks", [4, 200])
def test_an_explicit_count_is_kept(n_kicks):
    assert slices(0.785, n_kicks=n_kicks) == n_kicks


def test_no_step_turns_through_more_than_the_limit():
    angle = 0.785
    assert angle / slices(angle) <= BEND_ANGLE_PER_KICK


def test_bmad_still_takes_only_an_explicit_count():
    """Bmad's writer skips ``n_kicks`` unless the lattice set it; the scaled
    count is ELEGANT's integrator's need, not Bmad's."""
    assert "num_steps" not in bend(0.785).to_bmad().lower()


@pytest.mark.skipif(ELEGANT is None, reason="elegant is not installed")
def test_elegant_keeps_a_strong_bend_on_its_reference(tmp_path):
    """An on-axis particle through LAURA's own 45-degree bend leaves on axis.
    At four kicks it left 3.3e-4 rad off."""
    (tmp_path / "bend.lte").write_text(
        bend(0.785).to_elegant()
        + 'W: WATCH, FILENAME="w.sdds", MODE=coordinate\n'
        "L1: LINE=(B1,W)\n"
    )
    (tmp_path / "run.ele").write_text(
        '&run_setup lattice = "bend.lte", use_beamline = L1, '
        "p_central_mev = 1000 &end\n"
        "&run_control &end\n"
        "&bunched_beam n_particles_per_bunch = 1 &end\n"
        "&track &end\n"
    )
    subprocess.run(
        [ELEGANT, "run.ele"], cwd=tmp_path, check=True, capture_output=True
    )
    read = subprocess.run(
        ["sdds2stream", "-col=x,xp", "w.sdds"],
        cwd=tmp_path, check=True, capture_output=True, text=True,
    )
    x, xp = (float(value) for value in read.stdout.split())
    assert abs(xp) < 1e-8
    assert abs(x) < 1e-8
