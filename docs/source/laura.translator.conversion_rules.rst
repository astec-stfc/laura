laura.translator.conversion\_rules package
==========================================

Element-, keyword- and type-level mapping tables between the :mod:`LAURA` data
model and each target simulation code.

The YAML tables in ``conversion_rules/elements``, ``conversion_rules/keywords``
and ``conversion_rules/types`` are data, not code, and are loaded by the
converters in :doc:`laura.translator.converters`. The Python modules below hold
the rules that cannot be expressed declaratively -- object construction for the
codes whose lattices are Python objects rather than text files.

Subpackages
-----------

.. toctree::
   :maxdepth: 4

   laura.translator.conversion_rules.codes
