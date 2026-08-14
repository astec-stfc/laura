import warnings

import pytest


xt = pytest.importorskip("xtrack")

from laura.translator.converters.codes.xsuite import XsuiteLatticeImporter
from laura.models.element import Combined_Corrector, Marker
from laura.models.elementList import ElementList, SectionLattice
from laura.translator.converters.section import SectionLatticeTranslator


def test_xsuite_importer_uses_common_s_lifecycle():
    line = xt.Line(
        elements=[
            xt.Drift(length=1.0),
            xt.Quadrupole(length=0.5, k1=0.2),
            xt.Bend(length=0.4, angle=0.1),
            xt.Cavity(voltage=3e6, frequency=4e8, lag=30),
            xt.Marker(),
        ],
        element_names=["drift", "quad", "bend", "cavity", "marker"],
    )

    importer = XsuiteLatticeImporter(line=line, name="test")
    elements = importer.create_element_dictionary()
    layout = importer.create_layout()

    assert list(elements) == ["quad", "bend", "cavity", "marker"]
    assert elements["quad"].magnetic.KnL(1) == pytest.approx(0.1)
    assert elements["bend"].magnetic.KnL(0) == pytest.approx(-0.1)
    assert elements["cavity"].cavity.phase == pytest.approx(30)
    assert layout.sections["test"].order == list(elements)
    assert elements["quad"].physical.middle.z == pytest.approx(1.25)


def test_xsuite_importer_retains_environment_reference(tmp_path):
    env = xt.Environment()
    env["quad_k1l"] = 0.3
    env.new("quad", xt.Quadrupole, length=0.5, k1="quad_k1l / 0.5")
    line = env.new_line(components=["quad"])
    source = tmp_path / "line.json"
    line.to_json(source)

    importer = XsuiteLatticeImporter(source_file=str(source), name="test")
    elements = importer.create_element_dictionary()
    layout = importer.create_layout()

    assert importer.functional_definitions == {"quad_k1l": pytest.approx(0.3)}
    assert elements["quad"].magnetic.multipoles.K1L.normal == "quad_k1l"
    assert layout.functional_definitions == {"quad_k1l": pytest.approx(0.3)}
    assert layout.sections["test"].functional_definitions == {
        "quad_k1l": pytest.approx(0.3)
    }


def test_xsuite_environment_json_builds_one_section_per_line(tmp_path):
    env = xt.Environment()
    env["quad_k1l"] = 0.3
    env.new("q1", xt.Quadrupole, length=0.5, k1="quad_k1l / 0.5")
    env.new("q2", xt.Quadrupole, length=0.5, k1="quad_k1l / 0.5")
    env.new_line(name="section_a", components=["q1"])
    env.new_line(name="section_b", components=["q2"])
    source = tmp_path / "environment.json"
    env.to_json(source)

    layout = XsuiteLatticeImporter(source_file=str(source)).create_layout()

    assert list(layout.sections) == ["section_a", "section_b"]
    assert layout.functional_definitions == {"quad_k1l": pytest.approx(0.3)}


def test_xsuite_importer_maps_monitors_and_transverse_limits():
    line = xt.Line(
        elements=[
            xt.BeamPositionMonitor(
                start_at_turn=0, stop_at_turn=1, frev=1, sampling_frequency=1
            ),
            xt.BeamProfileMonitor(
                start_at_turn=0,
                stop_at_turn=1,
                frev=1,
                sampling_frequency=1,
                n=4,
                range=0.02,
            ),
            xt.ParticlesMonitor(start_at_turn=0, stop_at_turn=1, num_particles=1),
            xt.LimitEllipse(a=0.02, b=0.01),
            xt.LimitRect(min_x=-0.03, max_x=0.01, min_y=-0.01, max_y=0.01),
            xt.LimitPolygon(
                x_vertices=[-0.02, 0.02, 0.01],
                y_vertices=[-0.01, -0.01, 0.02],
            ),
            xt.LongitudinalLimitRect(
                min_zeta=-0.1,
                max_zeta=0.1,
                min_pzeta=-0.01,
                max_pzeta=0.01,
            ),
        ],
        element_names=["bpm", "profile", "particles", "ellipse", "rect", "polygon", "long"],
    )

    with pytest.warns(UserWarning) as caught:
        elements = XsuiteLatticeImporter(line=line).create_element_dictionary()

    assert elements["bpm"].hardware_type == "Beam_Position_Monitor"
    assert elements["profile"].hardware_type == "Screen"
    assert elements["particles"].hardware_type == "Screen"
    assert elements["ellipse"].hardware_type == "Collimator"
    assert elements["ellipse"].aperture.shape == "elliptical"
    assert elements["ellipse"].aperture.horizontal_size == pytest.approx(0.04)
    assert elements["rect"].aperture.horizontal_size == pytest.approx(0.04)
    assert elements["polygon"].aperture.vertical_size == pytest.approx(0.03)
    assert "long" not in elements

    messages = [str(item.message) for item in caught]
    assert any(
        "ParticlesMonitor" in message and "reduced to a Screen" in message
        for message in messages
    )
    assert any("LimitPolygon" in message and "bounding size" in message for message in messages)
    assert any("LongitudinalLimitRect" in message and "skipping" in message for message in messages)


