"""
Section/layout/model assembly shared by the importers that build one flat,
ordered ``{name: element}`` dict (MAD-X, ELEGANT, Xsuite, Ocelot), plus the
pieces Bmad shares with them.
"""

import math
import os
import re
from pathlib import Path
from typing import Dict, Optional, Union
from warnings import warn

from pydantic import BaseModel

from laura.models.element_list import (
    ElementList,
    MachineLayout,
    MachineModel,
    SectionLattice,
)

from ....exporters.yaml_exporter import PositionMode, export_machine_combined_file

CLOSED_ANGLE_TOLERANCE = 1e-5
"""How near 2*pi [rad] a section's total bend must be for :func:`infer_geometry`
to call it closed."""


def infer_geometry(section: SectionLattice) -> None:
    """Mark ``section`` ``closed`` when its bends total 2*pi, unless the source
    already said."""
    if section.geometry is not None:
        return
    total = sum(
        element.physical._physical_angle
        for element in section.elements.elements.values()
        if not element.is_subelement()
    )
    if abs(abs(total) - 2 * math.pi) < CLOSED_ANGLE_TOLERANCE:
        section.geometry = "closed"


def section_entry(elements: list, section: Optional[SectionLattice] = None):
    """A :class:`MachineModel` section entry: the element names, plus the
    section's geometry and reference energy where the import knows them."""
    metadata = {
        key: getattr(section, key, None) for key in ("geometry", "reference_energy")
    }
    metadata = {key: value for key, value in metadata.items() if value is not None}
    return {"elements": elements, **metadata} if metadata else elements


def twiss_simulation(*values: float) -> dict:
    """A ``TwissMatch`` ``simulation`` dict from beta_x, beta_y, alpha_x,
    alpha_y, eta_x, eta_y, eta_xp and eta_yp, in that order."""
    fields = ("beta_x", "beta_y", "alpha_x", "alpha_y")
    fields += ("eta_x", "eta_y", "eta_xp", "eta_yp")
    return dict(zip(fields, values, strict=True), from_beam=False)


def keyword_rules(rules: Dict, hardware_type: str) -> Dict:
    """``rules["general"]`` merged over ``hardware_type``'s own rules."""
    key = hardware_type.lower()
    # ``in``/``[]``, not ``.get``: a LazyDict loads only through those
    return rules[key] | rules["general"] if key in rules else rules["general"]


def compact_expression(expression: str) -> str:
    """``expression`` lower-cased, without spaces or parentheses."""
    return expression.lower().replace(" ", "").replace("(", "").replace(")", "")


def check_layouts(
    layouts: Dict,
    skipped: list,
    min_section_length: int,
    skipped_label: str,
    empty_label: Optional[str] = None,
) -> None:
    """Warn about ``skipped`` sections; raise if no layout survived."""
    if skipped:
        warn(
            f"Skipped {skipped_label} shorter than min_section_length="
            f"{min_section_length}: {', '.join(skipped)}"
        )
    if not layouts:
        raise ValueError(
            f"No {empty_label or skipped_label} meet "
            f"min_section_length={min_section_length}."
        )


def read_with_calls(path: Path, call: "re.Pattern", _seen: Optional[set] = None) -> str:
    """Read a ``!``-commented lattice file, inlining the files ``call`` matches.

    ``call``'s first group is the called filename, resolved relative to the
    file containing the call as MAD-X and Bmad both do, after expanding any
    environment variables in it (``$LCLS_LATTICE/...``). A missing file is
    left as written, and a file already inlined is not inlined again.
    """
    seen = _seen if _seen is not None else set()
    path = path.resolve()
    if path in seen:
        return ""
    seen.add(path)
    text = re.sub(r"!.*", "", path.read_text())

    def _inline(match: "re.Match") -> str:
        called = os.path.expandvars(match.group(1).strip().strip("'\""))
        called = (path.parent / called).resolve()
        if not called.is_file():
            return match.group(0)
        return read_with_calls(called, call, seen)

    return call.sub(_inline, text)


