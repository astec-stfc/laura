"""Optional parity checks against the Bmad documentation lattices."""

import math
import os
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pytao")

from laura.translator.converters.codes import magnetic_orders
from laura.translator.converters.codes.bmad import BmadLatticeImporter

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
def test_documentation_lattice_matches_tao_s_positions(
    relative_path, expected_elements
):
    importer = BmadLatticeImporter(
        lattice_file=str(LATTICES / relative_path),
        libtao=str(LIBTAO),
        position_mode="s",
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
                names,
                importer.lengths[universe][branch],
                importer.spos[universe][branch],
            ):
                if name in elements:
                    assert elements[name].physical.s == pytest.approx(
                        s_position - length / 2
                    )
            assert layout.sections[branch].order == [
                name
                for name, element in elements.items()
                if not element.is_subelement()
            ]

    assert imported_count == expected_elements


@pytest.mark.parametrize(
    "relative_path",
    ["small_ring/small_ring.bmad", "jlab_fel/bates.bmad"],
)
def test_floor_position_mode_matches_tao_floor_coordinates(relative_path):
    """Parity check on *global geometry*, which nothing else covers.

    The two **faces** are checked as well as the centre, and that is the point:
    ``middle`` comes straight from Tao and so cannot be wrong, while
    ``start``/``end`` are reconstructed by LAURA from the length, the bend angle
    and the orientation.
    """
    from pytao import Tao

    importer = BmadLatticeImporter(
        lattice_file=str(LATTICES / relative_path),
        libtao=str(LIBTAO),
        position_mode="floor",
    )
    tao = Tao(
        lattice_file=str(LATTICES / relative_path), so_lib=str(LIBTAO), noplot=True
    )

    checked = 0
    for universe, branches in importer.branches.items():
        for branch_index, branch in enumerate(branches):
            section = importer.create_section(universe, branch)[branch]
            elements = section.elements.elements
            names = importer.names_numbered[universe][branch]
            lengths = importer.lengths[universe][branch]
            spos = importer.spos[universe][branch]
            for index, name in enumerate(names):
                element = elements.get(name)
                if element is None or element.physical.middle is None:
                    continue
                for where, attribute in (
                    ("beginning", "start"),
                    ("center", "middle"),
                    ("end", "end"),
                ):
                    reference = tao.ele_floor(
                        f"{universe}@{branch_index}>>{index}", where=where
                    )["Reference"]
                    face = getattr(element.physical, attribute)
                    assert face.x == pytest.approx(reference[0], abs=1e-9)
                    assert face.y == pytest.approx(reference[1], abs=1e-9)
                    assert face.z == pytest.approx(reference[2], abs=1e-9)
                # Bmad's arc-length must survive the floor-mode resolve.
                assert element.physical.s == pytest.approx(
                    spos[index] - lengths[index] / 2.0, abs=1e-9
                )
                checked += 1

    assert checked > 0


