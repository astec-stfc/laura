#!/usr/bin/env python3
"""Generate laura/schema/generated/laura_shacl.ttl from laura/schema/YAML/laura_schema.yaml.

Runs gen-shacl then collapses the duplicate property shapes it emits, the same
kind of correction :mod:`generate_orm` and :mod:`generate_sql` make to their own
generators' output.

gen-shacl (linkml 1.11.1) emits one ``sh:property`` block per contribution to a
slot as it walks a class's ancestry, rather than one per effective slot: 1593 of
the 1681 (shape, path) pairs in this schema arrive with two, three or four
blocks.  Most are byte-identical apart from ``sh:order`` and merely bloat the
file.  Six are fatal.  Where a class overrides a parent's ``slot_usage``, both
the inherited and the overriding block survive, and ``sh:property`` is
conjunctive, so the shape becomes unsatisfiable::

    laura:Collimator sh:property
        [ sh:path laura:hardware_type ; sh:in ( "Collimator" ) ],
        [ sh:path laura:hardware_type ; sh:in ( "Aperture" ) ] .   # inherited

No Collimator can validate against that, even though the schema says exactly
what a Collimator's hardware_type must be.  The classes affected are Collimator,
CrabCavity, FaradayCupMonitor, IntegratedCurrentTransformer, RFDeflectingCavity
and WallCurrentMonitor -- every class that overrides an override.

The block kept is the one that agrees with LinkML's own induced (fully
inherited, then overridden) view of the slot, so the schema stays the authority
rather than a heuristic about which block gen-shacl happened to emit first.

Usage (from repo root)::

    python laura/schema/generate_shacl.py

Or via the generate.ps1 / generate.sh scripts.
"""

import collections
import subprocess
import sys
from pathlib import Path

import rdflib
from linkml_runtime import SchemaView

SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")

# The predicates that actually differ between blocks of the same group.  Every
# other predicate is either identical across the group or is sh:order, which
# only records the slot's rank in whichever class contributed the block.
_VARYING = ("in", "class", "defaultValue", "description", "hasValue")


