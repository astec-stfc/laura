.. LAURA documentation master file, created by
   sphinx-quickstart on Tue Sep 24 10:00:24 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

LAURA: Lattice Architecture for a Unified Representation of Accelerators
========================================================================

**LAURA** (Lattice Architecture for a Unified Representation of Accelerators) is a ``python`` package for handling particle accelerator lattice data.

This package provides a standardized interface for interacting with objects representing elements in an accelerator lattice. The intention is to collate as much information as possible about each element, in order to achieve the following goals:

* Representing a ground source of truth about a given particle accelerator lattice.
* Providing a basis for producing configurable simulation lattice files for a range of codes.
* Store auxiliary data -- mechanical, survey, electrical, for example.
* Provide a basic interface to the controls system for each element.

Schema-first
------------

The definitive description of an accelerator element in :mod:`LAURA` is not Python code. It is a
`LinkML <https://linkml.io/>`_ ontology, held in ``laura/schema/YAML/``, from which everything
else is generated: the Pydantic classes you import, a JSON Schema that validates lattice files,
an OWL ontology, SHACL shapes, a SQLAlchemy ORM, a GraphQL schema and TypeScript types.

This is what makes "a ground source of truth" more than an aspiration. An element's properties,
their units, their defaults and their permitted values are stated once, in a machine-readable
form that is not tied to Python -- so a lattice can be validated, reasoned over, queried with
SPARQL or loaded into a database without :mod:`LAURA` itself being involved.

:doc:`Read about the schema → <Schema>`

.. warning::
   | This site is currently **under construction**.
   | Some pages may have missing or incomplete reference documentation.

Installation
------------

:mod:`LAURA` is published on PyPI as ``laura-accelerator`` and requires Python 3.11 or newer
(tested against 3.11, 3.12, 3.13 and 3.14):

.. code-block:: bash

   pip install laura-accelerator

The core install has no simulation-code dependencies -- reading, writing and manipulating lattices
works out of the box. Support for individual target codes is pulled in through extras:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Extra
     - Provides
   * - ``[xsuite]``, ``[ocelot]``, ``[cheetah]``, ``[wake_t]``, ``[madx]``, ``[bmad]``
     - A single simulation-code backend; see :ref:`translator`.
   * - ``[conversion]``
     - All of the above at once.
   * - ``[rdf]``
     - RDF / linked-data export and SPARQL queries; see :ref:`interfaces`.
   * - ``[sql]``
     - Relational (SQLAlchemy) export; see :ref:`interfaces`.
   * - ``[schema]``
     - LinkML tooling for regenerating the schema artefacts and for YAML validation.
   * - ``[docs]``
     - The Sphinx toolchain used to build this site.
   * - ``[full]``
     - Everything.

.. note::

   `RF-Track <https://gitlab.cern.ch/rf-track>`_ is not distributed on PyPI, so it has no extra --
   install its wheel manually into the same environment to use :ref:`rftrack-translator`.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   Schema
   Architecture/index
   Translator
   Interfaces
   Examples


Participation
-------------

We welcome contributions and suggestions from the community! :mod:`LAURA` is currently under active development,
and as such certain features may be missing or not working as expected. If you find any issues, please
raise it `here <https://github.com/astec-stfc/laura/issues>`_.

We are also happy to help with installation and setting up your accelerator lattice. 
   

.. API
   ---

.. toctree::
   :maxdepth: 2
   :caption: API

   laura

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


References
----------

.. bibliography::
   :style: unsrt
