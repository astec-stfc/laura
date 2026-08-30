.. _translator:

Translator Module
=================

The :mod:`LAURA` translator module provides functionality for converting accelerator elements and lattice structures
into formats compatible with various particle simulation codes. The translation system supports export to multiple
simulation codes including:

* `ASTRA <https://www.desy.de/~mpyflo/>`_ :cite:`ASTRA`
* `GPT <https://www.pulsar.nl/gpt/>`_ :cite:`GPT`
* `Elegant <https://www.aps.anl.gov/Accelerator-Operations-Physics/Software#elegant>`_ :cite:`Elegant`
* `CSRTrack <https://www.desy.de/xfel-beam/csrtrack/>`_ :cite:`CSRTrack`
* `Ocelot <https://github.com/ocelot-collab/ocelot>`_ :cite:`OCELOT`
* `Xsuite <https://github.com/xsuite>`_ :cite:`Xsuite`
* `Wake-T <https://github.com/AngelFP/Wake-T/>`_ :cite:`WakeT`
* `Genesis <https://github.com/svenreiche/Genesis-1.3-Version4>`_ :cite:`Genesis`
* `MAD-X <https://cern.ch/madx>`_ :cite:`MADX`, via `cpymad <https://hibtc.github.io/cpymad/index.html>`_
* `RF-Track <https://gitlab.cern.ch/rf-track>`_ -- see :ref:`rftrack-translator`

The translator module uses a hierarchical approach: individual elements are translated first, then combined into
sections that can be exported as complete input files or objects for each simulation code.

.. warning::

   :mod:`LAURA` in its current state does not support export of **all possible** element types and **all possible**
   simulation configurations for all codes.
   
   If an important feature is missing, then please raise an issue `here <https://github.com/astec-stfc/laura/issues>`_.

.. _base-element-translator:

Base Element Translator
-----------------------

The :py:class:`BaseElementTranslator <laura.translator.converters.base.BaseElementTranslator>` class extends
:py:class:`PhysicalBaseElement <laura.models.element.PhysicalBaseElement>` and provides the core functionality for
translating individual elements into simulation-specific formats.

Key attributes include:

* ``type_conversion_rules: Dict``: Rules for converting element types between :mod:`LAURA` and target codes.
* ``conversion_rules: Dict``: Rules for converting element keywords/parameters.
* ``counter: int``: Counter for numbering elements of the same type.
* ``master_lattice: str``: Directory containing lattice and data files.
* ``directory: str``: Output directory for generated files.
* ``ccs: gpt_ccs``: Coordinate system definition for GPT elements.

Translation methods for each supported code:

* ``to_elegant()``: Generates Elegant lattice format strings.
* ``to_ocelot()``: Creates Ocelot element objects.
* ``to_cheetah()``: Creates Cheetah accelerator objects.
* ``to_xsuite(beam_length)``: Generates Xsuite line components.
* ``to_genesis(index)``: Produces Genesis v4 lattice format.
* ``to_astra(n)``: Creates ASTRA input format.
* ``to_csrtrack(n)``: Generates CSRTrack input format.
* ``to_gpt(Brho, ccs)``: Produces GPT element definitions.
* ``to_wake_t()``: Creates Wake-T beamline objects.
* ``to_opal(sval, designenergy)``: Generates OPAL lattice format.
* ``to_madx(at)``: Generates a MAD-X element-definition string, for use with :py:meth:`cpymad.madx.Madx.input`.
* ``to_rftrack(P_Q)``: Creates an RF-Track element object; see :ref:`rftrack-translator`.
* ``to_rftrack_repr(varname, P_Q)``: Emits the Python source lines that reconstruct the same RF-Track object standalone.

Utility methods for field and file management:

* ``full_dump()``: Returns a flattened dictionary of all element attributes.
* ``update_field_definition()``: Updates field file references.
* ``generate_field_file_name(param, code)``: Creates appropriate field file names.
* ``get_field_amplitude``: Returns scaled field amplitude values.

Example usage:

.. code-block:: python

    from laura.translator.converters.base import BaseElementTranslator

    translator = BaseElementTranslator.model_validate(element.model_dump())
    translator.directory = "./output"

    elegant_string = translator.to_elegant()
    ocelot_obj = translator.to_ocelot()

.. _corrector-translation:

Corrector Translation
~~~~~~~~~~~~~~~~~~~~~

:py:class:`CorrectorTranslator <laura.translator.converters.magnet.CorrectorTranslator>` handles
:py:class:`Horizontal_Corrector <laura.models.element.Horizontal_Corrector>`,
:py:class:`Vertical_Corrector <laura.models.element.Vertical_Corrector>`, and
:py:class:`Combined_Corrector <laura.models.element.Combined_Corrector>` (see :ref:`corrector-magnet`
for the underlying model). It does **not** extend
:py:class:`MagnetTranslator <laura.translator.converters.magnet.MagnetTranslator>`, since that class's
``k1``/``k2``/``k3`` etc. and its ASTRA/CSRTrack/GPT writers all assume a multipole-based magnetic model
that a corrector no longer uses.

Most codes' native kicker elements (Elegant's ``HKICK``/``VKICK``/``KICKER``, MAD-X's
``HKICKER``/``VKICKER``/``KICKER``, Genesis's ``corrector``) support both planes directly, so a
:py:class:`Combined_Corrector <laura.models.element.Combined_Corrector>` translates as a single element
there. Two codes need special handling because their native elements are single-plane only:

* **Ocelot** has no combined-plane corrector, so a
  :py:class:`Combined_Corrector <laura.models.element.Combined_Corrector>` is *split* into an ``Hcor``
  immediately followed by a ``Vcor``, each given half the original element's length (so the pair has the
  same total length as the original single element).
  :py:meth:`to_ocelot <laura.translator.converters.magnet.CorrectorTranslator.to_ocelot>` therefore
  returns a two-element list rather than a single object in this one case, and
  :py:meth:`SectionLatticeTranslator.to_ocelot <laura.translator.converters.section.SectionLatticeTranslator.to_ocelot>`
  expands it into the lattice sequence accordingly.
* **Cheetah** *does* have a combined-plane class (``CombinedCorrector``, with independent
  ``horizontal_angle``/``vertical_angle`` buffers), so no split is needed there.
* **Xsuite** has no dedicated corrector element at all; a corrector is represented as an
  ``xtrack.Multipole`` with the horizontal kick as ``knl[0]`` and the vertical kick as ``ksl[0]``, which
  naturally carries both planes of a
  :py:class:`Combined_Corrector <laura.models.element.Combined_Corrector>` in one element. Xtrack's
  normal-multipole sign convention deflects toward *negative* x for a positive ``knl`` -- the opposite of
  the "positive kick deflects toward positive x/y" convention used by MAD-X/Ocelot/Cheetah (verified
  against each by direct particle tracking) -- so ``knl[0]`` is written as the *negated* horizontal kick;
  the skew component (``ksl[0]``) needs no such negation.

.. _element-translation:

Element Translation
-------------------

The :py:func:`translate_elements <laura.translator.converters.converter.translate_elements>` function converts
lists of :py:class:`Element <laura.models.element.Element>` objects into their appropriate translator classes.

Parameters:

* ``elements: List[Element]``: List of LAURA elements to translate.
* ``master_lattice: str``: Directory containing reference files.
* ``directory: str``: Output directory for generated files.

Returns:

* ``Dict[str, BaseElementTranslator]``: Dictionary of translator objects, keyed by element name.

The function automatically selects the appropriate translator class based on element type:

