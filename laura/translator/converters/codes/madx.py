import os
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Literal, Optional, Union
from warnings import warn

import numpy as np
from pydantic import BaseModel, PrivateAttr, model_validator

import laura.models.element as LAURA_elements
from laura.models.elementList import SectionLattice, MachineLayout, ElementList
from ...utils.functions import introspect_model_defaults
from ...utils.madx.TFSFile import TFSFile
from .. import type_conversion_rules_Madx, keyword_conversion_rules_madx
from ....Exporters.YAML import export_machine_combined_file, PositionMode

_SILENTLY_SKIPPED_TYPES = ("drift",)

_RAW_KEYS = ("k0", "k1", "k2", "k3", "angle", "l", "kick", "hkick", "vkick", "ks")


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
    before running ``TWISS``).
    Provides both element parameters and -- via its own ``S`` column,
    MAD-X's cumulative arc-length at the *exit* of each element --
    ``position_mode="s"`` positioning."""

    source_file: Optional[str] = None
    """Original MAD-X input file, used instead of ``twiss_file``."""

    sequence: Optional[str] = None
    """Sequence to import from ``source_file``; defaults to its sole sequence."""

    survey_file: Optional[str] = None
    """Path to a MAD-X SURVEY TFS table. Only read for ``position_mode="floor"``."""

    position_mode: Literal["s", "floor"] = "s"
    """How element positions are resolved from MAD-X:

    ``"s"`` (default): each element is given cumulative
    arc-length ``s`` (``physical.s``, ``s_point="end"``).

    ``"floor"``: the legacy behaviour -- each element's global ``middle``
    and rotation are taken directly from :attr:`survey_file`, bypassing
    LAURA's trajectory integration entirely.
    """

    madx_data: Dict = {}
    """Dictionary containing data about the MAD-X lattice, keyed by element name."""

    floor_data: Dict = {}
    """Dictionary containing floor positions for the MAD-X lattice
    (``position_mode="floor"`` only)."""

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

    def _source_rows(self) -> list:
        try:
            from cpymad.madx import Madx
        except ImportError as exc:
            raise ImportError(
                "cpymad is required for MAD-X source import. Install with: "
                'pip install "laura-accelerator[madx]"'
            ) from exc

        madx = Madx(stdout=False)
        madx.call(self.source_file)
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
        self.lattice_name = sequence

        self.deferred_parameters = {}
        rows = []
        used = set()
        declared = set(
            re.findall(
                r"(?im)^\s*([A-Za-z_][\w.]*)\s*(?::=|=)",
                Path(self.source_file).read_text(),
            )
        )
        native_elements = list(madx.sequence[sequence].elements)
        totals = Counter(element.name for element in native_elements)
        seen = Counter()
        for element in native_elements:
            seen[element.name] += 1
            name = (
                f"{element.name}.{seen[element.name]}"
                if totals[element.name] > 1
                else element.name
            ).replace("$", "_")
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

    def create_element_dictionary(self) -> Dict:
        if self.source_file:
            rows = self._source_rows()
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

    def update_floor_coordinates(self):
        if not self.survey_file:
            raise ValueError("survey_file must be given for position_mode='floor'.")
        tfs = TFSFile()
        tfs.read_file(self.survey_file)
        self.floor_data = {}
        rows = tfs.rows()
        for i, row in enumerate(rows):
            name = str(row["name"])
            end = [row.get("x", 0.0), row.get("y", 0.0), row.get("z", 0.0)]
            end_rotation = [row.get("phi", 0.0), row.get("psi", 0.0), row.get("theta", 0.0)]
            if i == 0:
                start, start_rotation = end, end_rotation
            else:
                prev = rows[i - 1]
                start = [prev.get("x", 0.0), prev.get("y", 0.0), prev.get("z", 0.0)]
                start_rotation = [prev.get("phi", 0.0), prev.get("psi", 0.0), prev.get("theta", 0.0)]
            self.floor_data[name] = {
                "start": start,
                "start_rotation": start_rotation,
                "end": end,
                "end_rotation": end_rotation,
            }

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
        if self.position_mode == "floor" and not self.floor_data:
            self.update_floor_coordinates()
        self.elements = {}

        def calculate_middle_from_start(start_pos, end_pos):
            start = np.array(start_pos)
            end = np.array(end_pos)
            return (start + end) / 2

        for k, v in self.madx_data.items():
            vtype = v["hardware_type"]
            elem_length = v.get("l", 0.0)
            v = self._convert_raw_fields(v)

            if self.position_mode == "s":
                s_val = v.get("s", 0.0)
                if "physical" in v:
                    v["physical"].update({"s": s_val, "s_point": "end", "length": elem_length})
                else:
                    v["physical"] = {"s": s_val, "s_point": "end", "length": elem_length}
            else:
                floor = self.floor_data[k]
                if elem_length > 0:
                    centre = calculate_middle_from_start(floor["start"], floor["end"])
                else:
                    centre = np.array(floor["start"])
                rotation = floor["end_rotation"]
                middle = {p: c for p, c in zip(["x", "y", "z"], centre.tolist())}
                if "physical" in v:
                    v["physical"].update(
                        {"middle": middle, "global_rotation": rotation, "length": elem_length}
                    )
                else:
                    v["physical"] = {"middle": middle, "global_rotation": rotation, "length": elem_length}

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
