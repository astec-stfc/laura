"""Optional parity checks against the Bmad documentation lattices."""

import math
import os
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pytao")

from pytao import Tao

from laura.translator.converters.codes import magnetic_orders
from laura.translator.converters.codes.bmad import BmadLatticeImporter
from laura.translator.converters.section import SectionLatticeTranslator
from laura.translator.utils.bmad import bmad_floor_rotation_matrix

# Bmad's own variable; pytao already reads it.
BMAD_DIST = Path(
    os.environ.get("BMAD_DIST")
    or os.environ.get("ACC_ROOT_DIR")
    or Path.home() / "Documents" / "bmad-ecosystem"
).expanduser()
LIBTAO = Path(
    os.environ.get("LAURA_LIBTAO", BMAD_DIST / "production" / "lib" / "libtao.so")
).expanduser()
LATTICES = BMAD_DIST / "bmad-doc" / "lattices"

pytestmark = pytest.mark.skipif(
    not LIBTAO.exists() or not LATTICES.exists(),
    reason="Bmad documentation lattices and libtao are not installed",
)

_ELECTRON = "parameter[particle] = electron\nparameter[p0c] = 10e6\n"
_OPEN = "beginning[e_tot] = 1e9\nparameter[geometry] = open\n"
_TWISS = "beginning[beta_a] = 5.0\nbeginning[beta_b] = 3.0\n"


def _write(tmp_path, text, name="source.bmad"):
    path = tmp_path / name
    path.write_text(text)
    return path


def _import(source, **kwargs):
    """Import a lattice file; returns ``(importer, first branch)``."""
    importer = BmadLatticeImporter(
        lattice_file=str(source), libtao=str(LIBTAO), **kwargs
    )
    return importer, importer.branches[1][0]


def _elements(source, **kwargs):
    importer, branch = _import(source, **kwargs)
    return importer.create_laura_element_dictionary(1)[branch]


def _section(source, **kwargs):
    importer, branch = _import(source, **kwargs)
    return importer.create_section(1, branch)[branch]


def _to_bmad(section, **kwargs):
    return SectionLatticeTranslator.from_section(section).to_bmad(**kwargs)


def _roundtrip(tmp_path, text, header="", position_mode="floor"):
    """Import ``text``, export to Bmad; returns ``(source, exported, section)``."""
    source = _write(tmp_path, text)
    section = _section(source, position_mode=position_mode)
    written = _to_bmad(section, particle="Electron")
    return source, _write(tmp_path, header + written, "roundtrip.bmad"), section


def _tao(path):
    return Tao(lattice_file=str(path), so_lib=str(LIBTAO), noplot=True)


def _tao_elements(path):
    """``{NAME: (ele_head, ele_gen_attribs)}`` for every tracking element, in order."""
    tao = _tao(path)
    found = {}
    for index in range(tao.lat_branch_list(ix_uni=1)[0]["n_ele_track"] + 1):
        head = tao.ele_head(f"1@0>>{index}")
        found[head["name"].upper()] = (head, tao.ele_gen_attribs(f"1@0>>{index}"))
    return found


