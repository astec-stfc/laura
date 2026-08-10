"""BDSIM export: keyword coverage, element typing and functional parameters.

BDSIM is object-based -- ``to_bdsim`` builds real ``pybdsim.Builder`` objects
rather than formatting text -- which makes it easy for keywords to go missing
without anything raising. These tests pin the behaviours that previously broke
silently:

* pybdsim declares only two to four named parameters per builder and takes
  everything else through ``**kwargs``, so filtering on ``inspect.signature``
  dropped edge angles, fringe fields, tilt and material. Filtering is against
  ``elements_bdsim.yaml`` instead, mirroring MAD-X's ``elements_madx.yaml``.
* ``Marker`` has no ``**kwargs`` at all, so a section beam-pipe aperture raised
  ``TypeError`` for every BPM/screen/monitor in the lattice.
* gmad has no MAD-X ``:=``, so functional parameters need an inline expression
  plus a variable block included ahead of the components.
"""

import warnings

import pytest

pytest.importorskip("pybdsim")

from laura.models.element import (  # noqa: E402
    Dipole,
    Horizontal_Corrector,
    Marker,
    Quadrupole,
    Sextupole,
)
from laura.models.elementList import ElementList, SectionLattice  # noqa: E402
from laura.models.physical import PhysicalElement, Position  # noqa: E402
from laura.translator.converters.converter import translate_elements  # noqa: E402
from laura.translator.converters.section import SectionLatticeTranslator  # noqa: E402


def _translate(element):
    return translate_elements([element])[element.name]


def _quadrupole(k1l=0.6):
    quad = Quadrupole(
        name="Q1", machine_area="T", physical=PhysicalElement(length=0.2)
    )
    quad.magnetic.length = 0.2
    quad.magnetic.multipoles.K1L.normal = k1l
    return quad


def _dipole(k0l=0.15, edges="angle/2"):
    dipole = Dipole(name="D1", machine_area="T", physical=PhysicalElement(length=0.5))
    dipole.magnetic.length = 0.5
    dipole.magnetic.multipoles.K0L.normal = k0l
    dipole.magnetic.entrance_edge_angle = edges
    dipole.magnetic.exit_edge_angle = edges
    return dipole


class TestKeywordCoverage:
    def test_bend_keeps_edge_angles_and_fringe_fields(self):
        """The parameters pybdsim only accepts via **kwargs must survive."""
        gmad = str(_translate(_dipole()).to_bdsim())
        for keyword in ("e1=", "e2=", "fint=", "hgap=", "l=", "angle="):
            assert keyword in gmad, f"{keyword} missing from {gmad!r}"

    @pytest.mark.parametrize(
        "element_factory, keyword",
        [(_quadrupole, "k1="), (lambda: _sextupole(), "k2=")],
    )
    def test_normalised_strength_is_exported(self, element_factory, keyword):
        assert keyword in str(_translate(element_factory()).to_bdsim())

    def test_strength_is_normalised_not_integrated(self):
        """k1 is KnL/length, matching MAD-X rather than the stored integrated value."""
        translator = _translate(_quadrupole(k1l=0.6))
        assert translator.to_bdsim()["k1"] == pytest.approx(3.0)


def _sextupole():
    sextupole = Sextupole(
        name="S1", machine_area="T", physical=PhysicalElement(length=0.1)
    )
    sextupole.magnetic.length = 0.1
    sextupole.magnetic.multipoles.K2L.normal = 0.5
    return sextupole


class TestElementTyping:
    def test_single_plane_corrector_becomes_a_kicker_with_its_kick(self):
        corrector = Horizontal_Corrector(
            name="C1", machine_area="T", physical=PhysicalElement(length=0.1)
        )
        corrector.magnetic.length = 0.1
        corrector.magnetic.horizontal_kick = 0.002
        gmad = str(_translate(corrector).to_bdsim())
        assert "hkicker" in gmad
        assert "hkick=0.002" in gmad

    def test_marker_tolerates_a_section_aperture(self):
        """pybdsim's Marker takes only a name -- extras used to raise TypeError."""
        marker = Marker(name="M1", machine_area="T", hardware_class="Marker")
        built = _translate(marker).to_bdsim(
            section_aperture={"type": "circular", "size": 0.01, "material": "iron"}
        )
        assert "marker" in str(built)

    def test_aperture_reaches_elements_that_accept_it(self):
        built = _translate(_quadrupole()).to_bdsim(
            section_aperture={"type": "circular", "size": 0.01, "material": "iron"}
        )
        assert "apertureType" in str(built)