class LatticeImporter(BaseModel):
    """Builds sections, layouts and models from :meth:`_element_map`."""

    functional_definitions: Dict[str, Union[int, float]] = {}

    def _default_name(self) -> str:
        """Name for an auto-derived section/layout."""
        raise NotImplementedError

    def _element_map(self) -> Dict:
        """The imported ``{name: element}`` dict, in beamline order."""
        return self.elements

    def _default_sections(self) -> Dict[str, SectionLattice]:
        """The sections :meth:`create_layout` uses when none are given."""
        return self.create_section()

    def _reference_energy(self) -> Optional[float]:
        """Total energy [eV] of the source's design particle, for the
        section's ``reference_energy``; None where the format has none."""
        return None

    def create_element_dictionary(self):
        return self.create_laura_element_dictionary()

    def create_section(
        self, section: Optional[Dict] = None
    ) -> Dict[str, SectionLattice]:
        """Build a named :class:`SectionLattice` from imported elements.

        Parameters
        ----------
        section: dict, optional
            ``{section_name: [first_element_name, last_element_name]}``. When
            omitted, a single section spanning the whole imported lattice is
            derived, named by :meth:`_default_name`.
        """
        if not self._element_map():
            self.create_laura_element_dictionary()
        imported = self._element_map()
        names = list(imported)
        if section is None:
            if not names:
                raise ValueError("No elements were imported; cannot build a section.")
            section = {self._default_name(): [names[0], names[-1]]}
        if len(section) != 1:
            raise ValueError("A section definition must contain exactly one section.")
        name, bounds = next(iter(section.items()))
        if len(bounds) != 2:
            raise ValueError(
                "A section definition must contain first and last elements."
            )
        try:
            first, last = names.index(bounds[0]), names.index(bounds[1])
        except ValueError as exc:
            missing = bounds[0] if bounds[0] not in imported else bounds[1]
            raise KeyError(f"element {missing} not found in lattice") from exc
        if first > last:
            raise ValueError("The first section element must precede the last.")
        elements = dict(list(imported.items())[first : last + 1])
        lattice = SectionLattice(
            order=list(elements),
            elements=ElementList(elements=elements),
            name=name,
            functional_definitions=self.functional_definitions,
            reference_energy=self._reference_energy(),
        )
        lattice.resolve_positions(imported)
        return {name: lattice}

    def create_layout(
        self, name: Optional[str] = None, sections: Optional[Dict] = None
    ) -> MachineLayout:
        """Build a :class:`MachineLayout` from one or more sections.

        Parameters
        ----------
        name: str, optional
            Layout name. Defaults to :meth:`_default_name` when omitted.
        sections: dict, optional
            ``{section_name: [first_element_name, last_element_name]}`` for
            each section. When omitted, :meth:`_default_sections` is used.
        """
        if sections is None:
            layout_sections = self._default_sections()
        else:
            layout_sections = {}
            for section_name, bounds in sections.items():
                layout_sections.update(self.create_section({section_name: bounds}))
        for section in layout_sections.values():
            infer_geometry(section)
        return MachineLayout(
            name=name or self._default_name(),
            sections=layout_sections,
            functional_definitions=self.functional_definitions,
        )

    def _single_layout_model(self, sections: Optional[Dict] = None) -> MachineModel:
        """Wrap :meth:`create_layout` in a one-layout :class:`MachineModel`."""
        layout = self.create_layout(sections=sections)
        return MachineModel(
            elements={
                element.name: element
                for section in layout.sections.values()
                for element in section.elements.list()
            },
            section={
                "sections": {
                    name: section_entry(section.order, section)
                    for name, section in layout.sections.items()
                }
            },
            layout={
                "layouts": {layout.name: list(layout.sections)},
                "default_layout": layout.name,
            },
            functional_definitions=self.functional_definitions,
        )

    def _layouts_model(
        self,
        elements: Dict,
        section_definitions: Dict,
        built_sections: Dict,
        layout_definitions: Dict,
        functional_definitions: Dict,
    ) -> MachineModel:
        """A multi-layout :class:`MachineModel` rooted beside ``source_file``."""
        return MachineModel(
            elements=elements,
            section={
                "sections": {
                    name: section_entry(names, built_sections.get(name))
                    for name, names in section_definitions.items()
                }
            },
            layout={
                "layouts": layout_definitions,
                "default_layout": next(iter(layout_definitions)),
            },
            master_lattice=str(Path(self.source_file).resolve().parent),
            functional_definitions=functional_definitions,
        )

    def export_yaml(
        self,
        path: str,
        source: Union[SectionLattice, MachineLayout, MachineModel],
        position_mode: PositionMode = "s",
    ) -> None:
        """Export ``source`` to a combined LAURA YAML file in ``path``.

        See :func:`~laura.exporters.yaml_exporter.export_machine_combined_file`
        for ``position_mode``.
        """
        export_machine_combined_file(path, source, position_mode=position_mode)