* Magnets → :py:class:`MagnetTranslator`, :py:class:`SolenoidTranslator`, :py:class:`DipoleTranslator`, :py:class:`WigglerTranslator`, :py:class:`NonLinearLensTranslator`, :py:class:`CorrectorTranslator`
* RF Cavities → :py:class:`RFCavityTranslator`
* Drifts → :py:class:`DriftTranslator`
* Diagnostics → :py:class:`DiagnosticTranslator`
* Apertures and collimators → :py:class:`ApertureTranslator`
* Plasma elements → :py:class:`PlasmaTranslator`
* Laser elements → :py:class:`LaserTranslator`
* Twiss matching points → :py:class:`TwissMatchTranslator`
* Anything else → :py:class:`BaseElementTranslator <laura.translator.converters.base.BaseElementTranslator>`

Example:

.. code-block:: python

    from laura.translator.converters.converter import translate_elements

    translated = translate_elements(
        elements=element_list,
        master_lattice="/path/to/data",
        directory="./output"
    )

.. _section-lattice-translator:

Section Lattice Translator
--------------------------

The :py:class:`SectionLatticeTranslator <laura.translator.converters.section.SectionLatticeTranslator>` extends
:py:class:`SectionLattice <laura.models.elementList.SectionLattice>` to provide complete lattice section translation
capabilities.

Additional attributes for code-specific configuration:

* ``directory: str``: Output directory for generated files.
* ``astra_headers: Dict``: Configuration headers for ASTRA input files.
* ``csrtrack_headers: Dict``: Configuration headers for CSRTrack input files.
* ``gpt_headers: Dict``: Configuration headers for GPT input files.
* ``opal_headers: Dict``: Configuration headers for OPAL input files.
* ``csr_enable: bool``: Flag to enable calculation of CSR.
* ``lsc_enable: bool``: Flag to enable calculation of LSC.
* ``lsc_bins: PositiveInt``: Number of LSC bins.

Translation methods for complete lattice sections:

* ``to_astra()``: Creates complete ASTRA input files with headers.
* ``to_gpt(startz, endz, Brho)``: Generates GPT lattice definitions with coordinate systems.
* ``to_opal(energy, breakstr)``: Produces OPAL beamline definitions.
* ``to_elegant(charge)``: Creates Elegant lattice files.
* ``to_genesis(split_element, chicanes)``: Generates Genesis v4 lattice format, optionally splitting the lattice at a named element and describing chicanes.
* ``to_ocelot(save)``: Creates Ocelot :py:class:`MagneticLattice` objects.
* ``to_cheetah(save)``: Produces Cheetah :py:class:`Segment` objects.
* ``to_xsuite(beam_length, env, particle_ref, save)``: Generates Xsuite :py:class:`Line` objects.
* ``to_csrtrack()``: Creates CSRTrack input files.
* ``to_wake_t()``: Produces Wake-T :py:class:`Beamline` objects.
* ``to_madx(beam, refer)``: Creates a MAD-X ``SEQUENCE`` definition string; see :ref:`madx-translator`.
* ``to_rftrack(P_Q, save, sc_nsteps)`` / ``to_rftrack_volume(P_Q, save)``: Builds an RF-Track ``Lattice`` or ``Volume``; see :ref:`rftrack-translator`.

The translator automatically:

* Inserts drift spaces between elements using ``createDrifts()`` (except for :py:meth:`to_opal`,
  which places elements at absolute positions and relies on the target code to fill the gaps
  between them with implicit drifts)
* Handles sub-elements and overlapping components
* Manages field file references and wakefield definitions
* Updates energy/rigidity for sections with acceleration

Example workflow:

.. code-block:: python

    from laura.translator.converters.section import SectionLatticeTranslator

    # Create translator from existing section
    translator = SectionLatticeTranslator.from_section(section)
    translator.directory = "./simulations"

    # Export to different formats
    elegant_lattice = translator.to_elegant(charge=1e-9)

    ocelot_lattice = translator.to_ocelot(save=True)

    xsuite_line = translator.to_xsuite(
        beam_length=1000,
        save=True
    )

    # For codes requiring additional parameters
    gpt_input = translator.to_gpt(
        startz=0.0,
        endz=10.0,
        Brho=0.5
    )

    opal_input = translator.to_opal(
        energy=250.0e6,
        breakstr="//==============="
    )