class TestFunctionalParameters:
    def test_symbolic_strength_is_written_as_an_unquoted_expression(self):
        """A quoted value would be a gmad string literal, not an expression."""
        section = _section_with_definitions()
        gmad = str(_bdsim_elements(section)["Q1"])
        assert "k1=kquad / 0.2" in gmad
        assert '"kquad' not in gmad

    def test_symbolic_bend_angle_and_edges(self):
        gmad = str(_bdsim_elements(_section_with_definitions())["D1"])
        assert "angle=bend1" in gmad

    def test_variable_block_is_included_before_the_components(self, tmp_path):
        section = _section_with_definitions()
        translator = SectionLatticeTranslator.from_section(section)
        translator.directory = str(tmp_path)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            translator.to_bdsim(save=True)
        variables = tmp_path / "TEST_SEC_variables.gmad"
        assert variables.is_file()
        assert "kquad = 0.6;" in variables.read_text()
        main = (tmp_path / "TEST_SEC.gmad").read_text()
        assert main.index("TEST_SEC_variables.gmad") < main.index(
            "TEST_SEC_components.gmad"
        ), "variables must be declared before the components that reference them"


def _section_with_definitions():
    quad = _quadrupole(k1l="kquad")
    quad.physical.middle = Position(x=0, y=0, z=0.1)
    dipole = _dipole(k0l="bend1", edges=0.0)
    dipole.physical.middle = Position(x=0, y=0, z=1.0)
    return SectionLattice(
        name="TEST-SEC",
        order=["Q1", "D1"],
        functional_definitions={"kquad": 0.6, "bend1": 0.15},
        elements=ElementList(elements={"Q1": quad, "D1": dipole}),
    )


def _bdsim_elements(section):
    translator = SectionLatticeTranslator.from_section(section)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        machine = translator.to_bdsim()
    return dict(machine.elements)


class TestBuilderArgumentNames:
    """The allowlist is keyed by what ``pybdsim``'s constructor takes, which is
    not always the gmad keyword it writes."""

    def test_matrix_transform_builds(self):
        """Rmat's sixteen r-values are required args named rIJ, not rmatIJ."""
        import numpy as np

        from laura.models.element import MatrixTransform

        element = MatrixTransform(
            name="MT1", machine_area="T", physical=PhysicalElement(length=0.1)
        )
        element.simulation.r_matrix = np.diag([1.5, 1, 1, 1, 1, 1])
        gmad = str(_translate(element).to_bdsim())
        assert "rmatrix" in gmad
        assert "rmat11=1.5" in gmad
        assert "rmat44=" in gmad, "identity terms are required, not optional"

    def test_twiss_match_builds(self):
        from laura.models.element import TwissMatch

        element = TwissMatch(
            name="TW1", machine_area="T", physical=PhysicalElement(length=0.0)
        )
        assert "rmatrix" in str(_translate(element).to_bdsim())

    def test_wiggler_peak_field_survives_prefix_stripping(self):
        """magnetic_peak_magnetic_field repeats its own prefix.

        Stripping with ``str.replace`` removed both occurrences and produced
        ``peak_field``, which matched no rule, so the field was dropped.
        """
        from laura.models.element import Wiggler

        wiggler = Wiggler(
            name="W1", machine_area="T", physical=PhysicalElement(length=1.0)
        )
        wiggler.magnetic.length = 1.0
        wiggler.magnetic.peak_magnetic_field = 0.8
        wiggler.magnetic.period = 0.05
        gmad = str(_translate(wiggler).to_bdsim())
        assert "undulator" in gmad
        assert "B=0.8" in gmad
        assert "undulatorPeriod=0.05" in gmad


def test_tilt_is_exported_like_madx():
    """tilt is valid on every BDSIM element and MAD-X already emitted it."""
    quad = _quadrupole()
    quad.magnetic.tilt = 0.15
    translator = _translate(quad)
    assert "tilt = 0.15" in translator.to_madx()
    assert "tilt=0.15" in str(translator.to_bdsim())


