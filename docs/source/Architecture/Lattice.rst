.. _lattice:

Lattice Definition
==================

Lattice structures in :mod:`LAURA` provide a hierarchical way to organize accelerator elements into sections and
complete beam paths. The lattice system is built on three main classes that progressively combine elements into
larger structures: sections, layouts, and the complete machine model.

These classes work together to define the full accelerator lattice, from individual elements up to complete
beam paths through the machine.

These classes are outlined below; refer to :numref:`fig-lattice-structure` for an inheritance diagram.

.. _fig-lattice-structure:
.. figure:: assets/lattice-structure.png

   Class structure of :mod:`LAURA` sections, lattices and machines.

.. _element-list:

Element List
------------

The :py:class:`ElementList <laura.models.elementList.ElementList>` class provides a container for an unordered dictionary of element objects. It is used to manage collections of :py:class:`baseElement <laura.models.element.baseElement>` instances, typically within a section lattice.

**Attributes:**

* ``elements: Dict[str, baseElement | None]``: Dictionary of element objects, keyed by their names.

**Key Methods and Properties:**

* ``names``: Returns a list of element names contained in the list.
* ``index(element)``: Returns the index of an element (by name or object).
* ``list()``: Returns a list of all element objects.

**Example Usage:**

.. code-block:: python

    from laura.models.elementList import ElementList
    from laura.models.element import PhysicalBaseElement

    element_list = ElementList(
        elements={
            "cavity1": PhysicalBaseElement(
                name="cavity1",
                hardware_class="RFCavity",
                hardware_type="RFCavity",
                machine_area="INJ",
                physical={
                    "middle": [0, 0, 0.2],
                    "length": 0.4,
                }
            ),
            "quad1": PhysicalBaseElement(
                name="quad1",
                hardware_class="Magnet",
                hardware_type="Quadrupole",
                machine_area="INJ",
                physical={
                    "middle": [0, 0, 0.6],
                    "length": 0.1,
                }
            ),
            "cavity2": PhysicalBaseElement(
                name="cavity2",
                hardware_class="RFCavity",
                hardware_type="RFCavity",
                machine_area="INJ",
                physical={
                    "middle": [0, 0, 1.0],
                    "length": 0.2,
                }
            )
        }
    )

    print(element_list.names)  # ['cavity1', 'quad1', 'cavity2']
    cav1 = element_list["cavity1"]
    idx = element_list.index("quad1")  # 1
    all_elements = element_list.list()

.. _section-lattice:

Section Lattice
---------------

The :py:class:`SectionLattice <laura.models.elementList.SectionLattice>` class represents a section of a lattice,
consisting of an ordered list of elements along a beam path. Each section typically corresponds to a specific
area or functional region of the accelerator.

A section lattice must define:

* ``name: str``: The name of the lattice section.
* ``order: List[str]``: An ordered list of element names defining the sequence along the beam path.
* ``elements: ElementList``: A container holding the actual element objects.
* ``section_type: "beam" | "rf" | "laser"``: What kind of lattice this section belongs to (default ``"beam"``); see :ref:`lattice-types`.
* ``master_lattice: str | None``: Optional top-level directory containing lattice files.
* ``functional_definitions: str | dict``: Optional functional definitions (a mapping or YAML file path); see :ref:`functional-definitions`.
* ``resolve_functional: bool``: Optional global resolution mode (default ``False``); see :ref:`functional-definitions`.

Key methods and properties include:

