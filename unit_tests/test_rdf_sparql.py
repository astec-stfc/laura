"""Tests for laura.Exporters.RDF, laura.query.LAURAQuery, and
MachineModel.export_rdf / MachineModel.sparql."""

import os
import tempfile

import pytest

from laura.models.element import Quadrupole, Marker, Dipole, Horizontal_Corrector
from laura.models.physical import Position
from laura import LAURA

# ---------------------------------------------------------------------------
# Skip everything if rdflib is not installed.
# ---------------------------------------------------------------------------

rdflib = pytest.importorskip("rdflib", reason="rdflib not installed")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_quad():
    return Quadrupole(
        name="Q1",
        machine_area="SEC",
        magnetic={"length": 0.3, "k1l": -1.5},
        physical={"length": 0.3, "middle": {"x": 1.0, "y": 0.0, "z": 2.0}},
        downstream=["D1"],
        controls={
            "variables": {
                "SETI": {
                    "identifier": "SEC-Q1:SETI",
                    "protocol": "EPICS",
                    "units": "A",
                    "read_only": False,
                    "control_type": "scalar",
                    "target": "magnetic.k1l",
                    "buffer_size": 10,
                },
                "GETI": {"identifier": "SEC-Q1:GETI", "protocol": "EPICS"},
            }
        },
    )