def test_full_dump_excludes_the_rule_tables():
    """conversion_rules are lookup tables, not element data."""
    dumped = _translate(_quadrupole()).full_dump()
    leaked = [key for key in dumped if key.startswith(("conversion_rules", "type_conversion_rules"))]
    assert not leaked, f"rule tables leaked into full_dump: {leaked[:3]}"


class TestTilt:
    """``tilt`` carries the design roll plus the psi alignment error.

    LAURA keeps the two apart -- ``magnetic.tilt`` is where the magnet is meant
    to sit, ``physical.error.rotation.psi`` is how far it actually is from that
    -- but MAD-X and BDSIM each expose a single roll angle, so they are summed
    (``BaseElementTranslator.roll``). ``dz_rot`` used to be mapped straight onto
    MAD-X's tilt for quadrupoles/sextupoles/octupoles, which meant an element
    with both a design tilt and a roll error silently reported only one.
    """

    @staticmethod
    def _quad_with(tilt, psi):
        quad = _quadrupole()
        quad.magnetic.tilt = tilt
        quad.physical.error.rotation.psi = psi
        return _translate(quad)

    @pytest.mark.parametrize(
        "tilt, psi, expected",
        [(0.15, 0.0, 0.15), (0.0, 0.05, 0.05), (0.15, 0.05, 0.2)],
    )
    def test_roll_sums_design_tilt_and_alignment_error(self, tilt, psi, expected):
        translator = self._quad_with(tilt, psi)
        assert translator.roll == pytest.approx(expected)
        assert f"tilt = {expected}" in translator.to_madx()
        assert f"tilt={expected}" in str(translator.to_bdsim())

    def test_roll_is_not_dumped(self):
        """A computed_field would collide with the magnetic_tilt -> tilt mapping."""
        assert "roll" not in self._quad_with(0.1, 0.0).full_dump()


@pytest.mark.parametrize(
    "element_name, has_tilt",
    [("Wiggler", True), ("Solenoid", True), ("NonLinearLens", True)],
)
def test_magnets_that_bypass_magneticelement_still_have_tilt(element_name, has_tilt):
    """These three declare their own attributes instead of inheriting
    MagneticElement, so they had no tilt slot until it was added to the schema."""
    import laura.models.magnetic as magnetic_models

    model = getattr(magnetic_models, f"{element_name}_Magnet")
    assert ("tilt" in model.model_fields) is has_tilt


class TestElementCoverage:
    """Which LAURA types BDSIM knows about, and what happens to the rest."""

    @pytest.mark.parametrize("hardware_type", ["Camera", "ChargeDiagnostic", "Photon_Monitor"])
    def test_diagnostics_are_markers_so_they_get_a_sampler(self, hardware_type):
        """These three fell through to a drift, which produces no sampler and so
        no output at a point the lattice explicitly instruments."""
        from laura.translator.conversion_rules.codes.bdsim_conversion import (
            bdsim_conversion_rules,
        )

        assert bdsim_conversion_rules[hardware_type].__name__ == "Marker"

    def test_every_diagnostic_is_mapped(self):
        """A Diagnostic with no mapping degrades to a drift and loses its sampler."""
        from laura.models.element import ELEMENT_REGISTRY
        from laura.translator.conversion_rules.codes.bdsim_conversion import (
            bdsim_conversion_rules,
        )

        unmapped = sorted(
            name
            for name, cls in ELEMENT_REGISTRY.items()
            if cls.model_fields["hardware_class"].default == "Diagnostic"
            and name not in bdsim_conversion_rules
        )
        assert not unmapped, f"diagnostics with no BDSIM mapping: {unmapped}"

    @pytest.mark.parametrize(
        "hardware_type",
        [
            "CombinedSolenoidQuadrupole",
            "NonLinearLens",
            "ElectrostaticSeparator",
            "BeamBeam",
            "Horizontal_AC_Dipole",
            "Vertical_AC_Dipole",
        ],
    )
    def test_types_bdsim_cannot_represent_are_flagged(self, hardware_type):
        """Without an entry they still export -- as a drift -- but silently."""
        from laura.translator.converters.codes.bdsim import bdsim_unsupported

        assert hardware_type in bdsim_unsupported

    def test_unsupported_elements_are_reported(self):
        """to_bdsim must run the shared check; it was the only to_<code> with a
        populated unsupported list that never called it, so the list was inert."""
        import pybdsim.Builder  # noqa: F401  -- import first; it resets warning filters

        from laura.models.element import NonLinearLens

        lens = NonLinearLens(
            name="NLL1",
            machine_area="T",
            physical=PhysicalElement(length=0.2, middle=Position(x=0, y=0, z=1.0)),
        )
        lens.magnetic.length = 0.2
        section = SectionLattice(
            name="SEC", order=["NLL1"], elements=ElementList(elements={"NLL1": lens})
        )
        translator = SectionLatticeTranslator.from_section(section)
        translator.verbose = True
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            translator.to_bdsim()
        assert any("not supported for bdsim" in str(w.message) for w in caught)

    def test_no_mapping_entry_is_unreachable(self):
        """hardware_type is a frozen per-class default, so an entry keyed on a
        string no class declares can never match."""
        from laura.models.element import ELEMENT_REGISTRY
        from laura.translator.conversion_rules.codes.bdsim_conversion import (
            bdsim_conversion_rules,
        )

        # These orphans are shared with the elegant/genesis/madx type tables, so
        # they are pruned across all of them together or not at all.
        shared_with_other_codes = {
            "APContour", "Bellows", "Cleaner", "FEL_Modulator",
            "Monitor", "Scatter", "Watch_Point",
        }
        orphans = set(bdsim_conversion_rules) - set(ELEMENT_REGISTRY)
        assert orphans <= shared_with_other_codes, (
            f"unreachable BDSIM-only entries: {sorted(orphans - shared_with_other_codes)}"
        )


