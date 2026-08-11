.. _schema:

The LAURA Schema
================

:mod:`LAURA` is **schema-first**. The definitive description of an accelerator element -- what
types exist, how they relate, which properties each carries, what units those properties are in
-- is not the Python source. It is a `LinkML <https://linkml.io/>`_ ontology in
``laura/schema/YAML/``. Everything else, including the Python classes you import, is generated
from it or checked against it.

That choice is what lets one description serve several audiences at once. The same file that
produces the Pydantic models also produces a JSON Schema for validating lattice YAML, an OWL
ontology for reasoners, SHACL shapes for RDF validation, a SQLAlchemy ORM, a GraphQL schema and
TypeScript types. A property added in one place appears, correctly typed and documented, in all
of them.

Layout
------

The schema is split across eleven files, all imported by ``laura_schema.yaml``, which is the
only file you should ever point a generator at. The others are *chunks*, not standalone models:
they refer freely to classes defined in their siblings, and generating from one on its own will
fail.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - File
     - Contents
   * - ``laura_schema.yaml``
     - The root. Prefixes, subsets, the ``HardwareClassEnum``, and the three abstract layers ``AcceleratorElement`` → ``StandardElement`` → ``Element`` → ``PhysicalAcceleratorElement``, plus the ``ElectricalElement`` / ``ManufacturerElement`` / ``ReferenceElement`` composition models.
   * - ``geometry.yaml``
     - ``Position``, ``Rotation``, ``PhysicalElement``, ``ElementPositionError``, ``ElementSurvey``, ``ReferencePlacement``.
   * - ``controls.yaml``
     - ``ControlVariable``, ``ControlsInformation``, ``IOTypeEnum``, ``ControlTypeEnum``.
   * - ``elements.yaml``
     - Simple physical elements: ``Drift``, ``Marker``, ``Aperture``, ``Collimator``, ``Shutter``, ``Valve``, ``Stage``, ``VacuumGauge``, ``Laser``, ``Lighting``, ``TwissMatch``, ``PowerSupply``.
   * - ``machine.yaml``
     - ``SectionLattice``, ``MachineLayout``, ``MachineModel``.
   * - ``simulation.yaml``
     - ``SimulationElement`` and its per-element-type subclasses.
   * - ``magnetic.yaml``
     - The magnetic composition models: ``Magnet`` (the element base), ``MagneticElement``, ``Multipole``, ``Multipoles``, ``FieldIntegral``, ``LinearSaturationFit``, ``DegaussableElement``.
   * - ``magnets.yaml``
     - The concrete magnet elements (``Dipole``, ``Quadrupole``, …) and their matching ``*_Magnet`` field models.
   * - ``rf.yaml``
     - ``RFCavityElement``, ``WakefieldElement``, ``LowLevelRFElement``, ``PIDElement``, and the RF element classes.
   * - ``diagnostics.yaml``
     - Diagnostic elements and their ``*DiagnosticElement`` measurement models, including the camera/screen chain.
   * - ``laser_plasma.yaml``
     - ``LaserElement``, ``PlasmaElement``, and the laser optics elements.

Anatomy of a class
------------------

A concrete element is usually a handful of lines, because almost everything is inherited. Here
is the whole of ``Quadrupole``:

.. code-block:: yaml

   Quadrupole:
     is_a: Magnet
     slot_usage:
       magnetic:
         range: Quadrupole_Magnet
       hardware_type:
         equals_string: Quadrupole
         ifabsent: Quadrupole

``is_a: Magnet`` brings in the physical placement, the electrical/manufacturer/controls
sub-models, the ``degauss`` block and ``hardware_class: Magnet``. The ``slot_usage`` block then
narrows two inherited slots for this class only: the generic ``magnetic`` slot is bound to
``Quadrupole_Magnet``, and ``hardware_type`` is pinned to the literal string ``Quadrupole``.

