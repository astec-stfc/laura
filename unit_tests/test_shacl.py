"""Validates exported RDF against the generated SHACL shapes.

This is the check the RDF exporter had no way of failing before: nothing tied
what ``laura.Exporters.RDF`` emits to what the schema says an element looks
like, so it spent a long time emitting ``laura:position_x`` -- a predicate the
schema does not declare at all -- and every element would have been rejected by
these shapes had anyone run them.

Requires the ``rdf`` extra::

    pip install "laura-accelerator[rdf]"
"""

import pathlib

import pytest

rdflib = pytest.importorskip("rdflib", reason="rdflib not installed")
pyshacl = pytest.importorskip("pyshacl", reason="pyshacl not installed")

from laura import LAURA  # noqa: E402
from laura.models.element import (  # noqa: E402
    Dipole,
    Horizontal_Corrector,
    Marker,
    Quadrupole,
)

SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
LAURA_NS = rdflib.Namespace("https://w3id.org/laura/")
_GENERATED = (
    pathlib.Path(__file__).resolve().parent.parent / "laura" / "schema" / "generated"
)
SHAPES_PATH = _GENERATED / "laura_shacl.ttl"
ONTOLOGY_PATH = _GENERATED / "laura_ontology.owl"


@pytest.fixture(scope="module")
def shapes():
    return rdflib.Graph().parse(SHAPES_PATH, format="turtle")


@pytest.fixture(scope="module")
def ontology():
    """The class hierarchy, without which half the shapes cannot be checked.

    ``sh:class laura:AcceleratorElement`` on ``elements``/``upstream``/
    ``downstream`` is satisfied via ``rdf:type/rdfs:subClassOf*``, and the
    ``rdfs:subClassOf`` axioms live here rather than in an export.  gen-owl
    writes Turtle despite the ``.owl`` suffix.
    """
    return rdflib.Graph().parse(ONTOLOGY_PATH, format="turtle")


@pytest.fixture
def small_machine():
    """One element of each shape the exporter treats differently."""
    elements = [
        Marker(
            name="M1",
            machine_area="SEC",
            hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
        ),
        Quadrupole(
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
                        "dtype": "float",
                        "read_only": False,
                        "control_type": "scalar",
                        "target": "magnetic.k1l",
                        "readback": "GETI",
                        "auto_buffer": True,
                        "buffer_size": 10,
                    },
                    "GETI": {"identifier": "SEC-Q1:GETI", "protocol": "EPICS"},
                }
            },
        ),
        Dipole(
            name="D1",
            machine_area="SEC",
            magnetic={"length": 0.5},
            physical={"length": 0.5, "middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
            upstream=["Q1"],
        ),
        # hardware_type and schema class name disagree for this one.
        Horizontal_Corrector(
            name="HCOR1",
            machine_area="SEC",
            magnetic={"length": 0.1, "horizontal_kick": 1e-4},
            physical={"length": 0.1, "middle": {"x": 0.0, "y": 0.0, "z": 7.0}},
        ),
    ]
    machine = LAURA(
        element_list=elements,
        layout={"default_layout": "beam", "layouts": {"beam": ["SEC"]}},
        section={"sections": {"SEC": ["M1", "Q1", "D1", "HCOR1"]}},
    )
    # The BaseLatticeModel slots, set here rather than in a second fixture so
    # the conformance test covers their datatypes too -- an enum emitted as
    # xsd:string, or revolution_frequency as xsd:float, only fails under SHACL.
    section = machine.sections["SEC"]
    section.section_type = "rf"
    section.revolution_frequency = 1.2e6
    section.functional_definitions = {"quad1_k1l": -2, "cav1_phase": 90.5}
    machine.lattices["beam"].layout_type = "laser"
    return machine


def test_exported_machine_conforms(small_machine, shapes, ontology):
    """Everything build_rdf_graph emits must satisfy the generated shapes."""
    from laura.Exporters.RDF import build_rdf_graph

    graph = build_rdf_graph(small_machine, machine_name="test")
    conforms, _, report = pyshacl.validate(
        graph,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="none",
        abort_on_first=False,
    )
    assert conforms, report


def test_parent_shapes_accept_their_subclasses(small_machine, shapes, ontology):
    """A Horizontal_Corrector must satisfy the laura:Dipole shape too.

    ``sh:targetClass`` matches subclasses, so every shape an element inherits is
    applied to it.  gen-shacl emits the ``slot_usage`` override as
    ``sh:in ( "Dipole" )`` on the Dipole shape, which rejected every corrector
    until ``generate_shacl.py`` started widening those lists over the class's
    descendants.  Guards that widening from the data side.
    """
    from laura.Exporters.RDF import build_rdf_graph

    graph = build_rdf_graph(small_machine, machine_name="test")
    hcor = next(
        s for s in graph.subjects(LAURA_NS["name"], rdflib.Literal("HCOR1"))
    )
    assert (hcor, rdflib.RDF.type, LAURA_NS["HorizontalCorrector"]) in graph

    conforms, _, report = pyshacl.validate(
        graph,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="none",
        focus=str(hcor),
    )
    assert conforms, report


def test_shapes_have_no_duplicate_property_blocks(shapes):
    """One ``sh:property`` per path per shape.

    gen-shacl emits a block per contribution as it walks a class's ancestry, so
    a class overriding a parent's ``slot_usage`` keeps both the inherited and
    the overriding constraint.  ``sh:property`` is conjunctive, which made
    Collimator, CrabCavity, FaradayCupMonitor, IntegratedCurrentTransformer,
    RFDeflectingCavity and WallCurrentMonitor unsatisfiable -- no instance could
    validate, whatever its hardware_type.  laura/schema/generate_shacl.py
    collapses them; this is the check that it still runs.
    """
    duplicated = []
    for shape in shapes.subjects(SH.targetClass, None):
        seen = set()
        for block in shapes.objects(shape, SH.property):
            path = next(shapes.objects(block, SH.path))
            if path in seen:
                duplicated.append(f"{shape} -> {path}")
            seen.add(path)
    assert not duplicated, (
        "duplicate sh:property blocks: "
        + ", ".join(sorted(duplicated)[:10])
        + ". Regenerate with `python laura/schema/generate_shacl.py`."
    )


def test_shapes_are_satisfiable(shapes):
    """No shape may constrain one path to two different ``sh:in`` lists."""
    unsatisfiable = []
    for shape in shapes.subjects(SH.targetClass, None):
        by_path = {}
        for block in shapes.objects(shape, SH.property):
            path = next(shapes.objects(block, SH.path))
            listed = next(shapes.objects(block, SH["in"]), None)
            if listed is None:
                continue
            values = frozenset(
                str(v) for v in rdflib.collection.Collection(shapes, listed)
            )
            if by_path.setdefault(path, values) != values:
                unsatisfiable.append(f"{shape} -> {path}")
    assert not unsatisfiable, f"contradictory sh:in constraints: {unsatisfiable}"