def test_multiword_branch_name_is_resolved_by_index():
    """model_post_init used to pass Tao's ``ix_branch`` kwarg a *name* string
    derived from the branch label rather than its numeric index. Tao's own
    ``lat_list`` silently returns an empty list for a name it doesn't
    recognize as an index instead of raising.
    """
    importer = BmadLatticeImporter(
        lattice_file=str(
            LATTICES
            / "rowland_circle_spectrometer"
            / "rowland_circle_spectrometer.bmad"
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
    assert twiss.physical.middle.z == pytest.approx(0.0)
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
        sigma = np.array([[beta, -alpha], [-alpha, (1 + alpha**2) / beta]])
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


def test_bmad_bend_geometry_is_the_negation_of_its_magnetic_angle():
    """LAURA bends toward +x for a positive angle, Bmad toward -x, so the
    *geometric* angle an imported bend carries is the negation of the strength
    it stores. Only the geometry flips: ``magnetic.KnL(0)`` keeps Bmad's own
    sign, which is what makes the angle export back out unchanged.

    ``physical_angle`` is the field that carries this, and it only works because
    ``_physical_angle`` prefers an explicitly-set value over re-deriving one
    from the magnetic model; ``codes/elegant.py`` relies on the same thing.

    A ``ref_tilt`` of half a turn flips the geometry back the other way, and is
    recorded as that sign rather than as a roll -- see
    :func:`test_bmad_ref_tilt_is_imported_and_turns_the_bend_the_other_way`.
    """
    importer = BmadLatticeImporter(
        lattice_file=str(LATTICES / "jlab_fel" / "bates.bmad"),
        libtao=str(LIBTAO),
        position_mode="floor",
    )
    branch = importer.branches[1][0]
    section = importer.create_section(1, branch)[branch]

    bends = [
        element
        for element in section.elements.elements.values()
        if element.hardware_type == "Dipole" and element.physical.length > 0
    ]
    assert bends, "bates is made of bends; the filter is wrong if this is empty"
    rolled = 0
    for bend in bends:
        angle = bend.magnetic.KnL(0)
        assert angle  # a zero angle would make the assertion below vacuous
        half_turn = abs(math.remainder(bend.magnetic.tilt or 0.0, 2 * math.pi)) > 1e-12
        rolled += half_turn
        expected = angle if half_turn else -angle
        assert bend.physical._physical_angle == pytest.approx(expected)
    assert rolled, "bates has ref_tilt = pi bends; the half-turn branch is untested"


def test_bmad_ref_tilt_is_imported_and_turns_the_bend_the_other_way():
    """``ref_tilt`` rolls the reference frame with the magnet, which is what
    makes a bend turn the opposite way; plain ``tilt`` rolls only the magnet
    inside an unchanged frame.

    Bmad reports the *frame* unrolled, putting the rolled bend plane into the
    curvature instead, so the roll also has to be added to the floor
    orientation or the arc bows the wrong way. Both halves are checked here.
    """
    importer = BmadLatticeImporter(
        lattice_file=str(LATTICES / "jlab_fel" / "bates.bmad"),
        libtao=str(LIBTAO),
        position_mode="floor",
    )
    branch = importer.branches[1][0]
    section = importer.create_section(1, branch)[branch]
    elements = section.elements.elements

    plain, rolled = elements["B11B.1"], elements["B12B.1"]
    assert plain.magnetic.tilt == pytest.approx(0.0)
    assert rolled.magnetic.tilt == pytest.approx(math.pi)
    assert rolled.magnetic.KnL(0) == pytest.approx(plain.magnetic.KnL(0))

    turns = []
    for element in (plain, rolled):
        physical = element.physical
        direction = physical.rotation_matrix @ np.array([0.0, 0.0, 1.0])
        chord = np.array(physical.end.array) - np.array(physical.start.array)
        turns.append(float(np.cross(direction, chord)[1]))
    assert abs(turns[0]) > 1e-6
    assert turns[0] == pytest.approx(-turns[1])


@pytest.mark.parametrize(
    "lattice",
    [
        "small_ring/small_ring.bmad",
        "jlab_fel/bates.bmad",
        "jlab_ep_collider/original_e_ring.bmad",
    ],
)
def test_floor_mode_reproduces_taos_exit_frame_as_well_as_its_entrance(lattice):
    """Both faces of every element carry Tao's own surveyed orientation.

    The entrance frame has to match because that is what the importer is handed;
    the *exit* frame has to match because nothing hands it over -- LAURA derives
    it from the entrance frame and the element's own geometry.

    This is the precondition for ``section.to_bmad()`` synthesising ``patch``
    elements: a patch is the transform from one element's exit frame to the
    next one's entrance frame, so an exit frame that is a half turn out -- which
    is what carrying ``ref_tilt = pi`` as a roll did -- invents patches that are
    not there.
    """
    from pytao import Tao

    from laura.translator.utils.bmad import bmad_floor_rotation_matrix

    importer = BmadLatticeImporter(
        lattice_file=str(LATTICES / lattice),
        libtao=str(LIBTAO),
        position_mode="floor",
    )
    branch = importer.branches[1][0]
    section = importer.create_section(1, branch)[branch]
    tao = Tao(lattice_file=str(LATTICES / lattice), so_lib=str(LIBTAO), noplot=True)
    tracked = tao.lat_branch_list(ix_uni=1)[0]["n_ele_track"]

    named = [
        (index, tao.ele_head(f"1@0>>{index}")["name"]) for index in range(tracked + 1)
    ]
    kept = {name.split(".")[0] for name in section.order}
    named = [(index, name) for index, name in named if name in kept]
    assert len(named) == len(section.order)

    checked = 0
    for (index, _), name in zip(named, section.order):
        physical = section.elements.elements[name].physical
        if physical.middle is None:
            continue
        for where, attribute in (
            ("beginning", "rotation_matrix"),
            ("end", "end_rotation_matrix"),
        ):
            reference = tao.ele_floor(f"1@0>>{index}", where=where)["Reference"]
            expected = bmad_floor_rotation_matrix(
                *(float(value) for value in reference[3:6])
            )
            assert np.abs(getattr(physical, attribute) - expected).max() < 1e-12
        checked += 1
    assert checked > 10


def test_bmad_floor_elevation_has_the_sign_that_points_the_line_upward(tmp_path):
    """Bmad's floor ``W`` is ``Ry(theta) Rx(-phi) Rz(psi)``, not ``Rx(+phi)``.

    A positive ``phi`` means the reference line points *up*, and a right-handed
    rotation about +x tips it down -- hence the minus. Nothing in a flat machine
    can tell the two apart, ``phi`` being zero the whole way round, so all five
    documentation lattices agreed under either sign.
    """
    from pytao import Tao

    from laura.translator.utils.bmad import bmad_floor_rotation_matrix

    source = tmp_path / "elevation.bmad"
    source.write_text(
        "beginning[e_tot] = 1e9\n"
        "parameter[geometry] = open\n"
        "P: patch, y_pitch = 0.2, tilt = 0.35\n"
        "B: sbend, l = 1.0, angle = 0.3\n"
        "L: line = (P, B)\n"
        "use, L\n"
    )
    tao = Tao(lattice_file=str(source), so_lib=str(LIBTAO), noplot=True)
    frames = [
        bmad_floor_rotation_matrix(
            *(
                float(value)
                for value in tao.ele_floor("1@0>>2", where=where)["Reference"][3:6]
            )
        )
        for where in ("beginning", "end")
    ]
    relative = frames[0].T @ frames[1]

    turn = math.acos(max(-1.0, min(1.0, (np.trace(relative) - 1.0) / 2.0)))
    assert turn == pytest.approx(0.3, abs=1e-9)

    cosine, sine = math.cos(-0.3), math.sin(-0.3)
    expected = np.array([[cosine, 0, sine], [0, 1, 0], [-sine, 0, cosine]])
    assert np.abs(relative - expected).max() < 1e-12


def test_bmad_export_rebuilds_a_patch_from_the_reference_geometry(tmp_path):
    """A Bmad ``patch`` survives the round trip even though LAURA has no patch.

    Nothing imports a patch as an element -- it is a frame transform, and LAURA's
    model has no place to put one. Floor mode does record its *effect*, because
    every element downstream is placed at Tao's surveyed coordinates, but
    ``createDrifts()`` then reduces the gap to a straight line and the
    orientation is lost on the way out.

    It need not be. The transform is exactly the step from one element's exit
    frame to the next one's entrance frame, and floor mode holds both exactly,
    so the exporter can reconstitute the patch it never imported. Check the
    angles come back to the bit, not merely that some patch was written.
    """
    from laura.translator.converters.section import SectionLatticeTranslator

    source = tmp_path / "patched.bmad"
    source.write_text(
        "beginning[e_tot] = 1e9\n"
        "parameter[geometry] = open\n"
        "D1: drift, l = 0.5\n"
        "Q1: quadrupole, l = 0.3, k1 = 0.7\n"
        "P1: patch, x_offset = 0.02, z_offset = 0.4, tilt = 0.25, x_pitch = 0.06\n"
        "D2: drift, l = 0.6\n"
        "B1: sbend, l = 1.0, angle = 0.2\n"
        "Q2: quadrupole, l = 0.3, k1 = -0.7\n"
        "L: line = (D1, Q1, P1, D2, B1, Q2)\n"
        "use, L\n"
    )
    importer = BmadLatticeImporter(
        lattice_file=str(source), libtao=str(LIBTAO), position_mode="floor"
    )
    branch = importer.branches[1][0]
    section = importer.create_section(1, branch)[branch]
    written = SectionLatticeTranslator.from_section(section).to_bmad()

    patches = [line for line in written.splitlines() if ": patch," in line]
    assert len(patches) == 1, f"one patch went in, so one comes out: {patches}"
    assert "tilt = 0.25" in patches[0]
    assert "x_pitch = 0.06" in patches[0]
    line = next(item for item in written.splitlines() if item.startswith("L_1: line"))
    name = patches[0].split(":")[0]
    assert line.index("Q1") < line.index(name) < line.index("B1")


def test_bmad_export_writes_no_patch_for_an_ordinary_lattice():
    """The escape hatch stays shut unless a lattice actually needs it.

    A patch is only correct where a drift is not, so every gap that *is* a plain
    step downstream must still come out as a drift. ``bates`` is the sharp case:
    its ``ref_tilt = pi`` bends leave LAURA's frames turned a half turn from
    Bmad's own survey, and a patch synthesised from those unadjusted frames
    would appear beside every one of them -- rolling the beam twice, since the
    export already writes the roll as ``ref_tilt``.
    """
    from laura.translator.converters.section import SectionLatticeTranslator

    for relative_path in ("small_ring/small_ring.bmad", "jlab_fel/bates.bmad"):
        importer = BmadLatticeImporter(
            lattice_file=str(LATTICES / relative_path),
            libtao=str(LIBTAO),
            position_mode="floor",
        )
        branch = importer.branches[1][0]
        section = importer.create_section(1, branch)[branch]
        written = SectionLatticeTranslator.from_section(section).to_bmad()
        assert ": patch," not in written, relative_path


def test_bmad_bend_without_a_half_gap_does_not_acquire_one(tmp_path):
    """``hgap = 0`` is data, not a missing value.

    Bmad's default half gap is zero, meaning a bend with no fringe-field
    focusing at all -- which is what almost every documentation lattice
    actually says. The import used to test the attribute for truth rather than
    for presence, so a zero read as "Bmad did not tell us" and LAURA's own
    default of 16 mm was left standing. The export then wrote that back out,
    inventing a half gap for every bend in ``small_ring``, ``bates`` and
    ``original_e_ring``.

    That is not a cosmetic difference. ``fint`` is carried across faithfully,
    and the edge focusing goes as ``fint * hgap``, so a fabricated gap turns a
    hard-edged bend into one with real vertical focusing and moves the tune.
    Check both halves: the zero survives, and a genuine value still arrives.
    """
    source = tmp_path / "gaps.bmad"
    source.write_text(
        "beginning[e_tot] = 1e9\n"
        "parameter[geometry] = open\n"
        "BARE: sbend, l = 1.0, angle = 0.1, fint = 0.5\n"
        "GAPPED: sbend, l = 1.0, angle = 0.1, fint = 0.5, hgap = 0.03\n"
        "L: line = (BARE, GAPPED)\n"
        "use, L\n"
    )
    importer = BmadLatticeImporter(
        lattice_file=str(source), libtao=str(LIBTAO), position_mode="floor"
    )
    branch = importer.branches[1][0]
    converted = importer.create_laura_element_dictionary(1)[branch]
    bends = {name.upper(): element for name, element in converted.items()}
    assert bends["BARE"].magnetic.half_gap == 0.0
    assert bends["GAPPED"].magnetic.half_gap == pytest.approx(0.03)
    # The edge integral is unaffected either way -- it was always read by
    # presence -- and it is what makes the fabricated gap bite.
    assert bends["BARE"].magnetic.edge_field_integral == pytest.approx(0.5)


def test_bmad_x_pitch_is_a_rotation_about_y_not_a_roll(tmp_path):
    """Bmad's misalignment angles are named for a plane, not for an axis.

    ``x_pitch`` turns the element about **y** -- it is the tilt that moves the
    orbit in x -- and ``y_pitch`` turns it about x. LAURA's ``Rotation`` reads
    ``theta`` as the ``Ry`` factor, ``phi`` as ``Rx`` and ``psi`` as ``Rz``, so
    the pairing is ``x_pitch -> theta`` and ``y_pitch -> phi``. ``x_pitch``
    used to land in ``psi``, turning a tilt into a roll about the beam axis.

    Both pairs also cross over in **sign**, which the matching names make easy
    to miss: LAURA's ``Ry`` factor turns the opposite way to an ordinary
    right-handed one, so the same number means opposite rotations. The signs
    were copied straight across until 2026-09-01, which left an imported
    misalignment disagreeing with the ``global_rotation`` of the same element.
    A round trip cannot catch it, because the export made the same mistake.

    The lattice below is the measurement that settles both. The pitched
    elements carry one angle each, and the orbit is in the matching plane with
    the other identically zero; the patches at the front carry the same angles
    and are surveyed, so the sign is pinned to the floor angles that
    ``bmad_floor_angles_to_laura`` -- the definition of what these angles mean
    in LAURA -- reads back, rather than to a constant written into the test.
    """
    source = tmp_path / "pitched.bmad"
    source.write_text(
        "beginning[e_tot] = 1e9\n"
        "beginning[beta_a] = 10.0\n"
        "beginning[beta_b] = 10.0\n"
        "parameter[geometry] = open\n"
        "QX: quadrupole, l = 0.5, k1 = 2.0, x_pitch = 0.05\n"
        "QY: quadrupole, l = 0.5, k1 = 2.0, y_pitch = 0.03\n"
        "PX: patch, x_pitch = 0.05\n"
        "PY: patch, y_pitch = 0.03\n"
        "TAIL: marker\n"
        "L: line = (QX, QY, PX, PY, TAIL)\n"
        "use, L\n"
    )
    importer = BmadLatticeImporter(
        lattice_file=str(source), libtao=str(LIBTAO), position_mode="floor"
    )
    branch = importer.branches[1][0]
    elements = importer.create_laura_element_dictionary(1)[branch]
    pitched = {name.upper(): element for name, element in elements.items()}

    assert pitched["QX"].physical.error.rotation.theta == pytest.approx(-0.05)
    assert pitched["QX"].physical.error.rotation.phi == 0.0
    assert pitched["QX"].physical.error.rotation.psi == 0.0
    assert pitched["QY"].physical.error.rotation.phi == pytest.approx(-0.03)
    assert pitched["QY"].physical.error.rotation.theta == 0.0

    # The same two angles, this time applied to the reference frame by a pair
    # of patches and read back out of the surveyed floor coordinates. A
    # misalignment and a patch of the same angle have to land on the same LAURA
    # number, and the patches are what tie that number to Bmad's own survey
    # rather than to a constant written into this test. They sit after the
    # quadrupoles so that they do not disturb the orbit measured below. The two
    # compose in Bmad's order and are decomposed in LAURA's, so the recovered
    # angles agree only to second order in the angles -- far tighter than the
    # sign this is here to pin.
    frame = pitched["TAIL"].physical.global_rotation
    assert frame.theta == pytest.approx(-0.05, abs=1e-3)
    assert frame.phi == pytest.approx(-0.03, abs=1e-3)

    # Bmad itself agrees on which plane x_pitch acts in: an on-axis particle
    # through QX picks up horizontal motion and no vertical motion at all.
    from pytao import Tao

    tao = Tao(lattice_file=str(source), so_lib=str(LIBTAO), noplot=True)
    orbit = tao.ele_orbit("QX")
    assert abs(orbit["x"]) > 1e-6
    assert orbit["y"] == 0.0


def test_bmad_active_fixer_imports_as_the_sections_twiss_point(tmp_path):
    """An active ``fixer`` is a ``beginning_ele`` that stands mid-line.

    Bmad lets a branch nominate one fixer as the place its Twiss is declared;
    from there the optics propagate in both directions and ``beginning`` is
    switched off. Nothing about the beam changes -- a fixer is a statement about
    what is known, not an element the particle passes through -- so LAURA holds
    it as the same zero-length ``TwissMatch`` a ``beginning_ele`` becomes.

    Only the active one. A fixer that is off carries stored numbers that are not
    this lattice's Twiss, and reading them as if they were would plant a false
    optics point in the middle of the line, so it stays a ``Marker``.
    """
    import warnings

    source = tmp_path / "fixed.bmad"
    source.write_text(
        "beginning[e_tot] = 1e9\n"
        "beginning[beta_a] = 10.0\n"
        "beginning[beta_b] = 12.0\n"
        "parameter[geometry] = open\n"
        "D1: drift, l = 0.5\n"
        "Q1: quadrupole, l = 0.3, k1 = 0.7\n"
        "FX: fixer, beta_a_stored = 3.0, beta_b_stored = 4.0, "
        "alpha_a_stored = 0.5, alpha_b_stored = -0.25, "
        "eta_x_stored = 0.11, etap_x_stored = 0.02, is_on = T\n"
        "D2: drift, l = 0.6\n"
        "FY: fixer, beta_a_stored = 7.0, beta_b_stored = 8.0\n"
        "Q2: quadrupole, l = 0.3, k1 = -0.7\n"
        "L: line = (D1, Q1, FX, D2, FY, Q2)\n"
        "use, L\n"
    )
    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        importer = BmadLatticeImporter(
            lattice_file=str(source), libtao=str(LIBTAO), position_mode="floor"
        )
        branch = importer.branches[1][0]
        elements = importer.create_laura_element_dictionary(1)[branch]
    named = {name.upper(): element for name, element in elements.items()}

    active = named["FX"]
    assert active.hardware_type == "TwissMatch"
    assert active.physical.length == 0.0
    # The stored values, to the bit -- Bmad copies stored onto real when it
    # activates a fixer, so ele_twiss and the *_stored attributes agree.
    assert active.simulation.beta_x == pytest.approx(3.0)
    assert active.simulation.beta_y == pytest.approx(4.0)
    assert active.simulation.alpha_x == pytest.approx(0.5)
    assert active.simulation.alpha_y == pytest.approx(-0.25)
    assert active.simulation.eta_x == pytest.approx(0.11)
    assert active.simulation.eta_xp == pytest.approx(0.02)

    # The inactive one keeps its placement and loses its stored optics, and says
    # so rather than doing it quietly.
    assert named["FY"].hardware_type == "Marker"
    assert any("FY" in str(item.message) for item in raised)
    assert not any("FX" in str(item.message) for item in raised)

    # It is not the head of the section, so the export writes it as a Bmad
    # `match`, not as a fixer. That reproduces the Twiss downstream and nothing
    # else; see BmadLatticeImporter._store_twiss_point.
    from laura.translator.converters.section import SectionLatticeTranslator

    section = importer.create_section(1, branch)[branch]
    written = SectionLatticeTranslator.from_section(section).to_bmad()
    assert "matrix = match_twiss" in written


def test_bmad_misalignments_survive_the_round_trip(tmp_path):
    """``physical.error`` used to be dropped on the way back out to Bmad.

    A quadrupole imported with ``x_pitch = 0.05`` was written as
    ``quadrupole, l = 0.5, tilt = 0.0, k1 = 2.0`` -- the alignment error simply
    vanished, silently, because no element type in ``elements_bmad.yaml``
    listed the offset or pitch attributes. Every misalignment Bmad states is
    now stated back.

    The roll is the one that cannot be round-tripped everywhere, and the two
    branches below are why. A bend keeps its design plane in ``ref_tilt`` and
    its roll error in ``roll``, so both survive separately. Everything else has
    only ``tilt``, which Bmad defines as the two added together: the total is
    preserved, but on the way back in it all lands in ``magnetic.tilt``, so a
    second export writes the same number with the split gone.
    """
    from pytao import Tao

    from laura.translator.converters.section import SectionLatticeTranslator

    source = tmp_path / "misaligned.bmad"
    source.write_text(
        "beginning[e_tot] = 1e9\n"
        "beginning[beta_a] = 5.0\n"
        "beginning[beta_b] = 3.0\n"
        "parameter[geometry] = open\n"
        "Q1: quadrupole, l = 0.5, k1 = 2.0, x_offset = 0.001, "
        "y_offset = -0.002, z_offset = 0.003, x_pitch = 0.004, "
        "y_pitch = -0.005, tilt = 0.06\n"
        "B1: sbend, l = 1.0, angle = 0.1, x_offset = 0.0011, "
        "y_pitch = 0.0022, roll = 0.033\n"
        "S1: sextupole, l = 0.2, k2 = 3.0, y_offset = 0.007\n"
        "C1: rcollimator, l = 0.1, x_limit = 0.01, y_limit = 0.02, "
        "x_offset = 0.0009, y_pitch = 0.0008\n"
        "M1: marker, x_offset = 0.0005\n"
        "Q2: quadrupole, l = 0.4, k1 = -1.5\n"
        "L: line = (Q1, B1, S1, C1, M1, Q2)\n"
        "use, L\n"
    )
    importer = BmadLatticeImporter(
        lattice_file=str(source), libtao=str(LIBTAO), position_mode="floor"
    )
    branch = importer.branches[1][0]
    section = importer.create_section(1, branch)[branch]
    written = SectionLatticeTranslator.from_section(section).to_bmad(
        particle="Electron"
    )
    exported = tmp_path / "misaligned_rt.bmad"
    exported.write_text(written)

    attributes = ("X_OFFSET", "Y_OFFSET", "Z_OFFSET", "X_PITCH", "Y_PITCH")

    def misalignments(path):
        tao = Tao(lattice_file=str(path), so_lib=str(LIBTAO), noplot=True)
        found = {}
        for index in range(tao.lat_branch_list(ix_uni=1)[0]["n_ele_track"] + 1):
            head = tao.ele_head(f"1@0>>{index}")
            gen = tao.ele_gen_attribs(f"1@0>>{index}")
            found[head["name"].upper()] = {
                key: gen.get(key, 0.0)
                for key in attributes + ("TILT", "ROLL", "REF_TILT")
            }
        return found

    before = misalignments(source)
    after = misalignments(exported)

    for name in ("Q1", "B1", "S1", "C1", "M1"):
        for key in attributes:
            assert after[name][key] == pytest.approx(before[name][key]), (
                f"{name}[{key}]"
            )
    # The bend's roll stays its own attribute, separate from the design plane.
    assert after["B1"]["ROLL"] == pytest.approx(0.033)
    assert after["B1"]["REF_TILT"] == pytest.approx(0.0)
    # The quadrupole's tilt is design plus roll, and Bmad has nowhere to put
    # the two of them separately, so the total is what is checked.
    assert after["Q1"]["TILT"] == pytest.approx(before["Q1"]["TILT"])

    # An element with no alignment error is written exactly as it was: no
    # ``x_offset = 0.0`` padding on every definition in the lattice.
    definition = next(line for line in written.splitlines() if line.startswith("Q2:"))
    assert "offset" not in definition
    assert "pitch" not in definition


def test_bmad_collimator_apertures_survive_the_round_trip(tmp_path):
    """A collimator used to double in size on every export.

    LAURA's ``horizontal_size``/``vertical_size`` are *full* apertures -- the
    schema says so, and ``_rftrack_aperture`` reads them that way -- while
    Bmad's ``x1_limit`` and friends are half widths measured from the axis. The
    exporter wrote one straight into the other, so a Bmad ``x_limit = 0.01``
    came back as ``x1_limit = 0.02``, and a lattice passed through LAURA twice
    came back four times too wide. ``radius`` is already a half width and is
    the one that must *not* be halved, which is what the ecollimator here is
    for.
    """
    from pytao import Tao

    from laura.translator.converters.section import SectionLatticeTranslator

    source = tmp_path / "collimators.bmad"
    source.write_text(
        "beginning[e_tot] = 1e9\n"
        "beginning[beta_a] = 5.0\n"
        "beginning[beta_b] = 3.0\n"
        "parameter[geometry] = open\n"
        "R1: rcollimator, l = 0.1, x_limit = 0.01, y_limit = 0.02\n"
        "E1: ecollimator, l = 0.05, x_limit = 0.003, y_limit = 0.003\n"
        "D1: drift, l = 0.5\n"
        "L: line = (R1, D1, E1)\n"
        "use, L\n"
    )
    importer = BmadLatticeImporter(
        lattice_file=str(source), libtao=str(LIBTAO), position_mode="floor"
    )
    branch = importer.branches[1][0]
    section = importer.create_section(1, branch)[branch]
    written = SectionLatticeTranslator.from_section(section).to_bmad(
        particle="Electron"
    )
    exported = tmp_path / "collimators_rt.bmad"
    exported.write_text(written)

    limits = ("X1_LIMIT", "X2_LIMIT", "Y1_LIMIT", "Y2_LIMIT")

    def apertures(path):
        tao = Tao(lattice_file=str(path), so_lib=str(LIBTAO), noplot=True)
        found = {}
        for index in range(tao.lat_branch_list(ix_uni=1)[0]["n_ele_track"] + 1):
            head = tao.ele_head(f"1@0>>{index}")
            gen = tao.ele_gen_attribs(f"1@0>>{index}")
            found[head["name"].upper()] = {key: gen.get(key, 0.0) for key in limits}
        return found

    before = apertures(source)
    after = apertures(exported)

    for name in ("R1", "E1"):
        for key in limits:
            assert after[name][key] == pytest.approx(before[name][key]), (
                f"{name}[{key}]"
            )
    # Not merely self-consistent: these are the numbers the source file states.
    assert after["R1"]["X1_LIMIT"] == pytest.approx(0.01)
    assert after["R1"]["Y1_LIMIT"] == pytest.approx(0.02)
    assert after["E1"]["X1_LIMIT"] == pytest.approx(0.003)


def test_bmad_cavity_phase_round_trip_keeps_the_sign_of_the_chirp(tmp_path):
    """The importer used to read ``phi0`` straight through, and the exporter
    negates it, so every cavity came back off-crest the other way.

    Nothing about a single element gives the mistake away -- the reference
    energy gain goes as ``cos(phi0)``, which does not care about the sign -- so
    the test is the energy a particle picks up as a function of where it sits
    in the bunch. That is what a linac is actually set up for, and flipping it
    turns bunch compression into decompression: tracking the LCLS CU_HXR
    lattice end to end, the round-tripped copy left the beam 96 times longer
    than Bmad's own run of the same lattice.

    ``phi0 = -0.05972222`` is the real setting of the first L1 cavity there.
    """
    from pytao import Tao

    from laura.translator.converters.section import SectionLatticeTranslator

    header = (
        "beginning[e_tot] = 1.35e8\n"
        "beginning[beta_a] = 5.0\n"
        "beginning[beta_b] = 3.0\n"
        "parameter[geometry] = open\n"
        "parameter[particle] = electron\n"
    )
    source = tmp_path / "chirp.bmad"
    source.write_text(
        header + "C1: lcavity, l = 1.0, rf_frequency = 2856e6, voltage = 2e7, "
        "phi0 = -0.05972222\n"
        "L: line = (C1)\n"
        "use, L\n"
    )
    importer = BmadLatticeImporter(
        lattice_file=str(source), libtao=str(LIBTAO), position_mode="s"
    )
    branch = importer.branches[1][0]
    section = importer.create_section(1, branch)[branch]
    exported = tmp_path / "chirp_rt.bmad"
    exported.write_text(
        header
        + SectionLatticeTranslator.from_section(section).to_bmad(particle="Electron")
    )

    def cavity(path):
        tao = Tao(lattice_file=str(path), so_lib=str(LIBTAO), noplot=True)
        last = tao.lat_branch_list(ix_uni=1)[0]["n_ele_track"]
        gain = {}
        for offset in (-1e-3, 1e-3):
            tao.cmd(f"set particle_start z = {offset}")
            gain[offset] = tao.ele_orbit(f"1@0>>{last}")["pz"]
        return tao.ele_gen_attribs("1@0>>1")["PHI0"], gain

    phi0_before, chirp_before = cavity(source)
    phi0_after, chirp_after = cavity(exported)

    assert phi0_after == pytest.approx(phi0_before)
    for offset, value in chirp_before.items():
        assert chirp_after[offset] == pytest.approx(value, rel=1e-9)
    # The head of the bunch (z > 0 in Bmad) is the end that loses energy at a
    # negative phi0 -- the sign that compresses downstream.
    assert chirp_before[1e-3] < 0.0 < chirp_before[-1e-3]


def test_reserved_names_export_to_a_lattice_bmad_will_actually_parse(tmp_path):
    """Bmad keeps a set of names for itself, and an element carrying one is a
    hard parse failure -- ``BEGINNING`` comes back as ``RESERVED WORD``, and
    every element class is rejected as ``NOT ALLOWED TO BE THE SAME AS AN
    ELEMENT CLASS``. ``END`` parses but is then confused with the end-of-branch
    element Bmad makes itself.

    The LCLS cu_hxr lattice really does end on a marker called END, so this is
    the difference between a round trip Tao can read back and one it cannot.
    """
    from pytao import Tao

    from laura.models.element import Marker, Quadrupole
    from laura.models.elementList import SectionLattice
    from laura.models.physical import PhysicalElement, Position
    from laura.translator.converters.section import SectionLatticeTranslator

    section = SectionLattice(
        name="S",
        order=["BEGINNING", "Q", "MARKER", "END"],
        elements=[
            Marker(
                name="BEGINNING",
                machine_area="S",
                physical=PhysicalElement(length=0.0, middle=Position(z=0.0)),
            ),
            Quadrupole(
                name="Q",
                machine_area="S",
                magnetic={"magnetic_length": 0.5, "k1l": 0.15},
                physical=PhysicalElement(length=0.5, middle=Position(z=0.25)),
            ),
            Marker(
                name="MARKER",
                machine_area="S",
                physical=PhysicalElement(length=0.0, middle=Position(z=0.5)),
            ),
            Marker(
                name="END",
                machine_area="S",
                physical=PhysicalElement(length=0.0, middle=Position(z=1.0)),
            ),
        ],
        geometry="open",
    )
    with pytest.warns(UserWarning, match="reserves"):
        body = SectionLatticeTranslator.from_section(section).to_bmad(
            particle="Electron"
        )
    path = tmp_path / "reserved.bmad"
    path.write_text(
        "beginning[e_tot] = 1.35e8\n"
        "beginning[beta_a] = 5.0\n"
        "beginning[beta_b] = 3.0\n" + body
    )

    tao = Tao(lattice_file=str(path), so_lib=str(LIBTAO), noplot=True)
    names = [
        tao.ele_head(f"1@0>>{index}")["name"]
        for index in range(tao.lat_branch_list(ix_uni=1)[0]["n_ele_track"] + 1)
    ]

    assert "BEGINNING_ELEMENT" in names
    assert "MARKER_ELEMENT" in names
    assert "END_ELEMENT" in names
    # Bmad's own end-of-branch element is still the one called END, and the
    # renamed marker sits before it rather than merging into it.
    assert names.index("END_ELEMENT") < len(names) - 1
    assert names[-1] == "END"


_WAKE_LATTICE = """beginning[p0c] = 1.35e8
beginning[beta_a] = 5.0
beginning[beta_b] = 3.0
parameter[geometry] = open
parameter[particle] = electron
C1: lcavity, l = 2.0, rf_frequency = 2856e6, voltage = 0, phi0 = 0,
    sr_wake = {z_max = 0.01, amp_scale = 2, scale_with_length = F,
      longitudinal = {1e14, 200, 0, 0.25, none}}
M1: marker, sr_wake = {z_max = 0.01, amp_scale = 1, scale_with_length = F,
      longitudinal = {5e13, 500, 1000, 0.25, none}}
SPLIT: marker, superimpose, ref = C1, offset = 0
L: line = (C1, M1)
use, L
"""


def _wake_model(tmp_path):
    """Import a lattice whose wake sits on a cavity, on a lord, and on a marker."""
    path = tmp_path / "wakes.bmad"
    path.write_text(_WAKE_LATTICE)
    importer = BmadLatticeImporter(
        lattice_file=str(path), libtao=str(LIBTAO), position_mode="s"
    )
    converted = importer.create_laura_element_dictionary(1)
    return next(iter(converted.values()))


def test_a_short_range_wake_is_imported_as_sampled_arrays(tmp_path):
    """Bmad states a short-range wake as a sum of damped sinusoids and LAURA's
    field model holds sampled arrays, so the modes are evaluated onto a grid on
    the way in. amp_scale multiplies them; the mode here is a quarter turn, so
    W(0) is amp_scale * amp exactly.
    """
    elements = _wake_model(tmp_path)

    wake = elements["C1#1"].simulation.wakefield_definition
    assert wake.field_type == "LongitudinalWake"
    assert wake.z.value.val[-1] == 0.0
    assert wake.z.value.val[0] == pytest.approx(-0.01)
    assert wake.Wz.value.val[-1] == pytest.approx(2.0e14)


def test_a_super_lord_s_wake_reaches_the_slaves_that_are_tracked(tmp_path):
    """A superimposed element splits the cavity into slaves and turns the
    cavity itself into a lord. ``lat_list`` returns only the slaves, the wake
    stays on the lord, and asking a slave for it is an error -- so the lords
    have to be swept separately and mapped back down.
    """
    elements = _wake_model(tmp_path)

    for slave in ("C1#1", "C1#2"):
        wake = elements[slave].simulation.wakefield_definition
        assert wake is not None, f"{slave} lost its lord's wake"
        assert wake.Wz.value.val[-1] == pytest.approx(2.0e14)


def test_a_wake_on_a_marker_is_imported_too(tmp_path):
    """A zero-length marker is how a Bmad lattice hangs a resistive-wall wake
    off a point in the line -- cu_hxr does it three times -- and markers are
    built by a different path from every other element.
    """
    elements = _wake_model(tmp_path)

    wake = elements["M1"].simulation.wakefield_definition
    assert wake is not None
    assert wake.Wz.value.val[-1] == pytest.approx(5.0e13)


def test_an_exported_element_keeps_its_wake_beside_it(tmp_path):
    """Thousands of samples do not belong inline in an element's YAML, and a
    field with no file behind it has nothing to name. So export writes the
    samples out and records the file, which is how a wake read from a file is
    stored in the first place.
    """
    import h5py

    from laura.Exporters.YAML import export_as_yaml

    elements = _wake_model(tmp_path)
    output = tmp_path / "export"
    output.mkdir()

    export_as_yaml(str(output / "M1.yaml"), elements["M1"])

    sidecar = output / "M1_wake.hdf5"
    assert sidecar.is_file()
    with h5py.File(sidecar, "r") as written:
        assert written["Wz"][-1] == pytest.approx(5.0e13)
        assert written["z"].attrs["units"] == "m"
    assert "M1_wake.hdf5" in (output / "M1.yaml").read_text()


def test_the_exported_wake_tracks_the_way_the_modes_it_came_from_do(
    tmp_path, monkeypatch
):
    """The whole point of sampling. Bmad applies a tabulated wake by FFT
    convolution against a binned bunch rather than mode by mode, so the two
    agree only if the grid, its sign and its zero point are all right: the
    table is indexed by the trailing particle's position minus the source's,
    which is negative, and w(0) is not halved the way the mode sum's self-wake
    is.
    """
    from pytao import Tao

    from laura.translator.converters.section import SectionLatticeTranslator

    charge, separation = 1e-10, 2.0e-3
    elements = _wake_model(tmp_path)
    beam = tmp_path / "two.beam0"
    beam.write_text(
        "!ASCII::3\n0\n1\n2\nBEGIN_BUNCH\nelectron\n"
        f"{2 * charge:.16e}\n0\n0\n"
        + "".join(f" 0 0 0 0 {z:.16e} 0 {charge:.16e} 1\n" for z in (separation, 0.0))
        + "END_BUNCH\n"
    )

    def track(lattice: Path) -> np.ndarray:
        init = lattice.with_suffix(".init")
        init.write_text(
            "&tao_start\n n_universes = 1\n/\n"
            f"&tao_design_lattice\n design_lattice(1)%file = '{lattice}'\n/\n"
            "&tao_params\n global%track_type = 'beam'\n global%plot_on = F\n/\n"
            '&tao_beam_init\n ix_universe = 1\n beam_saved_at = "*"\n'
            f" beam_init%position_file = '{beam}'\n/\n"
        )
        tao = Tao(init_file=str(init), so_lib=str(LIBTAO), noplot=True)
        tao.cmd("set global track_type = beam")
        pz = np.array(tao.bunch1("1@0>>1", coordinate="pz", which="model", ix_bunch=1))
        z = np.array(tao.bunch1("1@0>>1", coordinate="z", which="model", ix_bunch=1))
        return pz[np.argsort(-z)]

    modes = tmp_path / "modes.bmad"
    modes.write_text(
        "beginning[p0c] = 1.35e8\nbeginning[beta_a] = 5.0\nbeginning[beta_b] = 3.0\n"
        "parameter[geometry] = open\nparameter[particle] = electron\n"
        "W1: lcavity, l = 2.0, rf_frequency = 2856e6, voltage = 0, phi0 = 0,\n"
        "    sr_wake = {z_max = 0.01, amp_scale = 2, scale_with_length = F,\n"
        "      longitudinal = {1e14, 200, 0, 0.25, none}}\n"
        "L: line = (W1)\nuse, L\n"
    )

    from laura.models.elementList import SectionLattice
    from laura.models.physical import Position

    element = elements["C1#1"].model_copy(deep=True)
    element.name = "W1"
    element.physical.length = 2.0
    element.simulation.wakefield_definition.filename = "W1_wake.bmad"
    element.physical.middle = Position(z=1.0)
    section = SectionLattice(
        name="L", order=["W1"], elements=[element], geometry="open"
    )
    # to_bmad writes the wake sidecar beside whatever the working directory is,
    # and refers to it by name, so the lattice has to be written there too.
    monkeypatch.chdir(tmp_path)
    sampled = tmp_path / "sampled.bmad"
    sampled.write_text(
        "beginning[p0c] = 1.35e8\nbeginning[beta_a] = 5.0\nbeginning[beta_b] = 3.0\n"
        "parameter[geometry] = open\nparameter[particle] = electron\n"
        + SectionLatticeTranslator.from_section(section).to_bmad(particle="Electron")
    )

    from_modes, from_table = track(modes), track(sampled)

    # Two point particles interpolate the table rather than convolving with
    # it, so the grid's own resolution barely shows: this agrees to better than
    # 1e-7 in practice.
    assert from_table == pytest.approx(from_modes, rel=1e-6)
    assert from_modes[0] < 0.0


def test_bmad_split_bend_keeps_its_exit_fringe_field(tmp_path):
    """A bend split by superposition owns its faces separately.

    Superimposing a marker inside a bend replaces it with two tracking
    super-slaves, and Bmad divides the fringe between them: the first piece
    carries ``FINT``/``HGAP`` and zero at its exit, the last carries zero at its
    entrance and ``FINTX``/``HGAPX``. The interior faces are not physical, and
    Bmad is careful to say so.

    An unsplit bend must stay single-valued: absent means "same as the
    entrance", so a lattice quoting one integral reads, and writes, as it
    always did.
    """
    source = tmp_path / "split.bmad"
    source.write_text(
        "beginning[e_tot] = 1e9\n"
        "parameter[geometry] = open\n"
        "D: drift, l = 0.5\n"
        "B: sbend, l = 1.0, angle = 0.1, fint = 0.45, hgap = 0.015\n"
        "WHOLE: sbend, l = 1.0, angle = 0.1, fint = 0.45, hgap = 0.015\n"
        "M: marker, superimpose, ref = B, offset = 0.0\n"
        "L: line = (D, B, D, WHOLE)\n"
        "use, L\n"
    )
    importer = BmadLatticeImporter(
        lattice_file=str(source), libtao=str(LIBTAO), position_mode="floor"
    )
    branch = importer.branches[1][0]
    converted = importer.create_laura_element_dictionary(1)[branch]
    bends = {name.upper(): element for name, element in converted.items()}

    entrance, exit_ = bends["B#1"].magnetic, bends["B#2"].magnetic
    assert entrance.edge_field_integral == pytest.approx(0.45)
    assert entrance.half_gap == pytest.approx(0.015)
    assert entrance.exit_fringe_integral == 0.0
    assert entrance.exit_half_gap == 0.0
    assert exit_.edge_field_integral == 0.0
    assert exit_.half_gap == 0.0
    assert exit_.exit_fringe_integral == pytest.approx(0.45)
    assert exit_.exit_half_gap == pytest.approx(0.015)

    whole = bends["WHOLE"].magnetic
    assert whole.exit_edge_field_integral is None
    assert whole.exit_gap is None
    assert whole.exit_fringe_integral == pytest.approx(0.45)
    assert whole.exit_half_gap == pytest.approx(0.015)
