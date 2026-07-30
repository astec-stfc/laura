"""SPARQL query interface for LAURA machine models.

Wraps a :class:`~laura.models.elementList.MachineModel` in an in-memory
rdflib graph and exposes SPARQL SELECT queries over it via
:meth:`LAURAQuery.sparql`, along with convenience helpers for common lookups.

The RDF graph is built lazily on first use and cached; call
:meth:`LAURAQuery.invalidate` after modifying the machine to force a rebuild.

Requires the optional ``rdf`` dependency group::

    pip install "laura-accelerator[rdf]"
"""

from __future__ import annotations

from typing import Any

# Standard PREFIX declarations prepended automatically to every query.
_PREFIXES = """\
PREFIX laura: <https://w3id.org/laura/>
PREFIX schema: <http://schema.org/>
PREFIX qudt:   <http://qudt.org/schema/qudt/>
PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:    <http://www.w3.org/2001/XMLSchema#>
"""


class LAURAQuery:
    """SPARQL query interface for a loaded LAURA machine model.

    Parameters
    ----------
    machine:
        :class:`~laura.models.elementList.MachineModel` to query.
    machine_name:
        Logical accelerator name used when building element IRIs.
        Default ``"machine"``.

    Examples
    --------
    ::

        from laura.query import LAURAQuery

        q = LAURAQuery(machine, machine_name="clara")
        quads = q.get_elements_by_hardware_type("Quadrupole")
        results = q.sparql(
            "SELECT ?name WHERE { ?e rdf:type laura:Dipole ; laura:name ?name . }"
        )
    """

    def __init__(self, machine, machine_name: str = "machine") -> None:
        self._machine = machine
        self._machine_name = machine_name
        self._graph = None

    # ------------------------------------------------------------------
    # Graph management
    # ------------------------------------------------------------------

    def _get_graph(self):
        if self._graph is None:
            from .Exporters.RDF import build_rdf_graph  # deferred import

            self._graph = build_rdf_graph(
                self._machine, machine_name=self._machine_name
            )
        return self._graph

    def invalidate(self) -> None:
        """Discard the cached RDF graph; it will be rebuilt on the next query."""
        self._graph = None

    # ------------------------------------------------------------------
    # Core SPARQL method
    # ------------------------------------------------------------------

    def sparql(self, query: str) -> list[dict[str, Any]]:
        """Execute a SPARQL SELECT query and return results as a list of dicts.

        Standard PREFIX declarations for ``laura:``, ``schema:``, ``qudt:``,
        ``rdf:``, ``rdfs:``, and ``xsd:`` are automatically prepended so
        callers need not repeat them.

        Parameters
        ----------
        query:
            SPARQL SELECT query.

        Returns
        -------
        list[dict[str, Any]]
            One dict per result row; keys are variable names, values are
            Python native types (``str``, ``int``, ``float``, ``bool``).
        """
        g = self._get_graph()
        full_query = _PREFIXES + "\n" + query
        results = g.query(full_query)
        rows: list[dict[str, Any]] = []
        for row in results:
            record: dict[str, Any] = {}
            for var in results.vars:
                val = row[var]
                if val is None:
                    record[str(var)] = None
                elif hasattr(val, "toPython"):
                    record[str(var)] = val.toPython()
                else:
                    record[str(var)] = str(val)
            rows.append(record)
        return rows

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def get_elements_in_area(self, area: str) -> list[str]:
        """Return names of all elements in the given machine area.

        Parameters
        ----------
        area:
            Machine area label (e.g. ``"S01"``, ``"LINAC"``).
        """
        safe = area.replace("\\", "\\\\").replace('"', '\\"')
        return [
            r["name"]
            for r in self.sparql(
                f'SELECT ?name WHERE {{\n'
                f'    ?elem laura:machine_area ?a ;\n'
                f'          laura:name ?name .\n'
                f'    FILTER(str(?a) = "{safe}")\n'
                f'}}'
            )
        ]

    def get_elements_by_hardware_type(self, hardware_type: str) -> list[str]:
        """Return names of all elements whose ``hardware_type`` matches.

        Parameters
        ----------
        hardware_type:
            Python class name used for ELEMENT_REGISTRY dispatch
            (e.g. ``"Quadrupole"``, ``"Screen"``).
        """
        safe = hardware_type.replace("\\", "\\\\")
        return [
            r["name"]
            for r in self.sparql(
                f"SELECT ?name WHERE {{\n"
                f"    ?elem rdf:type laura:{safe} ;\n"
                f"          laura:name ?name .\n"
                f"}}"
            )
        ]

    def get_elements_by_hardware_class(self, hardware_class: str) -> list[str]:
        """Return names of all elements whose ``hardware_class`` matches.

        Parameters
        ----------
        hardware_class:
            Hardware category label (e.g. ``"Magnet"``, ``"Diagnostic"``).
        """
        safe = hardware_class.replace("\\", "\\\\").replace('"', '\\"')
        return [
            r["name"]
            for r in self.sparql(
                f'SELECT ?name WHERE {{\n'
                f'    ?elem laura:hardware_class ?c ;\n'
                f'          laura:name ?name .\n'
                f'    FILTER(str(?c) = "{safe}")\n'
                f'}}'
            )
        ]