* ``names``: Returns a list of element names in the section.
* ``createDrifts()``: Automatically inserts drift spaces between elements based on their physical positions. Drifts are named ``{section_name}_drift_{n}``.
* ``get_s_values(as_dict, at_entrance, starting_s)``: Calculates the cumulative S-position values for elements along the beamline. This operates on the section *with drifts inserted*, so the returned sequence has no gaps.
* ``get_resolved_s_values(...)``: As ``get_s_values``, but reading the ``s`` values already assigned by ``resolve_positions`` rather than re-accumulating lengths.
* ``resolve_positions(element_registry)``: Resolves the :ref:`positioning modes <positioning-modes>` -- ``reference_placement``, ``s``, and global ``middle`` -- into a consistent set of global coordinates, and builds the section's :py:class:`Trajectory <laura.models.trajectory.Trajectory>`. Called automatically when a :ref:`machine-model` is assembled.
* ``is_sequential(element_registry)``: True if any element in the section is awaiting a position, which is the trigger for :ref:`sequential-placement`. Sequential sections are normalised to ``s`` *before* ``resolve_positions`` runs, so it never sees them.

Example usage:

.. code-block:: python

    from laura.models.elementList import SectionLattice

    section = SectionLattice(
        name="injector",
        order=["cavity1", "quad1", "cavity2"],
        elements=element_list
    )
    s_positions = section.get_s_values(as_dict=True, at_entrance=True)

.. _sequential-placement:

Sequential (drift-based) placement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A section whose elements carry no position at all is placed by its ``order``: the lengths are
accumulated along the line. This is the fourth of the
:ref:`positioning modes <positioning-modes>`, and the only one that lives on the
section rather than on the element.

.. code-block:: yaml

    sections:
      INJ:
        elements: [GUN, D1, Q1, D1, Q2] # lengths alone place these

Resolution happens on the :py:class:`MachineModel <laura.models.elementList.MachineModel>`,
before anything else looks at coordinates:

1. **Repeated names are split.** Every section is checked with
   :py:meth:`is_sequential <laura.models.elementList.SectionLattice.is_sequential>`; in those
   that are, a name appearing more than once in ``order`` gets one copy per occurrence
   (``D1.1``, ``D1.2``, ...), because the model stores one placement per name. The original
   bare name is retired only if no other section still refers to it, and a warning lists the
   renames. The split is undone on the way out again by a ``position_mode="sequential"``
   export, which writes the repeated name as it was authored -- see :ref:`interfaces`.
2. **The section is normalised to** ``s``. Each unpositioned element receives
   ``s_point: "end"`` and the running total of the lengths. An element that states a
   position anchors the line and accumulation resumes from its exit; a warning is raised in
   case of disagreements.
3. **Ordinary resolution runs.** ``resolve_positions`` then sees a section that is uniformly
   ``s``-coordinate and needs no knowledge of the ordering at all. It rewrites ``s`` to the
   arc length at each element's **middle** and sets ``s_point: "middle"`` to match, so a
   resolved element's ``s``/``s_point`` pair always agrees with itself -- an important
   invariant for anything reading an exported file by the schema's own meaning rather than
   through LAURA.

Drifts in a sequential section are written by hand and are ordinary elements, which is the
mirror image of ``createDrifts()``: one derives positions from an explicit drift, the other
derives drifts from explicit positions. A resolved machine can be written back out in this
compact form with ``position_mode="sequential"`` -- see :ref:`interfaces`.

.. _repeated-lines:

Repeated and nested lines
~~~~~~~~~~~~~~~~~~~~~~~~~

A section's element list may repeat an entry and may splice in another section, so a lattice
built from identical cells is written once rather than once per cell:

.. code-block:: yaml

    sections:
      fodo_channel:
        - fodo_cell: {repeat: 3}

      fodo_cell: [drift1, quad1, drift2, quad2, drift1]

An entry is either a bare name or a single-key mapping carrying a ``repeat`` count. A name
that matches another section is a nested line and is expanded in place; anything else is an
element name. A line may be referenced before it is defined, and a line that no layout lists
-- i.e. ``fodo_cell`` above -- never becomes a section of the machine, so it costs nothing to
define one purely to be reused.

:py:func:`expand_section_order <laura.models.elementList.expand_section_order>` flattens this
into the ordinary name list during
:py:meth:`MachineModel <laura.models.elementList.MachineModel>` construction, so everything
downstream. A line that includes itself is a
:py:class:`LatticeError <laura.models.exceptions.LatticeError>` rather than an
infinite lattice, and a ``repeat`` of zero is a ``ValueError`` rather than a silently dropped
entry.