class TestApertureAndOffsets:
    SECTION = {"type": "circular", "size": 0.01, "material": "iron"}

    def test_section_beampipe_is_applied(self):
        gmad = str(_translate(_quadrupole()).to_bdsim(section_aperture=self.SECTION))
        assert 'apertureType="circular"' in gmad
        assert "aper1=0.01*m" in gmad

    def test_element_aperture_overrides_the_section_beampipe(self):
        """An element's aperture is the pipe through that element."""
        from laura.models.simulation import ApertureElement

        quad = _quadrupole()
        quad.aperture = ApertureElement(
            shape="rectangular", horizontal_size=0.004, vertical_size=0.002
        )
        gmad = str(_translate(quad).to_bdsim(section_aperture=self.SECTION))
        assert 'apertureType="rectangular"' in gmad
        assert "aper1=0.004*m" in gmad and "aper2=0.002*m" in gmad
        assert "aper1=0.01*m" not in gmad

    def test_four_aperture_parameters(self):
        """rectellipse, lhc, racetrack and octagonal need more than two."""
        gmad = str(
            _translate(_quadrupole()).to_bdsim(
                section_aperture={"type": "rectellipse", "size": [0.01, 0.02, 0.03, 0.04]}
            )
        )
        for i, value in enumerate([0.01, 0.02, 0.03, 0.04], start=1):
            assert f"aper{i}={value}*m" in gmad

    def test_every_beampipe_shape_is_a_valid_gmad_type(self):
        """Anything that can reach `apertureType` must be a shape gmad accepts.

        `scraper` is the deliberate exception: rectangular extents, but jaws
        positioned independently, so it is a jcol/Scr_X-Scr_Y device rather than
        a beam-pipe cross-section and carries no apertureType.
        """
        from laura.models._generated import ApertureShapeEnum
        from laura.translator.utils.bdsim import BDSIM_APERTURE_TYPES

        shapes = {member.value for member in ApertureShapeEnum} - {"scraper"}
        assert shapes <= BDSIM_APERTURE_TYPES, sorted(shapes - BDSIM_APERTURE_TYPES)

    def test_a_scraper_carries_extents_but_no_aperture_type(self):
        from laura.models.simulation import ApertureElement

        quad = _quadrupole()
        quad.aperture = ApertureElement(shape="scraper", horizontal_size=0.004)
        gmad = str(_translate(quad).to_bdsim())
        assert "aper1=0.004*m" in gmad
        assert "apertureType" not in gmad

    def test_transverse_alignment_errors_become_offsets(self):
        quad = _quadrupole()
        quad.physical.error.position.x = 0.001
        quad.physical.error.position.y = -0.002
        gmad = str(_translate(quad).to_bdsim())
        assert "offsetX=0.001" in gmad
        assert "offsetY=-0.002" in gmad