def test_dipole_edge_adjacent_to_bend_is_merged_not_dropped():
    """A DipoleEdge immediately bracketing a Bend (the shape produced by,
    e.g., MAD-X-to-Xtrack conversion, where edge focusing is split into
    separate elements rather than baked into the Bend's own edge_entry_*/
    edge_exit_* attributes) must have its e1/hgap/fint folded into that
    Bend's entrance_edge_angle/exit_edge_angle/gap/edge_field_integral --
    mirroring how the MAD-X importer already folds standalone `dipedge`
    elements into their dipole. No warning, no leftover Marker for the
    edge: the data is fully preserved on the Bend, not discarded."""
    line = xt.Line(
        elements=[
            xt.DipoleEdge(k=0.1, e1=0.05, hgap=0.02, fint=0.4, side="entry"),
            xt.Bend(k0=0.1, length=1.0),
            xt.DipoleEdge(k=0.1, e1=0.03, hgap=0.02, fint=0.4, side="exit"),
        ],
        element_names=["entry_edge", "bend", "exit_edge"],
    )

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        elements = XsuiteLatticeImporter(line=line).create_element_dictionary()

    assert list(elements) == ["bend"]
    bend = elements["bend"]
    assert bend.magnetic.entrance_edge_angle == pytest.approx(0.05)
    assert bend.magnetic.exit_edge_angle == pytest.approx(0.03)
    assert bend.magnetic.gap == pytest.approx(0.04)
    assert bend.magnetic.edge_field_integral == pytest.approx(0.4)


def test_dipole_edge_with_own_bend_data_is_not_overridden():
    """When the Bend already carries its own non-zero edge attributes (the
    normal shape for a LAURA-exported lattice), that data wins -- there's
    no adjacent DipoleEdge in this case, but the merge logic must not
    require one to leave the Bend's own values alone."""
    line = xt.Line(
        elements=[
            xt.Bend(
                k0=0.1,
                length=1.0,
                edge_entry_angle=0.07,
                edge_exit_angle=0.08,
                edge_entry_hgap=0.03,
                edge_entry_fint=0.5,
            ),
        ],
        element_names=["bend"],
    )

    bend = XsuiteLatticeImporter(line=line).create_element_dictionary()["bend"]

    assert bend.magnetic.entrance_edge_angle == pytest.approx(0.07)
    assert bend.magnetic.exit_edge_angle == pytest.approx(0.08)
    assert bend.magnetic.gap == pytest.approx(0.06)
    assert bend.magnetic.edge_field_integral == pytest.approx(0.5)


def test_orphan_dipole_edge_conversion_is_flagged():
    """A DipoleEdge with no adjacent Bend/RBend has nothing to merge into --
    it must still warn and fall back to a bare Marker, like any other
    lossy conversion, rather than silently dropping the edge data."""
    line = xt.Line(
        elements=[xt.DipoleEdge(k=0.1, e1=0.05, hgap=0.02, fint=0.4), xt.Marker()],
        element_names=["edge", "marker"],
    )

    with pytest.warns(UserWarning, match="DipoleEdge.*edge-focusing"):
        elements = XsuiteLatticeImporter(line=line).create_element_dictionary()

    assert elements["edge"].hardware_type == "Marker"

    assert elements["edge"].hardware_type == "Marker"