A **negative** count reverses the entry before repeating it:

.. code-block:: yaml

    sections:
      mirrored:
        - fodo_cell                    # forwards
        - fodo_cell: {repeat: -1}      # and back again

This reverses the order only. The result is a different lattice built
from the same definitions. True path reversal flips the sign of every
magnetic element's effect in the beam frame (traversing an element backwards is equivalent
to traversing it forwards with the opposite-sign particle). That transform exists as
:ref:`element-reversal`, but it is deliberately *not* applied here: a negative ``repeat``
changes the order and nothing else.

The authored list is kept on the section, so a ``position_mode="sequential"`` export writes
the ``repeat`` count and the nested line back out, defining them alongside the elements.

.. _machine-layout:

Machine Layout
--------------

The :py:class:`MachineLayout <laura.models.elementList.MachineLayout>` class represents a complete beam path
through the accelerator, composed of multiple :py:class:`SectionLattice <laura.models.elementList.SectionLattice>`
instances arranged in sequence.

A machine layout defines:

* ``name: str``: The name of the layout/beam path.
* ``sections: Dict[str, SectionLattice]``: Dictionary of lattice sections, keyed by section name.
* ``passes: List[LayoutPass]``: The beam order, one entry per section traversal, carrying ``section``, ``direction``, ``number``, ``momentum`` and ``overrides``. A name-keyed dictionary cannot say that a path enters a section twice; this can. See :ref:`multipass`.
* ``layout_type: "beam" | "rf" | "laser"``: What kind of lattice this beam path represents (default ``"beam"``); see :ref:`lattice-types`.
* ``master_lattice: str | None``: Directory containing lattice files.
* ``functional_definitions: str | dict``: Optional functional definitions (a mapping or YAML file path); see :ref:`functional-definitions`.
* ``resolve_functional: bool``: Optional global resolution mode (default ``False``); see :ref:`functional-definitions`.

Important methods include:

* ``get_element(name)``: Returns the element object for a given element name.
* ``get_all_elements(element_type, element_model, element_class)``: Returns filtered lists of element names.
* ``elements_between(start, end, element_type, element_model, element_class)``: Returns elements within a specified range along the beam path.
* ``_get_all_elements()``: Returns all elements in the layout in order.
* ``arc_lengths(direction=None)``: Arc length of each element's entrance *along this beam path*; see :ref:`path-arc-lengths`.
* ``pass_strengths(number)``: Integrated multipole strengths as one pass of a :ref:`multipass <multipass>` section sees them; see :ref:`per-pass-strengths`.

.. _path-arc-lengths:

Arc length along a beam path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An element carries one ``s``, resolved in its own section's frame. That is where it
belongs -- the magnet is installed once -- but it is not the whole story for a beam path:

* A :ref:`sequentially-placed <sequential-placement>` section starts at its own ``s = 0``.
  Placement runs per section: two sequential sections in one layout both begin at the origin.
* A section a path traverses backwards measures its arc length from the far end.

:py:meth:`arc_lengths <laura.models.elementList.MachineLayout.arc_lengths>` is the view that
resolves both, walking the layout's sections in order with a running offset:

.. code-block:: python

    layout.arc_lengths()                          # chained, all forwards
    layout.arc_lengths(direction={"ARC": -1})     # ARC traversed backwards

A section whose elements state absolute positions already has a meaningful ``s`` and is not
shifted; only sequentially-placed sections take an offset. Naming a section the layout does
not contain raises :py:class:`LatticeError <laura.models.exceptions.LatticeError>` rather
than being ignored.

A layout declares which of its sections it runs backwards, and ``arc_lengths()`` then uses
that by default (an explicit ``direction`` argument still overrides it):

