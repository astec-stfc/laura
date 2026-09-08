from typing import Any, Dict, Iterator, Tuple

from laura.models.control import set_attr_by_path
from laura.models.elementList import MachineLayout, SectionLattice
from laura.models.reversal import reverse_section

from .converter import translate_elements
from .fanout import ContainerTranslator, wrap_lattice_line
from .section import SectionLatticeTranslator


class MachineLayoutTranslator(ContainerTranslator, MachineLayout):
    """
    Translator for a :class:`~laura.models.elementList.MachineLayout`.

    Its children are its sections, so every ``to_CODE`` method inherited from
    :class:`~laura.translator.converters.fanout.ContainerTranslator` returns
    ``{section_name: result}``.
    """

    directory: str = "."

    @classmethod
    def from_layout(cls, layout: MachineLayout) -> "MachineLayoutTranslator":
        """Build a translator for *layout*, resolving traversal direction once.

        :func:`~laura.models.reversal.reverse_section` -- reversed order,
        reversed elements, re-placed from its own lengths. The result is an
        ordinary section.

        The source layout and its sections are untouched if there is a reversal:
        the same section can be traversed forwards by another beam path.
        """
        if getattr(layout, "passes", None):
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
            if entry.momentum is not None:
                strengths = layout.pass_strengths(entry.number, entry.section)
                for name, kl in strengths.items():
                    element = registry.get(renamed.get(name, name))
                    if element is not None and element.magnetic is not None:
                        element.magnetic.kl = kl
            for name, values in entry.overrides.items():
                element = registry.get(renamed.get(name, name))
                if element is None:
                    continue
                for path, value in values.items():
                    set_attr_by_path(element, path, value)
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

        def renamed(name: str) -> str:
            base, _, tail = name.rpartition(".")
            if base and tail.isdigit():
                return f"{base}.{number}.{tail}"
            return f"{name}.{number}"

        names = {name: renamed(name) for name in section.order}
        names[section.name] = f"{section.name}.{number}"
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

    def _genesis_body(self) -> str:
        body = ""
        for section in self.sections.values():
            elem_dict = self._translate_section(section)
            for i, d in enumerate(elem_dict.values()):
                body += d.to_genesis(index=i)

            names = ", ".join(f"{i}{elem}" for i, elem in enumerate(elem_dict))
            body += f"\n{section.name}: LINE = " + "{" + names + "};\n\n\n"
        return body
