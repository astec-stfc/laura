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


_CONTROL_VARIABLE_SLOTS: dict[str, str] = {
    "identifier": "string",
    "protocol": "string",
    "units": "string",
    "dtype": "string",
    "description": "string",
    "control_type": "enum",
    "target": "string",
    "readback": "string",
    "setpoint": "string",
    "read_only": "boolean",
    "auto_buffer": "boolean",
    "buffer_size": "integer",
}

_LITERAL_COERCE = {"string": str, "boolean": bool, "integer": int}


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

    Control variables hang off the element the same way::

        <element> laura:controls <element>/controls .
        <element>/controls a laura:ControlsInformation ;
            laura:variables <element>/controls/SETI .
        <element>/controls/SETI a laura:ControlVariable ;
            laura:name "SETI" ;
            laura:identifier "SEC-Q1:SETI" ;
            laura:protocol "EPICS" .

    ``laura:name`` comes from the key the variable is filed under, which is what
    the schema's ``key: true`` on ``ControlVariable.name`` means -- the Pydantic
    model does not carry it as a field.

    The machine itself is a node, so sections and layouts are reachable rather
    than being lost at export time::

        <machine> a laura:MachineModel ;
            laura:elements <machine>/SEC/Q1 ;
            laura:sections <machine>/sections/SEC ;
            laura:layouts  <machine>/layouts/beam .
        <machine>/sections/SEC a laura:SectionLattice ;
            laura:name "SEC" ;
            laura:elements <machine>/SEC/Q1 .

    ``SectionLattice.elements`` and ``MachineLayout.sections`` are class-ranged,
    so they are emitted as IRIs into the same element and section nodes the
    machine links -- matching the Python models, where both hold the objects and
    not their names.  Ordering is not carried: no LinkML multivalued collection
    is ordered, so ``SectionLattice.order`` has no slot to go in -- recover the
    sequence from each element's ``laura:physical/laura:s``.  A name that no
    element or section in the machine matches is skipped rather than minted as a
    dangling IRI, which would fail ``sh:class``.

    ``upstream``/``downstream`` are emitted as IRIs between elements, giving the
    control/signal graph.

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

    # Minted up front: upstream/downstream reference elements by name and may
    # point forward, so the whole map has to exist before the first triple.
    elem_uris = {
        name: URIRef(
            f"{base}{str(getattr(elem, 'machine_area', None) or 'unknown')}/{name}"
        )
        for name, elem in machine.elements.items()
        if elem is not None
    }

    for name, elem in machine.elements.items():
        if elem is None:
            continue

        area = str(getattr(elem, "machine_area", None) or "unknown")
        elem_uri = elem_uris[name]

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

        for slot in ("upstream", "downstream"):
            for other in getattr(elem, slot, None) or []:
                target = elem_uris.get(str(other))
                if target is not None:
                    g.add((elem_uri, LAURA[slot], target))

        variables = getattr(getattr(elem, "controls", None), "variables", None)
        if variables:
            controls_uri = URIRef(f"{elem_uri}/controls")
            g.add((elem_uri, LAURA["controls"], controls_uri))
            g.add((controls_uri, RDF.type, LAURA["ControlsInformation"]))

            for var_name, variable in variables.items():
                var_uri = URIRef(f"{controls_uri}/{var_name}")
                g.add((controls_uri, LAURA["variables"], var_uri))
                g.add((var_uri, RDF.type, LAURA["ControlVariable"]))
                g.add((var_uri, LAURA["name"], Literal(str(var_name))))

                for slot, kind in _CONTROL_VARIABLE_SLOTS.items():
                    raw = getattr(variable, slot, None)
                    if raw is None:
                        continue
                    if isinstance(raw, type):
                        # dtype is held as the Python type itself; the schema
                        # says to serialise it by name.
                        raw = raw.__name__
                    value = (
                        Literal(str(raw))
                        if kind == "enum"
                        else Literal(
                            _LITERAL_COERCE[kind](raw), datatype=XSD[kind]
                        )
                    )
                    g.add((var_uri, LAURA[slot], value))

    def add_lattice_common(uri, lattice, type_slot: str) -> None:
        """The slots SectionLattice and MachineLayout share via BaseLatticeModel."""
        master = getattr(lattice, "master_lattice", None)
        if master:
            g.add((uri, LAURA["master_lattice"], Literal(str(master))))

        # Enum-ranged, so a plain literal -- see _CONTROL_VARIABLE_SLOTS.
        kind = getattr(lattice, type_slot, None)
        if kind:
            g.add((uri, LAURA[type_slot], Literal(str(kind))))

        freq = getattr(lattice, "revolution_frequency", None)
        if freq is not None:
            g.add(
                (
                    uri,
                    LAURA["revolution_frequency"],
                    Literal(float(freq), datatype=XSD.double),
                )
            )

        # Always a resolved mapping by the time we see it: BaseLatticeModel's
        # model_post_init turns a YAML path into the dict it names.
        for def_name, value in (
            getattr(lattice, "functional_definitions", None) or {}
        ).items():
            def_uri = URIRef(f"{uri}/functional_definitions/{def_name}")
            g.add((uri, LAURA["functional_definitions"], def_uri))
            g.add((def_uri, RDF.type, LAURA["FunctionalDefinition"]))
            g.add((def_uri, LAURA["name"], Literal(str(def_name))))
            g.add((def_uri, LAURA["value"], Literal(float(value), datatype=XSD.double)))

    # ── Machine, sections and layouts ────────────────────────────────────────
    machine_uri = URIRef(base.rstrip("/"))
    g.add((machine_uri, RDF.type, LAURA["MachineModel"]))
    for uri in elem_uris.values():
        g.add((machine_uri, LAURA["elements"], uri))

    section_uris: dict[str, URIRef] = {}
    for sec_name, section in (getattr(machine, "sections", None) or {}).items():
        sec_uri = URIRef(f"{base}sections/{sec_name}")
        g.add((machine_uri, LAURA["sections"], sec_uri))
        g.add((sec_uri, RDF.type, LAURA["SectionLattice"]))
        g.add((sec_uri, LAURA["name"], Literal(str(sec_name))))
        add_lattice_common(sec_uri, section, "section_type")
        for member in getattr(section, "order", None) or []:
            target = elem_uris.get(str(member))
            if target is not None:
                g.add((sec_uri, LAURA["elements"], target))
        section_uris[sec_name] = sec_uri

    for layout_name, layout in (getattr(machine, "lattices", None) or {}).items():
        layout_uri = URIRef(f"{base}layouts/{layout_name}")
        g.add((machine_uri, LAURA["layouts"], layout_uri))
        g.add((layout_uri, RDF.type, LAURA["MachineLayout"]))
        g.add((layout_uri, LAURA["name"], Literal(str(layout_name))))
        add_lattice_common(layout_uri, layout, "layout_type")
        for sec_name in getattr(layout, "sections", None) or []:
            target = section_uris.get(str(sec_name))
            if target is not None:
                g.add((layout_uri, LAURA["sections"], target))

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