.. code-block:: yaml

    layouts:
      RING:
        - ARC_A
        - ARC_B: {direction: -1}

Direction belongs to the beam path, not the section. The same section may be traversed
forwards by one layout and backwards by another --- which is the counter-propagating-beam
case, one installed magnet in two beam paths.

Nothing is mutated, so the same section reports different arc lengths to different beam
paths. Note this is the arc length only: changing where a section sits in the line is not
the same as reversing the traversal of its elements, which flips the sign of every normal
multipole's effect in the beam frame -- see :ref:`element-reversal` for that transform, which
this view does not apply. Export *does* apply it: see :ref:`path-reversal-on-export`.

A worked example of both -- one arc, two beam paths, one of them reversed -- is
``examples/testing/reversal_{elements,sections,layouts}.yaml``.

.. note::

   ``arc_lengths`` is a **query API with no internal consumer, deliberately.** Export takes
   a different route: it substitutes a reversed section outright (see
   :ref:`path-reversal-on-export`).
   However, this is the only way to obtain a cumulative arc length that crosses section
   boundaries; for :ref:`sequentially-placed <sequential-placement>` sections it restarts
   at zero in every one.

   What it is *for* is the two cases :ref:`composition <layout-composition>` cannot write
   back into the model: a section this path traverses **backwards**, and a section shared
   by two layouts, whose single stored position belongs to whichever path composed it
   first.

.. note::

   Every element in a layout must have physical data -- i.e. be a
   :py:class:`PhysicalBaseElement <laura.models.element.PhysicalBaseElement>` subclass.
   A position-less :py:class:`Element <laura.models.element.Element>` (an LLRF module,
   a laser mirror, a lighting controller) may live in ``MachineModel.elements`` and in a
   section, but cannot take part in a beam path.

.. _multipass:

Repetition and multipass
~~~~~~~~~~~~~~~~~~~~~~~~

A layout may list the same section more than once, and this has two possible meanings:

**Repetition**
   *N identical devices at N positions.* A FODO channel built from three cells has three
   cells' worth of hardware.

**Multipass**
   *One device at one position, traversed N times.* A recirculating linac has one linac, and
   the beam goes through it twice.

Both are written by naming a section twice, so LAURA does not infer which was meant.
**Repetition is the default**, because that is already what the same shape means one level
down in a section's element list (:ref:`repeated-lines`):

.. code-block:: yaml

    layouts:
      ERL:
        - INJECTOR
        - LINAC          # LINAC.1 -- its own cavities, at its own positions
        - ARC
        - LINAC          # LINAC.2 -- a second, independent linac
        - DUMP

Each occurrence is given its own section (``LINAC.1``, ``LINAC.2``) holding its own
deep-copied, numbered elements, before any section is built. Setting one occurrence's
gradient does not reach the other, because these really are two magnets (see
:ref:`functional-definitions` for how to do this).

Two shapes cannot be repetition: occurrences that differ in ``direction``, and a
repeated section that states its own positions (the copies would coincide rather than chain).

``multipass: N`` is the other option. It says this entry is the Nth traversal
of hardware an earlier entry has already been through:

.. code-block:: yaml

    layouts:
      ERL:
        - INJECTOR
        - LINAC: {multipass: 1}
        - ARC
        - LINAC: {multipass: 2}
        - DUMP

Both entries now name the same section and the same element objects. Because it is a claim
about the hardware, it must be stated on *every* occurrence of that section or none of them,
and the numbers must be exactly ``1..N`` in beam order.

.. _occurrence-addressing:

Addressing one pass
~~~~~~~~~~~~~~~~~~~

On a multipass path, an ambiguous name takes an occurrence selector, spelled ``NAME#N``:

