"""Optional parity checks against the Bmad documentation lattices."""

import os
from pathlib import Path

import pytest
import numpy as np

pytest.importorskip("pytao")

from laura.translator.converters.codes.bmad import BmadLatticeImporter
from laura.translator.converters.codes import magnetic_orders


BMAD_DIST = Path(
    os.environ.get("BMAD_DIST", Path.home() / "Documents" / "bmad_dist")
).expanduser()
LIBTAO = Path(
    os.environ.get("LAURA_LIBTAO", BMAD_DIST / "production" / "lib" / "libtao.so")
).expanduser()
LATTICES = BMAD_DIST / "bmad-doc" / "lattices"

pytestmark = pytest.mark.skipif(
    not LIBTAO.exists() or not LATTICES.exists(),
    reason="Bmad documentation lattices and libtao are not installed",
)


@pytest.mark.parametrize(
    "relative_path, expected_elements",
    [
        ("small_ring/small_ring.bmad", 58),
        ("Dragt_PSR_small_ring/Dragt_PSR_small_ring.bmad", 36),
        ("jlab_ep_collider/original_e_ring.bmad", 754),
        ("jlab_ep_collider/original_p_ring.bmad", 496),
        ("jlab_fel/bates.bmad", 113),
    ],
)
def test_documentation_lattice_matches_tao_s_positions(relative_path, expected_elements):
    importer = BmadLatticeImporter(
        lattice_file=str(LATTICES / relative_path), libtao=str(LIBTAO)
    )
    imported_count = 0

    for universe, branches in importer.names_numbered.items():
        converted = importer.create_laura_element_dictionary(universe)
        imported_count += sum(len(elements) for elements in converted.values())

        for branch, names in branches.items():
            elements = converted[branch]
            for name, native_type, length, s_position, parameters in zip(
                names,
                importer.types[universe][branch],
                importer.lengths[universe][branch],
                importer.spos[universe][branch],
                importer.params[universe][branch],
            ):
                if name not in elements:
                    continue
                element = elements[name]
                assert element.name == name
                assert element.hardware_type != "Generic"
                assert element.physical.length == pytest.approx(length)
                assert element.physical.s == pytest.approx(s_position)
                assert element.physical.s_point == "end"
                if native_type in magnetic_orders:
                    order = magnetic_orders[native_type]
                    expected = (
                        parameters[f"K{order}"] * length
                        if f"K{order}" in parameters
                        else parameters["ANGLE"]
                    )
                    assert element.magnetic.KnL(order) == pytest.approx(expected)
                elif native_type == "Solenoid":
                    assert element.magnetic.ks == pytest.approx(
                        parameters["BS_FIELD"] * length
                    )
                elif native_type in ("Lcavity", "RFCavity"):
                    assert element.cavity.frequency == pytest.approx(
                        parameters["RF_FREQUENCY"]
                    )
                    assert element.simulation.field_amplitude == pytest.approx(
                        parameters["VOLTAGE"]
                    )

        layout = importer.create_layout(universe)
        assert set(layout.sections) == set(branches)
        for branch, names in branches.items():
            elements = converted[branch]
            for name, length, s_position in zip(
                names, importer.lengths[universe][branch], importer.spos[universe][branch]
            ):
                if name in elements:
                    assert elements[name].physical.s == pytest.approx(
                        s_position - length / 2
                    )
            assert layout.sections[branch].order == [
                name for name, element in elements.items() if not element.is_subelement()
            ]

    assert imported_count == expected_elements


def test_multiword_branch_name_is_resolved_by_index():
    """model_post_init used to pass Tao's ``ix_branch`` kwarg a *name* string
    derived from the branch label rather than its numeric index. Tao's own
    ``lat_list`` silently returns an empty list for a name it doesn't
    recognize as an index instead of raising, so any branch whose name
    wasn't itself a parseable integer (e.g. "DAVES_LINE") imported zero
    elements. Regression test for that fix, using a documentation lattice
    whose sole branch is named DAVES_LINE.
    """
    importer = BmadLatticeImporter(
        lattice_file=str(
            LATTICES / "rowland_circle_spectrometer" / "rowland_circle_spectrometer.bmad"
        ),
        libtao=str(LIBTAO),
    )
    branch = next(iter(importer.names[1]))
    assert branch == "DAVES_LINE_1"
    assert importer.names[1][branch] == [
        "BEGINNING",
        "SOURCE",
        "DRIFT1",
        "CRYST",
        "DRIFT2",
        "DET",
        "END",
    ]