def _run_gen_shacl(schema_dir: Path) -> str:
    """Merge the schema chunks, run gen-shacl on the result, return its stdout.

    gen-shacl fails with a KeyError on a multi-file schema, so the imports have
    to be merged first.  The merged file is written next to the chunks because
    it still carries the ``imports:`` list and they resolve relatively.
    """
    python_dir = Path(sys.executable).parent

    def _tool(name: str) -> str:
        for candidate in (python_dir / name, python_dir / f"{name}.exe"):
            if candidate.exists():
                return str(candidate)
        return name

    merged = schema_dir / "_merged_temp.yaml"
    try:
        yaml_out = subprocess.run(
            [_tool("gen-yaml"), "--mergeimports", "laura_schema.yaml"],
            cwd=schema_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if yaml_out.returncode != 0:
            sys.stderr.write(yaml_out.stderr)
            raise RuntimeError(f"gen-yaml failed with exit code {yaml_out.returncode}")
        merged.write_text(yaml_out.stdout, encoding="utf-8")

        result = subprocess.run(
            [_tool("gen-shacl"), merged.name],
            cwd=schema_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            raise RuntimeError(f"gen-shacl failed with exit code {result.returncode}")
        return result.stdout
    finally:
        merged.unlink(missing_ok=True)


def _expected(induced, sv: SchemaView) -> dict:
    """What the induced slot says each of the varying predicates should be."""
    expected: dict[str, object] = {}

    if induced.equals_string is not None:
        expected["in"] = (str(induced.equals_string),)
        expected["hasValue"] = str(induced.equals_string)
    elif induced.equals_string_in:
        expected["in"] = tuple(str(v) for v in induced.equals_string_in)
    elif induced.range in sv.all_enums():
        expected["in"] = tuple(sv.all_enums()[induced.range].permissible_values)

    if induced.range in sv.all_classes():
        expected["class"] = sv.get_uri(sv.all_classes()[induced.range], expand=True)

    if induced.ifabsent is not None:
        # ``string(Generic)`` / ``float(0)`` -> ``Generic`` / ``0``
        raw = str(induced.ifabsent)
        expected["defaultValue"] = (
            raw.split("(", 1)[1].rsplit(")", 1)[0] if "(" in raw else raw
        )

    if induced.description is not None:
        expected["description"] = str(induced.description)

    return expected


def _read(graph: rdflib.Graph, block, predicate: str):
    """Read one predicate off a property block, normalising sh:in to a tuple."""
    value = next(graph.objects(block, SH[predicate]), None)
    if value is None:
        return None
    if predicate == "in":
        return tuple(str(v) for v in rdflib.collection.Collection(graph, value))
    return str(value)


def _score(graph: rdflib.Graph, block, expected: dict) -> tuple[int, int, int]:
    """Rank a block: agreement with the induced slot first, then completeness.

    A block that contradicts the induced slot is pushed below one that merely
    stays silent -- being wrong about hardware_type is what makes a shape
    unsatisfiable, whereas omitting it only makes the shape more permissive.
    """
    agree = disagree = 0
    for predicate in _VARYING:
        actual = _read(graph, block, predicate)
        if actual is None or predicate not in expected:
            continue
        if actual == expected[predicate]:
            agree += 1
        else:
            disagree += 1
    richness = len(set(graph.predicates(block)))
    return (-disagree, agree, richness)


def _drop_list(graph: rdflib.Graph, head) -> None:
    """Remove an RDF collection, cell by cell.

    Dropping only the triple that points at the list would strand the
    ``rdf:first``/``rdf:rest`` chain, which rdflib then serialises as a floating
    collection.
    """
    node = head
    while node is not None and node != rdflib.RDF.nil:
        nxt = next(graph.objects(node, rdflib.RDF.rest), None)
        graph.remove((node, None, None))
        node = nxt


def _drop(graph: rdflib.Graph, shape, block) -> None:
    """Remove a property block, its triples, and any RDF list it owns."""
    graph.remove((shape, SH.property, block))
    for predicate, obj in list(graph.predicate_objects(block)):
        if isinstance(obj, rdflib.BNode) and (obj, rdflib.RDF.first, None) in graph:
            _drop_list(graph, obj)
        graph.remove((block, predicate, obj))


def _dedupe(graph: rdflib.Graph, sv: SchemaView) -> int:
    """Collapse every (shape, path) group to the one block the schema implies."""
    by_uri = {
        str(sv.get_uri(cls, expand=True)): name
        for name, cls in sv.all_classes().items()
    }
    dropped = 0

    for shape in list(graph.subjects(SH.targetClass, None)):
        class_name = by_uri.get(str(next(graph.objects(shape, SH.targetClass))))
        if class_name is None:
            continue

        groups = collections.defaultdict(list)
        for block in graph.objects(shape, SH.property):
            groups[next(graph.objects(block, SH.path))].append(block)

        for path, blocks in groups.items():
            if len(blocks) == 1:
                continue
            slot_name = str(path).rsplit("/", 1)[-1].split("#")[-1]
            try:
                expected = _expected(sv.induced_slot(slot_name, class_name), sv)
            except (KeyError, ValueError):
                expected = {}
            keeper = max(blocks, key=lambda b: _score(graph, b, expected))
            for block in blocks:
                if block is not keeper:
                    _drop(graph, shape, block)
                    dropped += 1

    return dropped


def _induced_in(sv: SchemaView, slot_name: str, class_name: str):
    """The ``sh:in`` the induced slot implies for a class, or ``None``."""
    try:
        induced = sv.induced_slot(slot_name, class_name)
    except (KeyError, ValueError):
        return None
    return _expected(induced, sv).get("in")


def _widen_for_subclasses(graph: rdflib.Graph, sv: SchemaView) -> int:
    """Widen every ``sh:in`` that a subclass instance would contradict.

    LinkML resolves a ``slot_usage`` override by replacing the parent's
    constraint.  SHACL does not work that way: ``sh:targetClass`` matches
    subclasses too, so a parent's shape is also applied to every descendant
    instance.  Left as gen-shacl emits it, ``laura:Dipole`` carries
    ``sh:in ( "Dipole" )`` on hardware_type and therefore rejects every
    Horizontal_Corrector, because HorizontalCorrector is ``rdfs:subClassOf``
    Dipole.  Eleven shapes in this schema are unsatisfiable that way, including
    AcceleratorElement -- which every element is.

    The sound reading of a parent's fixed value is the union over the class and
    its descendants.  Nothing is lost: each descendant's own shape still pins it
    to its own single value, so a Horizontal_Corrector cannot claim to be a
    Quadrupole.  Only a node typed as the bare parent gains any freedom.

    This only bites when the validator is given the class hierarchy -- via
    ``ont_graph`` or an inferencer -- which is exactly when ``sh:class
    laura:AcceleratorElement`` on ``elements``/``upstream``/``downstream``
    becomes checkable, so an export cannot dodge both at once.
    """
    by_uri = {
        str(sv.get_uri(cls, expand=True)): name
        for name, cls in sv.all_classes().items()
    }
    widened = 0

    for shape in list(graph.subjects(SH.targetClass, None)):
        class_name = by_uri.get(str(next(graph.objects(shape, SH.targetClass))))
        if class_name is None:
            continue
        descendants = [c for c in sv.class_descendants(class_name) if c != class_name]
        if not descendants:
            continue

        for block in list(graph.objects(shape, SH.property)):
            listed = next(graph.objects(block, SH["in"]), None)
            if listed is None:
                continue
            slot_name = str(next(graph.objects(block, SH.path))).rsplit("/", 1)[-1]

            values = list(_read(graph, block, "in") or ())
            for descendant in descendants:
                for value in _induced_in(sv, slot_name, descendant) or ():
                    if value not in values:
                        values.append(value)
            if len(values) == len(_read(graph, block, "in") or ()):
                continue

            # Replace the collection wholesale; editing an rdf:first/rdf:rest
            # chain in place is how you end up with two of them.
            _drop_list(graph, listed)
            graph.remove((block, SH["in"], listed))
            head = rdflib.BNode()
            rdflib.collection.Collection(graph, head, [rdflib.Literal(v) for v in values])
            graph.add((block, SH["in"], head))
            # sh:hasValue demands the single fixed value, so it cannot survive
            # the widening either.
            graph.remove((block, SH.hasValue, None))
            widened += 1

    return widened


def generate(schema_dir: str = "laura/schema/YAML") -> str:
    """Generate and return the full content of the SHACL shapes graph."""
    path = Path(schema_dir)
    graph = rdflib.Graph()
    graph.parse(data=_run_gen_shacl(path), format="turtle")

    sv = SchemaView(str(path / "laura_schema.yaml"))
    dropped = _dedupe(graph, sv)
    print(f"Collapsed {dropped:,} duplicate property shapes", file=sys.stderr)

    widened = _widen_for_subclasses(graph, sv)
    print(f"Widened {widened:,} sh:in lists for subclasses", file=sys.stderr)

    return graph.serialize(format="turtle")


if __name__ == "__main__":
    out_path = Path("laura/schema/generated/laura_shacl.ttl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = generate()
    out_path.write_text(content, encoding="utf-8")
    print(f"Written {len(content):,} chars to {out_path}", file=sys.stderr)