@pytest.fixture
def sample_dipole():
    return Dipole(
        name="D1",
        machine_area="SEC",
        magnetic={"length": 0.5},
        physical={"length": 0.5, "middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
        upstream=["Q1"],
    )


@pytest.fixture
def sample_marker():
    return Marker(
        name="M1",
        machine_area="SEC",
        hardware_class="Marker",
        physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
    )


@pytest.fixture
def sample_corrector():
    """A type whose hardware_type label and schema class name differ."""
    return Horizontal_Corrector(
        name="HCOR1",
        machine_area="SEC",
        magnetic={"length": 0.1, "horizontal_kick": 1e-4},
        physical={"length": 0.1, "middle": {"x": 0.0, "y": 0.0, "z": 7.0}},
    )


@pytest.fixture
def small_machine(sample_marker, sample_quad, sample_dipole, sample_corrector):
    sections = {"sections": {"SEC": ["M1", "Q1", "D1", "HCOR1"]}}
    layouts = {"default_layout": "beam", "layouts": {"beam": ["SEC"]}}
    return LAURA(
        element_list=[sample_marker, sample_quad, sample_dipole, sample_corrector],
        layout=layouts,
        section=sections,
    )


# ---------------------------------------------------------------------------
# build_rdf_graph
# ---------------------------------------------------------------------------


class TestBuildRdfGraph:
    def test_returns_graph(self, small_machine):
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        assert isinstance(g, rdflib.Graph)

    def test_element_count(self, small_machine):
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        # Each element gets at least rdf:type, name, and machine_area triples
        assert len(g) >= 3 * 3

    def test_rdf_type_triple(self, small_machine):
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        quad_uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
        types = list(g.objects(quad_uri, rdflib.RDF.type))
        assert LAURA_NS["Quadrupole"] in types

    def test_rdf_type_is_the_schema_class_not_the_hardware_type(self, small_machine):
        """A corrector types as laura:HorizontalCorrector, its ontology class.

        The label is ``Horizontal_Corrector``, and using that built a URI the
        ontology declares as an owl:DatatypeProperty -- a slot of
        CombinedCorrector -- rather than a class.
        """
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/HCOR1")
        types = list(g.objects(uri, rdflib.RDF.type))
        assert types == [LAURA_NS["HorizontalCorrector"]]
        # The label is still available, as a literal.
        assert rdflib.Literal("Horizontal_Corrector") in set(
            g.objects(uri, LAURA_NS["hardware_type"])
        )

    def test_every_rdf_type_is_declared_in_the_ontology(self, small_machine):
        """No element may be typed with a URI the generated ontology lacks."""
        import pathlib

        import laura as laura_pkg
        from laura.Exporters.RDF import build_rdf_graph

        onto = rdflib.Graph()
        onto.parse(
            pathlib.Path(laura_pkg.__file__).parent
            / "schema"
            / "generated"
            / "laura_ontology.owl",
            format="turtle",
        )
        g = build_rdf_graph(small_machine, machine_name="test")
        undeclared = [
            str(o)
            for _, _, o in g.triples((None, rdflib.RDF.type, None))
            if (o, rdflib.RDF.type, rdflib.OWL.Class) not in onto
        ]
        assert not undeclared, f"rdf:type URIs absent from the ontology: {undeclared}"

    def test_name_triple(self, small_machine):
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        quad_uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
        names = list(g.objects(quad_uri, LAURA_NS["name"]))
        assert rdflib.Literal("Q1") in names

    def test_physical_length_triple(self, small_machine):
        """``length`` hangs off the PhysicalElement node, not the element."""
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        quad_uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")

        assert list(g.objects(quad_uri, LAURA_NS["length"])) == []

        phys = list(g.objects(quad_uri, LAURA_NS["physical"]))
        assert len(phys) == 1
        assert (phys[0], rdflib.RDF.type, LAURA_NS["PhysicalElement"]) in g
        lengths = list(g.objects(phys[0], LAURA_NS["length"]))
        assert len(lengths) == 1
        assert abs(float(lengths[0]) - 0.3) < 1e-9

    def test_position_triples(self, small_machine):
        """Coordinates live on a laura:Position node under laura:middle."""
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        quad_uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")

        # The old flat spelling was not a slot of anything in the schema.
        for gone in ("position_x", "position_y", "position_z"):
            assert list(g.objects(quad_uri, LAURA_NS[gone])) == []

        (phys,) = g.objects(quad_uri, LAURA_NS["physical"])
        (middle,) = g.objects(phys, LAURA_NS["middle"])
        assert (middle, rdflib.RDF.type, LAURA_NS["Position"]) in g
        coords = {
            axis: float(next(g.objects(middle, LAURA_NS[axis])))
            for axis in ("x", "y", "z")
        }
        assert coords == pytest.approx({"x": 1.0, "y": 0.0, "z": 2.0})

    def test_position_is_reachable_by_sparql_through_the_schema_path(
        self, small_machine
    ):
        """The nesting is what makes an ontology-driven query possible at all."""
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        rows = list(
            g.query(
                """
                PREFIX laura: <https://w3id.org/laura/>
                SELECT ?name ?z WHERE {
                    ?e laura:name ?name ;
                       laura:physical/laura:middle/laura:z ?z .
                }
                """
            )
        )
        assert {str(r[0]): float(r[1]) for r in rows} == pytest.approx(
            {"M1": 0.0, "Q1": 2.0, "D1": 5.0, "HCOR1": 7.0}
        )

    def test_machine_area_triple(self, small_machine):
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        quad_uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
        areas = list(g.objects(quad_uri, LAURA_NS["machine_area"]))
        assert rdflib.Literal("SEC") in areas


# ---------------------------------------------------------------------------
# Relations: sections, layouts, controls, upstream/downstream
# ---------------------------------------------------------------------------

LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
MACHINE = rdflib.URIRef("https://w3id.org/laura/test")


class TestRelations:
    """Without these the export is a bag of unconnected element nodes."""

    def test_machine_node_links_every_element(self, small_machine):
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        assert (MACHINE, rdflib.RDF.type, LAURA_NS["MachineModel"]) in g
        linked = {str(u).rsplit("/", 1)[-1] for u in g.objects(MACHINE, LAURA_NS["elements"])}
        assert linked == {"M1", "Q1", "D1", "HCOR1"}

    def test_section_membership(self, small_machine):
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        sec = rdflib.URIRef("https://w3id.org/laura/test/sections/SEC")
        assert (MACHINE, LAURA_NS["sections"], sec) in g
        assert (sec, rdflib.RDF.type, LAURA_NS["SectionLattice"]) in g
        assert rdflib.Literal("SEC") in set(g.objects(sec, LAURA_NS["name"]))
        names = ("M1", "Q1", "D1", "HCOR1")
        # IRIs, not names: SectionLattice.elements is range AcceleratorElement.
        assert set(g.objects(sec, LAURA_NS["elements"])) == {
            rdflib.URIRef(f"https://w3id.org/laura/test/SEC/{n}") for n in names
        }

    def test_lattice_metadata(self, small_machine):
        """The BaseLatticeModel slots both SectionLattice and MachineLayout have."""
        from laura.Exporters.RDF import build_rdf_graph

        section = small_machine.sections["SEC"]
        section.section_type = "rf"
        section.revolution_frequency = 1.2e6
        section.functional_definitions = {"quad1_k1l": -2, "cav1_phase": 90.5}
        small_machine.lattices["beam"].layout_type = "laser"

        g = build_rdf_graph(small_machine, machine_name="test")
        sec = rdflib.URIRef("https://w3id.org/laura/test/sections/SEC")
        layout = rdflib.URIRef("https://w3id.org/laura/test/layouts/beam")

        # Enum-ranged, so plain literals: the shapes carry sh:in and no
        # sh:datatype, and sh:in compares terms, not lexical forms.
        assert set(g.objects(sec, LAURA_NS["section_type"])) == {rdflib.Literal("rf")}
        assert set(g.objects(layout, LAURA_NS["layout_type"])) == {
            rdflib.Literal("laser")
        }
        assert set(g.objects(sec, LAURA_NS["revolution_frequency"])) == {
            rdflib.Literal(1.2e6, datatype=rdflib.XSD.double)
        }

        defs = {
            str(next(g.objects(d, LAURA_NS["name"]))): float(
                next(g.objects(d, LAURA_NS["value"]))
            )
            for d in g.objects(sec, LAURA_NS["functional_definitions"])
        }
        assert defs == {"quad1_k1l": -2.0, "cav1_phase": 90.5}

    def test_layout_membership(self, small_machine):
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        layout = rdflib.URIRef("https://w3id.org/laura/test/layouts/beam")
        assert (MACHINE, LAURA_NS["layouts"], layout) in g
        assert (layout, rdflib.RDF.type, LAURA_NS["MachineLayout"]) in g
        assert set(g.objects(layout, LAURA_NS["sections"])) == {
            rdflib.URIRef("https://w3id.org/laura/test/sections/SEC")
        }

    def test_upstream_downstream_are_iris_between_elements(self, small_machine):
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        q1 = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
        d1 = rdflib.URIRef("https://w3id.org/laura/test/SEC/D1")
        assert (q1, LAURA_NS["downstream"], d1) in g
        assert (d1, LAURA_NS["upstream"], q1) in g

    def test_unknown_upstream_name_is_skipped(self, sample_marker):
        """A dangling IRI would fail the sh:class constraint on the slot."""
        from laura.Exporters.RDF import build_rdf_graph

        sample_marker.upstream = ["NOT_IN_THIS_MACHINE"]
        machine = LAURA(
            element_list=[sample_marker],
            layout={"default_layout": "beam", "layouts": {"beam": ["SEC"]}},
            section={"sections": {"SEC": ["M1"]}},
        )
        g = build_rdf_graph(machine, machine_name="test")
        assert list(g.objects(None, LAURA_NS["upstream"])) == []

    def test_control_variables(self, small_machine):
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        q1 = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
        controls = next(g.objects(q1, LAURA_NS["controls"]))
        assert (controls, rdflib.RDF.type, LAURA_NS["ControlsInformation"]) in g

        seti = rdflib.URIRef(f"{controls}/SETI")
        assert (controls, LAURA_NS["variables"], seti) in g
        assert (seti, rdflib.RDF.type, LAURA_NS["ControlVariable"]) in g
        # name is the key the variable is filed under; the Pydantic model has no
        # such field, so this triple can only come from the mapping key.
        assert next(g.objects(seti, LAURA_NS["name"])) == rdflib.Literal("SETI")
        assert next(g.objects(seti, LAURA_NS["identifier"])) == rdflib.Literal(
            "SEC-Q1:SETI", datatype=rdflib.XSD.string
        )
        assert next(g.objects(seti, LAURA_NS["read_only"])) == rdflib.Literal(
            False, datatype=rdflib.XSD.boolean
        )
        assert next(g.objects(seti, LAURA_NS["buffer_size"])) == rdflib.Literal(
            10, datatype=rdflib.XSD.integer
        )
        # Enum-ranged: plain literal, because the shape carries sh:in and no
        # sh:datatype, and rdflib keeps the two terms distinct.
        assert next(g.objects(seti, LAURA_NS["control_type"])) == rdflib.Literal(
            "scalar"
        )

    def test_dtype_is_serialised_by_name(self, small_machine):
        """It is held as the Python type object, not a string."""
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        dtypes = set(g.objects(None, LAURA_NS["dtype"]))
        assert dtypes and all(
            str(d) in {"float", "int", "str", "bool"} for d in dtypes
        ), dtypes

    def test_pv_for_a_magnet_is_reachable_by_sparql(self, small_machine):
        """The point of the exercise: one query from machine to PV address."""
        from laura.Exporters.RDF import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        rows = list(
            g.query(
                """
                PREFIX laura: <https://w3id.org/laura/>
                SELECT ?elem ?var ?pv WHERE {
                    ?m a laura:MachineModel ; laura:elements ?e .
                    ?e laura:name ?elem ;
                       laura:controls/laura:variables ?v .
                    ?v laura:name ?var ; laura:identifier ?pv .
                }
                """
            )
        )
        assert {(str(r[0]), str(r[1]), str(r[2])) for r in rows} == {
            ("Q1", "SETI", "SEC-Q1:SETI"),
            ("Q1", "GETI", "SEC-Q1:GETI"),
        }


# ---------------------------------------------------------------------------
# export_machine_rdf
# ---------------------------------------------------------------------------


class TestExportMachineRdf:
    def test_writes_turtle_file(self, small_machine, tmp_path):
        from laura.Exporters.RDF import export_machine_rdf

        out = str(tmp_path / "machine.ttl")
        export_machine_rdf(small_machine, path=out, machine_name="test")
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_turtle_is_parseable(self, small_machine, tmp_path):
        from laura.Exporters.RDF import export_machine_rdf

        out = str(tmp_path / "machine.ttl")
        export_machine_rdf(small_machine, path=out, format="turtle", machine_name="test")
        g2 = rdflib.Graph()
        g2.parse(out, format="turtle")
        assert len(g2) > 0

    def test_writes_jsonld_file(self, small_machine, tmp_path):
        from laura.Exporters.RDF import export_machine_rdf

        out = str(tmp_path / "machine.jsonld")
        export_machine_rdf(small_machine, path=out, format="json-ld", machine_name="test")
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_writes_ntriples_file(self, small_machine, tmp_path):
        from laura.Exporters.RDF import export_machine_rdf

        out = str(tmp_path / "machine.nt")
        export_machine_rdf(small_machine, path=out, format="nt", machine_name="test")
        assert os.path.exists(out)

    def test_format_aliases(self, small_machine, tmp_path):
        from laura.Exporters.RDF import export_machine_rdf

        for alias in ("ttl", "turtle", "jsonld", "json-ld", "ntriples", "nt"):
            out = str(tmp_path / f"machine_{alias}.rdf")
            export_machine_rdf(
                small_machine, path=out, format=alias, machine_name="test"
            )
            assert os.path.exists(out)

    def test_roundtrip_element_count(self, small_machine, tmp_path):
        """After exporting and re-parsing, every element should appear as a subject."""
        from laura.Exporters.RDF import export_machine_rdf

        out = str(tmp_path / "machine.ttl")
        export_machine_rdf(small_machine, path=out, format="turtle", machine_name="test")
        g2 = rdflib.Graph()
        g2.parse(out, format="turtle")
        subjects = set(g2.subjects())
        elem_names = list(small_machine.elements.keys())
        for name in elem_names:
            area = small_machine.elements[name].machine_area
            expected = rdflib.URIRef(f"https://w3id.org/laura/test/{area}/{name}")
            assert expected in subjects, f"Missing element URI for {name}"


# ---------------------------------------------------------------------------
# MachineModel.export_rdf
# ---------------------------------------------------------------------------


class TestMachineModelExportRdf:
    def test_method_exists(self, small_machine):
        assert hasattr(small_machine, "export_rdf")

    def test_creates_file(self, small_machine, tmp_path):
        out = str(tmp_path / "machine.ttl")
        small_machine.export_rdf(path=out, machine_name="test")
        assert os.path.exists(out)


# ---------------------------------------------------------------------------
# LAURAQuery.sparql
# ---------------------------------------------------------------------------


class TestLAURAQuery:
    def test_sparql_select_all(self, small_machine):
        from laura.query import LAURAQuery

        q = LAURAQuery(small_machine, machine_name="test")
        rows = q.sparql("SELECT ?name WHERE { ?elem laura:name ?name . }")
        names = {r["name"] for r in rows}
        assert "Q1" in names
        assert "M1" in names
        assert "D1" in names

    def test_get_elements_in_area(self, small_machine):
        from laura.query import LAURAQuery

        q = LAURAQuery(small_machine, machine_name="test")
        names = q.get_elements_in_area("SEC")
        assert set(names) == {"M1", "Q1", "D1", "HCOR1"}

    def test_get_elements_in_area_empty(self, small_machine):
        from laura.query import LAURAQuery

        q = LAURAQuery(small_machine, machine_name="test")
        names = q.get_elements_in_area("NONEXISTENT")
        assert names == []

    def test_get_elements_by_hardware_type(self, small_machine):
        from laura.query import LAURAQuery

        q = LAURAQuery(small_machine, machine_name="test")
        quads = q.get_elements_by_hardware_type("Quadrupole")
        assert quads == ["Q1"]

    def test_get_elements_by_hardware_class(self, small_machine):
        from laura.query import LAURAQuery

        q = LAURAQuery(small_machine, machine_name="test")
        magnets = q.get_elements_by_hardware_class("Magnet")
        assert set(magnets) == {"Q1", "D1", "HCOR1"}

    def test_invalidate_clears_cache(self, small_machine):
        from laura.query import LAURAQuery

        q = LAURAQuery(small_machine, machine_name="test")
        _ = q._get_graph()
        assert q._graph is not None
        q.invalidate()
        assert q._graph is None

    def test_graph_cached_after_first_query(self, small_machine):
        from laura.query import LAURAQuery

        q = LAURAQuery(small_machine, machine_name="test")
        q.sparql("SELECT ?n WHERE { ?e laura:name ?n . }")
        g1 = q._graph
        q.sparql("SELECT ?n WHERE { ?e laura:name ?n . }")
        g2 = q._graph
        assert g1 is g2  # same object — not rebuilt

    def test_sparql_returns_list_of_dicts(self, small_machine):
        from laura.query import LAURAQuery

        q = LAURAQuery(small_machine, machine_name="test")
        rows = q.sparql("SELECT ?name WHERE { ?elem laura:name ?name . }")
        assert isinstance(rows, list)
        assert all(isinstance(r, dict) for r in rows)
        assert all("name" in r for r in rows)


# ---------------------------------------------------------------------------
# MachineModel.sparql convenience method
# ---------------------------------------------------------------------------


class TestMachineModelSparql:
    def test_sparql_method_exists(self, small_machine):
        assert hasattr(small_machine, "sparql")

    def test_sparql_returns_results(self, small_machine):
        rows = small_machine.sparql(
            "SELECT ?name WHERE { ?elem laura:name ?name . }",
            machine_name="test",
        )
        names = {r["name"] for r in rows}
        assert "Q1" in names