def test_laura_xsuite_json_preserves_ambiguous_types_and_definitions(tmp_path):
    elements = {
        "marker": Marker(
            name="marker", machine_area="test", physical={"s": 0, "length": 0}
        ),
        "corrector": Combined_Corrector(
            name="corrector",
            machine_area="test",
            physical={"s": 0.5, "length": 0.1},
            magnetic={
                "length": 0.1,
                "horizontal_kick": 0.02,
                "vertical_kick": 0.03,
            },
        ),
    }
    section = SectionLattice(
        name="line",
        order=list(elements),
        elements=ElementList(elements=elements),
        functional_definitions={"unused_zero": 0},
    )
    section.resolve_positions(elements)
    translator = SectionLatticeTranslator.from_section(section)
    translator.directory = str(tmp_path)
    translator.to_xsuite(beam_length=1, save=True)

    importer = XsuiteLatticeImporter(source_file=str(tmp_path / "line.json"))
    imported = importer.create_element_dictionary()

    assert imported["marker"].hardware_type == "Marker"
    assert imported["corrector"].hardware_type == "Combined_Corrector"
    assert imported["corrector"].magnetic.horizontal_kick == pytest.approx(0.02)
    assert imported["corrector"].magnetic.vertical_kick == pytest.approx(0.03)
    assert importer.functional_definitions == {"unused_zero": 0}


def _sliced_line():
    """A short thick line, sliced the way a tracking-ready lattice arrives."""
    line = xt.Line(
        elements=[
            xt.Drift(length=1.0),
            xt.Quadrupole(length=0.5, k1=0.2),
            xt.Bend(length=0.4, angle=0.1),
        ],
        element_names=["d", "quad", "bend"],
    )
    line.slice_thick_elements(
        slicing_strategies=[xt.Strategy(slicing=xt.Uniform(4))]
    )
    return line


def test_sliced_line_imports_the_thick_elements_it_came_from():
    """slice_thick_elements replaces each magnet with a run of thin slices for
    tracking. Those are a numerical artefact, not hardware: importing them
    would turn a handful of magnets into a crowd of zero-length kicks with
    their strengths and positions divided between them. The importer follows
    Xtrack's own _line_before_slicing back to the thick elements."""
    line = _sliced_line()
    assert len(line.element_names) > 3  # actually sliced

    with pytest.warns(UserWarning, match="was sliced into"):
        importer = XsuiteLatticeImporter(line=line, name="test")
    elements = importer.create_element_dictionary()

    assert list(elements) == ["quad", "bend"]
    assert elements["quad"].physical.length == pytest.approx(0.5)
    assert elements["quad"].magnetic.KnL(1) == pytest.approx(0.1)
    assert elements["bend"].magnetic.KnL(0) == pytest.approx(-0.1)


def test_sliced_line_warns_once_not_on_every_revalidation():
    """The pre-slicing view shares the sliced line's __dict__, so it reports a
    _line_before_slicing of its own. Without recognising that, every field
    assignment re-ran the validator and warned again."""
    with pytest.warns(UserWarning, match="was sliced into") as caught:
        importer = XsuiteLatticeImporter(line=_sliced_line(), name="test")
        importer.create_element_dictionary()
        importer.create_layout()

    assert len([item for item in caught if "was sliced into" in str(item.message)]) == 1


def test_use_sliced_keeps_the_slices():
    importer = XsuiteLatticeImporter(line=_sliced_line(), name="test", use_sliced=True)
    assert len(importer.line.element_names) > 3


def test_thin_multipole_order_selects_the_magnet_type():
    """An Xtrack Multipole holds every order in one element, so its LAURA type
    comes from the highest knl/ksl entry actually set."""
    line = xt.Line(
        elements=[
            xt.Multipole(knl=[0.0, 0.3]),
            xt.Multipole(knl=[0.0, 0.0, 0.7]),
            xt.Multipole(knl=[0.0, 0.0, 0.0, 1500.0]),
            xt.Multipole(ksl=[0.0, 0.4]),
            xt.Multipole(knl=[0.0]),
        ],
        element_names=["quad", "sext", "oct", "skew", "empty"],
    )

    elements = XsuiteLatticeImporter(line=line).create_element_dictionary()

    assert elements["quad"].hardware_type == "Quadrupole"
    assert elements["sext"].hardware_type == "Sextupole"
    assert elements["oct"].hardware_type == "Octupole"
    assert elements["oct"].magnetic.KnL(3) == pytest.approx(1500.0)
    assert elements["skew"].hardware_type == "Quadrupole"
    # No order set anywhere: stays generic rather than being guessed into a type.
    assert elements["empty"].hardware_type == "Generic"


