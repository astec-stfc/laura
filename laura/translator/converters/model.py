from typing import Iterator, List, Optional, Tuple
from warnings import warn

from laura.models.element_list import MachineModel

from .fanout import ContainerTranslator, wrap_lattice_line
from .layout import MachineLayoutTranslator


def _layout_line_name(name: str, sections: List[str]) -> Optional[str]:
    """Name for a layout's ``LINE`` of section lines, or ``None`` to omit it."""
    if sections == [name]:
        return None
    if name not in sections:
        return name
    warn(
        f"Layout {name!r} contains a section of the same name; its line is "
        f"written as {name}_LAYOUT to keep the two distinct."
    )
    return f"{name}_LAYOUT"


class MachineModelTranslator(ContainerTranslator, MachineModel):
    """
    Translator for a :class:`~laura.models.elementList.MachineModel`.

    Its children are its layouts, so every ``to_CODE`` method inherited from
    :class:`~laura.translator.converters.fanout.ContainerTranslator` returns
    ``{layout_name: {section_name: result}}``.
    """

    directory: str = "."

    @classmethod
    def from_machine(cls, machine: MachineModel) -> "MachineModelTranslator":
        return cls.model_validate(
            {
                "layout": machine.model_copy().layout,
                "section": machine.model_copy().section,
                "elements": machine.model_copy().elements,
                "sections": machine.model_copy().sections,
                "lattices": machine.model_copy().lattices,
                "master_lattice": machine.model_copy().master_lattice,
                "functional_definitions": machine.functional_definitions,
                "resolve_functional": machine.resolve_functional,
                "revolution_frequency": machine.revolution_frequency,
                "particle": machine.particle,
            }
        )

    def _layout_translator(self, layout) -> MachineLayoutTranslator:
        """
        Build a :class:`MachineLayoutTranslator` for ``layout``, handing it this
        machine's output ``directory`` and falling back to this machine's own
        ``revolution_frequency`` if the layout does not define its own.
        """
        translator = MachineLayoutTranslator.from_layout(layout)
        translator.directory = self.directory
        if translator.revolution_frequency is None:
            translator.revolution_frequency = self.revolution_frequency
        return translator

    def _children(self) -> Iterator[Tuple[str, MachineLayoutTranslator]]:
        for name, latt in self.lattices.items():
            yield name, self._layout_translator(latt)

    def _elegant_body(self, charge: float | None = None) -> Tuple[str, str]:
        definitions = ""
        lines = ""
        for _, layout in self._children():
            layout_definitions, layout_lines = layout._elegant_body(charge=charge)
            definitions += layout_definitions
            lines += layout_lines

        for name, latt in self.lattices.items():
            line_name = _layout_line_name(name, list(latt.keys()))
            if line_name is None:
                continue
            line = f"{line_name}: LINE = (" + ", ".join(latt.keys()) + ")"
            lines += wrap_lattice_line(line) + "\n\n"
        return definitions, lines

    def _genesis_body(self) -> str:
        body = ""
        for _, layout in self._children():
            body += layout._genesis_body()

        for name, latt in self.lattices.items():
            line_name = _layout_line_name(name, list(latt.keys()))
            if line_name is None:
                continue
            body += f"{line_name}: LINE = " + "{" + ", ".join(latt.keys()) + "};\n\n"
        return body
