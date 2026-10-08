"""Tests for RDF export and SPARQL queries."""

import os

import pytest

from laura.models.element import Quadrupole, Marker, Dipole
from laura import LAURA

rdflib = pytest.importorskip("rdflib", reason="rdflib not installed")

from laura.exporters.rdf_exporter import build_rdf_graph, export_machine_rdf  # noqa: E402
from laura.query import LAURAQuery  # noqa: E402

LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
QUAD_URI = rdflib.URIRef("https://w3id.org/laura/test/SEC/Q1")
NAME_QUERY = "SELECT ?name WHERE { ?elem laura:name ?name . }"


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


@pytest.fixture
def graph(small_machine):
    return build_rdf_graph(small_machine, machine_name="test")


@pytest.fixture
def query(small_machine):
    return LAURAQuery(small_machine, machine_name="test")


class TestBuildRdfGraph:
    def test_returns_graph(self, graph):
        assert isinstance(graph, rdflib.Graph)
        # Each element gets at least rdf:type, name, and machine_area triples
        assert len(graph) >= 3 * 3

    @pytest.mark.parametrize(
        "predicate, expected",
        [
            (rdflib.RDF.type, LAURA_NS["Quadrupole"]),
            (LAURA_NS["name"], rdflib.Literal("Q1")),
            (LAURA_NS["machine_area"], rdflib.Literal("SEC")),
        ],
        ids=["type", "name", "machine_area"],
    )
    def test_quad_triple(self, graph, predicate, expected):
        assert expected in list(graph.objects(QUAD_URI, predicate))

    @pytest.mark.parametrize(
        "predicate, expected",
        [("length", 0.3), ("position_x", 1.0), ("position_z", 2.0)],
    )
    def test_numeric_triple(self, graph, predicate, expected):
        values = list(graph.objects(QUAD_URI, LAURA_NS[predicate]))
        assert len(values) == 1
        assert abs(float(values[0]) - expected) < 1e-9


class TestExportMachineRdf:
    @pytest.mark.parametrize("alias", ["ttl", "turtle", "jsonld", "json-ld", "ntriples", "nt"])
    def test_format_aliases(self, small_machine, tmp_path, alias):
        out = str(tmp_path / f"machine_{alias}.rdf")
        export_machine_rdf(small_machine, path=out, format=alias, machine_name="test")
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_roundtrip_element_count(self, small_machine, tmp_path):
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


class TestMachineModelExportRdf:
    def test_creates_file(self, small_machine, tmp_path):
        out = str(tmp_path / "machine.ttl")
        small_machine.export_rdf(path=out, machine_name="test")
        assert os.path.exists(out)


class TestLAURAQuery:
    def test_sparql_select_all(self, query):
        rows = query.sparql(NAME_QUERY)
        assert isinstance(rows, list)
        assert all(isinstance(r, dict) for r in rows)
        assert all("name" in r for r in rows)
        names = {r["name"] for r in rows}
        assert "Q1" in names
        assert "M1" in names
        assert "D1" in names

    def test_get_elements_in_area(self, query):
        assert set(query.get_elements_in_area("SEC")) == {"M1", "Q1", "D1"}
        assert query.get_elements_in_area("NONEXISTENT") == []

    def test_get_elements_by_hardware_type(self, query):
        assert query.get_elements_by_hardware_type("Quadrupole") == ["Q1"]

    def test_get_elements_by_hardware_class(self, query):
        assert set(query.get_elements_by_hardware_class("Magnet")) == {"Q1", "D1"}

    def test_invalidate_clears_cache(self, query):
        _ = query._get_graph()
        assert query._graph is not None
        query.invalidate()
        assert query._graph is None

    def test_graph_cached_after_first_query(self, query):
        query.sparql("SELECT ?n WHERE { ?e laura:name ?n . }")
        g1 = query._graph
        query.sparql("SELECT ?n WHERE { ?e laura:name ?n . }")
        g2 = query._graph
        assert g1 is g2


class TestMachineModelSparql:
    def test_sparql_returns_results(self, small_machine):
        rows = small_machine.sparql(NAME_QUERY, machine_name="test")
        names = {r["name"] for r in rows}
        assert "Q1" in names
