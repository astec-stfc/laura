"""Tests for laura.exporters.RDF, laura.query.LAURAQuery, and
MachineModel.export_rdf / MachineModel.sparql."""

import os
import tempfile

import pytest

from laura.models.element import Quadrupole, Marker, Dipole
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
    )


@pytest.fixture
def sample_dipole():
    return Dipole(
        name="D1",
        machine_area="SEC",
        magnetic={"length": 0.5},
        physical={"length": 0.5, "middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
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
def small_machine(sample_marker, sample_quad, sample_dipole):
    sections = {"sections": {"SEC": ["M1", "Q1", "D1"]}}
    layouts = {"default_layout": "beam", "layouts": {"beam": ["SEC"]}}
    return LAURA(
        element_list=[sample_marker, sample_quad, sample_dipole],
        layout=layouts,
        section=sections,
    )


# ---------------------------------------------------------------------------
# build_rdf_graph
# ---------------------------------------------------------------------------


class TestBuildRdfGraph:
    def test_returns_graph(self, small_machine):
        from laura.exporters.rdf_exporter import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        assert isinstance(g, rdflib.Graph)

    def test_element_count(self, small_machine):
        from laura.exporters.rdf_exporter import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        # Each element gets at least rdf:type, name, and machine_area triples
        assert len(g) >= 3 * 3

    def test_rdf_type_triple(self, small_machine):
        from laura.exporters.rdf_exporter import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        quad_uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
        types = list(g.objects(quad_uri, rdflib.RDF.type))
        assert LAURA_NS["Quadrupole"] in types

    def test_name_triple(self, small_machine):
        from laura.exporters.rdf_exporter import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        quad_uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
        names = list(g.objects(quad_uri, LAURA_NS["name"]))
        assert rdflib.Literal("Q1") in names

    def test_physical_length_triple(self, small_machine):
        from laura.exporters.rdf_exporter import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        quad_uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
        lengths = list(g.objects(quad_uri, LAURA_NS["length"]))
        assert len(lengths) == 1
        assert abs(float(lengths[0]) - 0.3) < 1e-9

    def test_position_triples(self, small_machine):
        from laura.exporters.rdf_exporter import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        quad_uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
        xs = list(g.objects(quad_uri, LAURA_NS["position_x"]))
        zs = list(g.objects(quad_uri, LAURA_NS["position_z"]))
        assert len(xs) == 1
        assert abs(float(xs[0]) - 1.0) < 1e-9
        assert len(zs) == 1
        assert abs(float(zs[0]) - 2.0) < 1e-9

    def test_machine_area_triple(self, small_machine):
        from laura.exporters.rdf_exporter import build_rdf_graph

        g = build_rdf_graph(small_machine, machine_name="test")
        LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
        quad_uri = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
        areas = list(g.objects(quad_uri, LAURA_NS["machine_area"]))
        assert rdflib.Literal("SEC") in areas


# ---------------------------------------------------------------------------
# export_machine_rdf
# ---------------------------------------------------------------------------


class TestExportMachineRdf:
    def test_writes_turtle_file(self, small_machine, tmp_path):
        from laura.exporters.rdf_exporter import export_machine_rdf

        out = str(tmp_path / "machine.ttl")
        export_machine_rdf(small_machine, path=out, machine_name="test")
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_turtle_is_parseable(self, small_machine, tmp_path):
        from laura.exporters.rdf_exporter import export_machine_rdf

        out = str(tmp_path / "machine.ttl")
        export_machine_rdf(small_machine, path=out, format="turtle", machine_name="test")
        g2 = rdflib.Graph()
        g2.parse(out, format="turtle")
        assert len(g2) > 0

    def test_writes_jsonld_file(self, small_machine, tmp_path):
        from laura.exporters.rdf_exporter import export_machine_rdf

        out = str(tmp_path / "machine.jsonld")
        export_machine_rdf(small_machine, path=out, format="json-ld", machine_name="test")
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_writes_ntriples_file(self, small_machine, tmp_path):
        from laura.exporters.rdf_exporter import export_machine_rdf

        out = str(tmp_path / "machine.nt")
        export_machine_rdf(small_machine, path=out, format="nt", machine_name="test")
        assert os.path.exists(out)

    def test_format_aliases(self, small_machine, tmp_path):
        from laura.exporters.rdf_exporter import export_machine_rdf

        for alias in ("ttl", "turtle", "jsonld", "json-ld", "ntriples", "nt"):
            out = str(tmp_path / f"machine_{alias}.rdf")
            export_machine_rdf(
                small_machine, path=out, format=alias, machine_name="test"
            )
            assert os.path.exists(out)

    def test_roundtrip_element_count(self, small_machine, tmp_path):
        """After exporting and re-parsing, every element should appear as a subject."""
        from laura.exporters.rdf_exporter import export_machine_rdf

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
        assert set(names) == {"M1", "Q1", "D1"}

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
        assert set(magnets) == {"Q1", "D1"}

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