@pytest.mark.parametrize(
    "relative_path, expected_elements",
    [
        ("small_ring/small_ring.bmad", 90),
        ("Dragt_PSR_small_ring/Dragt_PSR_small_ring.bmad", 80),
        ("jlab_ep_collider/original_e_ring.bmad", 1502),
        ("jlab_ep_collider/original_p_ring.bmad", 998),
        ("jlab_fel/bates.bmad", 117),
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
                    # KS (normalised), not BS_FIELD (tesla): LAURA's S0L is normalised.
                    assert element.magnetic.ks == pytest.approx(
                        parameters["KS"] * length
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
    """Geometry parity; LAURA rebuilds start/end, the middle comes from Tao."""
    importer, _ = _import(LATTICES / relative_path, position_mode="floor")
    tao = _tao(LATTICES / relative_path)

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
                assert element.physical.s == pytest.approx(
                    spos[index] - lengths[index] / 2.0, abs=1e-9
                )
                checked += 1

    assert checked > 0


def test_multiword_branch_name_is_resolved_by_index():
    """Tao's ``lat_list`` silently returns nothing for a branch name, not index."""
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
    lattice = _write(
        tmp_path,
        _ELECTRON + "t: taylor, {1: 3 |}, {1: 1 |1}, {1: 2 |22}, {1: 6 |123}, "
        "{S1: 0.9 |}, {Sx: 0.1 |1}, "
        "{2: 1 |2}, {3: 1 |3}, {4: 1 |4}, {5: 1 |5}, {6: 1 |6}\n"
        "sq: sol_quad, l = 2, k1 = 0.3, ks = 0.4\n"
        "lat: line = (t, sq)\n"
        "use, lat\n",
    )
    importer, branch = _import(lattice)
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
    # KS not BS_FIELD: ks = 0.4 over 2 m is 0.8; BS_FIELD is ~0.0267 at p0c = 10 MeV.
    assert sq.magnetic.ks == pytest.approx(
        importer.params[1][branch][sq_index]["KS"] * 2
    )
    assert sq.magnetic.ks == pytest.approx(0.8)


def test_beginning_ele_imports_as_twiss_match(tmp_path):
    """Bmad propagates Twiss from BEGINNING (cf. Ocelot ``Twiss()``, ELEGANT TWISS)."""
    elements = _elements(
        _write(
            tmp_path,
            _ELECTRON + "parameter[geometry] = open\n"
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
            "use, lat\n",
        )
    )

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
    elements = _elements(
        LATTICES / "spin_single_resonance_model" / "spin_single_res.bmad"
    )
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
    source = _write(
        tmp_path,
        _ELECTRON + "d: drift, l = 1\n"
        "k: kicker, l = 0.5, hkick = 0.01, vkick = 0.02\n"
        "lat: line = (d, k)\n"
        "use, lat\n",
    )
    elements = _section(source).elements.elements

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
    source = _write(
        tmp_path,
        _ELECTRON + "m: match, l = 2, beta_a0 = 4, alpha_a0 = 1, "
        "beta_a1 = 9, alpha_a1 = -0.5, beta_b0 = 5, alpha_b0 = -0.2, "
        "beta_b1 = 7, alpha_b1 = 0.3, dphi_a = 0.4, dphi_b = 0.2\n"
        "lat: line = (m)\n"
        "use, lat\n",
    )
    match = _elements(source)["M"]

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
    """LAURA bends toward +x for a positive angle, Bmad toward -x: the geometric angle
    is negated while ``magnetic.KnL(0)`` keeps Bmad's sign.
    """
    section = _section(LATTICES / "jlab_fel" / "bates.bmad")

    bends = [
        element
        for element in section.elements.elements.values()
        if element.hardware_type == "Dipole" and element.physical.length > 0
    ]
    assert bends, "bates is made of bends; the filter is wrong if this is empty"
    rolled = 0
    for bend in bends:
        angle = bend.magnetic.KnL(0)
        assert angle
        rolled += abs(math.remainder(bend.magnetic.tilt or 0.0, 2 * math.pi)) > 1e-12
        assert bend.physical._physical_angle == pytest.approx(-angle)
    assert rolled, "bates has ref_tilt = pi bends; the half-turn branch is untested"


def test_bmad_ref_tilt_is_imported_and_turns_the_bend_the_other_way():
    """``ref_tilt`` rolls the frame, so the bend turns the other way. Tao reports the
    frame unrolled, so the roll must also go into the floor orientation.
    """
    section = _section(LATTICES / "jlab_fel" / "bates.bmad")
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
    """LAURA derives exit frames itself; a wrong one invents patches on export."""
    section = _section(LATTICES / lattice)
    tao = _tao(LATTICES / lattice)
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
    """Bmad's floor ``W`` is ``Ry(theta) Rx(-phi) Rz(psi)``; positive ``phi`` is up."""
    tao = _tao(
        _write(
            tmp_path,
            _OPEN + "P: patch, y_pitch = 0.2, tilt = 0.35\n"
            "B: sbend, l = 1.0, angle = 0.3\n"
            "L: line = (P, B)\n"
            "use, L\n",
        )
    )
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
    """LAURA has no patch element; export rebuilds it from floor-mode frames."""
    source = _write(
        tmp_path,
        _OPEN + "D1: drift, l = 0.5\n"
        "Q1: quadrupole, l = 0.3, k1 = 0.7\n"
        "P1: patch, x_offset = 0.02, z_offset = 0.4, tilt = 0.25, x_pitch = 0.06\n"
        "D2: drift, l = 0.6\n"
        "B1: sbend, l = 1.0, angle = 0.2\n"
        "Q2: quadrupole, l = 0.3, k1 = -0.7\n"
        "L: line = (D1, Q1, P1, D2, B1, Q2)\n"
        "use, L\n",
    )
    written = _to_bmad(_section(source))

    patches = [line for line in written.splitlines() if ": patch," in line]
    assert len(patches) == 1, f"one patch went in, so one comes out: {patches}"
    assert "tilt = 0.25" in patches[0]
    assert "x_pitch = 0.06" in patches[0]
    line = next(item for item in written.splitlines() if item.startswith("L_1: line"))
    name = patches[0].split(":")[0]
    assert line.index("Q1") < line.index(name) < line.index("B1")


def test_bmad_export_writes_no_patch_for_an_ordinary_lattice():
    """Plain steps stay drifts; ``bates`` (``ref_tilt = pi``) is the sharp case."""
    for relative_path in ("small_ring/small_ring.bmad", "jlab_fel/bates.bmad"):
        written = _to_bmad(_section(LATTICES / relative_path))
        assert ": patch," not in written, relative_path


def test_bmad_bend_without_a_half_gap_does_not_acquire_one(tmp_path):
    """Bmad's default ``hgap`` is 0, and edge focusing goes as ``fint * hgap``."""
    source = _write(
        tmp_path,
        _OPEN + "BARE: sbend, l = 1.0, angle = 0.1, fint = 0.5\n"
        "GAPPED: sbend, l = 1.0, angle = 0.1, fint = 0.5, hgap = 0.03\n"
        "L: line = (BARE, GAPPED)\n"
        "use, L\n",
    )
    converted = _elements(source)
    bends = {name.upper(): element for name, element in converted.items()}
    assert bends["BARE"].magnetic.half_gap == 0.0
    assert bends["GAPPED"].magnetic.half_gap == pytest.approx(0.03)
    assert bends["BARE"].magnetic.edge_field_integral == pytest.approx(0.5)


def test_bmad_x_pitch_is_a_rotation_about_y_not_a_roll(tmp_path):
    """``x_pitch`` rotates about y (LAURA ``theta``), ``y_pitch`` about x (``phi``),
    both with flipped sign because LAURA's ``Ry`` turns opposite to a right-handed one.
    """
    source = _write(
        tmp_path,
        _OPEN + "beginning[beta_a] = 10.0\n"
        "beginning[beta_b] = 10.0\n"
        "QX: quadrupole, l = 0.5, k1 = 2.0, x_pitch = 0.05\n"
        "QY: quadrupole, l = 0.5, k1 = 2.0, y_pitch = 0.03\n"
        "PX: patch, x_pitch = 0.05\n"
        "PY: patch, y_pitch = 0.03\n"
        "TAIL: marker\n"
        "L: line = (QX, QY, PX, PY, TAIL)\n"
        "use, L\n",
    )
    elements = _elements(source)
    pitched = {name.upper(): element for name, element in elements.items()}

    assert pitched["QX"].physical.error.rotation.theta == pytest.approx(-0.05)
    assert pitched["QX"].physical.error.rotation.phi == 0.0
    assert pitched["QX"].physical.error.rotation.psi == 0.0
    assert pitched["QY"].physical.error.rotation.phi == pytest.approx(-0.03)
    assert pitched["QY"].physical.error.rotation.theta == 0.0

    # Same angles via patches, read back from the survey. Bmad and LAURA compose in
    # different orders, so they agree only to second order.
    frame = pitched["TAIL"].physical.global_rotation
    assert frame.theta == pytest.approx(-0.05, abs=1e-3)
    assert frame.phi == pytest.approx(-0.03, abs=1e-3)

    # Tao agrees: x_pitch gives horizontal motion only.
    orbit = _tao(source).ele_orbit("QX")
    assert abs(orbit["x"]) > 1e-6
    assert orbit["y"] == 0.0


def test_bmad_active_fixer_imports_as_the_sections_twiss_point(tmp_path):
    """An active ``fixer`` imports as a ``TwissMatch``, an inactive one a ``Marker``."""
    import warnings

    source = _write(
        tmp_path,
        _OPEN + "beginning[beta_a] = 10.0\n"
        "beginning[beta_b] = 12.0\n"
        "D1: drift, l = 0.5\n"
        "Q1: quadrupole, l = 0.3, k1 = 0.7\n"
        "FX: fixer, beta_a_stored = 3.0, beta_b_stored = 4.0, "
        "alpha_a_stored = 0.5, alpha_b_stored = -0.25, "
        "eta_x_stored = 0.11, etap_x_stored = 0.02, is_on = T\n"
        "D2: drift, l = 0.6\n"
        "FY: fixer, beta_a_stored = 7.0, beta_b_stored = 8.0\n"
        "Q2: quadrupole, l = 0.3, k1 = -0.7\n"
        "L: line = (D1, Q1, FX, D2, FY, Q2)\n"
        "use, L\n",
    )
    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        importer, branch = _import(source)
        elements = importer.create_laura_element_dictionary(1)[branch]
    named = {name.upper(): element for name, element in elements.items()}

    active = named["FX"]
    assert active.hardware_type == "TwissMatch"
    assert active.physical.length == 0.0
    # Bmad copies stored onto real when it activates a fixer.
    assert active.simulation.beta_x == pytest.approx(3.0)
    assert active.simulation.beta_y == pytest.approx(4.0)
    assert active.simulation.alpha_x == pytest.approx(0.5)
    assert active.simulation.alpha_y == pytest.approx(-0.25)
    assert active.simulation.eta_x == pytest.approx(0.11)
    assert active.simulation.eta_xp == pytest.approx(0.02)

    assert named["FY"].hardware_type == "Marker"
    assert any("FY" in str(item.message) for item in raised)
    assert not any("FX" in str(item.message) for item in raised)

    # Not the section head, so it exports as a fixer rather than in ``beginning``.
    written = _to_bmad(importer.create_section(1, branch)[branch])
    assert "FX: fixer, beta_a_stored = 3.0, beta_b_stored = 4.0" in written
    assert "alpha_a_stored = 0.5, alpha_b_stored = -0.25" in written
    assert "eta_x_stored = 0.11" in written
    assert "etap_x_stored = 0.02" in written
    assert "is_on = T" in written
    assert "match_twiss" not in written


def test_bmad_misalignments_survive_the_round_trip(tmp_path):
    """Only a bend keeps its roll separate (``roll`` vs ``ref_tilt``); elsewhere Bmad's
    ``tilt`` is the sum, so only the total survives.
    """
    source, exported, _ = _roundtrip(
        tmp_path,
        _OPEN + _TWISS + "Q1: quadrupole, l = 0.5, k1 = 2.0, x_offset = 0.001, "
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
        "use, L\n",
    )

    attributes = ("X_OFFSET", "Y_OFFSET", "Z_OFFSET", "X_PITCH", "Y_PITCH")

    def misalignments(path):
        return {
            name: {
                key: gen.get(key, 0.0)
                for key in attributes + ("TILT", "ROLL", "REF_TILT")
            }
            for name, (_, gen) in _tao_elements(path).items()
        }

    before = misalignments(source)
    after = misalignments(exported)

    for name in ("Q1", "B1", "S1", "C1", "M1"):
        for key in attributes:
            assert after[name][key] == pytest.approx(before[name][key]), (
                f"{name}[{key}]"
            )
    assert after["B1"]["ROLL"] == pytest.approx(0.033)
    assert after["B1"]["REF_TILT"] == pytest.approx(0.0)
    assert after["Q1"]["TILT"] == pytest.approx(before["Q1"]["TILT"])

    definition = next(
        line for line in exported.read_text().splitlines() if line.startswith("Q2:")
    )
    assert "offset" not in definition
    assert "pitch" not in definition


def test_bmad_collimator_apertures_survive_the_round_trip(tmp_path):
    """LAURA sizes are full widths, Bmad limits half; ``radius`` is already half."""
    source, exported, _ = _roundtrip(
        tmp_path,
        _OPEN + _TWISS + "R1: rcollimator, l = 0.1, x_limit = 0.01, y_limit = 0.02\n"
        "E1: ecollimator, l = 0.05, x_limit = 0.003, y_limit = 0.003\n"
        "D1: drift, l = 0.5\n"
        "L: line = (R1, D1, E1)\n"
        "use, L\n",
    )

    limits = ("X1_LIMIT", "X2_LIMIT", "Y1_LIMIT", "Y2_LIMIT")

    def apertures(path):
        return {
            name: {key: gen.get(key, 0.0) for key in limits} | {"key": head["key"]}
            for name, (head, gen) in _tao_elements(path).items()
        }

    before = apertures(source)
    after = apertures(exported)

    for name in ("R1", "E1"):
        for key in limits:
            assert after[name][key] == pytest.approx(before[name][key]), (
                f"{name}[{key}]"
            )
    assert after["R1"]["X1_LIMIT"] == pytest.approx(0.01)
    assert after["R1"]["Y1_LIMIT"] == pytest.approx(0.02)
    assert after["E1"]["X1_LIMIT"] == pytest.approx(0.003)

    # Tao reports no ``aperture_type``, so the class is the only record of shape.
    assert after["E1"]["key"] == "ECollimator"
    assert after["R1"]["key"] == "RCollimator"


def test_bmad_aperture_survives_on_an_element_that_is_not_a_collimator(tmp_path):
    """Bmad hangs apertures off any element (LCLS quadrupoles state their bore)."""
    _, exported, _ = _roundtrip(
        tmp_path,
        _OPEN
        + _TWISS
        + "Q1: quadrupole, l = 0.1, k1 = 1.2, x_limit = 0.016, y_limit = 0.016\n"
        "D1: drift, l = 0.5, x_limit = 0.02, y_limit = 0.01\n"
        "Q2: quadrupole, l = 0.1, k1 = -1.2\n"
        "L: line = (Q1, D1, Q2)\n"
        "use, L\n",
    )
    found = {name: gen for name, (_, gen) in _tao_elements(exported).items()}

    # LAURA full width -> Bmad half width.
    assert found["Q1"]["X1_LIMIT"] == pytest.approx(0.016)
    assert found["Q1"]["Y2_LIMIT"] == pytest.approx(0.016)
    assert found["D1"]["X1_LIMIT"] == pytest.approx(0.02)
    assert found["D1"]["Y1_LIMIT"] == pytest.approx(0.01)
    assert found["Q2"]["X1_LIMIT"] == pytest.approx(0.0)


def test_bmad_space_charge_settings_survive_the_round_trip(tmp_path):
    """Bmad treats ``n_bin = 0`` as unconfigured and loses the whole bunch."""
    _, exported, section = _roundtrip(
        tmp_path,
        _OPEN + _TWISS + "bmad_com[csr_and_space_charge_on] = T\n"
        "space_charge_com[n_bin] = 40\n"
        "space_charge_com[ds_track_step] = 0.01\n"
        "space_charge_com[beam_chamber_height] = 0.024\n"
        "space_charge_com[particle_bin_span] = 3\n"
        "B1: sbend, l = 0.5, angle = 0.05, csr_method = 1_Dim\n"
        "D1: drift, l = 0.5\n"
        "L: line = (B1, D1)\n"
        "use, L\n",
    )
    assert section.space_charge.number_of_bins == 40
    assert section.space_charge.step_size == pytest.approx(0.01)
    assert section.space_charge.chamber_height == pytest.approx(0.024)
    assert section.space_charge.bin_span == 3

    tao = _tao(exported)
    after = tao.space_charge_com()
    assert after["n_bin"] == 40
    assert after["ds_track_step"] == pytest.approx(0.01)
    assert after["beam_chamber_height"] == pytest.approx(0.024)
    assert after["particle_bin_span"] == 3
    assert tao.bmad_com()["csr_and_space_charge_on"] is True


def test_bmad_cavity_phase_round_trip_keeps_the_sign_of_the_chirp(tmp_path):
    """Energy gain goes as ``cos(phi0)``; only the chirp exposes a flipped sign."""
    header = (
        "beginning[e_tot] = 1.35e8\n"
        "beginning[beta_a] = 5.0\n"
        "beginning[beta_b] = 3.0\n"
        "parameter[geometry] = open\n"
        "parameter[particle] = electron\n"
    )
    source, exported, _ = _roundtrip(
        tmp_path,
        header + "C1: lcavity, l = 1.0, rf_frequency = 2856e6, voltage = 2e7, "
        "phi0 = -0.05972222\n"
        "L: line = (C1)\n"
        "use, L\n",
        header=header,
        position_mode="s",
    )

    def cavity(path):
        tao = _tao(path)
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
    # Bmad's head (z > 0) loses energy at negative phi0, which compresses.
    assert chirp_before[1e-3] < 0.0 < chirp_before[-1e-3]


def test_reserved_names_export_to_a_lattice_bmad_will_actually_parse(tmp_path):
    """Bmad rejects reserved words and element-class names as element names; ``END``
    clashes with its own end-of-branch element.
    """
    from laura.models.element import Marker, Quadrupole
    from laura.models.elementList import SectionLattice
    from laura.models.physical import PhysicalElement, Position

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
        body = _to_bmad(section, particle="Electron")
    path = _write(tmp_path, "beginning[e_tot] = 1.35e8\n" + _TWISS + body)

    names = list(_tao_elements(path))

    assert "BEGINNING_ELEMENT" in names
    assert "MARKER_ELEMENT" in names
    assert "END_ELEMENT" in names
    assert names.index("END_ELEMENT") < len(names) - 1
    assert names[-1] == "END"


_WAKE_HEADER = (
    "beginning[p0c] = 1.35e8\n"
    + _TWISS
    + "parameter[geometry] = open\nparameter[particle] = electron\n"
)
_WAKE_LATTICE = (
    _WAKE_HEADER
    + """C1: lcavity, l = 2.0, rf_frequency = 2856e6, voltage = 0, phi0 = 0,
    sr_wake = {z_max = 0.01, amp_scale = 2, scale_with_length = F,
      longitudinal = {1e14, 200, 0, 0.25, none}}
M1: marker, sr_wake = {z_max = 0.01, amp_scale = 1, scale_with_length = F,
      longitudinal = {5e13, 500, 1000, 0.25, none}}
SPLIT: marker, superimpose, ref = C1, offset = 0
L: line = (C1, M1)
use, L
"""
)


def _wake_model(tmp_path):
    """Import a lattice whose wake sits on a cavity, on a lord, and on a marker."""
    return _elements(_write(tmp_path, _WAKE_LATTICE, "wakes.bmad"), position_mode="s")


def test_a_short_range_wake_is_imported_as_sampled_arrays(tmp_path):
    """Modes are sampled to a grid; a quarter-turn mode gives W(0) = amp_scale*amp."""
    elements = _wake_model(tmp_path)

    wake = elements["C1"].simulation.wakefield_definition
    assert wake.field_type == "LongitudinalWake"
    assert wake.z.value.val[-1] == 0.0
    assert wake.z.value.val[0] == pytest.approx(-0.01)
    assert wake.Wz.value.val[-1] == pytest.approx(2.0e14)


def test_a_super_lord_is_imported_whole_and_keeps_its_wake(tmp_path):
    """``lat_list`` returns only super-slaves; the importer reassembles the lord."""
    elements = _wake_model(tmp_path)

    assert not [name for name in elements if name.startswith("C1#")]
    wake = elements["C1"].simulation.wakefield_definition
    assert wake is not None, "C1 lost its wake"
    assert wake.Wz.value.val[-1] == pytest.approx(2.0e14)
    assert elements["C1"].physical.length == pytest.approx(2.0)
    assert elements["SPLIT"].subelement == "C1"


def test_a_wake_on_a_marker_is_imported_too(tmp_path):
    """Bmad hangs resistive-wall wakes off markers, built by a separate path."""
    elements = _wake_model(tmp_path)

    wake = elements["M1"].simulation.wakefield_definition
    assert wake is not None
    assert wake.Wz.value.val[-1] == pytest.approx(5.0e13)


def test_an_exported_element_keeps_its_wake_beside_it(tmp_path):
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
    """Bmad applies tabulated wakes by FFT: indexed by trailing minus source position
    (negative), and w(0) is not halved like the mode sum's self-wake.
    """
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

    modes = _write(
        tmp_path,
        _WAKE_HEADER
        + "W1: lcavity, l = 2.0, rf_frequency = 2856e6, voltage = 0, phi0 = 0,\n"
        "    sr_wake = {z_max = 0.01, amp_scale = 2, scale_with_length = F,\n"
        "      longitudinal = {1e14, 200, 0, 0.25, none}}\n"
        "L: line = (W1)\nuse, L\n",
        "modes.bmad",
    )

    from laura.models.elementList import SectionLattice
    from laura.models.physical import Position

    element = elements["C1"].model_copy(deep=True)
    element.name = "W1"
    element.physical.length = 2.0
    element.simulation.wakefield_definition.filename = "W1_wake.bmad"
    element.physical.middle = Position(z=1.0)
    section = SectionLattice(
        name="L", order=["W1"], elements=[element], geometry="open"
    )
    # to_bmad writes the wake sidecar to the cwd and refers to it by name.
    monkeypatch.chdir(tmp_path)
    sampled = _write(
        tmp_path, _WAKE_HEADER + _to_bmad(section, particle="Electron"), "sampled.bmad"
    )

    from_modes, from_table = track(modes), track(sampled)

    # Point particles interpolate the table, so agreement is ~1e-7.
    assert from_table == pytest.approx(from_modes, rel=1e-6)
    assert from_modes[0] < 0.0


def test_bmad_split_bend_keeps_its_exit_fringe_field(tmp_path):
    """Bmad splits the fringe between slaves; reassembled, ``B`` equals ``WHOLE``."""
    source = _write(
        tmp_path,
        _OPEN + "D: drift, l = 0.5\n"
        "B: sbend, l = 1.0, angle = 0.1, fint = 0.45, hgap = 0.015\n"
        "WHOLE: sbend, l = 1.0, angle = 0.1, fint = 0.45, hgap = 0.015\n"
        "M: marker, superimpose, ref = B, offset = 0.0\n"
        "L: line = (D, B, D, WHOLE)\n"
        "use, L\n",
    )
    converted = _elements(source)
    bends = {name.upper(): element for name, element in converted.items()}

    assert not [name for name in bends if name.startswith("B#")]
    assert bends["M"].subelement == "B"

    split = bends["B"].magnetic
    assert bends["B"].physical.length == pytest.approx(1.0)
    assert split.edge_field_integral == pytest.approx(0.45)
    assert split.half_gap == pytest.approx(0.015)
    assert split.exit_fringe_integral == pytest.approx(0.45)
    assert split.exit_half_gap == pytest.approx(0.015)

    whole = bends["WHOLE"].magnetic
    # FINTX defaults to FINT; HGAPX has no combined slot.
    assert whole.edge_field_integral_exit == pytest.approx(0.45)
    assert whole.exit_gap is None
    assert whole.exit_fringe_integral == pytest.approx(0.45)
    assert whole.exit_half_gap == pytest.approx(0.015)


_BETA10_HEADER = (
    _OPEN
    + "beginning[beta_a] = 10\nbeginning[beta_b] = 10\nparameter[particle] = electron\n"
)
SKEW_LATTICE = (
    _BETA10_HEADER + "qn: quadrupole, l = 0.5, k1 = 4.0\n"
    "qs: quadrupole, l = 0.5, a1 = 0.15, scale_multipoles = F\n"
    "qm: quadrupole, l = 0.5, k1 = 4.0, a1 = 0.4, b2 = 0.45, scale_multipoles = F\n"
    "oct: octupole, l = 0.5, k3 = 15.0, a3 = 0.16666666666666666,"
    " scale_multipoles = F\n"
    "bn: sbend, l = 2.0, angle = 0.05, a1 = 0.02, scale_multipoles = F\n"
    "lat: line = (qn, qs, qm, oct, bn)\n"
    "use, lat\n"
)


def test_native_an_bn_multipoles_import_onto_ordinary_magnets(tmp_path):
    """Tao reports ``an``/``bn`` with 1/n! and omits the main ``kN``, so the two add."""
    elements = _elements(_write(tmp_path, SKEW_LATTICE))

    def poles(name, order):
        multipole = getattr(elements[name].magnetic.multipoles, f"K{order}L")
        return multipole.normal, multipole.skew

    assert poles("QN", 1) == (pytest.approx(2.0), 0.0)
    assert elements["QN"].magnetic.skew is False

    # Pure-skew magnet: ``KnL()`` needs ``magnetic.skew`` or reads zero.
    assert poles("QS", 1) == (0.0, pytest.approx(0.15))
    assert elements["QS"].magnetic.skew is True
    assert elements["QS"].magnetic.KnL(1) == pytest.approx(0.15)

    assert poles("QM", 1) == (pytest.approx(2.0), pytest.approx(0.4))
    assert poles("QM", 2) == (pytest.approx(0.9), 0.0)
    assert elements["QM"].magnetic.skew is False

    # a3 = Ks3L / 3!, so the factorial goes back in.
    assert poles("OCT", 3) == (pytest.approx(7.5), pytest.approx(1.0))

    assert poles("BN", 0) == (pytest.approx(0.05), 0.0)
    assert poles("BN", 1) == (0.0, pytest.approx(0.02))


def test_native_skew_multipoles_survive_a_round_trip_through_tao(tmp_path):
    """Re-parse the export in Tao; compare multipole tables and 6x6 matrices."""
    from laura.translator.converters.model import MachineModelTranslator

    source = _write(tmp_path, SKEW_LATTICE)
    model = BmadLatticeImporter(
        lattice_file=str(source), libtao=str(LIBTAO)
    ).create_machine_model(min_section_length=1)
    exported = tmp_path / "skew_round_trip.bmad"
    exported.write_text(
        "\n".join(
            text
            for lattice in MachineModelTranslator.from_machine(model).to_bmad().values()
            for text in lattice.values()
        )
    )

    original, round_tripped = _tao(source), _tao(exported)

    def table(tao, name):
        return {
            row["index"]: (row["An"], row["Bn"])
            for row in tao.ele_multipoles(name)["data"]
        }

    def mat6(tao, name):
        matrix = tao.ele_mat6(name)
        return np.array([matrix[str(row)] for row in range(1, 7)])

    for name in ("QN", "QS", "QM", "OCT", "BN"):
        before, after = table(original, name), table(round_tripped, name)
        assert before.keys() == after.keys(), name
        for order in before:
            assert after[order] == pytest.approx(before[order]), (name, order)
        assert mat6(round_tripped, name) == pytest.approx(mat6(original, name)), name

    assert round_tripped.lat_list("*", "ele.s")[-1] == pytest.approx(
        original.lat_list("*", "ele.s")[-1]
    )


ROLLED_BEND_LATTICE = (
    _BETA10_HEADER + "b1: sbend, l = 1.0, angle = 0.05, ref_tilt = 0.1\n"
    "q2: quadrupole, l = 0.2, k1 = 1.0\n"
    "d: drift, l = 0.5\n"
    "lat: line = (b1, d, q2)\n"
    "use, lat\n"
)


@pytest.mark.parametrize("position_mode", ["floor", "s"])
def test_native_rolled_bend_exports_as_ref_tilt_without_patches(
    tmp_path, position_mode
):
    """``ref_tilt`` is self-closing: a rolled bend needs no patch pair, either mode."""
    model = BmadLatticeImporter(
        lattice_file=str(_write(tmp_path, ROLLED_BEND_LATTICE)),
        libtao=str(LIBTAO),
        position_mode=position_mode,
    ).create_machine_model(min_section_length=1)

    written = _to_bmad(next(iter(model.sections.values())))

    assert "ref_tilt = 0.1" in written
    assert "patch" not in written.lower()


def test_zero_strength_multipoles_keep_their_declared_order_and_skew(tmp_path):
    # LCLS CQ01/SQ01: strengthless multipoles; Tao reports no poles, so order and skew
    # tilt come from the lattice source.
    elements = _elements(
        _write(
            tmp_path,
            _ELECTRON + "cq: multipole, k1l = 0\n"
            "sq: multipole, k1l = 0, t1\n"
            "d: drift, l = 1\n"
            "lat: line = (d, cq, sq, d)\n"
            "use, lat\n",
        )
    )

    assert elements["CQ"].hardware_type == "Quadrupole"
    assert not elements["CQ"].magnetic.skew
    assert elements["CQ"].magnetic.KnL(1) == 0
    assert elements["SQ"].hardware_type == "Quadrupole"
    assert elements["SQ"].magnetic.skew


def test_a_multipole_that_bends_the_reference_is_a_thin_bend(tmp_path):
    # LCLS DIAG0 DYQDG001: a vertical thin bend.
    from laura.translator.utils.bmad.geometry import bmad_survey_frame

    elements = _elements(
        _write(
            tmp_path,
            _ELECTRON + "parameter[geometry] = open\n"
            "dy: multipole, k0l = -0.01, t0, k0l_status = bends_reference\n"
            "m: marker\n"
            "d: drift, l = 1\n"
            "lat: line = (d, dy, d, m)\n"
            "use, lat\n",
        )
    )

    bend = elements["DY"]
    assert bend.hardware_type == "Dipole"
    assert bend.magnetic.KnL(0) == pytest.approx(-0.01)
    assert bend.magnetic.tilt == pytest.approx(math.pi / 2)
    np.testing.assert_allclose(
        bmad_survey_frame(bend, "end"),
        elements["M"].physical.rotation_matrix,
        atol=1e-12,
    )
    assert elements["M"].physical.middle.y == pytest.approx(0.01, rel=1e-4)


def test_lattice_source_follows_calls_through_environment_variables(
    tmp_path, monkeypatch
):
    from laura.translator.converters.codes.bmad import (
        _CALL_RE,
        _declared_multipole_terms,
    )
    from laura.translator.converters.codes.importer import read_with_calls

    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "mags.bmad").write_text("sq: multipole, k1l = 0, t1 ! skew\n")
    main = tmp_path / "main.bmad"
    main.write_text("call, file = $ZERO_ROOT/sub/mags.bmad\n")
    monkeypatch.setenv("ZERO_ROOT", str(tmp_path))

    text = read_with_calls(main, _CALL_RE)
    assert "sq: multipole" in text
    assert _declared_multipole_terms(text) == {"sq": {1: True}}


@pytest.mark.parametrize(
    "frequency, length",
    # The lengths LCLS-II's 1.3 and 3.9 GHz cavities import with.
    [(1.3e9, 1.0377431238461539), (3.9e9, 0.3459143746153846)],
)
def test_a_cavity_a_whole_number_of_cells_long_keeps_every_cell(frequency, length):
    """``l = 9*lambda/2`` is a hair under nine float cells; don't floor one away."""
    from scipy.constants import speed_of_light

    from laura.translator.converters.codes.bmad import _bmad_cavity_cells

    cell = speed_of_light / (2 * frequency)
    assert length // cell == 8
    assert _bmad_cavity_cells(-1, length, length, cell) == 9
    assert _bmad_cavity_cells(0, None, length, cell) == 9
    assert _bmad_cavity_cells(0, None, length - 1e-6, cell) == 8


def test_a_travelling_wave_cavity_keeps_its_voltage_round_trip(tmp_path):
    """``to_bmad`` sets voltage = peak field * L_eff / sqrt(2); import inverts it."""
    import re

    from scipy.constants import speed_of_light

    source = _write(
        tmp_path,
        "parameter[particle] = electron\n"
        "parameter[p0c] = 135e6\n"
        "parameter[geometry] = open\n"
        "c: lcavity, l = 2.8692, rf_frequency = 2856e6, voltage = 46.2080928e6, "
        "cavity_type = traveling_wave, phi0 = -0.0597222222\n"
        "lat: line = (c)\n"
        "use, lat\n",
    )
    cavity = _elements(source)["C"]

    # 2pi/3: cell = lambda/3, 82 span 2.8692 m; Bmad calls one coupler, so 81 import.
    assert cavity.cavity.mode_denominator == 3
    assert cavity.cavity.cell_length == pytest.approx(
        speed_of_light / (3 * 2856e6)
    )
    assert cavity.cavity.n_cells == 81
    # A peak field, not the 46.2 MV the deck states.
    assert cavity.simulation.field_amplitude == pytest.approx(21.9e6, rel=0.05)

    from laura.translator.converters.cavity import RFCavityTranslator

    written = RFCavityTranslator(**cavity.model_dump()).to_bmad()
    volt = float(re.search(r"voltage\s*=\s*([-0-9.eE+]+)", written).group(1))
    assert volt == pytest.approx(46.2080928e6, rel=1e-9)


_PATCH_LATTICE = (
    "parameter[particle] = electron\n"
    "parameter[p0c] = 8e9\n"
    "parameter[geometry] = open\n"
    "d: drift, l = 0.1\n"
    "p: patch, {}\n"
    "lat: line = (d, p, d)\n"
    "use, lat\n"
)


def test_a_tilt_only_patch_is_imported_as_a_roll_matrix(tmp_path):
    """A roll-only patch is linear, so imports as a roll matrix (LCLS HXR dump)."""
    tilt = 0.174519678252
    source = _write(tmp_path, _PATCH_LATTICE.format(f"tilt = {tilt}"))
    patch = _elements(source)["P"]

    assert patch.hardware_type == "MatrixTransform"
    assert patch.physical.length == 0.0
    cos, sin = np.cos(tilt), np.sin(tilt)
    expected = np.eye(6)
    expected[0, 0] = expected[1, 1] = expected[2, 2] = expected[3, 3] = cos
    expected[0, 2] = expected[1, 3] = sin
    expected[2, 0] = expected[3, 1] = -sin
    assert np.allclose(patch.simulation.r_matrix, expected)


def test_a_patch_that_moves_the_frame_is_still_dropped(tmp_path):
    """Only the roll is representable; an offset still has nowhere to go."""
    importer, branch = _import(
        _write(tmp_path, _PATCH_LATTICE.format("x_offset = 0.01")), position_mode="s"
    )
    with pytest.warns(UserWarning, match="moves the reference frame"):
        elements = importer.create_laura_element_dictionary(1)[branch]
    assert "P" not in elements