That ``equals_string`` is what makes the schema an enforcement mechanism rather than
documentation. ``hardware_type`` is the key :mod:`LAURA` dispatches on when loading YAML
(see :doc:`Architecture/yaml-pipeline`), so a file claiming ``hardware_type: Quadruple`` is
caught by schema validation, not just by a failed dictionary lookup at runtime.

A composition model looks much the same, but declares its own slots:

.. code-block:: yaml

   Multipole:
     description: >-
       Individual multipole field component, characterised by order and
       integrated normal / skew strengths at a reference radius.
     class_uri: laura:Multipole
     attributes:
       order:
         range: integer
         description: "Multipole order (0 = dipole, 1 = quadrupole, ...)."
         ifabsent: int(0)
         minimum_value: 0
       normal:
         range: float
         any_of:
           - range: float
           - range: string
         in_subset:
           - functional_parameters
         description: "Integrated normal (upright) multipole strength [T.m^{1-n}]."
         ifabsent: float(0)
       radius:
         range: float
         description: Reference radius for multipole normalisation [m].
         ifabsent: float(0)
         unit:
           ucum_code: m

Slot conventions
----------------

A handful of LinkML facets carry specific meaning in :mod:`LAURA`:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Facet
     - Meaning
   * - ``identifier: true``
     - Marks a unique key. Carried by ``AcceleratorElement.name``, ``SectionLattice.name`` and ``MachineLayout.name``.
   * - ``equals_string``
     - Pins a slot to a literal for one class. Used on ``hardware_type`` in every concrete element, and on ``order`` (as ``equals_number``) in the ``*_Magnet`` models, so a ``Sextupole_Magnet`` cannot claim ``order: 1``.
   * - ``ifabsent``
     - The default. ``generate_pydantic.py`` reads these back out of the schema and converts the corresponding generated field from ``Optional[T] = None`` to ``T = <default>``, so a Python default and a schema default can never drift apart.
   * - ``aliases``
     - Alternative *input* spellings, kept for backwards compatibility with older lattice files. They become a pydantic ``validation_alias=AliasChoices(...)``, so ``maxI`` is accepted when loading but ``max_i`` is the only name you can read back. Aliases are resolved per class, so the same slot name in two classes can carry different aliases.
   * - ``unit.ucum_code``
     - The physical unit, as a `UCUM <https://ucum.org/>`_ code (``m``, ``rad``, ``A``, ``Hz``, ``T``). Present on every dimensional quantity; carried into the OWL ontology through the QUDT vocabulary so units survive into linked-data tooling.
   * - ``minimum_value`` / ``maximum_value``
     - Range constraints, e.g. Euler angles bounded to ±π. These become pydantic ``ge`` / ``le``.
   * - ``multivalued``
     - A list-valued slot. With ``inlined: true`` and ``inlined_as_list: false`` it becomes a ``dict[str, T]`` instead -- the form used for keyed collections such as ``Multipoles`` and ``ControlsInformation.variables``.
   * - ``any_of``
     - Used where a slot accepts either a number or a symbolic name; see :ref:`functional-parameters`.
   * - ``slot_uri``
     - Alignment with an external vocabulary, e.g. ``manufacturer`` and ``serial_number`` map onto ``schema:manufacturer`` and ``schema:serialNumber``.

Subsets
-------

Subsets tag groups of slots that cut across the class hierarchy. Four are descriptive
(``physical_properties``, ``magnetic_properties``, ``rf_properties``,
``diagnostic_properties``, ``laser_properties``), but two are load-bearing:

* ``functional_parameters`` -- the slot may hold the *name* of a functional definition as well
  as a number. :py:func:`functional_references <laura.models.base_models.functional_references>`
  looks for exactly this membership when collecting the symbols an element refers to, so adding
  a slot to this subset is all that is needed to make it symbolically definable. See
  :ref:`functional-parameters`.