.. note::

   Some simulation codes require additional parameters for proper translation:

   * GPT requires magnetic rigidity (``Brho``) for dipole elements
   * RF-Track requires the reference momentum-over-charge (``P_Q``, in MV/c) for dipole elements
   * OPAL requires beam energy for proper dipole field calculations
   * Xsuite requires the number of particles for monitor elements
   * ASTRA and CSRTrack use specialized headers for configuration

.. warning::

   OPAL / GPT translation have not been fully benchmarked and tested. Use with caution.

The translator module ensures consistency across different simulation codes while preserving the physics
and geometry defined in the LAURA lattice model. Field maps, wakefields, and other external data files
are automatically referenced and managed during the translation process -- provided they are in the correct
format.

.. _madx-translator:

MAD-X Translator
-----------------

Unlike Elegant/Genesis (which build a ``LINE``) or OPAL (which uses ``ELEMEDGE`` positions),
:py:meth:`SectionLatticeTranslator.to_madx <laura.translator.converters.section.SectionLatticeTranslator.to_madx>`
generates a MAD-X ``SEQUENCE`` :cite:`MADX`, with each element placed at its absolute entrance s-position
(``refer=entry``, the default). Passing ``refer="centre"`` places elements at their centre instead,
which MAD-X requires before a ``MAKETHIN`` / ``TRACK``. Explicit ``drift`` elements are inserted
between elements via ``createDrifts()`` and written into the sequence like any other element --
the standard way of constructing a MAD-X lattice -- rather than relying on MAD-X's implicit
gap-filling between elements placed without a contiguous ``at=``.

An optional ``beam`` dictionary (keys as defined in the
`Beam section of the MAD-X User Guide <https://madx.web.cern.ch/webguide/manual.html#Ch7.S1>`_)
emits a ``BEAM`` statement before the sequence and a matching ``USE`` after it, so the returned
string is immediately usable. Without it, the output is a bare sequence definition and the caller
must issue its own ``BEAM`` and ``USE`` -- MAD-X aborts with *"USE - sequence without beam"*
otherwise.

The returned string is plain MAD-X input, intended to be passed directly to
`cpymad <https://hibtc.github.io/cpymad/index.html>`_:

.. code-block:: python

    from cpymad.madx import Madx
    from laura.translator.converters.section import SectionLatticeTranslator

    translator = SectionLatticeTranslator.from_section(section)
    sequence_string = translator.to_madx(
        beam={"particle": "electron", "energy": 1.0}
    )

    madx = Madx()
    madx.input(sequence_string)          # declares BEAM, SEQUENCE and USE
    twiss = madx.twiss(betx=1, bety=1)

At the layout and model level, ``to_madx`` takes the beam definitions keyed by section name
(and, for the model, by layout then section), so each sequence can be given its own beam.

As with the other codes, a :ref:`functional parameter <functional-parameters>` is carried through
symbolically rather than being resolved to a number: the header (produced by
:py:func:`madx_functional_definitions <laura.translator.utils.functions.madx_functional_definitions>`)
declares each definition as a MAD-X variable (``name = value;``), and any element attribute referencing
one is written as a *deferred expression* (``key := name`` / ``key := name / length``, using MAD-X's
``:=`` operator) rather than a plain assignment -- so, as with Xsuite's ``Environment`` variables, changing
the MAD-X global afterwards (``madx.globals["name"] = ...``) updates every element that references it.

.. note::

   Correctors (:py:class:`Horizontal_Corrector <laura.models.element.Horizontal_Corrector>`,
   :py:class:`Vertical_Corrector <laura.models.element.Vertical_Corrector>`,
   :py:class:`Combined_Corrector <laura.models.element.Combined_Corrector>`) translate to native
   ``HKICKER``/``VKICKER``/``KICKER`` elements, with the ``KICK``/``HKICK``/``VKICK`` attributes set
   directly from :py:class:`Corrector_Magnet <laura.models.magnetic.Corrector_Magnet>`'s
   ``horizontal_kick``/``vertical_kick`` (see :ref:`corrector-magnet`) -- MAD-X's ``KICK`` sign
   convention agrees with LAURA's (a positive kick deflects toward positive x/y), so no sign
   adjustment is needed, unlike for Xsuite (see
   :py:meth:`CorrectorTranslator.to_xsuite <laura.translator.converters.magnet.CorrectorTranslator.to_xsuite>`).