def test_empty_multipole_imports_as_a_bare_magnet_with_a_warning():
    """A Multipole with nothing set carries no order information, so it stays a
    generic Magnet, left with MagneticElement's own all-zero default rather
    than an asserted order."""
    line = xt.Line(elements=[xt.Multipole(knl=[0.0])], element_names=["empty"])

    with pytest.warns(UserWarning, match="order could not be determined"):
        element = XsuiteLatticeImporter(line=line).create_element_dictionary()["empty"]

    assert element.hardware_type == "Generic"
    assert type(element).__name__ == "Magnet"
    assert all(element.magnetic.KnL(order) == 0.0 for order in range(5))


def test_generic_magnet_can_read_back_its_multipoles():
    """A generic Magnet gets the enriched MagneticElement, matching the schema's
    own `range: MagneticElement`. Without it the class held the bare generated
    base, which stores multipoles but has no KnL to read them -- so an order
    with no dedicated LAURA class (order 4 here) went in and could not come
    out."""
    line = xt.Line(
        elements=[xt.Multipole(knl=[0.0, 0.0, 0.0, 0.0, 7.0])],
        element_names=["deca"],
    )

    element = XsuiteLatticeImporter(line=line).create_element_dictionary()["deca"]

    assert type(element).__name__ == "Magnet"
    assert type(element.magnetic).__name__ == "MagneticElement"
    assert element.magnetic.KnL(4) == pytest.approx(7.0)
    assert element.magnetic.KnL(1) == pytest.approx(0.0)


def test_multipole_keeps_every_order_not_just_the_one_it_is_named_for():
    """The LAURA type comes from the highest order set, but the lower orders
    are part of the same element and must survive with it."""
    line = xt.Line(
        elements=[xt.Multipole(knl=[0.05, 0.3, 0.7], ksl=[0.0, 0.4])],
        element_names=["combined"],
    )

    element = XsuiteLatticeImporter(line=line).create_element_dictionary()["combined"]

    assert element.hardware_type == "Sextupole"
    assert element.magnetic.KnL(0) == pytest.approx(0.05)
    assert element.magnetic.KnL(1) == pytest.approx(0.3)
    assert element.magnetic.KnL(2) == pytest.approx(0.7)
    assert element.magnetic.multipoles.K1L.skew == pytest.approx(0.4)


def test_specialised_element_types_are_imported():
    """These have LAURA translators and export mappings; without the matching
    import entries a natively-authored Xtrack line lost them on the way in."""
    import numpy as np

    r_matrix = np.eye(6)
    r_matrix[0, 1] = 2.0
    t_matrix = np.zeros((6, 6, 6))
    t_matrix[0, 1, 1] = 3.0

    line = xt.Line(
        elements=[
            xt.SecondOrderTaylorMap(
                k=np.arange(6.0), R=r_matrix, T=t_matrix, length=1.5
            ),
            xt.CrabCavity(length=0.3, crab_voltage=2e6, frequency=4e8, lag=45),
            xt.Wire(L_phy=0.2, L_int=0.25, current=350.0, xma=0.01, yma=0.02),
            xt.RFMultipole(
                voltage=1e6, frequency=3e8, lag=30, knl=[0.0, 0.5], ksl=[0.0, 0.1]
            ),
            xt.ACDipole(volt=1e5, freq=0.31, lag=0.25, ramp=[0, 100, 200, 300], plane="v"),
            xt.ACDipole(volt=2e5, freq=0.28, lag=0.5, ramp=[0, 50, 100, 150], plane="h"),
        ],
        element_names=["taylor", "crab", "wire", "rfmult", "acd_v", "acd_h"],
    )

    elements = XsuiteLatticeImporter(line=line).create_element_dictionary()

    assert elements["taylor"].hardware_type == "MatrixTransform"
    assert elements["taylor"].simulation.c_matrix[1] == pytest.approx(1.0)
    assert elements["taylor"].simulation.r_matrix[0, 1] == pytest.approx(2.0)
    assert elements["taylor"].simulation.t_matrix[0, 1, 1] == pytest.approx(3.0)

    assert elements["crab"].hardware_type == "CrabCavity"
    # Xtrack keeps the deflecting voltage as crab_voltage, not voltage.
    assert elements["crab"].simulation.field_amplitude == pytest.approx(2e6)
    assert elements["crab"].cavity.frequency == pytest.approx(4e8)
    assert elements["crab"].cavity.phase == pytest.approx(45)

    assert elements["wire"].hardware_type == "Wire"
    assert elements["wire"].simulation.current == pytest.approx(350.0)
    assert elements["wire"].simulation.interaction_length == pytest.approx(0.25)
    assert elements["wire"].simulation.horizontal_offset == pytest.approx(0.01)

    assert elements["rfmult"].hardware_type == "RFMultipole"
    assert elements["rfmult"].simulation.field_amplitude == pytest.approx(1e6)
    assert list(elements["rfmult"].simulation.knl)[1] == pytest.approx(0.5)
    assert list(elements["rfmult"].simulation.ksl)[1] == pytest.approx(0.1)

    # ACDipole carries its plane as data, so the type is resolved per element.
    assert elements["acd_v"].hardware_type == "Vertical_AC_Dipole"
    assert elements["acd_h"].hardware_type == "Horizontal_AC_Dipole"
    assert elements["acd_v"].simulation.field_amplitude == pytest.approx(1e5)
    assert list(elements["acd_v"].simulation.ramp) == [0, 100, 200, 300]


