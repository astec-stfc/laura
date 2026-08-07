import os
import re
from pathlib import Path
from typing import Dict, Optional, Union
from warnings import warn

import numpy as np
from pydantic import BaseModel, PrivateAttr, model_validator

import laura.models.element as LAURA_elements
from laura.models.elementList import (
    SectionLattice,
    MachineLayout,
    MachineModel,
    ElementList,
)
from ...utils.functions import (
    introspect_model_defaults,
    merge_layout_elements,
    number_repeated_names,
)
from ...utils.madx.TFSFile import TFSFile
from .. import type_conversion_rules_Madx, keyword_conversion_rules_madx
from ....Exporters.YAML import export_machine_combined_file, PositionMode

_SILENTLY_SKIPPED_TYPES = ("drift",)

_RAW_KEYS = ("k0", "k1", "k2", "k3", "angle", "l", "kick", "hkick", "vkick", "ks")


def _read_lattice_text(path: Path, _seen: Optional[set] = None) -> str:
    """Read a MAD-X source file, inlining any ``call, file=...;`` statements
    it contains (recursively), so text-based scans (e.g. for declared
    constant names) see included files too.
    """
    seen = _seen if _seen is not None else set()
    path = path.resolve()
    if path in seen:
        return ""
    seen.add(path)
    text = re.sub(r"!.*", "", path.read_text())

    def _inline(match: "re.Match") -> str:
        called = (path.parent / match.group(1).strip().strip("'\"")).resolve()
        if not called.is_file():
            return match.group(0)
        return _read_lattice_text(called, seen)

    return re.sub(r"(?i)\bcall\s*,\s*file\s*=\s*([^;]+);", _inline, text)


def _switch_dict() -> Dict[str, str]:
    """MAD-X keyword -> LAURA type name, reversing ``type_conversion_rules_Madx``.

    Several LAURA types collide on the same (coarser) MAD-X keyword -- e.g.
    ``Beam_Position_Monitor``/``Screen`` /... all export as
    ``monitor``.
    """
    switch = {y: x for x, y in type_conversion_rules_Madx.items()}
    switch.update(
        {
            "monitor": "Beam_Position_Monitor",
            "marker": "Marker",
            "rcollimator": "Collimator",
        }
    )
    return switch