.. code-block:: python

    layout.arc_lengths()                                   # one entry per pass
    # {'INJ_Q': 0.0, ..., 'CAV_01#1': 1.2, ..., 'CAV_01#2': 7.1, ..., 'DMP_Q': 11.3}

    layout.elements_between(start="CAV_01#2", end="DMP_Q")
    # ['CAV_01#2', 'DRIFT_LIN.2#2', 'LIN_Q#2', ..., 'DRIFT_DUMP', 'DMP_Q']

    layout.get_element("CAV_01#1") is layout.get_element("CAV_01#2")   # True

The two numbering schemes compose and are orthogonal. ``DRIFT_LIN.2#2`` is the **second
drift** of a section that lists ``DRIFT_LIN`` four times -- ordinary
:ref:`repetition within a section order <repeated-lines>` -- on the
**second pass** of that section. Repetition numbers the hardware; multipass numbers the
traversals.

A name the path enters once stays bare, so a single-pass
path, a repetition path and every existing lattice are untouched.
``get_element`` accepts a selector and ignores it -- both passes are the same device.
``elements_between`` filters by **position** rather than by identity.

.. _per-pass-overrides:

What differs between passes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In an ERL the return bunch arrives half an RF period late and decelerates.
One cavity cannot store two phases, so the second pass's value lives on the pass:

.. code-block:: yaml

    - LINAC:
        multipass: 2
        overrides:
          CAV_01: {cavity.phase: 180.0}

``overrides`` maps an element name to the attribute paths that take a different value on
this traversal. ``overrides`` are refused on any entry not marked ``multipass``.
Every other traversal has an element of its own to write the value on:
a single pass has the element itself, and a repetition occurrence has its own copy.
Overrides exist only because the passes of a multipass section are one device.

.. note::

   Overrides never touch the model. They are recorded on the
   :py:class:`LayoutPass <laura.models.elementList.LayoutPass>` and the element keeps its
   stored value, because the passes share one device; they are applied to the per-pass copies
   :ref:`export <multipass-export>` makes. Read ``layout.passes[n].overrides`` to see what a
   pass declares.

.. _multipass-export:

Exporting a multipass path
~~~~~~~~~~~~~~~~~~~~~~~~~~

``sections`` is name-keyed and every backend iterates it, so a path that enters one section
twice has to become a set of distinct sections before any backend sees it.
:py:meth:`from_layout <laura.translator.converters.layout.MachineLayoutTranslator.from_layout>`
flattens it: one exported section per traversal, each a copy suffixed ``.N`` on the
section and on every element in it, carrying the values that pass sees -- reversal first, then
the resolved :ref:`per-pass strengths <per-pass-strengths>`, then the
:ref:`overrides <per-pass-overrides>` last, so an explicit statement wins over anything
derived.

.. code-block:: text

    INJECTOR: LINE = (INJ_Q, ...)
    LINAC.1:  LINE = (CAV_01.1, LIN_Q.1, ...)     k1 = 2.5    phase = 0
    ARC:      LINE = (ARC_B, ...)
    LINAC.2:  LINE = (CAV_01.2, LIN_Q.2, ...)     k1 = 1.25   phase = 180

``.N`` rather than the ``#N`` that *addresses* a pass, in order to be compatible with banned
strings in various simulation codes.

A flattened multipass path and the repetition reading of the
same file emit byte-identical section and element names. The pass number
is inserted before any within-section repeat index to keep it so.

Two backends can hold the identity instead of a copy per traversal, and both take a
translator built with ``from_layout(layout, multipass=True)``, which keeps the path unflattened:

* :py:meth:`to_bmad_multipass <laura.translator.converters.layout.MachineLayoutTranslator.to_bmad_multipass>`
  writes a ``line[multipass]`` whose slaves are ``NAME\1``, ``NAME\2``. ``phi0_multipass`` is
  the only attribute Bmad takes per slave; anything else a pass changes is dropped with a
  warning naming it.
* :py:meth:`to_pals_multipass <laura.translator.converters.layout.MachineLayoutTranslator.to_pals_multipass>`
  writes a ``BeamLine`` marked ``multipass`` and named once per pass; the PALS parser stamps a
  ``multipass_index`` on each visit. ``overrides`` and ``momentum`` are dropped with a warning.