def test_ac_dipole_with_an_unknown_plane_warns_and_falls_back():
    """Xtrack validates `plane` on assignment, so it can never hold a nonsense
    string -- but it is None on an ACDipole built without one, and there is no
    plane to read off it then."""
    line = xt.Line(
        elements=[xt.ACDipole(volt=1e5, freq=0.3, lag=0, ramp=[0, 1, 2, 3])],
        element_names=["acd"],
    )
    assert line.element_dict["acd"].plane is None

    with pytest.warns(UserWarning, match="neither 'h' nor 'v'"):
        element = XsuiteLatticeImporter(line=line).create_element_dictionary()["acd"]

    assert element.hardware_type == "Horizontal_AC_Dipole"


def test_bend_defined_by_k0_keeps_its_bending_strength():
    """Xtrack lets a Bend be defined by k0 (the dipole field) or by angle/h
    (the reference curvature). A bend built from k0 alone leaves h -- and so
    angle -- at zero, so reading angle discarded its strength entirely."""
    line = xt.Line(elements=[xt.Bend(length=1.0, k0=0.1)], element_names=["bend"])
    assert line.element_dict["bend"].angle == 0.0  # the trap

    element = XsuiteLatticeImporter(line=line).create_element_dictionary()["bend"]

    assert element.magnetic.KnL(0) == pytest.approx(-0.1)


def test_bend_defined_by_angle_is_unchanged():
    """The k0 == 'from_h' case must still read through angle."""
    line = xt.Line(elements=[xt.Bend(length=0.4, angle=0.1)], element_names=["bend"])
    assert isinstance(line.element_dict["bend"].k0, str)

    element = XsuiteLatticeImporter(line=line).create_element_dictionary()["bend"]

    assert element.magnetic.KnL(0) == pytest.approx(-0.1)


def test_per_metre_strength_variable_is_rescaled_to_integrated():
    """LAURA's own export writes `k1 = vars['k1l'] / length`, so the variable is
    already an integrated strength. A hand-written or MAD-X-converted lattice
    writes `k1 = vars['k1']` -- a strength *per metre*. Adopting that variable
    as K1L dropped the `* L` and left the strength wrong by a factor of the
    element length, while still looking parametrised."""
    env = xt.Environment()
    env["k2sf"] = -0.052
    env.new("sf", xt.Sextupole, length=1.5, k2="k2sf")
    line = env.new_line(components=["sf"])

    importer = XsuiteLatticeImporter(line=line, name="test")
    element = importer.create_element_dictionary()["sf"]

    # The parametrisation is kept, not flattened to a number ...
    assert element.magnetic.multipoles.K2L.normal == "k2sf"
    # ... and the definition now holds the integrated value.
    assert importer.functional_definitions["k2sf"] == pytest.approx(-0.052 * 1.5)

    # Resolving a symbol needs the definitions registered, which happens when
    # the section/layout is built.
    importer.create_layout()
    assert element.magnetic.KnL(2) == pytest.approx(-0.052 * 1.5)


