import os
import re
import subprocess
import tempfile
from pathlib import Path
import numpy as np
from pydantic import BaseModel, PrivateAttr, model_validator
from typing import Dict, Literal, Optional, Union
from ...utils.elegant import SDDSFile
import laura.models.element as LAURA_elements
from laura.models.elementList import SectionLattice, MachineLayout, ElementList
from ...utils.elegant.sdds_classes_APS import SDDS_Floor, SDDS_Params
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
        return os.path.splitext(os.path.basename(self.params_file or self.source_file))[0]

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
                if any(definition in value.split() for definition in self.functional_definitions)
            }
            if expressions:
                self._source_expressions[element.lower()] = expressions
        line_bodies = dict(
            re.findall(
                r"(?im)^\s*([^\s:]+)\s*:\s*line\s*=\s*\(([^)]*)\)", text
            )
        )
        beamlines = list(line_bodies)
        if self.beamline:
            matches = [name for name in beamlines if name.lower() == self.beamline.lower()]
            if not matches:
                raise KeyError(f"ELEGANT beamline {self.beamline!r} was not found.")
            beamlines = matches
        else:
            referenced = {
                re.sub(r"^(?:\d+\*)?-?", "", member.strip()).lower()
                for body in line_bodies.values()
                for member in body.split(",")
            }
            roots = [name for name in beamlines if name.lower() not in referenced]
            beamlines = roots or beamlines
        if len(beamlines) == 1:
            members = [
                re.sub(r"^(?:\d+\*)?-?", "", member.strip())
                for member in line_bodies[beamlines[0]].split(",")
            ]
            lookup = {name.lower(): name for name in line_bodies}
            if members and all(member.lower() in lookup for member in members):
                self.lattice_name = beamlines[0]
                beamlines = list(dict.fromkeys(lookup[member.lower()] for member in members))
        if not beamlines:
            raise ValueError("No ELEGANT LINE definitions were found in source_file.")

        self._source_tmp = tempfile.TemporaryDirectory(prefix="laura-elegant-")
        directory = Path(self._source_tmp.name)
        for name in beamlines:
            root = directory / name
            command = directory / f"{name}.ele"
            command.write_text(
                "&run_setup\n"
                f' lattice = "{Path(self.source_file).resolve()}",\n'
                f' use_beamline = "{name}",\n'
                f' rootname = "{root}",\n'
                " p_central_mev = 100,\n"
                f' parameters = "{root}.param",\n'
                "&end\n"
                "&run_control\n n_steps = 1,\n&end\n"
                "&bunched_beam\n n_particles_per_bunch = 1,\n&end\n"
                "&floor_coordinates\n"
                f' filename = "{root}.flr",\n'
                "&end\n"
                "&track\n&end\n"
            )
            try:
                subprocess.run(
                    ["elegant", str(command)],
                    cwd=directory,
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
            self._source_outputs[name] = (f"{root}.param", f"{root}.flr")

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
        self.elegant_data, filenames = params.create_element_dictionary()
        for name, data in self.elegant_data.items():
            expressions = self._source_expressions.get(name.split(".", 1)[0].lower(), {})
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
            source_to_laura = {source.lower(): target for target, source in rules.items()}
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
                for nested in data.values():
                    if isinstance(nested, dict) and target in nested:
                        nested[target] = expression
        return self.elegant_data, filenames

    def update_floor_coordinates(self):
        flr = SDDS_Floor()
        flr.import_sdds_floor_file(self.floor_file)
        self.floor_data = flr.data
        self.lattice_name = flr.lattice_name

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
                if "drift" not in vtype.lower():
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
                                    "middle": {p: c for p, c in zip(["x", "y", "z"], centre.tolist())},
                                    "global_rotation": rotation,
                                    "length": elem_length,
                                }
                            )
                        else:
                            v["physical"] = {
                                "middle": {p: c for p, c in zip(["x", "y", "z"], centre.tolist())},
                                "global_rotation": rotation,
                                "length": elem_length,
                            }

                        # Add physical_angle for bent elements
                        if abs(physical_angle) > 1e-9:
                            v["physical"]["physical_angle"] = physical_angle
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
        if self.source_file and sections is None:
            self._prepare_source()
            layout_sections = {
                beamline: self._source_section(beamline)
                for beamline in self._source_outputs
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

    def export_yaml(
        self,
        path: str,
        source: Union[SectionLattice, MachineLayout],
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
        source: SectionLattice | MachineLayout
            The section (from :meth:`create_section`) or layout (from
            :meth:`create_layout`) to export.
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
                    v["cavity"]["phase"] = 90 - value
        return v

    @staticmethod
    def import_sdds_params_file(filename: str, page: int = 0) -> list:
        elegantObject = SDDSFile(index=1)
        elegantObject.read_file(filename, page=page)
        elegantData = elegantObject.data
        return elegantData
