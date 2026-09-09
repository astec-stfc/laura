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

The exporter can write these featuresback out again (see :ref:`compact-yaml-output`):

* **Inheritance.** An element may name a parent with ``inherits_from`` (or ``inherit``) and
  state only what differs from it. Parents may be other elements or dedicated templates --
  files whose names begin with ``_``, or entries under the ``_templates`` key of a combined
  file. Templates need not be valid elements on their own.
* **Sequential placement.** An element may give no position at all and take its place from the
  section's ``order``; see :ref:`sequential-placement`.
* **Repeated, reversed and nested lines.** A section's element list may repeat an entry
  (``fodo_cell: {repeat: 3}``), reverse it (``{repeat: -1}``) and
  splice in another section by name; see :ref:`repeated-lines`.

All three are expanded at load time -- the loaded model always carries fully merged elements
with resolved coordinates and one flat list of names per section.
:doc:`Architecture/yaml-pipeline` describes them in detail.

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
the :ref:`positioning modes <positioning-modes>`. Because the model resolves every mode into
both global coordinates and an arc-length ``s``, a machine can be re-exported in a form
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
   * - ``"sequential"``
     - No position at all, where the element abuts its predecessor -- the compact drift-based form (see :ref:`sequential-placement`). The section orders are written alongside, to ``_sections.yaml``.

.. code-block:: python

    # Rewrite an absolute-coordinate machine as a chain of relative placements
    export_machine("./relative", machine, position_mode="reference")

.. _compact-yaml-output:

Compacting the output
~~~~~~~~~~~~~~~~~~~~~

A default export writes what the loader produced: every element fully merged, with resolved
coordinates. Three options invert the loader's expansions:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Option
     - Effect
   * - ``position_mode="sequential"``
     - Drops the position of every element that abuts its predecessor, and writes the section orders to ``_sections.yaml`` (``write_sections=False`` suppresses that file). An element that does not abut keeps an explicit ``s`` at its entrance, and a warning says so. A name the load split into numbered copies (``D1.1``, ``D1.2``, ...) is written back as one element listed twice, so the order reads as it was authored; a group whose copies have since been changed, or whose bare name is still an element in its own right, stays numbered and warns. Authored ``repeat`` counts and nested lines are put back into ``_sections.yaml`` too, along with the definition of every line referenced; if re-expanding them no longer reproduces the machine's own order, every section is written out fully expanded and a warning says so. Authored ``repeat`` counts and nested lines are put back into ``_sections.yaml`` too, along with the definition of every line referenced; if re-expanding them no longer reproduces the machine's own order, every section is written out fully expanded and a warning says so.
   * - ``collapse_inheritance=True``
     - Restores ``inherits_from`` and removes every key the parent already supplies, comparing against the parent as the loader would have merged it. ``template_root`` says where to look for the parents (default: the machine's own element directory); with ``copy_templates=True`` each parent used, and its own ancestors, is written into the export root as ``_<name>.yaml`` so the tree reloads on its own.
   * - ``collapse_schema=True``
     - The same idea for control-variable definitions: restores the ``schema`` reference and drops the entries it supplies. ``schema_root`` and ``copy_schemas`` behave like their template counterparts.

All three fail verbosely: anything that cannot be shown to be redundant is written out in
full. Unresolvable parents are warned about and the element is written expanded.

Empty containers are pruned from every export, collapsed or not, unless if they mean something
when empty.

.. code-block:: python

    # Round-trip a lattice back into the compact form it was written in
    export_machine(
        "./compact", machine,
        position_mode="sequential",
        collapse_inheritance=True,
    )

The result reloads to an equal model, and re-exporting it produces the same bytes again.
:doc:`Architecture/yaml-pipeline` documents the rules each collapse follows.

RDF / linked data
~~~~~~~~~~~~~~~~~

The LinkML schema doubles as an ontology (see :ref:`schema`), so a machine can be emitted as RDF
and consumed by standard linked-data tooling -- validated against the generated SHACL shapes,
reasoned over with the OWL ontology, or queried with SPARQL. Requires
``pip install "laura-accelerator[rdf]"``.

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