.. _rftrack-translator:

RF-Track Translator
-------------------

`RF-Track <https://gitlab.cern.ch/rf-track>`_ (CERN, A. Latina) is a tracking code whose
lattices are Python objects rather than text files, like Ocelot, Cheetah and Xsuite. It is not
distributed on PyPI, so :mod:`LAURA` has no extra for it -- install the wheel manually into the
same environment.

Unlike the other object-based codes, RF-Track conversion is not implemented as a per-category
override on each translator class. :py:meth:`BaseElementTranslator.to_rftrack
<laura.translator.converters.base.BaseElementTranslator.to_rftrack>` is a single generic
implementation that dispatches on ``hardware_type`` through
:py:data:`rftrack_conversion_rules
<laura.translator.conversion_rules.codes.rftrack_conversion.rftrack_conversion_rules>`; the
builder functions receive the fully-typed translator instance, so a
:py:class:`DipoleTranslator` still arrives with its edge angles intact. Element types with no
builder fall back to a drift, with a warning.

Two tracking environments
~~~~~~~~~~~~~~~~~~~~~~~~~

RF-Track offers two integration environments, and :mod:`LAURA` can produce either:

* :py:meth:`to_rftrack <laura.translator.converters.section.SectionLatticeTranslator.to_rftrack>`
  returns a ``Lattice`` -- the space-integration environment, tracked with a ``Bunch6d``. Space
  charge is applied as ``sc_nsteps`` evenly-spaced kicks per element.
* :py:meth:`to_rftrack_volume <laura.translator.converters.section.SectionLatticeTranslator.to_rftrack_volume>`
  wraps that ``Lattice`` in a ``Volume`` at the origin -- the time-integration environment,
  tracked with a ``Bunch6dT``. This is what RF-Track recommends for space-charge-dominated and
  cathode regimes. Space charge here is driven by the ``sc_dt_mm`` tracking option rather than
  per-element kicks, so ``sc_nsteps`` is not applied.

``P_Q``, the beam reference momentum-over-charge in MV/c, is threaded down to every element in
the same way ``Brho`` is for GPT. It matters for dipoles: RF-Track's ``SBend``, unlike its
``Quadrupole`` and ``Multipole``, cannot defer this to ``autophase()``, and an unset value
silently produces zero transmission.

.. code-block:: python

    from laura.translator.converters.section import SectionLatticeTranslator

    translator = SectionLatticeTranslator.from_section(section)
    translator.directory = "./simulations"

    # Space-integration lattice, with 10 space-charge kicks per element
    lattice = translator.to_rftrack(P_Q=250.0, sc_nsteps=10)

    # Time-integration volume, for a cathode / space-charge-dominated region
    volume = translator.to_rftrack_volume(P_Q=250.0)

Saving a standalone lattice
~~~~~~~~~~~~~~~~~~~~~~~~~~~

RF-Track has no equivalent of Ocelot's ``MagneticLattice.save_as_py_file()``, so
``to_rftrack(save=True)`` writes one: a Python script at ``{directory}/{name}.py`` that
rebuilds the lattice using only ``RF_Track`` and ``numpy``, with no :mod:`LAURA` import needed
to reload it. Each element contributes its own source lines via
:py:meth:`to_rftrack_repr <laura.translator.converters.base.BaseElementTranslator.to_rftrack_repr>`.