def test_integrated_strength_variable_is_left_alone():
    """The `vars['x'] / length` form LAURA itself emits is already integrated
    and must not be scaled again."""
    env = xt.Environment()
    env["quad_k1l"] = 0.3
    env.new("quad", xt.Quadrupole, length=0.5, k1="quad_k1l / 0.5")
    line = env.new_line(components=["quad"])

    importer = XsuiteLatticeImporter(line=line, name="test")
    element = importer.create_element_dictionary()["quad"]

    assert element.magnetic.multipoles.K1L.normal == "quad_k1l"
    assert importer.functional_definitions["quad_k1l"] == pytest.approx(0.3)
    assert element.magnetic.KnL(1) == pytest.approx(0.3)


def test_shared_per_metre_variable_with_differing_lengths_falls_back_to_numbers():
    """One variable cannot be rescaled to two different integrated values, so
    it is dropped and both elements keep their own numeric strength."""
    env = xt.Environment()
    env["k1q"] = 0.2
    env.new("short", xt.Quadrupole, length=0.5, k1="k1q")
    env.new("long", xt.Quadrupole, length=1.5, k1="k1q")
    line = env.new_line(components=["short", "long"])

    importer = XsuiteLatticeImporter(line=line, name="test")
    elements = importer.create_element_dictionary()

    assert "k1q" in importer._conflicting_symbols
    assert elements["short"].magnetic.KnL(1) == pytest.approx(0.2 * 0.5)
    assert elements["long"].magnetic.KnL(1) == pytest.approx(0.2 * 1.5)


def test_bend_per_metre_variable_keeps_the_sign_flip():
    """LAURA stores a bend's dipole term negated, so the rescaled definition
    has to carry the sign as well as the length."""
    env = xt.Environment()
    env["k0b"] = 0.1
    env.new("bend", xt.Bend, length=2.0, k0="k0b")
    line = env.new_line(components=["bend"])

    importer = XsuiteLatticeImporter(line=line, name="test")
    element = importer.create_element_dictionary()["bend"]
    importer.create_layout()

    assert element.magnetic.KnL(0) == pytest.approx(-0.2)


def test_thin_element_with_a_nominal_length_does_not_shift_the_lattice():
    """A thin Multipole can carry a nominal magnet length (for radiation) while
    occupying no space -- its table row has s_end == s. Taking that as the
    physical length laid it out as a thick element and pushed everything
    downstream along by it, accumulating over a ring."""
    corrector = xt.Multipole(knl=[0.0, 0.2], length=1.2)
    assert corrector.isthick is False and corrector.length == 1.2  # the trap

    line = xt.Line(
        elements=[xt.Drift(length=1.0), corrector, xt.Drift(length=1.0),
                  xt.Quadrupole(length=0.5, k1=0.2)],
        element_names=["d1", "corr", "d2", "quad"],
    )
    table = line.get_table()
    assert table.s_end[1] == pytest.approx(table.s[1])  # occupies no space

    elements = XsuiteLatticeImporter(line=line, name="test").create_element_dictionary()

    assert elements["corr"].physical.length == pytest.approx(0.0)
    # The nominal length is not lost -- it stays on the magnetic model.
    assert elements["corr"].magnetic.length == pytest.approx(1.2)
    # ... and the quadrupole downstream is where the source says it is.
    assert elements["quad"].physical.s == pytest.approx(float(table.s_end[3]))


def test_environment_variables_are_scaled_across_every_line():
    """An Environment's variables are shared between its lines. Scanning only
    the line being built left a variable used by the other line unscaled, and
    re-reading the definitions per line then reset it to its per-metre value."""
    env = xt.Environment()
    env["k1a"] = 0.2
    env["k1b"] = 0.3
    env.new("qa", xt.Quadrupole, length=1.5, k1="k1a")
    env.new("qb", xt.Quadrupole, length=1.5, k1="k1b")
    env.new_line(name="line_a", components=["qa"])
    env.new_line(name="line_b", components=["qb"])

    importer = XsuiteLatticeImporter(line=env, name="test")
    layout = importer.create_layout()

    assert list(layout.sections) == ["line_a", "line_b"]
    # Both variables integrated, not just the second line's.
    assert importer.functional_definitions["k1a"] == pytest.approx(0.2 * 1.5)
    assert importer.functional_definitions["k1b"] == pytest.approx(0.3 * 1.5)
    assert layout.sections["line_a"].elements.elements["qa"].magnetic.KnL(
        1
    ) == pytest.approx(0.2 * 1.5)