Both refuse a reversed pass rather than write something the reading code would
mis-expand. Flatten with the ordinary ``to_bmad()``/``to_pals()`` where the per-pass values
matter more than the shared hardware.

.. _per-pass-strengths:

Per-pass strengths
~~~~~~~~~~~~~~~~~~

For :ref:`multipass` configurations, state the beam's reference momentum on each pass, in eV/c, and
:py:meth:`pass_strengths <laura.models.elementList.MachineLayout.pass_strengths>` resolves it:

.. code-block:: yaml

    - LINAC: {multipass: 1, momentum: 100.0e+6}
    - ARC
    - LINAC: {multipass: 2, momentum: 200.0e+6}

.. code-block:: python

    layout.pass_strengths(1)     # {'LIN_Q': 0.5}    the stored value
    layout.pass_strengths(2)     # {'LIN_Q': 0.25}   half, at twice the energy

One magnet at one current holds one **field**, so that is what is resolved and held fixed:

.. code-block:: text

    field  = get_gradient(momentum of pass 1)
    KnL(N) = field * length / Brho(momentum of pass N)

:py:meth:`get_gradient <laura.models.magnetic.MagneticElement.get_gradient>` returns an
authored :py:attr:`gradient <laura.models.magnetic.MagneticElement.gradient>` untouched and
otherwise derives the field from the stored strength, so **stating a field and stating a
strength are one path, not two**. Substituting the second case gives
``KnL(N) = KnL(1) * Brho(1) / Brho(N)``, which is why pass 1 is the reference: it is simply
the pass the stored value describes. At order 0 the same expression is the dipole's own
:py:meth:`field_strength <laura.models.magnetic.Dipole_Magnet.field_strength>`.

Authoring a ``gradient`` is the more direct statement for a multipass magnet, since it is the
quantity that does not vary -- but it is not a separate mechanism, and a lattice that stores
strengths needs no rewriting to get the same answer.

A momentum is refused on any entry not marked ``multipass``, and on only some passes of a
multipass section: scaling is a ratio between two passes, so a pass without a momentum leaves
the others nothing to scale against.

.. note::

   One momentum per pass is a **reference value, not a profile**. A bunch really does
   accelerate through a linac, so a quadrupole near its exit sees a different energy from one
   near its entrance; state the momentum that makes that section's optics meaningful.
   Sections entered once are unaffected either way.

More than one section can be multipass, and in a **multi-turn** ERL more than one is: such a
machine accelerates and decelerates through the same linac several times, returning through
the same arc at a different energy on every turn. The arc is then shared hardware exactly as
the linac is, and needs its own per-pass momenta:

.. code-block:: yaml

    - LINAC: {multipass: 1, momentum: 100.0e+6}
    - ARC:   {multipass: 1, momentum: 100.0e+6}
    - LINAC: {multipass: 2, momentum: 200.0e+6}
    - ARC:   {multipass: 2, momentum: 200.0e+6}
    - LINAC: {multipass: 3, momentum: 100.0e+6}

Each section is numbered and referenced independently -- ``ARC`` pass 2 scales against ``ARC``
pass 1, never against the linac's. A pass number then no longer identifies a traversal on its
own, so name the section too:

.. code-block:: python

    layout.pass_strengths(2, "ARC")      # {'ARC_B': 0.5}
    layout.pass_strengths(2)             # LatticeError: enters ['ARC', 'LINAC'] on pass 2
    layout.pass_strengths(3)             # fine -- only LINAC makes a third pass

The bare form is refused rather than answered for whichever section happens to come first,
which is :ref:`the same rule <occurrence-addressing>` a bare element name follows on a
multipass path.

A section entered **once** needs no momentum at all, however many times its neighbours are
entered: it has one energy and its stored strength is already right for it. That is why the
single-turn ERL example below gives momenta to its linac but not to its arc.