* ``bend_angle_reference`` -- the slot additionally accepts an expression referencing the dipole
  bend angle (any string containing the reserved token ``angle``). Such values are not
  functional-definition names and are skipped when collecting references.

Subset membership is used rather than LinkML ``annotations`` because ``gen-yaml`` -- which the
SHACL generation step pipes through -- cannot serialise ``Annotation`` objects.

.. _schema-artefacts:

Generated artefacts
-------------------

Running ``laura/schema/generate.ps1`` (or ``generate.sh``) regenerates everything below from
``laura_schema.yaml``. It requires ``pip install "laura-accelerator[schema]"``.

.. list-table::
   :header-rows: 1
   :widths: 38 22 40

   * - Artefact
     - Generator
     - Purpose
   * - ``laura/models/_generated.py``
     - ``gen-pydantic`` (+ post-processing)
     - The Pydantic base classes the hand-written models wrap.
   * - ``generated/laura_element.schema.json``
     - ``gen-json-schema``
     - Runtime validation of lattice YAML (``validate=True``).
   * - ``generated/laura_ontology.owl``
     - ``gen-owl``
     - OWL ontology for Protégé and reasoners.
   * - ``generated/laura_context.jsonld``
     - ``gen-jsonld-context``
     - JSON-LD context for the RDF export.
   * - ``generated/laura_shacl.ttl``
     - ``gen-shacl``
     - SHACL shapes for validating exported RDF.
   * - ``generated/laura_orm.py``
     - ``generate_orm.py``
     - SQLAlchemy ORM used by the SQL exporter.
   * - ``generated/laura_schema.sql``
     - ``gen-sqltables``
     - Plain SQL DDL.
   * - ``generated/laura_schema.graphql``
     - ``gen-graphql``
     - GraphQL schema.
   * - ``generated/laura_types.ts``
     - ``gen-typescript``
     - TypeScript types, for browser-side tooling.
   * - ``docs/source/schema/``
     - ``gen-doc``
     - Per-class and per-slot reference documentation; published as :doc:`schema/index` and summarised in :ref:`schema-reference` below.
   * - ``generated/element-er-auto.md``
     - ``gen-erdiagram``
     - Skeletal ER diagram. The full hand-maintained class diagram lives in :doc:`Architecture/element-er` and is deliberately *not* overwritten.

.. warning::

   Nothing in ``laura/schema/generated/`` or in ``laura/models/_generated.py`` should be edited
   by hand -- the next regeneration will discard the change. Fix the schema instead.

From schema to Python
---------------------

``gen-pydantic`` alone does not produce classes that can be used directly, so
``laura/schema/generate_pydantic.py`` wraps it with six post-processing passes:

#. **Rename** every schema model class to ``_XxxBase``, leaving enums under their own names so
   they stay importable. This frees the plain names for the hand-written wrappers.
#. **Apply ``ifabsent`` defaults**, converting ``Optional[T] = None`` to ``T = <default>`` for
   primitive-typed slots.
#. **Fix multivalued slots**, emitting ``list[T]`` or ``dict[str, T]`` with the right
   ``default_factory``.
#. **Inject ``AliasChoices``** for slots declaring ``aliases``, resolved per class.
#. **Mirror descriptions as attribute docstrings**, because ``sphinx.ext.autodoc`` renders a
   string literal following an annotated assignment but ignores ``Field(description=...)``.
   This is why the API reference for the models is populated at all.
#. **Drop excluded slots** -- a handful of slots (``MagneticElement.angle``) are implemented as
   Python properties on the wrapper, and pydantic cannot have a subclass property shadowing an
   inherited field.

The hand-written classes in ``laura/models/`` then inherit from those bases and add what a
schema cannot express: validators, computed geometry, cascading attribute access, and the
``hardware_type`` defaults that drive the element registry. The mapping between the two naming
schemes is tabulated in :doc:`Architecture/element-hierarchy`.