def test_native_taylor_and_sol_quad_import(tmp_path):
    lattice = tmp_path / "maps.bmad"
    lattice.write_text(
        "parameter[particle] = electron\n"
        "parameter[p0c] = 10e6\n"
        "t: taylor, {1: 3 |}, {1: 1 |1}, {1: 2 |22}, {1: 6 |123}, "
        "{S1: 0.9 |}, {Sx: 0.1 |1}, "
        "{2: 1 |2}, {3: 1 |3}, {4: 1 |4}, {5: 1 |5}, {6: 1 |6}\n"
        "sq: sol_quad, l = 2, k1 = 0.3, ks = 0.4\n"
        "lat: line = (t, sq)\n"
        "use, lat\n"
    )
    importer = BmadLatticeImporter(lattice_file=str(lattice), libtao=str(LIBTAO))
    branch = next(iter(importer.names_numbered[1]))
    elements = importer.create_laura_element_dictionary(1)[branch]

    assert elements["T"].hardware_type == "MatrixTransform"
    assert elements["T"].simulation.c_matrix[0] == pytest.approx(3.0)
    assert elements["T"].simulation.r_matrix[0, 0] == pytest.approx(1.0)
    assert elements["T"].simulation.t_matrix[0, 1, 1] == pytest.approx(2.0)
    assert np.count_nonzero(elements["T"].simulation.t_matrix) == 1
    assert elements["T"].simulation.u_matrix[0, 0, 1, 2] == pytest.approx(1.0)
    assert np.count_nonzero(elements["T"].simulation.u_matrix) == 6
    assert elements["T"].simulation.spin_taylor[0]["index"] == 0
    assert elements["T"].simulation.spin_taylor[1]["index"] == 1
    assert elements["T"].simulation.spin_taylor[1]["exp1"] == 1

    sq = elements["SQ"]
    sq_index = importer.names_numbered[1][branch].index("SQ")
    assert sq.hardware_type == "CombinedSolenoidQuadrupole"
    assert sq.magnetic.KnL(1) == pytest.approx(0.6)
    assert sq.magnetic.ks == pytest.approx(
        importer.params[1][branch][sq_index]["BS_FIELD"] * 2
    )


def test_beginning_ele_imports_as_twiss_match(tmp_path):
    """Bmad always computes/propagates Twiss through a lattice starting from
    the BEGINNING element's values (explicit `beginning[...]` statements
    here; a ring's own closed periodic solution otherwise) -- the direct
    counterpart of Ocelot's separate `Twiss()` object and ELEGANT's native
    TWISS element. It used to be silently dropped alongside Drift/Pipe."""
    lattice = tmp_path / "twiss.bmad"
    lattice.write_text(
        "parameter[particle] = electron\n"
        "parameter[p0c] = 10e6\n"
        "parameter[geometry] = open\n"
        "beginning[beta_a] = 9.42\n"
        "beginning[alpha_a] = -0.66\n"
        "beginning[beta_b] = 22.19\n"
        "beginning[alpha_b] = 1.51\n"
        "beginning[eta_x] = 0.1\n"
        "beginning[etap_x] = 0.01\n"
        "beginning[eta_y] = 0.2\n"
        "beginning[etap_y] = 0.02\n"
        "d1: drift, l = 1.0\n"
        "lat: line = (d1)\n"
        "use, lat\n"
    )
    importer = BmadLatticeImporter(lattice_file=str(lattice), libtao=str(LIBTAO))
    branch = next(iter(importer.names_numbered[1]))
    elements = importer.create_laura_element_dictionary(1)[branch]

    twiss = elements["BEGINNING"]
    assert twiss.hardware_type == "TwissMatch"
    assert twiss.physical.s == pytest.approx(0.0)
    assert twiss.physical.length == pytest.approx(0.0)
    assert twiss.simulation.beta_x == pytest.approx(9.42)
    assert twiss.simulation.beta_y == pytest.approx(22.19)
    assert twiss.simulation.alpha_x == pytest.approx(-0.66)
    assert twiss.simulation.alpha_y == pytest.approx(1.51)
    assert twiss.simulation.eta_x == pytest.approx(0.1)
    assert twiss.simulation.eta_y == pytest.approx(0.2)
    assert twiss.simulation.eta_xp == pytest.approx(0.01)
    assert twiss.simulation.eta_yp == pytest.approx(0.02)
    assert twiss.simulation.from_beam is False
    assert next(iter(elements)) == "BEGINNING"