A worked ERL -- one linac, two passes, the return pass 180 degrees off crest and at twice the
momentum -- is ``examples/testing/multipass_{elements,sections,layouts}.yaml``.

.. _layout-composition:

Composing section frames
~~~~~~~~~~~~~~~~~~~~~~~~

A section resolves in its own frame, starting at the world origin pointing along
``+z``, because a section belongs to the machine rather than to any one beam path. For a
:ref:`sequentially-placed <sequential-placement>` section that is a problem on its own:
such a section states no positions at all. The :py:class:`MachineModel`. It walks each layout in
order and moves every sequentially-placed section onto the exit frame of whatever
precedes it.

Three deliberate limits:

* **A section that states its positions is never moved.** A surveyed machine's
  coordinates are already global and composing them would corrupt them. Such a section
  still contributes at the exit, so a sequential section following one starts from
  its end.
* **A section shared by two layouts is composed at most once**, by the first layout that
  reaches it. Its stored position cannot be right for two different predecessors, so a
  second, disagreeing demand raises a warning naming both paths rather than being applied
  silently. Use :py:meth:`arc_lengths <laura.models.elementList.MachineLayout.arc_lengths>`
  for the other path's view.
* **Nothing outside a layout is touched.**

The layout automatically handles element ordering and can filter elements by various criteria:

.. code-block:: python

    from laura.models.elementList import MachineLayout
    
    layout = MachineLayout(
        name="main_beam",
        sections={"injector": inj_section, "linac": linac_section}
    )
    quads = layout.get_all_elements(element_type="Quadrupole")

.. _machine-model:

Machine Model
-------------

The :py:class:`MachineModel <laura.models.elementList.MachineModel>` class represents the complete accelerator model,
containing all possible beam paths, sections, and elements. This is the top-level class for managing the entire
lattice structure.

The machine model includes:

* ``layout: str | Dict | None``: Definition of available beam paths, either as a file path or dictionary.
* ``section: str | Dict[str, Dict] | None``: Definition of sections and their elements.
* ``elements: Dict[str, baseElement]``: Complete dictionary of all elements in the machine.
* ``sections: Dict[str, SectionLattice]``: All section lattices available in the model.
* ``lattices: Dict[str, MachineLayout]``: All machine layouts (beam paths) defined.
* ``master_lattice: str | None``: Directory containing lattice YAML files.
* ``default_path: str``: The default beam path to use when not explicitly specified.
* ``functional_definitions: str | dict``: Functional definitions for the whole machine (a mapping or YAML file path); see :ref:`functional-definitions`.
* ``resolve_functional: bool``: Global resolution mode (default ``False``); see :ref:`functional-definitions`.

Key functionality:

* ``get_element(name)``: Retrieve any element by name from the full machine.
* ``get_all_elements(element_type, element_model, element_class, section_type)``: Filter all machine elements by criteria.
* ``elements_between(start, end, element_type, element_model, element_class, path, section_type)``: Get elements within a range on a specific beam path.
* ``get_sections_by_type(section_type)`` / ``get_layouts_by_type(layout_type)``: Filter sections/layouts by :ref:`lattice type <lattice-types>`.
* ``append(values)`` / ``update(values)``: Dynamically add new elements to the model.
* ``resolve_positions()``: Re-resolve every element's placement and rebuild the section trajectories after the model has been modified. ``resolve_reference_placements()`` is the older, narrower name for the same operation.
* ``export_rdf(path, format, machine_name)`` / ``sparql(query)``: Linked-data export and querying; see :ref:`interfaces`.

The machine model supports multiple beam paths and can automatically build sections from elements if no explicit
section definition is provided:

.. code-block:: python

    from laura.models.elementList import MachineModel

    model = MachineModel(
        layout="layouts.yaml",
        section="sections.yaml",
        elements=all_elements
    )

    # Get elements along default path
    elements = model.elements_between(
        start="gun",
        end="dump",
        element_type="Quadrupole"
    )

    # Access specific beam path
    bypass_elements = model.elements_between(
        start="split",
        end="merge",
        path="bypass_line"
    )