class MadxLatticeImporter(BaseModel):

    twiss_file: Optional[str] = None
    """Path to a MAD-X TWISS TFS table (``SELECT, flag=twiss, column=...;``
    before running ``TWISS``)."""

    source_file: Optional[str] = None
    """Original MAD-X input file, used instead of ``twiss_file``."""

    sequence: Optional[str] = None
    """Sequence to import from ``source_file``; defaults to its sole sequence."""

    madx_data: Dict = {}
    """Dictionary containing data about the MAD-X lattice, keyed by element name."""

    elements: Dict = {}
    """Dictionary containing converted
    :class:`~laura.models.element.Element` objects"""

    functional_definitions: Dict[str, Union[int, float]] = {}

    lattice_name: Optional[str] = None
    """Best-effort lattice name, parsed from the TWISS file's own
    ``SEQUENCE`` header parameter. Used as the default section/layout name
    in :meth:`create_section`/:meth:`create_layout` when not given
    explicitly."""

    deferred_parameters: Dict[str, Dict[str, str]] = {}
    _source_functional_definitions: Dict[str, float] = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def _check_input(self):
        if (self.twiss_file is None) == (self.source_file is None):
            raise ValueError("Give exactly one of twiss_file or source_file.")
        return self

    def _default_name(self) -> str:
        if self.lattice_name:
            return self.lattice_name
        return os.path.splitext(os.path.basename(self.twiss_file or self.source_file))[0]

    @staticmethod
    def _single_symbol(expression: str | None, definitions: Dict, length=0.0) -> str | None:
        if not isinstance(expression, str) or not expression:
            return None
        compact = expression.lower().replace(" ", "").replace("(", "").replace(")", "")
        for name in definitions:
            if compact == name.lower():
                return name
            if compact in {
                f"{name.lower()}*1e-06",
                f"1e-06*{name.lower()}",
                f"90-{name.lower()}/360",
            }:
                return name
            if length and compact.startswith(name.lower() + "/"):
                try:
                    if np.isclose(float(compact.split("/", 1)[1]), length):
                        return name
                except ValueError:
                    pass
        return None

    def _load_madx(self):
        """Parse ``source_file`` into a fresh ``cpymad`` ``Madx`` instance.

        MAD-X's own ``call, file="...";`` statements resolve relative
        filenames against the *process's* working directory.
        """
        try:
            from cpymad.madx import Madx
        except ImportError as exc:
            raise ImportError(
                "cpymad is required for MAD-X source import. Install with: "
                'pip install "laura-accelerator[madx]"'
            ) from exc

        madx = Madx(stdout=False)
        source = Path(self.source_file).resolve()
        with madx.chdir(str(source.parent)):
            madx.call(str(source))
        return madx

    def _rows_for_sequence(self, madx, sequence: str) -> list:
        """Extract element rows for one already-loaded MAD-X sequence."""
        self.lattice_name = sequence

        self.deferred_parameters = {}
        rows = []
        used = set()
        declared = set(
            re.findall(
                r"(?im)^\s*([A-Za-z_][\w.]*)\s*(?::=|=)",
                _read_lattice_text(Path(self.source_file)),
            )
        )
        native_elements = list(madx.sequence[sequence].elements)
        numbered_names = number_repeated_names(
            [element.name for element in native_elements]
        )
        for element, numbered_name in zip(native_elements, numbered_names):
            name = numbered_name.replace("$", "_")
            length = float(element.length)
            row = {
                "name": name,
                "keyword": element.base_type.name,
                "l": length,
                "s": float(element.position) + length,
            }
            for name, parameter in element.cmdpar.items():
                if parameter.inform:
                    row[name] = parameter.value
                if parameter.inform > 1 and isinstance(parameter.expr, str):
                    self.deferred_parameters.setdefault(row["name"], {})[name] = parameter.expr
                    used.update(re.findall(r"[A-Za-z_][\w.]*", parameter.expr))
            rows.append(row)
        self._source_functional_definitions = {
            name: float(madx.globals[name])
            for name in used | declared
            if name in madx.globals
        }
        self.functional_definitions = dict(self._source_functional_definitions)
        return self._merge_dipedges(rows)

    def _source_rows(self, madx=None) -> list:
        if madx is None:
            madx = self._load_madx()
        sequences = list(madx.sequence.keys())
        if self.sequence:
            sequence = self.sequence.lower()
            if sequence not in sequences:
                raise KeyError(f"MAD-X sequence {self.sequence!r} was not found.")
        elif len(sequences) == 1:
            sequence = sequences[0]
        else:
            raise ValueError(
                f"MAD-X source defines {sequences}; set sequence to choose one."
            )
        return self._rows_for_sequence(madx, sequence)

    def _merge_dipedges(self, rows: list) -> list:
        """Fold MAD-X thin edge elements into their adjacent thick dipole."""
        bends = {"sbend", "rbend"}
        merged = set()
        for index, edge in enumerate(rows):
            if str(edge["keyword"]).lower() != "dipedge":
                continue
            target = None
            edge_parameter = None
            if index + 1 < len(rows):
                candidate = rows[index + 1]
                if (
                    str(candidate["keyword"]).lower() in bends
                    and np.isclose(edge["s"], candidate["s"] - candidate["l"])
                ):
                    target, edge_parameter = candidate, "e1"
            if target is None and index:
                candidate = rows[index - 1]
                if (
                    str(candidate["keyword"]).lower() in bends
                    and np.isclose(edge["s"], candidate["s"])
                ):
                    target, edge_parameter = candidate, "e2"
            if target is None:
                continue

            target[edge_parameter] = edge.get("e1", 0.0)
            for source, destination, scale in (
                ("hgap", "gap", 2.0),
                ("fint", "fint", 1.0),
                ("tilt", "tilt", 1.0),
            ):
                if source not in edge:
                    continue
                value = float(edge[source]) * scale
                if destination in target and not np.isclose(target[destination], value):
                    warn(
                        f"MAD-X dipedge values differ across {target['name']!r}; "
                        f"keeping its first {destination} value."
                    )
                else:
                    target[destination] = value
            expression = self.deferred_parameters.get(edge["name"], {}).get("e1")
            if expression:
                self.deferred_parameters.setdefault(target["name"], {})[
                    edge_parameter
                ] = expression
            self.deferred_parameters.pop(edge["name"], None)
            merged.add(edge["name"])
        return [row for row in rows if row["name"] not in merged]

    def create_element_dictionary(self, madx=None) -> Dict:
        if self.source_file:
            rows = self._source_rows(madx)
        else:
            tfs = TFSFile()
            tfs.read_file(self.twiss_file)
            self.lattice_name = tfs.headers.get("sequence")
            rows = tfs.rows()

        switch_dict = _switch_dict()
        source_definitions = self._source_functional_definitions
        scaled_definitions = {}
        conflicting_definitions = set()
        for row in rows:
            length = row.get("l", 0.0)
            for param, expression in self.deferred_parameters.get(str(row["name"]), {}).items():
                symbol = self._single_symbol(expression, source_definitions, length)
                compact = expression.lower().replace(" ", "").replace("(", "").replace(")", "")
                if symbol and param in {"k0", "k1", "k2", "k3", "ks"} and compact == symbol.lower():
                    value = source_definitions[symbol] * length
                    if symbol in scaled_definitions and not np.isclose(scaled_definitions[symbol], value):
                        conflicting_definitions.add(symbol)
                    scaled_definitions[symbol] = value
        self.functional_definitions.update(
            {
                name: value
                for name, value in scaled_definitions.items()
                if name not in conflicting_definitions
            }
        )
        self.madx_data = {}
        for row in rows:
            name = str(row["name"])
            elemtype = str(row["keyword"]).lower()
            if elemtype in _SILENTLY_SKIPPED_TYPES:
                continue
            if elemtype not in switch_dict:
                warn(f"Could not parse MAD-X element type {elemtype!r} for {name!r}; skipping.")
                continue
            sftype = switch_dict[elemtype]
            try:
                model_fields = introspect_model_defaults(
                    getattr(LAURA_elements, sftype), resolve_optional=True,
                )
            except AttributeError:
                warn(
                    f"LAURA has no element type {sftype!r} (from MAD-X {elemtype!r}) "
                    f"for {name!r}; skipping."
                )
                continue

            entry = {
                "hardware_type": sftype,
                "name": name,
                "machine_area": "test",
                "l": row.get("l", 0.0),
                "s": row.get("s", 0.0),
            }
            for subk in ("magnetic", "cavity", "simulation", "diagnostic", "physical", "aperture"):
                if subk in model_fields:
                    entry[subk] = {}

            merged = keyword_conversion_rules_madx["general"]
            if sftype.lower() in keyword_conversion_rules_madx:
                merged = keyword_conversion_rules_madx[sftype.lower()] | merged
            kwele = {y: x for x, y in merged.items()}

            for param, val in row.items():
                if param in ("name", "keyword", "s"):
                    continue
                if param == "hgap" and "magnetic" in entry:
                    entry["magnetic"]["gap"] = 2 * float(val)
                if param in _RAW_KEYS:
                    entry[param] = val
                if val in (None, "", 0):
                    continue
                for subk in model_fields:
                    if not isinstance(model_fields[subk], dict):
                        continue
                    if param in model_fields[subk]:
                        entry[subk][param] = val
                    elif param in kwele and kwele[param] in model_fields[subk]:
                        entry[subk][kwele[param]] = val
            for param, expression in self.deferred_parameters.get(name, {}).items():
                symbol = self._single_symbol(
                    expression, source_definitions, row.get("l", 0)
                )
                if not symbol or symbol in conflicting_definitions:
                    continue
                if param in _RAW_KEYS:
                    entry[param] = symbol
                for subk in model_fields:
                    if not isinstance(model_fields[subk], dict):
                        continue
                    target = param if param in model_fields[subk] else kwele.get(param)
                    if target in model_fields[subk]:
                        entry[subk][target] = symbol
            self.madx_data[name] = entry
        return self.madx_data

    @staticmethod
    def _convert_raw_fields(v: dict) -> dict:
        """Turn TWISS's raw per-length/per-element attributes into LAURA's
        integrated-strength and plane-specific fields.
        """
        htype = v.get("hardware_type", "")
        length = (
            v.get("magnetic", {}).get("length")
            or v.get("physical", {}).get("length")
            or v.get("l", 0.0)
        )

        if "angle" in v:
            v["k0"] = v["angle"]
            if "physical" in v:
                v["physical"]["physical_angle"] = v["angle"]

        if "magnetic" in v:
            multi = {}
            for n in range(4):
                key = f"k{n}"
                if key in v:
                    raw = v[key]
                    knl = raw if isinstance(raw, str) or n == 0 else float(raw) * length
                    multi[f"K{n}L"] = {"order": n, "normal": knl}
            if multi:
                v["magnetic"].setdefault("multipoles", {}).update(multi)

            if htype == "Combined_Corrector":
                v["magnetic"]["horizontal_kick"] = v.get("hkick", 0.0)
                v["magnetic"]["vertical_kick"] = v.get("vkick", 0.0)
            elif htype == "Horizontal_Corrector":
                v["magnetic"]["horizontal_kick"] = v.get("kick", 0.0)
            elif htype == "Vertical_Corrector":
                v["magnetic"]["vertical_kick"] = v.get("kick", 0.0)
            if htype == "Solenoid" and "ks" in v:
                v["magnetic"].setdefault("fields", {})["S0L"] = (
                    v["ks"] if isinstance(v["ks"], str) else float(v["ks"]) * length
                )

        if "cavity" in v and "phase" in v["cavity"]:
            if not isinstance(v["cavity"]["phase"], str):
                v["cavity"]["phase"] = 90 - 360 * float(v["cavity"]["phase"])
        if "cavity" in v and "frequency" in v["cavity"]:
            if not isinstance(v["cavity"]["frequency"], str):
                v["cavity"]["frequency"] = float(v["cavity"]["frequency"]) * 1e6
        if "simulation" in v and "field_amplitude" in v["simulation"]:
            if not isinstance(v["simulation"]["field_amplitude"], str):
                v["simulation"]["field_amplitude"] = (
                    float(v["simulation"]["field_amplitude"]) * 1e6
                )

        return v

    def create_laura_element_dictionary(self):
        if not self.madx_data:
            self.create_element_dictionary()
        self.elements = {}

        for k, v in self.madx_data.items():
            vtype = v["hardware_type"]
            elem_length = v.get("l", 0.0)
            v = self._convert_raw_fields(v)

            s_val = v.get("s", 0.0)
            physical = {"s": s_val, "s_point": "end", "length": elem_length}
            if "physical" in v:
                v["physical"].update(physical)
            else:
                v["physical"] = physical

            self.elements.update({k: getattr(LAURA_elements, vtype)(**v)})
        return self.elements

    def create_section(self, section: Optional[Dict] = None) -> Dict[str, SectionLattice]:
        """Build a named :class:`SectionLattice` from imported elements.

        Parameters
        ----------
        section: dict, optional
            ``{section_name: [first_element_name, last_element_name]}``. When
            omitted, a single section spanning the *entire* imported lattice
            (its first through last element, in beamline order) is derived
            automatically. The name defaults to :meth:`_default_name`.
        """
        if not self.elements:
            self.create_laura_element_dictionary()
        if section is None:
            names = list(self.elements)
            if not names:
                raise ValueError("No elements were imported; cannot build a section.")
            section = {self._default_name(): [names[0], names[-1]]}
        if len(section) != 1:
            raise ValueError("A section definition must contain exactly one section.")
        secname, bounds = next(iter(section.items()))
        if len(bounds) != 2:
            raise ValueError("A section definition must contain first and last elements.")
        names = list(self.elements)
        try:
            first, last = names.index(bounds[0]), names.index(bounds[1])
        except ValueError as exc:
            missing = bounds[0] if bounds[0] not in self.elements else bounds[1]
            raise KeyError(f"element {missing} not found in lattice") from exc
        if first > last:
            raise ValueError("The first section element must precede the last.")
        elems = dict(list(self.elements.items())[first : last + 1])
        seclat = SectionLattice(
            order=list(elems), elements=ElementList(elements=elems), name=secname,
            functional_definitions=self.functional_definitions,
        )
        seclat.resolve_positions(self.elements)
        return {secname: seclat}

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
            each section. When omitted, a single auto-derived section
            spanning the whole imported lattice is used (see
            :meth:`create_section`).
        """
        if sections is None:
            layout_sections = self.create_section()
        else:
            layout_sections = {}
            for secname, secpos in sections.items():
                layout_sections.update(self.create_section({secname: secpos}))
        return MachineLayout(
            name=name or self._default_name(),
            sections=layout_sections,
            functional_definitions=self.functional_definitions,
        )

    def create_machine_model(self, min_section_length: int = 5) -> MachineModel:
        """Build a model with one layout per MAD-X sequence.

        Only usable with ``source_file`` -- a single ``twiss_file`` table
        only ever describes one already-selected sequence, so that case
        falls back to a single-layout model wrapping :meth:`create_layout`.
        Each sequence becomes its own layout with a single section spanning
        it. Sequences importing fewer than ``min_section_length`` elements
        are omitted, and elements with the same name and placement are
        shared between layouts. When MAD-X gives the same name a different
        position, orientation, or arc-length in another sequence, a
        sequence-specific ``name__sequence`` copy is created because
        :class:`MachineModel` stores one placement per name.
        """
        if min_section_length < 1:
            raise ValueError("min_section_length must be at least 1.")

        if not self.source_file:
            layout = self.create_layout()
            return MachineModel(
                elements={
                    element.name: element
                    for section in layout.sections.values()
                    for element in section.elements.list()
                },
                section={
                    "sections": {
                        name: section.order for name, section in layout.sections.items()
                    }
                },
                layout={
                    "layouts": {layout.name: list(layout.sections)},
                    "default_layout": layout.name,
                },
                functional_definitions=self.functional_definitions,
            )

        madx = self._load_madx()
        sequences = list(madx.sequence.keys())
        if not sequences:
            raise ValueError(f"MAD-X source {self.source_file!r} defines no sequences.")

        elements = {}
        section_definitions = {}
        layout_definitions = {}
        skipped_sections = []
        all_functional_definitions = {}

        for sequence in sequences:
            self.sequence = sequence
            self.madx_data = {}
            self.elements = {}
            self.create_element_dictionary(madx)
            all_functional_definitions.update(self.functional_definitions)
            layout = self.create_layout(name=sequence)
            layout_sections = []
            for source_name, section in layout.sections.items():
                if len(section.order) < min_section_length:
                    skipped_sections.append(f"{sequence}/{source_name}")
                    continue
                section_name = source_name
                if section_name in section_definitions:
                    section_name = f"{sequence}_{section_name}"
                merge_layout_elements(
                    elements,
                    section_definitions,
                    section_name,
                    section.elements.elements.items(),
                    section.order,
                    sequence,
                )
                layout_sections.append(section_name)
            if layout_sections:
                layout_definitions[sequence] = layout_sections

        if skipped_sections:
            warn(
                "Skipped MAD-X sequences shorter than min_section_length="
                f"{min_section_length}: {', '.join(skipped_sections)}"
            )
        if not layout_definitions:
            raise ValueError(
                "No MAD-X sequences meet min_section_length="
                f"{min_section_length}."
            )

        return MachineModel(
            elements=elements,
            section={"sections": section_definitions},
            layout={
                "layouts": layout_definitions,
                "default_layout": next(iter(layout_definitions)),
            },
            master_lattice=str(Path(self.source_file).resolve().parent),
            functional_definitions=all_functional_definitions,
        )

    def export_yaml(
        self,
        path: str,
        source: Union[SectionLattice, MachineLayout],
        position_mode: PositionMode = "s",
    ) -> None:
        """Export this importer's resolved lattice to a combined LAURA YAML file.

        Defaults to ``position_mode="s"`` (arc-length positioning).

        Parameters
        ----------
        path: str
            Directory in which to write ``summary.yaml``.
        source: SectionLattice | MachineLayout
            The section (from :meth:`create_section`) or layout (from
            :meth:`create_layout`) to export.
        position_mode: "global" | "s" | "reference"
            Position representation forwarded to
            :func:`~laura.Exporters.YAML.export_machine_combined_file`; see
            there for the meaning of each mode.
        """
        export_machine_combined_file(path, source, position_mode=position_mode)
