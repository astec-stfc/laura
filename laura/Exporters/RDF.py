"""RDF serialisation of LAURA accelerator element models.

Converts a :class:`~laura.models.elementList.MachineModel` to an
``rdflib.Graph`` and writes it to Turtle, JSON-LD, N-Triples, or RDF/XML.

Requires the optional ``rdf`` dependency group::

    pip install "laura-accelerator[rdf]"
"""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import rdflib

_LAURA_NS = "https://w3id.org/laura/"
_BASE_IRI = "https://w3id.org/laura/"

# Map user-friendly format strings to rdflib serialiser names.
_FORMAT_ALIASES: dict[str, str] = {
    "turtle": "turtle",
    "ttl": "turtle",
    "json-ld": "json-ld",
    "jsonld": "json-ld",
    "json_ld": "json-ld",
    "n-triples": "nt",
    "ntriples": "nt",
    "nt": "nt",
    "xml": "xml",
    "rdfxml": "xml",
    "rdf": "xml",
}


def _require_rdflib():
    """Import rdflib or raise a helpful ImportError."""
    try:
        import rdflib  # noqa: PLC0415

        return rdflib
    except ImportError as exc:
        raise ImportError(
            "rdflib is required for RDF export and SPARQL queries. "
            'Install with: pip install "laura-accelerator[rdf]"'
        ) from exc


def _resolve_format(format: str) -> str:
    return _FORMAT_ALIASES.get(format.lower(), format)


def build_rdf_graph(
    machine,
    machine_name: str = "machine",
) -> "rdflib.Graph":
    """Build an ``rdflib.Graph`` from all elements in a *MachineModel*.

    Each element is given an IRI of the form::

        https://w3id.org/laura/{machine_name}/{machine_area}/{element_name}

    Core metadata slots (``name``, ``hardware_type``, ``hardware_class``,
    ``hardware_model``, ``machine_area``) are emitted as datatype properties
    under the ``laura:`` namespace.

    Physical data is nested as the schema declares it, not flattened onto the
    element::

        <element> laura:physical <element>/physical .
        <element>/physical a laura:PhysicalElement ;
            laura:length 0.3 ;
            laura:middle <element>/physical/middle .
        <element>/physical/middle a laura:Position ;
            laura:x 1.0 ; laura:y 0.0 ; laura:z 2.0 .

    The intermediate nodes get derived IRIs rather than blank nodes so that
    successive exports of the same machine diff cleanly.

    Parameters
    ----------
    machine:
        Loaded :class:`~laura.models.elementList.MachineModel`.
    machine_name:
        Logical accelerator name embedded in element IRIs.
        Default ``"machine"``.

    Returns
    -------
    rdflib.Graph
    """
    rdflib = _require_rdflib()
    from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD  # noqa: PLC0415

    LAURA = Namespace(_LAURA_NS)
    g = Graph()
    g.bind("laura", LAURA)
    g.bind("schema", "http://schema.org/")
    g.bind("qudt", "http://qudt.org/schema/qudt/")

    base = f"{_BASE_IRI}{machine_name}/"

    for name, elem in machine.elements.items():
        if elem is None:
            continue

        area = str(getattr(elem, "machine_area", None) or "unknown")
        elem_uri = URIRef(f"{base}{area}/{name}")

        g.add((elem_uri, RDF.type, LAURA[elem.linkml_class_name()]))

        # Core metadata
        g.add((elem_uri, LAURA["name"], Literal(name)))
        g.add((elem_uri, LAURA["machine_area"], Literal(area)))

        hw_type = getattr(elem, "hardware_type", None)
        if hw_type:
            g.add((elem_uri, LAURA["hardware_type"], Literal(str(hw_type))))

        hw_class = getattr(elem, "hardware_class", None)
        if hw_class:
            g.add((elem_uri, LAURA["hardware_class"], Literal(str(hw_class))))

        hw_model = getattr(elem, "hardware_model", None)
        if hw_model:
            g.add((elem_uri, LAURA["hardware_model"], Literal(str(hw_model))))

        physical = getattr(elem, "physical", None)
        if physical is not None:
            phys_uri = URIRef(f"{elem_uri}/physical")
            g.add((elem_uri, LAURA["physical"], phys_uri))
            g.add((phys_uri, RDF.type, LAURA["PhysicalElement"]))

            for slot in ("length", "s"):
                value = getattr(physical, slot, None)
                if value is not None:
                    g.add(
                        (
                            phys_uri,
                            LAURA[slot],
                            Literal(float(value), datatype=XSD.double),
                        )
                    )

            for slot in ("middle", "datum"):
                pos = getattr(physical, slot, None)
                if pos is None:
                    continue
                pos_uri = URIRef(f"{phys_uri}/{slot}")
                g.add((phys_uri, LAURA[slot], pos_uri))
                g.add((pos_uri, RDF.type, LAURA["Position"]))
                for axis in ("x", "y", "z"):
                    coord = getattr(pos, axis, None)
                    if coord is not None:
                        g.add(
                            (
                                pos_uri,
                                LAURA[axis],
                                Literal(float(coord), datatype=XSD.double),
                            )
                        )

    return g


def export_machine_rdf(
    machine,
    path: str,
    format: str = "turtle",
    machine_name: str = "machine",
) -> None:
    """Serialise a :class:`~laura.models.elementList.MachineModel` to an RDF file.

    Parameters
    ----------
    machine:
        Machine to serialise.
    path:
        Output file path (e.g. ``"machine.ttl"``).
    format:
        RDF serialisation format.  Accepted values (case-insensitive):
        ``"turtle"`` / ``"ttl"`` (default), ``"json-ld"`` / ``"jsonld"``,
        ``"n-triples"`` / ``"nt"``, ``"xml"`` / ``"rdfxml"``.
    machine_name:
        Logical accelerator name embedded in element IRIs.  Default ``"machine"``.
    """
    g = build_rdf_graph(machine, machine_name=machine_name)
    g.serialize(destination=path, format=_resolve_format(format))