The machine model automatically manages the relationships between elements, sections, and layouts, ensuring
consistency across the entire lattice definition. It provides both dictionary-style access (``model["element_name"]``)
and method-based queries for flexible interaction with the lattice data.

.. _lattice-types:

Lattice Types
-------------

An accelerator is not described by a single chain of elements. Alongside the beam path there
is an RF distribution network -- modulators, klystrons, waveguide, LLRF -- and, on a
photoinjector machine, a laser transport line. These are lattices in their own right: ordered,
connected, and worth querying separately, but they are not beam paths and should not be
returned by a query for "the elements between the gun and the dump".

Both :py:class:`SectionLattice <laura.models.elementList.SectionLattice>` and
:py:class:`MachineLayout <laura.models.elementList.MachineLayout>` therefore carry a type,
one of ``"beam"`` (the default), ``"rf"`` or ``"laser"``. In a ``sections.yaml`` a section is
either a bare list (implying ``beam``) or a mapping with an explicit ``type``:

.. code-block:: yaml

    sections:
      INJ:
        elements: [GUN, SOL-01, BPM-01]
        type: beam
      LASER:
        elements: [LSR-HWP-01, LSR-MIRROR-01]
        type: laser

    # in layouts.yaml
    layouts:
      main_beam: [INJ, LINAC]
      laser_line: [LASER]
    layout_metadata:
      laser_line: laser
    default_layout: main_beam

They can then be selected with
:py:meth:`get_sections_by_type <laura.models.elementList.MachineModel.get_sections_by_type>` and
:py:meth:`get_layouts_by_type <laura.models.elementList.MachineModel.get_layouts_by_type>`, and
element queries can be restricted with ``section_type``:

.. code-block:: python

    laser_sections = model.get_sections_by_type("laser")
    beam_bpms = model.get_all_elements(element_type="BPM", section_type="beam")

See :ref:`example-lattice-types` for a complete worked example.

.. _functional-definitions:

Functional Definitions
----------------------

Every lattice container — :ref:`section-lattice`, :ref:`machine-layout`, and
:ref:`machine-model` (and therefore the top-level
:py:class:`LAURA <laura.laura.LAURA>` class) — accepts two related options that
govern :ref:`functional parameters <functional-parameters>`, i.e. element
attributes that are defined symbolically by name rather than as numbers:

* ``functional_definitions: str | dict``: a mapping of functional-parameter names
  to numeric values (e.g. ``{"quad1_k1l": -2, "cav1_phase": 90}``), or a path to a
  YAML file holding such a mapping (optionally nested under a top-level
  ``functional_definitions`` key).
* ``resolve_functional: bool``: the global resolution mode (default ``False``);
  see :ref:`functional-parameters`.

When provided to a :py:class:`MachineModel <laura.models.elementList.MachineModel>`,
both are cascaded into the sections and layouts that it builds — and on into the
translators — so that a single declaration at the top level applies to the whole
machine.

Loading from a file and validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from laura.models.elementList import MachineModel

    model = MachineModel(
        layout="layouts.yaml",
        section="sections.yaml",
        elements=all_elements,
        functional_definitions="functional_definitions.yaml",
    )

As the model is built, every functional reference used by an element is validated
against the available definitions. If an element references a name that is not
defined, a ``ValueError`` is raised that names the missing parameter, the
element(s) that use it, and the source (the YAML file path, or the supplied
dictionary).

Export behaviour
~~~~~~~~~~~~~~~~

When exporting with the :ref:`translator`, codes that do not support symbolic
parameters always receive resolved numbers. Codes that do — ELEGANT (via a
``% <value> sto <name>`` rpn store at the top of the file) and Xsuite (via
variables on the ``xt.Environment``) — render the symbolic references by default,
or resolved numbers when ``resolve_functional`` is ``True``.