Supported elements
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - :mod:`LAURA` element
     - RF-Track object
   * - ``Drift``, ``Aperture``, ``Collimator``, ``Marker``
     - ``Drift``
   * - ``Quadrupole``
     - ``Quadrupole``
   * - ``Dipole``
     - ``SBend``
   * - ``Sextupole``, ``Octupole``
     - ``Multipole`` (RF-Track has no dedicated class; MAD-X multipole convention, as in :mod:`LAURA`)
   * - ``Solenoid``
     - ``Solenoid``, or ``Static_Magnetic_FieldMap_1d`` when an on-axis field map is available
   * - ``Wiggler`` / undulator
     - ``Undulator``
   * - ``Horizontal_Corrector``, ``Vertical_Corrector``, ``Combined_Corrector``
     - ``Corrector``
   * - ``RFCavity``
     - ``RF_FieldMap_1d`` from a real field map where one is resolved, otherwise the analytic ``TW_Structure`` or ``Pillbox_Cavity``
   * - ``Beam_Position_Monitor``
     - ``Bpm``
   * - ``Screen``
     - ``Screen``

.. note::

   A few builders -- notably the stitched travelling-wave field map
   (``build_tw_fieldmap``: input coupler, complex core, output coupler) -- return a *list* of
   RF-Track objects rather than one. These are flattened into the caller's own ``Lattice`` as
   siblings rather than nested in a sub-lattice, because nesting a ``Lattice`` inside a
   ``Lattice`` inside a ``Volume`` breaks ``Volume.autophase()`` for the inner elements.

.. warning::

   Corrector kick strengths are **not** carried across: a converted ``Corrector`` is created at
   zero strength and is expected to be set at run time, mirroring how ASTRA and GPT correctors
   are handled. Screens are created with infinite extent and an unbounded time window;
   width, height and time window are not yet carried over from :mod:`LAURA`.

.. _machine-layout-translator:

Machine Layout Translator
-------------------------

The :py:class:`MachineLayoutTranslator <laura.translator.converters.layout.MachineLayoutTranslator>` extends
:py:class:`MachineLayout <laura.models.elementList.MachineLayout>` to translate complete beam paths consisting
of multiple sections.

Attributes:

* ``directory: str``: Output directory for generated files.

The class provides a factory method for creating translators from existing layouts:

* ``from_layout(layout)``: Creates a translator instance from an existing :py:class:`MachineLayout`.

Translation methods produce complete beamline definitions:

* ``to_astra()``: Returns a dictionary of ASTRA input files, keyed by section name.
* ``to_elegant(string, charge)``: Generates a complete Elegant lattice file with LINE definitions.
* ``to_genesis(string)``: Creates Genesis v4 lattice format with beamline structure.
* ``to_ocelot(save)``: Returns a dictionary of Ocelot :py:class:`MagneticLattice` objects.
* ``to_cheetah(save)``: Produces a dictionary of Cheetah :py:class:`Segment` objects.
* ``to_xsuite(beam_length, env, particle_ref, save)``: Generates a dictionary of Xsuite :py:class:`Line` objects.
* ``to_rftrack(P_Q, save)``: Returns a dictionary of RF-Track ``Lattice`` objects; see :ref:`rftrack-translator`.
* ``to_madx(beam)``: Returns a dictionary of MAD-X ``SEQUENCE`` definition strings, keyed by section name. ``beam`` is itself keyed by section name.

The translator automatically:

* Processes all sections within the layout
* Maintains section ordering and relationships
* Generates appropriate LINE definitions for codes that support them
* Handles drift insertion for each section

Example usage:

.. code-block:: python

    from laura.translator.converters.layout import MachineLayoutTranslator

    # Create translator from existing layout
    translator = MachineLayoutTranslator.from_layout(machine_layout)
    translator.directory = "./output"

    # Export entire layout to Elegant
    elegant_file = translator.to_elegant(charge=1e-9)

    # Generate section-wise ASTRA files
    astra_sections = translator.to_astra()
    for section_name, astra_input in astra_sections.items():
        with open(f"{section_name}.in", "w") as f:
            f.write(astra_input)

    # Create Ocelot lattices for all sections
    ocelot_lattices = translator.to_ocelot(save=True)

.. _machine-model-translator:

Machine Model Translator
------------------------