def test_spin_single_resonance_terms_are_preserved():
    importer = BmadLatticeImporter(
        lattice_file=str(
            LATTICES / "spin_single_resonance_model" / "spin_single_res.bmad"
        ),
        libtao=str(LIBTAO),
    )
    branch = next(iter(importer.names_numbered[1]))
    elements = importer.create_laura_element_dictionary(1)[branch]
    spin_elements = [
        element for name, element in elements.items() if name.startswith("ELE1.")
    ]

    assert len(spin_elements) == 1000
    assert [term["index"] for term in spin_elements[0].simulation.spin_taylor] == [
        0,
        1,
        2,
        2,
        3,
    ]


def test_kicker_subelements_inherit_resolved_s_position(tmp_path):
    lattice = tmp_path / "kicker.bmad"
    lattice.write_text(
        "parameter[particle] = electron\n"
        "parameter[p0c] = 10e6\n"
        "d: drift, l = 1\n"
        "k: kicker, l = 0.5, hkick = 0.01, vkick = 0.02\n"
        "lat: line = (d, k)\n"
        "use, lat\n"
    )
    importer = BmadLatticeImporter(lattice_file=str(lattice), libtao=str(LIBTAO))
    branch = next(iter(importer.names_numbered[1]))
    elements = importer.create_section(1, branch)[branch].elements.elements

    parent = elements["K"]
    horizontal = elements["K_H"]
    vertical = elements["K_V"]

    assert parent.physical.s_point == "middle"
    assert parent.physical.s == pytest.approx(1.25)
    for sub in (horizontal, vertical):
        assert sub.is_subelement()
        assert sub.physical.s_point == parent.physical.s_point
        assert sub.physical.s == pytest.approx(parent.physical.s)


def test_match_matrix_reproduces_declared_exit_twiss(tmp_path):
    lattice = tmp_path / "match.bmad"
    lattice.write_text(
        "parameter[particle] = electron\n"
        "parameter[p0c] = 10e6\n"
        "m: match, l = 2, beta_a0 = 4, alpha_a0 = 1, "
        "beta_a1 = 9, alpha_a1 = -0.5, beta_b0 = 5, alpha_b0 = -0.2, "
        "beta_b1 = 7, alpha_b1 = 0.3, dphi_a = 0.4, dphi_b = 0.2\n"
        "lat: line = (m)\n"
        "use, lat\n"
    )
    importer = BmadLatticeImporter(lattice_file=str(lattice), libtao=str(LIBTAO))
    branch = next(iter(importer.names_numbered[1]))
    match = importer.create_laura_element_dictionary(1)[branch]["M"]

    def exit_twiss(beta, alpha, matrix):
        sigma = np.array(
            [[beta, -alpha], [-alpha, (1 + alpha**2) / beta]]
        )
        sigma = matrix @ sigma @ matrix.T
        return sigma[0, 0], -sigma[0, 1]

    assert match.hardware_type == "MatrixTransform"
    assert match.physical.length == pytest.approx(2.0)
    assert exit_twiss(4, 1, match.simulation.r_matrix[:2, :2]) == pytest.approx(
        (9, -0.5)
    )
    assert exit_twiss(5, -0.2, match.simulation.r_matrix[2:4, 2:4]) == pytest.approx(
        (7, 0.3)
    )