.. code-block:: bash

   # Regenerate just the Pydantic bases
   python laura/schema/generate_pydantic.py

   # Regenerate everything
   .\laura\schema\generate.ps1        # Windows
   bash laura/schema/generate.sh      # Linux / macOS

Validation
----------

The schema is enforced at two points, both optional:

**On load.** Passing ``validate=True`` to any YAML loader checks the raw dictionary against
``laura_element.schema.json`` *before* Pydantic parsing. This turns a silently-dropped element
into an explicit ``jsonschema.ValidationError`` naming the offending field, which is usually
what you want when a machine description is not loading as expected:

.. code-block:: python

   from laura.importers.yaml_loader import read_yaml_element_file

   element = read_yaml_element_file("INJ-MAG-DIP-01.yaml", validate=True)

**On export.** RDF written by :py:meth:`export_rdf <laura.models.element_list.MachineModel.export_rdf>`
(see :ref:`interfaces`) can be checked against ``laura_shacl.ttl`` with any SHACL engine.

Beyond that, Pydantic enforces the schema's ranges, defaults and constraints on every element
constructed in Python, whether it came from a file or not.

Extending the schema
--------------------

Adding an element type is a schema change first and a Python change second; the full recipe,
including the concrete-magnet case, is in
:doc:`Architecture/element-hierarchy`. In outline:

#. Add the class to the appropriate chunk file, with an ``equals_string`` constraint on
   ``hardware_type``.
#. Regenerate: ``python laura/schema/generate_pydantic.py``.
#. Add the wrapper in ``laura/models/element.py``, inheriting the generated base and either
   ``PhysicalBaseElement`` (if it has a position) or ``Element`` (if not).

The wrapper is registered in ``ELEMENT_REGISTRY`` automatically at import time -- the registry
is derived from the module's own classes, not hand-maintained -- so no separate registration
step is needed.

.. _schema-reference:

Schema reference
----------------

Every class, slot, enumeration and type in the ontology has its own generated reference page,
listing its description, range, defaults, constraints, URI mappings and the classes it is used
by. These are produced by ``gen-doc`` and are the authoritative per-item documentation; the
narrative pages on this site link into them where a detail matters.

:doc:`Browse the full schema reference → <schema/index>`

Useful entry points:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Page
     - What it covers
   * - :doc:`AcceleratorElement <schema/AcceleratorElement>`
     - The root class every element inherits: naming, hardware classification, and the signal-graph slots.
   * - :doc:`PhysicalAcceleratorElement <schema/PhysicalAcceleratorElement>`
     - The layer that adds ``physical``, and through it :doc:`PhysicalElement <schema/PhysicalElement>`, :doc:`Position <schema/Position>`, :doc:`Rotation <schema/Rotation>` and :doc:`ReferencePlacement <schema/ReferencePlacement>`.
   * - :doc:`Magnet <schema/Magnet>`
     - The magnet base, and from there each concrete type and its :doc:`MagneticElement <schema/MagneticElement>` field model.
   * - :doc:`ControlVariable <schema/ControlVariable>`
     - A single control-system process variable, with its ``update`` and ``dynamics`` hooks.
   * - :doc:`HardwareClassEnum <schema/HardwareClassEnum>` / :doc:`IOTypeEnum <schema/IOTypeEnum>`
     - The permissible values for ``hardware_class`` and for the signal types on ``inputs`` / ``outputs``.
   * - :doc:`MachineModel <schema/MachineModel>`
     - The top-level container, with :doc:`SectionLattice <schema/SectionLattice>` and :doc:`MachineLayout <schema/MachineLayout>`.

.. note::

   These pages are generated, and the directory is cleared before each run -- do not edit them,
   and do not add anything else to ``docs/source/schema/``.

.. toctree::
   :maxdepth: 1

   schema/index

.. toctree::
   :hidden:
   :glob:

   schema/*