class TestThinAndMultipoleElements:
    def test_rf_multipole_exports_its_integrated_strengths(self):
        from laura.models.element import RFMultipole

        element = RFMultipole(
            name="RFM1", machine_area="T", physical=PhysicalElement(length=0.3)
        )
        element.simulation.knl = [0.0, 0.5]
        element.simulation.ksl = [0.0, 0.1]
        gmad = str(_translate(element).to_bdsim())
        assert "multipole" in gmad
        assert "knl={0.0,0.5}" in gmad and "ksl={0.0,0.1}" in gmad

    def test_rf_multipole_warns_that_the_rf_terms_are_dropped(self):
        import pybdsim.Builder  # noqa: F401  -- imported first; it resets warning filters

        from laura.models.element import RFMultipole

        element = RFMultipole(
            name="RFM1", machine_area="T", physical=PhysicalElement(length=0.3)
        )
        element.simulation.knl = [0.0, 0.5]
        element.simulation.frequency = 1e9
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _translate(element).to_bdsim()
        assert any("no RF multipole" in str(w.message) for w in caught)

    @pytest.mark.parametrize(
        "element_name, length, expected",
        [
            ("RFMultipole", 0.0, "thinmultipole"),
            ("RFMultipole", 0.3, "multipole"),
            ("MatrixTransform", 0.0, "thinrmatrix"),
            ("MatrixTransform", 0.1, "rmatrix"),
            ("TwissMatch", 0.0, "thinrmatrix"),
        ],
    )
    def test_zero_length_uses_the_thin_variant(self, element_name, length, expected):
        import laura.models.element as element_models

        element = getattr(element_models, element_name)(
            name="X1", machine_area="T", physical=PhysicalElement(length=length)
        )
        if element_name == "RFMultipole":
            element.simulation.knl = [0.0, 0.5]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert expected in str(_translate(element).to_bdsim())


def test_compensating_wire_is_not_a_wire_scanner():
    """LAURA's Wire carries a current to act on the beam (MAD-X WIRE); BDSIM's
    wirescanner is an intercepting diagnostic. They are not interchangeable."""
    from laura.translator.conversion_rules.codes.bdsim_conversion import (
        bdsim_conversion_rules,
    )
    from laura.translator.converters.codes.bdsim import bdsim_unsupported

    assert "Wire" not in bdsim_conversion_rules
    assert "Wire" in bdsim_unsupported


class TestWireScanner:
    """A wire scanner intercepts the beam to measure its profile. LAURA's Wire is
    the opposite device -- a current-carrying beam-beam compensator -- so the two
    are separate element types."""

    @staticmethod
    def _wire_scanner():
        from laura.models.element import WireScanner

        scanner = WireScanner(
            name="WS1", machine_area="T", physical=PhysicalElement(length=0.05)
        )
        scanner.diagnostic.wire_diameter = 1e-4
        scanner.diagnostic.wire_length = 0.05
        return scanner

    def test_exports_as_a_bdsim_wirescanner(self):
        gmad = str(_translate(self._wire_scanner()).to_bdsim())
        assert "wirescanner" in gmad
        assert "wireDiameter=0.0001" in gmad
        assert "wireLength=0.05" in gmad
        assert 'material="carbon"' in gmad

    def test_wire_geometry_survives_model_dump(self):
        """translate_elements round-trips through model_dump(); the diagnostic
        payload is declared as the fieldless schema base on Diagnostic, so
        without a concrete re-declaration it serialises to {}."""
        scanner = self._wire_scanner()
        assert scanner.model_dump()["diagnostic"]["wire_diameter"] == 1e-4
        translator = _translate(scanner)
        assert translator.diagnostic.wire_length == 0.05

    def test_falls_back_to_a_diagnostic_in_codes_without_one(self):
        translator = _translate(self._wire_scanner())
        assert "monitor" in translator.to_madx()
        assert "mark" in translator.to_elegant()

    def test_is_distinct_from_the_compensating_wire(self):
        from laura.models.element import Wire, WireScanner

        assert Wire.model_fields["hardware_type"].default == "Wire"
        assert WireScanner.model_fields["hardware_type"].default == "WireScanner"
        # the compensating wire carries a current; the scanner has wire geometry
        assert "current" in Wire(name="W", machine_area="T").simulation.model_fields
        assert "wire_diameter" in WireScanner(
            name="WS", machine_area="T"
        ).diagnostic.model_fields
