"""A bend at the default kick count gets enough steps for its angle and gradient.

ELEGANT's ``CSBEND`` misses its reference by ~0.3 θ (θ/N)⁴ and, with a ``K1``,
lengthens its on-axis path by ~0.09 |k1| L² θ² / N⁴.
"""

import re
import shutil
import subprocess

import pytest

from laura.models.element import Dipole
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.magnet import BEND_ANGLE_PER_KICK, BEND_PATH_ERROR

ELEGANT = shutil.which("elegant")

CLIC_DR_DIPOLE = dict(angle=0.0314, length=0.29, k1l=-1.1 * 0.29)
"""Half of a CLIC DR arc dipole: 0.29 m, k1 = -1.1."""


def bend(angle, length=1.0, k1l=0.0, **simulation):
    element = Dipole(
        name="B1", machine_area="A", physical={"length": length},
        magnetic={"length": length, "k0l": angle, "k1l": k1l},
        simulation={"csr_enable": False, "sr_enable": False,
                    "isr_enable": False, **simulation},
    )
    return translate_elements([element])["B1"]


def slices(angle, **parameters):
    written = bend(angle, **parameters).to_elegant()
    return int(re.search(r"n_slices = (\d+)", written).group(1))


def track(tmp_path, element, run_setup=""):
    (tmp_path / "bend.lte").write_text(
        element.to_elegant()
        + 'W: WATCH, FILENAME="w.sdds", MODE=coordinate\n'
        "L1: LINE=(B1,W)\n"
    )
    (tmp_path / "run.ele").write_text(
        '&run_setup lattice = "bend.lte", use_beamline = L1, '
        f"p_central_mev = 1000{run_setup} &end\n"
        "&run_control &end\n"
        "&bunched_beam n_particles_per_bunch = 1 &end\n"
        "&track &end\n"
    )
    subprocess.run(
        [ELEGANT, "run.ele"], cwd=tmp_path, check=True, capture_output=True
    )


def columns(tmp_path, filename, names):
    read = subprocess.run(
        ["sdds2stream", f"-col={','.join(names)}", filename],
        cwd=tmp_path, check=True, capture_output=True, text=True,
    )
    return [[float(value) for value in row.split()]
            for row in read.stdout.strip().splitlines()]


@pytest.mark.parametrize("angle, expected", [
    (0.0, 4),
    (0.02, 4),  # small bends keep the schema default
    (0.17, 17),
    (0.785, 79),
    (-0.785, 79),  # the sign bends the other way, not less
])
def test_an_unset_count_scales_with_the_angle(angle, expected):
    assert slices(angle) == expected


@pytest.mark.parametrize("k1l, expected", [
    (-1.1 * 0.29, 18),
    (1.1 * 0.29, 18),  # either sign of gradient
    (0.0, 4),  # the angle alone needs only the default
])
def test_an_unset_count_scales_with_the_gradient(k1l, expected):
    assert slices(**{**CLIC_DR_DIPOLE, "k1l": k1l}) == expected


def test_a_straight_gradient_magnet_needs_no_more_kicks():
    """The path error goes with θ²: no angle, no error."""
    assert slices(0.0, k1l=5.0) == 4


@pytest.mark.parametrize("n_kicks", [4, 200])
def test_an_explicit_count_is_kept(n_kicks):
    assert slices(0.785, n_kicks=n_kicks) == n_kicks
    assert slices(**CLIC_DR_DIPOLE, n_kicks=n_kicks) == n_kicks


def test_no_step_turns_through_more_than_the_limit():
    angle = 0.785
    assert angle / slices(angle) <= BEND_ANGLE_PER_KICK


def test_bmad_still_takes_only_an_explicit_count():
    """Bmad's writer skips ``n_kicks`` unless the lattice set it; the scaled
    count is ELEGANT's integrator's need, not Bmad's."""
    assert "num_steps" not in bend(0.785).to_bmad().lower()
    assert "num_steps" not in bend(**CLIC_DR_DIPOLE).to_bmad().lower()


@pytest.mark.skipif(ELEGANT is None, reason="elegant is not installed")
def test_elegant_keeps_a_strong_bend_on_its_reference(tmp_path):
    track(tmp_path, bend(0.785))
    [[x, xp]] = columns(tmp_path, "w.sdds", ["x", "xp"])
    assert abs(xp) < 1e-8
    assert abs(x) < 1e-8


@pytest.mark.skipif(ELEGANT is None, reason="elegant is not installed")
@pytest.mark.parametrize("parameters", [
    CLIC_DR_DIPOLE,
    dict(angle=0.05, length=0.5, k1l=1.0),
    dict(angle=0.2, length=1.0, k1l=0.5),
])
def test_elegant_keeps_a_gradient_bend_to_its_length(tmp_path, parameters):
    track(tmp_path, bend(**parameters), run_setup=', centroid = "c.sdds"')
    s, path = columns(tmp_path, "c.sdds", ["s", "Cs"])[-1]
    assert abs(path - s) / parameters["length"] <= BEND_PATH_ERROR
