.. _interfaces:

Importing and Exporting
=======================

Beyond translation to simulation codes (:ref:`translator`), :mod:`LAURA` can read a machine
description from, and write one back out to, a number of general-purpose formats. These are
lossless-ish round trips of the *model* rather than lattice files for a particular tracking
code: YAML on disk, RDF for linked-data tooling, and a relational database for querying and
archiving.

.. _importers:

Importers
---------

:py:mod:`laura.Importers` reads element definitions into model objects.

YAML
~~~~

:py:mod:`laura.Importers.YAML_Loader` is the primary route, and the one used when a
:py:class:`LAURA <laura.laura.LAURA>` machine is constructed from a lattice package. The
loading pipeline -- dispatch on ``hardware_type``, lazy directory loading, optional JSON Schema
validation -- is described in detail in :doc:`Architecture/yaml-pipeline`.

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Function
     - Use
   * - ``read_YAML_Element_File(path, exclude_keys, validate)``
     - One element per file.
   * - ``read_YAML_Combined_File(path, exclude_keys, validate)``
     - A combined ``summary.yaml`` (or ``.json``) holding many elements.
   * - ``interpret_YAML_Element(dict)``
     - Turn an already-parsed dictionary into the right element class.
   * - ``validate_element_dict(dict)``
     - Check a raw dictionary against the generated JSON Schema. Requires ``pip install "laura-accelerator[schema]"``.

SimFrame
~~~~~~~~

:py:mod:`laura.Importers.SimFrame_Loader` converts lattices written for the ASTeC SimFrame
framework into :mod:`LAURA` elements.

.. warning::

   :py:mod:`laura.Importers.CATAP_Loader`, :py:mod:`laura.Importers.MySafeLoader` and
   :py:mod:`laura.Exporters.Export_CATAP_YAML` still use pre-package absolute imports
   (``from Importers... import``) and a ``laura.models.PV`` module that no longer exists.
   They cannot currently be imported, and are mocked out when this documentation is built.

.. _exporters:

Exporters
---------

:py:mod:`laura.Exporters` writes a
:py:class:`MachineModel <laura.models.elementList.MachineModel>` back out.

YAML
~~~~

:py:mod:`laura.Exporters.YAML` writes either one file per element, mirroring the
``{hardware_class}/{hardware_type}/{name}.yaml`` directory layout, or a single combined
summary file:

.. code-block:: python

    from laura.Exporters.YAML import (
        export_machine, export_machine_combined_file, export_as_yaml,
    )

    export_machine("./out", machine)                     # one file per element
    export_machine_combined_file("./out", machine)       # ./out/summary.yaml
    element_dict = export_as_yaml(None, machine["QUAD-01"])   # return, don't write

All of these take a ``position_mode`` that selects how each element's placement is written --
the three :ref:`positioning modes <positioning-modes>`. Because the model resolves every mode
into both global coordinates and an arc-length ``s``, a machine can be re-exported in a form
different from the one it was read in:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - ``position_mode``
     - Output
   * - ``"global"`` (default)
     - Cartesian ``middle: {x, y, z}``.
   * - ``"s"``
     - Arc-length ``s: <float>``. Requires a resolved trajectory.
   * - ``"reference"``
     - ``reference_placement`` with an ``s_offset`` relative to the preceding element in section order. The first element of a section falls back to ``"s"``.

.. code-block:: python

    # Rewrite an absolute-coordinate machine as a chain of relative placements
    export_machine("./relative", machine, position_mode="reference")

RDF / linked data
~~~~~~~~~~~~~~~~~

The LinkML schema doubles as an ontology, so a machine can be emitted as RDF and consumed by
standard linked-data tooling. Requires ``pip install "laura-accelerator[rdf]"``.

.. code-block:: python

    machine.export_rdf("machine.ttl")                     # Turtle (default)
    machine.export_rdf("machine.jsonld", format="json-ld")

Accepted formats are ``"turtle"`` / ``"ttl"``, ``"json-ld"`` / ``"jsonld"``,
``"n-triples"`` / ``"nt"``, and ``"xml"`` / ``"rdfxml"``. The underlying functions are
:py:func:`build_rdf_graph <laura.Exporters.RDF.build_rdf_graph>` and
:py:func:`export_machine_rdf <laura.Exporters.RDF.export_machine_rdf>`.

SQL
~~~

:py:mod:`laura.Exporters.SQL` persists a machine to any SQLAlchemy-supported database, using
the ORM generated from the same schema (``laura/schema/generated/laura_orm.py``). Tables are
created if absent, and each export is a separate snapshot identified by an integer ID.
Requires ``pip install "laura-accelerator[sql]"``.

.. code-block:: python

    from laura.Exporters.SQL import (
        export_machine, load_machine_elements, load_machine_sections,
    )

    machine_id = export_machine(machine, db_url="sqlite:///machine.db")

    elements = load_machine_elements("sqlite:///machine.db", machine_id)
    sections = load_machine_sections("sqlite:///machine.db", machine_id)

CATAP
~~~~~

:py:mod:`laura.Exporters.CATAP` writes elements in the format used by the CATAP control-system
abstraction layer, via ``export_machine(path, machine)`` or ``export_machine_dict(machine)``.

.. _sparql-queries:

Querying with SPARQL
--------------------

:py:class:`LAURAQuery <laura.query.LAURAQuery>` wraps a machine model in an in-memory rdflib
graph and runs SPARQL ``SELECT`` queries against it. The graph is built lazily on first use and
cached; call :py:meth:`invalidate <laura.query.LAURAQuery.invalidate>` after modifying the
machine to force a rebuild. Requires ``pip install "laura-accelerator[rdf]"``.

Standard ``PREFIX`` declarations for ``laura:``, ``schema:``, ``qudt:``, ``rdf:``, ``rdfs:``
and ``xsd:`` are prepended automatically, so queries can be written without them:

.. code-block:: python

    from laura.query import LAURAQuery

    q = LAURAQuery(machine, machine_name="clara")

    quads = q.get_elements_by_hardware_type("Quadrupole")
    magnets = q.get_elements_by_hardware_class("Magnet")
    injector = q.get_elements_in_area("INJ")

    rows = q.sparql(
        "SELECT ?name WHERE { ?e rdf:type laura:Dipole ; laura:name ?name . }"
    )

The same query is available directly on the model, which builds and caches a
:py:class:`LAURAQuery <laura.query.LAURAQuery>` internally:

.. code-block:: python

    rows = machine.sparql(
        "SELECT ?name WHERE { ?e rdf:type laura:Dipole ; laura:name ?name . }"
    )

Each result row is returned as a dictionary keyed by variable name, with values converted to
native Python types.
