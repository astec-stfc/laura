from typing import Any, Dict, Iterator, List, Tuple
from warnings import warn

from laura.models.elementList import (
    LayoutPass,
    MachineLayout,
    SectionLattice,
    flatten_occurrence,
)
from laura.models.reversal import reverse_section

from ..utils.functions import sanitize_string
from ..utils.pals import pals_document
from .converter import translate_elements
from .fanout import ContainerTranslator, wrap_lattice_line
from .section import SectionLatticeTranslator

bmad_per_pass_attributes = {"phi0": "phi0_multipass"}
"""Attributes a Bmad multipass *slave* can hold on its own, and the name Bmad
wants each under.

Everything else belongs to the lord: Bmad accepts ``NAME\\N[k1] = ...`` in a
lattice file and then silently ignores it, so per-pass strength cannot be
written this way. That needs ``field_master``.
"""


class MachineLayoutTranslator(ContainerTranslator, MachineLayout):
    """
    Translator for a :class:`~laura.models.elementList.MachineLayout`.

    Its children are its sections, so every ``to_CODE`` method inherited from
    :class:`~laura.translator.converters.fanout.ContainerTranslator` returns
    ``{section_name: result}``.
    """

    directory: str = "."

    passes: List[LayoutPass] = []
    """Kept only by :meth:`from_layout` with ``multipass=True``."""

    @classmethod
    def from_layout(
        cls, layout: MachineLayout, *, multipass: bool = False
    ) -> "MachineLayoutTranslator":
        """Build a translator for *layout*, resolving traversal direction once.

        :func:`~laura.models.reversal.reverse_section` -- reversed order,
        reversed elements, re-placed from its own lengths. The result is an
        ordinary section.

        The source layout and its sections are untouched if there is a reversal:
        the same section can be traversed forwards by another beam path.

        Parameters
        ----------
        layout: MachineLayout
            The :class:`~laura.models.elementList.MachineLayout` to translate.
        multipass: bool
            Keep the passes as passes, rather than flattening them to one
            section each. Only :meth:`to_bmad_multipass` can use the result --
            every other backend needs one section per occurrence.
        """
        if multipass:
            sections = dict(layout.model_copy().sections)
        elif getattr(layout, "passes", None):
            sections = cls._flattened_passes(layout)
        else:
            sections = dict(layout.model_copy().sections)
            for name in getattr(layout, "_direction", {}) or {}:
                section = sections.get(name)
                if section is None:
                    continue
                sections[name] = reverse_section(
                    section, section.elements.elements, name=section.name
                )
        return cls.model_validate(
            {
                "name": layout.model_copy().name,
                "sections": sections,
                "master_lattice": layout.model_copy().master_lattice,
                "functional_definitions": layout.functional_definitions,
                "resolve_functional": layout.resolve_functional,
                "revolution_frequency": layout.revolution_frequency,
                "particle": layout.particle,
                "passes": layout.passes if multipass else [],
            }
        )

    @staticmethod
    def _flattened_passes(layout: MachineLayout) -> Dict[str, SectionLattice]:
        """One section per traversal, in beam order -- multipass export.

        ``sections`` is name-keyed and every consumer below iterates it, so a
        multipass path has to become a set of distinct sections before any
        of them sees it. Each pass gets its own deep copy, suffixed ``.N`` on
        the section and on every element in it.

        Per pass, in order: reverse if the pass is backwards, resolve the
        strengths that pass sees, then apply the author's ``overrides`` last.

        A single-pass or repetition layout arrives here with ``number`` unset
        and comes out unchanged but for reversal.
        """
        sections: Dict[str, SectionLattice] = {}
        for entry in layout.passes:
            section = layout.sections.get(entry.section)
            if section is None:
                continue
            renamed = MachineLayoutTranslator._pass_names(section, entry.number)
            section = MachineLayoutTranslator._numbered_copy(section, renamed)
            if entry.direction == -1:
                section = reverse_section(
                    section, section.elements.elements, name=section.name
                )
            registry = section.elements.elements
            for base in layout.sections[entry.section].order:
                element = registry.get(renamed.get(base, base))
                if element is not None:
                    layout.apply_pass_values(element, entry, base)
            sections[section.name] = section
        return sections

    @staticmethod
    def _pass_names(section: SectionLattice, number: int | None) -> Dict[str, str]:
        """``{name: name for pass N}`` for a section's elements, plus itself.

        The pass number is inserted before any within-section repeat index
        rather than appended after it, so that flattened multipass and plain
        repetition emit byte-identical names.
        """
        if number is None:
            return {}

        names = {
            name: flatten_occurrence(name, number) for name in section.order
        }
        names[section.name] = flatten_occurrence(section.name, number)
        return names

    @staticmethod
    def _numbered_copy(
        section: SectionLattice, renamed: Dict[str, str]
    ) -> SectionLattice:
        """A deep copy of ``section`` under the names ``renamed`` gives it.
        Positions are carried over untouched rather than re-resolved.

        Deep, because the passes of a multipass section are one device and the
        whole point of flattening is to give each traversal values of its own
        to carry.
        """
        if not renamed:
            return section.model_copy(deep=True)
        elements = []
        order = []
        for name in section.order:
            source = section.elements.elements.get(name)
            if source is None:
                continue
            clone = source.model_copy(deep=True)
            clone.name = renamed.get(name, name)
            elements.append(clone)
            order.append(clone.name)
        return SectionLattice(
            name=renamed.get(section.name, section.name),
            elements=elements,
            order=order,
            section_type=section.section_type,
            master_lattice=section.master_lattice,
            functional_definitions=section.functional_definitions,
            resolve_functional=section.resolve_functional,
            revolution_frequency=section.revolution_frequency,
        )

    def _section_translator(self, section) -> SectionLatticeTranslator:
        """
        Build a :class:`SectionLatticeTranslator` for ``section``, handing it
        this layout's output ``directory`` and falling back to this layout's own
        ``revolution_frequency`` if the section does not define its own.
        """
        translator = SectionLatticeTranslator.from_section(section)
        translator.directory = self.directory
        if translator.revolution_frequency is None:
            translator.revolution_frequency = self.revolution_frequency
        return translator

    def _children(self) -> Iterator[Tuple[str, SectionLatticeTranslator]]:
        for section in self.sections.values():
            yield section.name, self._section_translator(section)

    def _translate_section(self, section) -> Dict[str, Any]:
        """
        Drift-fill ``section`` and translate the result, returning the element
        translators keyed by name and in beamline order.
        """
        return translate_elements(
            section.createDrifts().values(),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )

    def _elegant_body(self, charge: float | None = None) -> Tuple[str, str]:
        definitions = ""
        lines = ""
        for section in self.sections.values():
            elem_dict = self._translate_section(section)
            if charge:
                definitions += f"{section.name}_Q: CHARGE, TOTAL = {charge};\n"
            for d in elem_dict.values():
                definitions += d.to_elegant()

            line = f"{section.name}: LINE = ("
            if charge:
                line += f"{section.name}_Q, "
            line += ", ".join(elem_dict.keys()) + ")"
            lines += "\n" + wrap_lattice_line(line) + "\n\n\n"
        return definitions, lines

    def to_pals(self, particle: str | None = None) -> str:
        """
        Create a PALS document holding this layout's sections as the branches of
        one lattice.

        Parameters
        ----------
        particle: str | None
            Used only if the layout does not name a particle itself.

        Returns
        -------
        str
            The contents of a ``*.pals.yaml`` file.
        """
        beamlines = [
            section._pals_beamline(particle=self.particle or particle)
            for _, section in self._children()
        ]
        return pals_document(beamlines, self.name)

    def to_bmad_multipass(
        self,
        particle: str | None = None,
        *,
        space_charge_n_bin: int | None = None,
        initial_twiss: Any = None,
    ) -> str:
        """
        Create one Bmad lattice file for this whole beam path, with a multipass
        section written as a Bmad multipass lord and one slave per traversal.

        :meth:`to_bmad` flattensm, while this keeps the identity Bmad can hold: the
        hardware is defined once, and ``NAME\\1``, ``NAME\\2`` are the beam's
        visits to it.

        Requires a translator built with ``from_layout(..., multipass=True)``.

        Parameters
        ----------
        particle: str | None
            Used only if the layout does not name a particle itself.
        space_charge_n_bin: int | None
            Optional positive number of Bmad space-charge bins.
        initial_twiss: TwissMatchSimulationElement | None
            Beginning Twiss parameters.

        Returns
        -------
        str
            A Bmad-compatible lattice file.
        """
        entries = self._passes_in_beam_order()
        if not entries:
            raise ValueError(
                "to_bmad_multipass needs a layout with passes; build the "
                "translator with from_layout(layout, multipass=True)"
            )
        reversed_passes = [entry for entry in entries if entry.direction == -1]
        if reversed_passes:
            raise NotImplementedError(
                f"Bmad needs a reflection patch either side of a reversed "
                f"element, which LAURA does not write yet, so {reversed_passes} "
                f"cannot be exported natively. Use to_bmad() to flatten instead."
            )

        shared = {entry.section for entry in entries if entry.number is not None}
        translators = {
            name: self._section_translator(self.sections[name])
            for name in dict.fromkeys(entry.section for entry in entries)
        }
        first = translators[entries[0].section]
        geometry = getattr(first.geometry, "value", first.geometry) or "open"
        bodies = {
            name: translator._bmad_body(geometry, multipass=name in shared)
            for name, translator in translators.items()
        }

        name = sanitize_string(self.name)
        settings = "".join(
            self._bmad_pass_settings(entry, bodies[entry.section].renames)
            for entry in entries
            if entry.number is not None
        )
        return (
            first.bmad_header(
                geometry,
                particle=self.particle or particle,
                space_charge_n_bin=space_charge_n_bin,
                reference_energy=first.reference_energy,
                initial_twiss=(
                    initial_twiss
                    if initial_twiss is not None
                    else bodies[entries[0].section].origin
                ),
                beginning=bodies[entries[0].section].beginning,
            )
            + "".join(body.definitions for body in bodies.values())
            + "\n"
            + "".join(body.line for body in bodies.values())
            + f"{name}: line = ("
            + ", ".join(bodies[entry.section].name for entry in entries)
            + ")\n"
            + "".join(body.superpositions for body in bodies.values())
            + f"use, {name}\n"
            + ("expand_lattice\n" + settings if settings else "")
        )

    def _bmad_pass_settings(self, entry: LayoutPass, renames: Dict[str, str]) -> str:
        """``NAME\\N[attribute] = value`` for whatever ``entry`` changes.

        Found by exporting the section twice -- once as stored, once with the
        pass applied -- and diffing what each wrote, rather than by mapping each
        override path onto a Bmad attribute by hand.
        """
        section = self.sections[entry.section]
        applied = self._numbered_copy(section, {})
        for element_name in section.order:
            element = applied.elements.elements.get(element_name)
            if element is not None:
                self.apply_pass_values(element, entry, element_name)

        def written(source):
            translated = translate_elements(
                source.elements.elements.values(),
                master_lattice=self.master_lattice,
                directory=self.directory,
            )
            return {
                name: (translator.to_bmad(), translator.bmad_attributes())[1]
                for name, translator in translated.items()
            }

        stored = written(section)
        settings = ""
        lord_only = set()
        for element_name, parameters in written(applied).items():
            was = stored[element_name]
            for key, value in parameters.items():
                if was.get(key) == value:
                    continue
                if key not in bmad_per_pass_attributes:
                    lord_only.add(key)
                    continue
                target = sanitize_string(renames.get(element_name, element_name))
                attribute = bmad_per_pass_attributes[key]
                settings += f"{target}\\{entry.number}[{attribute}] = {value}\n"
        if lord_only:
            warn(
                f"Pass {entry.number} of {entry.section} changes "
                f"{sorted(lord_only)}, which Bmad holds on the multipass lord "
                f"and shares across every pass. Those values are not in the "
                f"export; flatten with to_bmad() if you need them."
            )
        return settings

    def _genesis_body(self) -> str:
        body = ""
        for section in self.sections.values():
            elem_dict = self._translate_section(section)
            for i, d in enumerate(elem_dict.values()):
                body += d.to_genesis(index=i)

            names = ", ".join(f"{i}{elem}" for i, elem in enumerate(elem_dict))
            body += f"\n{section.name}: LINE = " + "{" + names + "};\n\n\n"
        return body
