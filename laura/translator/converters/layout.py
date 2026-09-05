from typing import Any, Dict, Iterator, Tuple

from laura.models.elementList import MachineLayout

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
        return cls.model_validate(
            {
                "name": layout.model_copy().name,
                "sections": layout.model_copy().sections,
                "master_lattice": layout.model_copy().master_lattice,
                "functional_definitions": layout.functional_definitions,
                "resolve_functional": layout.resolve_functional,
                "revolution_frequency": layout.revolution_frequency,
            }
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
