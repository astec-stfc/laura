import os
import numpy as np
from pydantic import BaseModel
from typing import Dict, Literal, Optional, Union
from ...utils.elegant import SDDSFile
import laura.models.element as LAURA_elements
from laura.models.elementList import SectionLattice, MachineLayout, ElementList
from ...utils.elegant.sdds_classes_APS import SDDS_Floor, SDDS_Params
from ....Exporters.YAML import export_machine_combined_file, PositionMode


class ElegantLatticeImporter(BaseModel):

    params_file: str
    """Name of ELEGANT parameters file"""

    floor_file: str
    """Name of ELEGANT floor file"""

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

    lattice_name: Optional[str] = None
    """Best-effort lattice name parsed from the floor file's own ELEGANT
    description (``&floor_coordinates``'s ``"...lattice: Linac.lte"``);
    ``None`` until :meth:`update_floor_coordinates` has run, or if the
    description didn't match that format. Used as the default section/layout
    name in :meth:`create_section`/:meth:`create_layout` when not given
    explicitly."""

    def _default_name(self) -> str:
        """Best-effort name for an auto-derived section/layout.

        Prefers the lattice name parsed from the floor file's description
        (e.g. ``"Linac"``); falls back to the params file's basename, which
        is always available, when that parse didn't match.
        """
        if self.lattice_name:
            return self.lattice_name
        return os.path.splitext(os.path.basename(self.params_file))[0]

    def create_element_dictionary(self):
        params = SDDS_Params(self.params_file)
        self.elegant_data, filenames = params.create_element_dictionary()
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
            order=list(elems), elements=ElementList(elements=elems), name=secname
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

    @staticmethod
    def _convert_k_to_kl(v) -> dict:
        multi = {}
        if "angle" in v:
            v["k0"] = v["angle"] / float(v["magnetic"]["length"])
            v["physical"]["physical_angle"] = -v["angle"]
        for n in range(0, 9):
            if f"k{n}" in v and (
                "length" in v["magnetic"] or "length" in v["physical"]
            ):
                try:
                    knl = float(v[f"k{n}"]) * float(v["magnetic"]["length"])
                except KeyError:
                    knl = float(v[f"k{n}"]) * float(v["physical"]["length"])
                multi.update({f"K{n}L": {"order": n, "normal": knl}})
                del v[f"k{n}"]
        if "magnetic" in v:
            v["magnetic"].update({"multipoles": multi})
        return v

    @staticmethod
    def _convert_ele_phase_to_phase(v) -> dict:
        if "cavity" in v:
            if "phase" in v["cavity"]:
                v["cavity"]["phase"] = 90 - v["cavity"]["phase"]
        return v

    @staticmethod
    def import_sdds_params_file(filename: str, page: int = 0) -> list:
        elegantObject = SDDSFile(index=1)
        elegantObject.read_file(filename, page=page)
        elegantData = elegantObject.data
        return elegantData
