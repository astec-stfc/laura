import os
import re
import subprocess
import tempfile
from pathlib import Path
from warnings import warn
import numpy as np
from pydantic import BaseModel, PrivateAttr, model_validator
from typing import Dict, Literal, Optional, Union
from ...utils.elegant import SDDSFile
import laura.models.element as LAURA_elements
from laura.models.elementList import (
    SectionLattice,
    MachineLayout,
    MachineModel,
    ElementList,
)
from ...utils.elegant.sdds_classes_APS import SDDS_Floor, SDDS_Params
from ...utils.fields import field
from ....Exporters.YAML import export_machine_combined_file, PositionMode
from .. import keyword_conversion_rules_elegant


class ElegantLatticeImporter(BaseModel):

    params_file: Optional[str] = None
    """Name of ELEGANT parameters file"""

    floor_file: Optional[str] = None
    """Name of ELEGANT floor file"""

    source_file: Optional[str] = None
    """Original ELEGANT lattice file, used instead of SDDS output files."""

    beamline: Optional[str] = None
    """Optional beamline selector for source import."""

    position_mode: Literal["s", "floor"] = "s"
    """How element positions are resolved from the ELEGANT floor file:

    ``"s"`` (default): each element is given its ELEGANT-computed cumulative
    arc-length ``s`` (``physical.s``, ``s_point="end"``) and LAURA integrates
    the design orbit itself (see
    :meth:`~laura.models.elementList.SectionLattice._resolve_s_coordinates`)
    to produce global ``middle``/rotation.

    ``"floor"``: the legacy behaviour -- each element's global ``middle``
    and rotation are taken directly from the floor file, bypassing LAURA's
    trajectory integration entirely.
    """

    elegant_data: Dict = {}
    """Dictionary containing data about the ELEGANT lattice"""

    floor_data: Dict = {}
    """Dictionary containing floor positions for the ELEGANT lattice"""

    elements: Dict = {}
    """Dictionary containing converted
    :class:`~laura.models.element.Element` objects"""

    functional_definitions: Dict[str, Union[int, float]] = {}

    lattice_name: Optional[str] = None
    """Best-effort lattice name parsed from the floor file's own ELEGANT
    description (``&floor_coordinates``'s ``"...lattice: Linac.lte"``);
    ``None`` until :meth:`update_floor_coordinates` has run, or if the
    description didn't match that format. Used as the default section/layout
    name in :meth:`create_section`/:meth:`create_layout` when not given
    explicitly."""

    _source_outputs: Dict[str, tuple] = PrivateAttr(default_factory=dict)
    _source_tmp: object = PrivateAttr(default=None)
    _source_expressions: Dict[str, Dict[str, str]] = PrivateAttr(default_factory=dict)
    _source_lines: Dict[str, list[str]] = PrivateAttr(default_factory=dict)
    _source_roots: list[str] = PrivateAttr(default_factory=list)
    _source_sections: list[str] = PrivateAttr(default_factory=list)

    @staticmethod
    def _saved_lattice_params(filename: str) -> Dict[str, Dict[str, list]]:
        """Read Elegant's evaluated ``save_lattice, output_seq=2`` output."""
        text = Path(filename).read_text().replace("&\n", " ")
        lines = dict(
            (name1 or name2, body)
            for name1, name2, body in re.findall(
                r'(?im)^\s*(?:"([^"]+)"|([^\s:]+))\s*:\s*line\s*=\s*\(([^)]*)\)',
                text,
            )
        )
        definitions = {}
        for name1, name2, element_type, parameters in re.findall(
            r'(?im)^\s*(?:"([^"]+)"|([^\s:]+))\s*:\s*([^,\s]+)\s*(?:,(.*))?$',
            text,
        ):
            name = name1 or name2
            if element_type.lower() == "line":
                continue
            parsed = re.findall(r'(\w+)\s*=\s*("[^"]*"|[^,]+)', parameters or "")
            values, strings = [], []
            for _, value in parsed:
                if value.startswith('"'):
                    values.append(0.0)
                    strings.append(value[1:-1])
                else:
                    try:
                        values.append(float(value))
                        strings.append("")
                    except ValueError:
                        values.append(0.0)
                        strings.append(value.strip())
            definitions[name.lower()] = {
                "ElementType": [element_type],
                "ElementParameter": [parameter for parameter, _ in parsed],
                "ParameterValue": values,
                "ParameterValueString": strings,
            }

        use = re.search(r'(?im)^\s*use\s*,\s*"?([^"\s]+)"?', text)
        root = use.group(1) if use else next(reversed(lines))
        lookup = {name.lower(): (name, body) for name, body in lines.items()}

        def expand(name: str) -> list[str]:
            found = lookup.get(name.lower())
            if not found:
                return [name]
            return [
                element
                for member in found[1].split(",")
                for element in expand(member.strip().strip('"'))
            ]

        sequence = expand(root)
        totals = {
            name.lower(): sum(item.lower() == name.lower() for item in sequence)
            for name in sequence
        }
        occurrences = {}
        result = {}
        for name in sequence:
            key = name.lower()
            occurrences[key] = occurrences.get(key, 0) + 1
            output_name = f"{name}.{occurrences[key]}" if totals[key] > 1 else name
            if key in definitions:
                result[output_name] = definitions[key]
        return result

    @model_validator(mode="after")
    def _check_input(self):
        outputs = self.params_file is not None and self.floor_file is not None
        if outputs == (self.source_file is not None):
            raise ValueError(
                "Give either source_file or both params_file and floor_file."
            )
        return self

    def _default_name(self) -> str:
        """Best-effort name for an auto-derived section/layout.

        Prefers the lattice name parsed from the floor file's description
        (e.g. ``"Linac"``); falls back to the params file's basename, which
        is always available, when that parse didn't match.
        """
        if self.lattice_name:
            return self.lattice_name
        return os.path.splitext(os.path.basename(self.params_file or self.source_file))[
            0
        ]

    def _prepare_source(self) -> None:
        if self._source_outputs:
            return
        text = Path(self.source_file).read_text()
        text = re.sub(r"!.*", "", text).replace("&\n", " ")
        self.functional_definitions = {
            name: float(value)
            for value, name in re.findall(
                r"(?im)^\s*%\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)\s+sto\s+(\S+)",
                text,
            )
        }
        for element, parameters in re.findall(
            r"(?im)^\s*([^\s:%]+)\s*:\s*[^,\n]+,(.*)$", text
        ):
            expressions = {
                name.lower(): value
                for name, value in re.findall(r'(\w+)\s*=\s*"([^"]+)"', parameters)
                if any(
                    definition in value.split()
                    for definition in self.functional_definitions
                )
            }
            if expressions:
                self._source_expressions[element.lower()] = expressions
        line_bodies = dict(
            re.findall(r"(?im)^\s*([^\s:]+)\s*:\s*line\s*=\s*\(([^)]*)\)", text)
        )
        self._source_lines = {
            name: [member.strip() for member in body.split(",") if member.strip()]
            for name, body in line_bodies.items()
        }
        beamlines = list(line_bodies)
        if self.beamline:
            matches = [
                name for name in beamlines if name.lower() == self.beamline.lower()
            ]
            if not matches:
                raise KeyError(f"ELEGANT beamline {self.beamline!r} was not found.")
            beamlines = matches
        else:
            referenced = {
                re.sub(r"^(?:\d+\*)?-?", "", member.strip())
                .strip()
                .strip('"')
                .lower()
                for body in line_bodies.values()
                for member in body.split(",")
            }
            roots = [name for name in beamlines if name.lower() not in referenced]
            beamlines = roots or beamlines
        self._source_roots = beamlines.copy()
        if len(beamlines) == 1:
            members = [
                re.sub(r"^(?:\d+\*)?-?", "", member.strip()).strip().strip('"')
                for member in line_bodies[beamlines[0]].split(",")
            ]
            lookup = {name.lower(): name for name in line_bodies}
            if members and all(member.lower() in lookup for member in members):
                self.lattice_name = beamlines[0]
                beamlines = list(
                    dict.fromkeys(lookup[member.lower()] for member in members)
                )
        self._source_sections = beamlines
        if not beamlines:
            raise ValueError("No ELEGANT LINE definitions were found in source_file.")

        self._source_tmp = tempfile.TemporaryDirectory(prefix="laura-elegant-")
        directory = Path(self._source_tmp.name)
        for name in dict.fromkeys(self._source_roots + self._source_sections):
            root = directory / name
            command = directory / f"{name}.ele"
            saved = directory / f"{name}.lte"
            command.write_text(
                "&run_setup\n"
                f' lattice = "{Path(self.source_file).resolve()}",\n'
                f' use_beamline = "{name}",\n'
                f' rootname = "{root}",\n'
                " p_central_mev = 100,\n"
                "&end\n"
                "&floor_coordinates\n"
                f' filename = "{root}.flr",\n'
                "&end\n"
                "&save_lattice\n"
                f' filename = "{saved}",\n'
                " output_seq = 2,\n"
                " suppress_defaults = 0,\n"
                "&end\n"
            )
            try:
                subprocess.run(
                    ["elegant", str(command)],
                    cwd=Path(self.source_file).resolve().parent,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except FileNotFoundError as exc:
                raise ImportError(
                    "The elegant executable is required for ELEGANT source import."
                ) from exc
            except subprocess.CalledProcessError as exc:
                raise ValueError(
                    f"ELEGANT could not load beamline {name!r}: {exc.stderr or exc.stdout}"
                ) from exc
            self._source_outputs[name] = (str(saved), f"{root}.flr")

    def _select_source_output(self, name: str) -> None:
        self.params_file, self.floor_file = self._source_outputs[name]
        self.elegant_data = {}
        self.floor_data = {}
        self.elements = {}

    def _source_section(self, name: str) -> SectionLattice:
        self._select_source_output(name)
        self.create_laura_element_dictionary()
        bounds = [next(iter(self.elements)), next(reversed(self.elements))]
        return next(iter(self.create_section({name: bounds}).values()))

    def create_element_dictionary(self):
        if self.source_file and not self.params_file:
            self._prepare_source()
            self._select_source_output(next(iter(self._source_outputs)))
        params = SDDS_Params(self.params_file)
        if self.source_file:
            params.elegantParams = self._saved_lattice_params(self.params_file)
        self.elegant_data, filenames = params.create_element_dictionary()
        for name, data in self.elegant_data.items():
            source_name = name.lower()
            expressions = self._source_expressions.get(source_name, {})
            if not expressions and source_name.rpartition(".")[2].isdigit():
                expressions = self._source_expressions.get(
                    source_name.rpartition(".")[0], {}
                )
            length = data.get("magnetic", {}).get(
                "length", data.get("physical", {}).get("length", data.get("l", 0.0))
            )
            for parameter in ("k0", "k1", "k2", "k3", "angle"):
                expression = expressions.get(parameter)
                if expression and self._rpn_symbol(
                    expression, 0.0 if parameter == "angle" else length
                ):
                    data[parameter] = expressions[parameter]
            rules = keyword_conversion_rules_elegant["general"]
            element_type = data["hardware_type"].lower()
            if element_type in keyword_conversion_rules_elegant:
                rules = keyword_conversion_rules_elegant[element_type] | rules
            source_to_laura = {
                source.lower(): target for target, source in rules.items()
            }
            for parameter, expression in expressions.items():
                tokens = expression.strip('"').split()
                supported = self._rpn_symbol(expression) or (
                    len(tokens) == 3
                    and tokens[0] == "90"
                    and tokens[2] == "-"
                    and self._rpn_symbol(tokens[1])
                )
                if not supported:
                    continue
                target = source_to_laura.get(parameter, parameter)
                if target not in {"phase", "field_amplitude"}:
                    continue
                for nested in data.values():
                    if isinstance(nested, dict) and target in nested:
                        nested[target] = expression
            wakefiles = filenames.get(name, {})
            wakefile = wakefiles.get("zwakefile") or wakefiles.get("wakefile")
            if wakefile and data["hardware_type"] == "RFCavity":
                wakepath = Path(wakefile)
                if not wakepath.is_absolute():
                    imported_from = self.source_file or self.params_file
                    wakepath = Path(imported_from).resolve().parent / wakepath
                simulation = data.setdefault("simulation", {})
                simulation["wakefield_definition"] = field(
                    filename=str(wakepath.resolve()),
                    field_type="LongitudinalWake",
                    t_column=simulation.get("t_column"),
                    wz_column=simulation.get("wz_column"),
                )
                for raw_name in ("wakefile", "zwakefile", "trwakefile"):
                    simulation.pop(raw_name, None)
        return self.elegant_data, filenames

    def update_floor_coordinates(self):
        flr = SDDS_Floor()
        flr.import_sdds_floor_file(self.floor_file)
        self.floor_data = flr.data
        self.lattice_name = (
            self.beamline if self.source_file and self.beamline else flr.lattice_name
        )

        i = 0
        for k, v in self.floor_data.items():
            if i == 0:
                pass
            else:
                prevind = list(self.floor_data.keys()).index(k) - 1
                thisind = list(self.floor_data.keys()).index(k)
                self.floor_data[k].update(
                    {
                        "start": list(self.floor_data.values())[prevind]["end"],
                        "start_rotation": list(self.floor_data.values())[prevind][
                            "end_rotation"
                        ],
                        "end": list(self.floor_data.values())[thisind]["end"],
                        "end_rotation": list(self.floor_data.values())[thisind][
                            "end_rotation"
                        ],
                    }
                )
            i += 1

    def create_laura_element_dictionary(self):
        if not self.elegant_data:
            self.create_element_dictionary()
        if not self.floor_data:
            self.update_floor_coordinates()
        self.elements = {}

        def calculate_middle_from_start(start_pos, end_pos):
            """
            Calculate middle position as midpoint between start and end positions.
            """
            start = np.array(start_pos)
            end = np.array(end_pos)
            return (start + end) / 2

        for k, v in self.elegant_data.items():
            if k in self.floor_data:
                vtype = v["hardware_type"]
                if vtype:
                    elem_length = v.get("l", 0.0)

                    if self.position_mode == "s":
                        v = self._convert_k_to_kl(v)
                        v = self._convert_ele_phase_to_phase(v)

                        if "physical" in v:
                            v["physical"].update(
                                {
                                    "s": self.floor_data[k]["s"],
                                    "s_point": "end",
                                    "length": elem_length,
                                }
                            )
                        else:
                            v["physical"] = {
                                "s": self.floor_data[k]["s"],
                                "s_point": "end",
                                "length": elem_length,
                            }
                    else:
                        if "l" in v and v["l"] > 0:
                            # Get physical angle for bent elements
                            physical_angle = 0.0
                            if v["hardware_type"].lower() == "dipole" and "angle" in v:
                                physical_angle = v["angle"]

                            # Calculate middle position properly
                            centre = calculate_middle_from_start(
                                start_pos=self.floor_data[k]["start"],
                                end_pos=self.floor_data[k]["end"],
                            )
                        else:
                            # Zero length element - middle is same as start
                            centre = np.array(self.floor_data[k]["start"])
                            physical_angle = 0.0

                        v = self._convert_k_to_kl(v)
                        v = self._convert_ele_phase_to_phase(v)

                        rotation = self.floor_data[k]["end_rotation"]
                        if "physical" in v:
                            v["physical"].update(
                                {
                                    "middle": {
                                        p: c
                                        for p, c in zip(
                                            ["x", "y", "z"], centre.tolist()
                                        )
                                    },
                                    "global_rotation": rotation,
                                    "length": elem_length,
                                }
                            )
                        else:
                            v["physical"] = {
                                "middle": {
                                    p: c
                                    for p, c in zip(["x", "y", "z"], centre.tolist())
                                },
                                "global_rotation": rotation,
                                "length": elem_length,
                            }

                        # Add physical_angle for bent elements
                        if abs(physical_angle) > 1e-9:
                            v["physical"]["physical_angle"] = physical_angle
                    self.elements.update({k: getattr(LAURA_elements, vtype)(**v)})
        return self.elements

    def create_section(
        self, section: Optional[Dict] = None
    ) -> Dict[str, SectionLattice]:
        """Build a named :class:`SectionLattice` from imported elements.

        Parameters
        ----------
        section: dict, optional
            ``{section_name: [first_element_name, last_element_name]}``. When
            omitted, a single section spanning the *entire* imported lattice
            (its first through last element, in beamline order) is derived
            automatically -- the natural default, since ELEGANT's own
            params/floor files describe exactly one flat, ordered beamline
            with no further native sub-division. The name defaults to
            :meth:`_default_name`.
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
            raise ValueError(
                "A section definition must contain first and last elements."
            )
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
            order=list(elems),
            elements=ElementList(elements=elems),
            name=secname,
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
        if self.source_file and sections is None:
            self._prepare_source()
            layout_sections = {
                beamline: self._source_section(beamline)
                for beamline in self._source_sections
            }
        elif sections is None:
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

    def _source_section_blocks(
        self, root: str, min_section_length: int
    ) -> list[tuple[str, int]]:
        """Return section names and expanded element counts for one root line."""
        lookup = {name.lower(): name for name in self._source_lines}

        def member_name(member: str) -> tuple[str, int]:
            value = member.strip()
            match = re.match(r"^(\d+)\s*\*\s*(.*)$", value)
            repeats, value = (int(match.group(1)), match.group(2)) if match else (1, value)
            return value.lstrip("-").strip().strip('"'), repeats

        def expanded_length(name: str, stack: tuple[str, ...] = ()) -> int:
            key = lookup.get(name.lower())
            if key is None:
                return 1
            if key.lower() in stack:
                raise ValueError(f"Recursive ELEGANT LINE definition involving {key!r}.")
            return sum(
                repeats * expanded_length(child, stack + (key.lower(),))
                for child, repeats in map(member_name, self._source_lines[key])
            )

        raw: list[tuple[str | None, int]] = []
        for member in self._source_lines[root]:
            child, repeats = member_name(member)
            line_name = lookup.get(child.lower())
            for _ in range(repeats):
                if line_name and expanded_length(line_name) >= min_section_length:
                    raw.append((line_name, expanded_length(line_name)))
                else:
                    raw.append((None, expanded_length(child)))

        if not any(name for name, _ in raw):
            return [(root, sum(count for _, count in raw))]

        blocks: list[tuple[str, int]] = []
        leading = 0
        occurrences: dict[str, int] = {}
        for name, count in raw:
            if name is None:
                if blocks:
                    previous, previous_count = blocks[-1]
                    blocks[-1] = (previous, previous_count + count)
                else:
                    leading += count
                continue
            occurrences[name] = occurrences.get(name, 0) + 1
            suffix = f"_{occurrences[name]}" if occurrences[name] > 1 else ""
            blocks.append((name + suffix, count + leading))
            leading = 0
        return blocks

    def create_machine_model(self, min_section_length: int = 5) -> MachineModel:
        """Build a complete model from all top-level ELEGANT ``LINE`` objects.

        Independent top-level lines become layouts. Nested lines whose expanded
        length is at least ``min_section_length`` become sections; shorter lines
        are folded into an adjacent section without dropping elements. If a
        layout has no qualifying nested line, the whole layout becomes one section.
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

        self._prepare_source()
        elements = {}
        section_definitions = {}
        layout_definitions = {}
        skipped_layouts = []

        for root in self._source_roots:
            full_section = self._source_section(root)
            if len(full_section.order) < min_section_length:
                skipped_layouts.append(root)
                continue
            blocks = self._source_section_blocks(root, min_section_length)
            if sum(count for _, count in blocks) != len(full_section.order):
                blocks = [(root, len(full_section.order))]

            layout_sections = []
            offset = 0
            for source_section_name, count in blocks:
                section_name = source_section_name
                if section_name in section_definitions:
                    section_name = f"{root}_{section_name}"
                names = []
                for element in full_section.elements.list()[offset : offset + count]:
                    element_name = element.name
                    elements.setdefault(element_name, element)
                    names.append(element_name)
                offset += count
                section_definitions[section_name] = names
                layout_sections.append(section_name)
            layout_definitions[root] = layout_sections

        if skipped_layouts:
            warn(
                "Skipped ELEGANT layouts shorter than min_section_length="
                f"{min_section_length}: {', '.join(skipped_layouts)}"
            )
        if not layout_definitions:
            raise ValueError(
                "No ELEGANT layouts meet min_section_length="
                f"{min_section_length}."
            )
        default_layout = next(iter(layout_definitions))
        return MachineModel(
            elements=elements,
            section={"sections": section_definitions},
            layout={
                "layouts": layout_definitions,
                "default_layout": default_layout,
            },
            master_lattice=str(Path(self.source_file).resolve().parent),
            functional_definitions=self.functional_definitions,
        )

    def export_yaml(
        self,
        path: str,
        source: Union[SectionLattice, MachineLayout, MachineModel],
        position_mode: PositionMode = "s",
    ) -> None:
        """Export this importer's resolved lattice to a combined LAURA YAML file.

        Defaults to ``position_mode="s"`` (arc-length positioning). Call
        :meth:`~laura.models.elementList.SectionLattice.resolve_positions` on
        ``source`` first so every element's ``s`` value is populated.

        Parameters
        ----------
        path: str
            Directory in which to write ``summary.yaml``.
        source: SectionLattice | MachineLayout | MachineModel
            The section, layout, or complete model to export.
        position_mode: "global" | "s" | "reference"
            Position representation forwarded to
            :func:`~laura.Exporters.YAML.export_machine_combined_file`; see
            there for the meaning of each mode.
        """
        export_machine_combined_file(path, source, position_mode=position_mode)

    def _rpn_symbol(self, value, length=0.0) -> str | None:
        if not isinstance(value, str):
            return None
        tokens = value.strip('"').split()
        for name in self.functional_definitions:
            if tokens == [name]:
                return name
            if length and len(tokens) == 3 and tokens[0] == name and tokens[2] == "/":
                try:
                    if np.isclose(float(tokens[1]), length):
                        return name
                except ValueError:
                    pass
        return None

    def _convert_k_to_kl(self, v) -> dict:
        multi = {}
        if "angle" in v:
            symbol = self._rpn_symbol(v["angle"])
            if symbol:
                v["k0"] = symbol
            else:
                v["k0"] = v["angle"] / float(v["magnetic"]["length"])
                v["physical"]["physical_angle"] = -v["angle"]
        for n in range(0, 9):
            if f"k{n}" in v and (
                "length" in v["magnetic"] or "length" in v["physical"]
            ):
                try:
                    length = float(v["magnetic"]["length"])
                except KeyError:
                    length = float(v["physical"]["length"])
                symbol = self._rpn_symbol(v[f"k{n}"], length)
                knl = symbol or float(v[f"k{n}"]) * length
                multi.update({f"K{n}L": {"order": n, "normal": knl}})
                del v[f"k{n}"]
        if "magnetic" in v:
            v["magnetic"].update({"multipoles": multi})
        return v

    def _convert_ele_phase_to_phase(self, v) -> dict:
        if "cavity" in v:
            if "phase" in v["cavity"]:
                value = v["cavity"]["phase"]
                tokens = value.strip('"').split() if isinstance(value, str) else []
                if len(tokens) == 3 and tokens[0] == "90" and tokens[2] == "-":
                    symbol = self._rpn_symbol(tokens[1])
                    v["cavity"]["phase"] = symbol or value
                else:
                    symbol = self._rpn_symbol(value)
                    if symbol:
                        converted = f"{symbol}_laura_phase"
                        self.functional_definitions[converted] = (
                            90 - self.functional_definitions[symbol]
                        )
                        v["cavity"]["phase"] = converted
                    else:
                        v["cavity"]["phase"] = 90 - value
        return v

    @staticmethod
    def import_sdds_params_file(filename: str, page: int = 0) -> list:
        elegantObject = SDDSFile(index=1)
        elegantObject.read_file(filename, page=page)
        elegantData = elegantObject.data
        return elegantData