The :py:class:`MachineModelTranslator <laura.translator.converters.model.MachineModelTranslator>` extends
:py:class:`MachineModel <laura.models.elementList.MachineModel>` to provide translation capabilities for
the complete accelerator model, including all defined beam paths and sections.

Attributes:

* ``directory: str``: Output directory for generated files.

Factory method:

* ``from_machine(machine)``: Creates a translator from an existing :py:class:`MachineModel`.

Translation methods handle the full machine hierarchy:

* ``to_astra()``: Returns nested dictionaries of ASTRA files (by layout, then section).
* ``to_elegant(string, charge)``: Generates complete Elegant lattice with all paths.
* ``to_genesis(string)``: Creates full Genesis v4 lattice structure.
* ``to_ocelot(save)``: Returns nested dictionaries of :py:class:`MagneticLattice` objects.
* ``to_cheetah(save)``: Produces nested dictionaries of :py:class:`Segment` objects.
* ``to_xsuite(beam_length, env, particle_ref, save)``: Generates nested dictionaries of :py:class:`Line` objects.
* ``to_rftrack(P_Q, save)``: Returns nested dictionaries of RF-Track ``Lattice`` objects.
* ``to_madx(beam)``: Returns nested dictionaries of MAD-X ``SEQUENCE`` definition strings (by layout, then section). ``beam`` is required here, and is keyed by layout then section.

The translator provides:

* Complete machine model export with all beam paths
* Hierarchical organization of sections and layouts
* Automatic generation of composite LINE definitions
* Consistent naming across all exported formats

Example workflow:

.. code-block:: python


    from laura.translator.converters.model import MachineModelTranslator

    # Create translator from machine model
    translator = MachineModelTranslator.from_machine(machine_model)
    translator.directory = "./simulations"

    # Export complete machine to Elegant
    with open("machine.lte", "w") as f:
        f.write(translator.to_elegant(charge=250e-12))

    # Generate all ASTRA configurations
    astra_model = translator.to_astra()
    for layout_name, sections in astra_model.items():
        for section_name, content in sections.items():
            filename = f"{layout_name}_{section_name}.in"
            with open(filename, "w") as f:
                f.write(content)

    # Create Xsuite models for all beam paths
    xsuite_model = translator.to_xsuite(
        beam_length=10000,
        save=True
    )

    # Access specific layout/section
    main_beam_injector = xsuite_model["main_beam"]["injector"]

Output structure for nested translations:

* ASTRA: ``Dict[layout_name, Dict[section_name, str]]``
* Ocelot: ``Dict[layout_name, Dict[section_name, MagneticLattice]]``
* Cheetah: ``Dict[layout_name, Dict[section_name, Segment]]``
* Xsuite: ``Dict[layout_name, Dict[section_name, Line]]``
* RF-Track: ``Dict[layout_name, Dict[section_name, Lattice]]``
* MAD-X: ``Dict[layout_name, Dict[section_name, str]]``

For string-based formats (Elegant, Genesis), the translator generates:

1. Individual element definitions
2. Section LINE definitions
3. Layout LINE definitions composing sections
4. Complete beamline hierarchies

.. note::

   The layout and model translators support a subset of simulation codes compared to individual
   element translators. Currently supported formats are:

   * ASTRA (dictionary output)
   * Elegant (string format)
   * Genesis v4 (string format)
   * Ocelot (object dictionaries)
   * Cheetah (object dictionaries)
   * Xsuite (object dictionaries)
   * RF-Track (object dictionaries; see :ref:`rftrack-translator`)
   * MAD-X (dictionary of strings; see :ref:`madx-translator`)

   For GPT, OPAL, CSRTrack, Wake-T, and the RF-Track ``Volume`` environment, use the
   :py:class:`SectionLatticeTranslator <laura.translator.converters.section.SectionLatticeTranslator>` directly.

The hierarchical translation system ensures that complex machine models with multiple beam paths
can be efficiently exported while maintaining the relationships between elements, sections, and layouts
defined in the LAURA model.

.. toctree::
   :maxdepth: 1

   Translator/Fields
