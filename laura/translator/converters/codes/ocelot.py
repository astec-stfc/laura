from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, Literal, Optional, Union
from scipy.spatial.transform import Rotation
import laura.models.element as LAURA_elements
from laura.models.elementList import SectionLattice, MachineLayout, ElementList
from . import magnetic_orders
from .. import keyword_conversion_rules_ocelot as keyword_conversion_rules
from ...utils.functions import introspect_model_defaults
from ....Exporters.YAML import export_machine_combined_file, PositionMode
from warnings import warn


def _switch_dict(type_rules: Dict[str, type]) -> Dict[str, str]:
    """Reverse Ocelot's many-to-one type map without ambiguous winners."""
    switch = {
        native_type.__name__.lower(): laura_type
        for laura_type, native_type in type_rules.items()
        if native_type.__name__.lower() != "drift"
    }
    switch.update(
        {
            "aperture": "Aperture",
            "hcor": "Horizontal_Corrector",
            "marker": "Marker",
            "monitor": "Monitor",
            "undulator": "Wiggler",
            "vcor": "Vertical_Corrector",
        }
    )
    return switch


class OcelotLatticeImporter(BaseModel):

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    name: str = "Lattice"

    machine_area: str = "Lattice"

    magnetic_lattice: Any
    """Ocelot ``MagneticLattice`` instance to import."""

    position_mode: Literal["s", "cartesian"] = "s"
    """How element positions are resolved from the Ocelot lattice:

    ``"s"`` (default): each element is given the cumulative arc-length
    (``physical.s``, ``s_point="end"``) obtained by summing ``elem.l`` in
    sequence order. LAURA integrates the design orbit itself (see
    :meth:`~laura.models.elementList.SectionLattice._resolve_s_coordinates`)
    to produce global ``middle``/rotation.

    ``"cartesian"``: the legacy behaviour -- global ``middle``/rotation are
    computed directly by :meth:`lattice_to_cartesian_with_rotation`.
    """

    laura_elements: Dict = {}
    """Dictionary containing converted element objects"""

    def _default_name(self) -> str:
        return self.name

    def magnetic_lattice_to_elements(self):
        return self.lattice_to_cartesian_with_rotation(self.magnetic_lattice.sequence)

    def create_element_dictionary(self):
        return self.create_laura_element_dictionary()

    def create_laura_element_dictionary(self):
        from ...conversion_rules.codes.ocelot_conversion import (
            ocelot_conversion_rules,
        )

        self.laura_elements = {}
        switch_dict = _switch_dict(ocelot_conversion_rules)

        sequence = list(self.magnetic_lattice.sequence)
        cartesian = (
            self.magnetic_lattice_to_elements()
            if self.position_mode == "cartesian"
            else {}
        )

        cumulative_s = 0.0
        for elem in sequence:
            length = float(getattr(elem, "l", 0.0))

            if self.position_mode == "s":
                cumulative_s += length
                phys_common = {"s": cumulative_s, "s_point": "end", "length": length}
            else:
                pos_and_rot = cartesian.get(elem)
                if pos_and_rot is None:
                    continue
                pos = pos_and_rot[0][::-1]
                rot = [
                    float(pos_and_rot[1][0]),
                    float(pos_and_rot[1][2]),
                    float(pos_and_rot[1][1]),
                ]
                phys_common = {"position": pos, "global_rotation": rot, "length": length}

            typeconv = type(elem).__name__.lower()
            if typeconv == "drift":
                continue
            sftype = switch_dict.get(typeconv)
            if not sftype:
                warn(
                    f"Could not parse Ocelot element type {type(elem)} for "
                    f"{elem.id!r}; skipping."
                )
                continue
            newobj = {
                "name": elem.id,
                "hardware_type": sftype,
                "machine_area": self.machine_area,
                "physical": dict(phys_common),
            }
            try:
                merged = (
                    keyword_conversion_rules[sftype.lower()]
                    | keyword_conversion_rules["general"]
                )
            except KeyError:
                merged = keyword_conversion_rules["general"]
            for sfparam, oceparam in merged.items():
                if hasattr(elem, oceparam):
                    newobj.update({sfparam: getattr(elem, oceparam)})
            try:
                if "Cavity" not in sftype:
                    classname = (
                        sftype if hasattr(LAURA_elements, sftype) else sftype.capitalize()
                    )
                else:
                    classname = sftype
                model_fields = introspect_model_defaults(
                    getattr(LAURA_elements, classname), resolve_optional=True
                )
                newobj["hardware_type"] = classname
            except AttributeError:
                warn(f"Ocelot type {sftype!r} for {elem.id!r} not recognized; skipping.")
                continue
            for subk in ["magnetic", "cavity", "simulation", "diagnostic", "physical"]:
                if subk in model_fields and subk not in newobj:
                    newobj.update({subk: {}})
            for oceparam, value in elem.element.__dict__.items():
                oceparam = oceparam.lower()
                kwele = {y: x for x, y in merged.items()}
                for subk in model_fields:
                    if isinstance(model_fields[subk], dict):
                        if (
                            oceparam in ["k1", "k2", "k3", "angle"]
                            and newobj["hardware_type"] in magnetic_orders
                        ):
                            if "magnetic" not in newobj:
                                newobj.update({"magnetic": {}})
                            order = magnetic_orders[newobj["hardware_type"]]
                            try:
                                kl_value = (
                                    getattr(elem.element, f"k{order}") * length
                                )
                            except AttributeError:
                                kl_value = elem.element.angle
                            newobj["magnetic"].setdefault("multipoles", {})[
                                f"K{order}L"
                            ] = {"normal": kl_value, "order": order}
                        if oceparam in model_fields[subk] and hasattr(elem, oceparam):
                            newobj[subk].update({oceparam: getattr(elem, oceparam)})
                        elif oceparam in kwele:
                            if kwele[oceparam] in model_fields[subk]:
                                if (
                                    not isinstance(
                                        model_fields[subk][kwele[oceparam]], str
                                    )
                                    or model_fields[subk][kwele[oceparam]]
                                ):
                                    try:
                                        if (
                                            oceparam == "v"
                                            and "Cavity" in newobj["hardware_type"]
                                        ):
                                            newobj[subk].update(
                                                {
                                                    kwele[oceparam]: getattr(
                                                        elem, oceparam
                                                    )
                                                    * 1e9
                                                }
                                            )
                                        else:
                                            newobj[subk].update(
                                                {
                                                    kwele[oceparam]: getattr(
                                                        elem, oceparam
                                                    )
                                                }
                                            )
                                    except KeyError:
                                        pass
                                    except AttributeError:
                                        pass
            self.laura_elements.update(
                {elem.id: getattr(LAURA_elements, newobj["hardware_type"])(**newobj)}
            )
        return self.laura_elements

    def create_section(self, section: Optional[Dict] = None) -> Dict[str, SectionLattice]:
        if not self.laura_elements:
            self.create_laura_element_dictionary()
        if section is None:
            names = list(self.laura_elements)
            if not names:
                raise ValueError("No elements were imported; cannot build a section.")
            section = {self._default_name(): [names[0], names[-1]]}
        if len(section) != 1:
            raise ValueError("A section definition must contain exactly one section.")
        secname, bounds = next(iter(section.items()))
        if len(bounds) != 2:
            raise ValueError("A section definition must contain first and last elements.")
        names = list(self.laura_elements)
        try:
            first, last = names.index(bounds[0]), names.index(bounds[1])
        except ValueError as exc:
            missing = bounds[0] if bounds[0] not in self.laura_elements else bounds[1]
            raise KeyError(f"element {missing} not found in lattice") from exc
        if first > last:
            raise ValueError("The first section element must precede the last.")
        elems = dict(list(self.laura_elements.items())[first : last + 1])
        seclat = SectionLattice(
            order=list(elems), elements=ElementList(elements=elems), name=secname
        )
        seclat.resolve_positions(self.laura_elements)
        return {secname: seclat}

    def create_layout(
        self, name: Optional[str] = None, sections: Optional[Dict] = None
    ) -> MachineLayout:
        if sections is None:
            layout_sections = self.create_section()
        else:
            layout_sections = {}
            for secname, bounds in sections.items():
                layout_sections.update(self.create_section({secname: bounds}))
        return MachineLayout(
            name=name or self._default_name(), sections=layout_sections
        )

    def export_yaml(
        self,
        path: str,
        source: Union[SectionLattice, MachineLayout],
        position_mode: PositionMode = "s",
    ) -> None:
        export_machine_combined_file(path, source, position_mode=position_mode)

    @staticmethod
    def lattice_to_cartesian_with_rotation(elements) -> Dict:
        """
        Compute Cartesian coordinates [x, y, z] of accelerator lattice elements
        and the global rotation (Euler angles) at the MIDPOINT of each element.
        """

        x, y, z = 0.0, 0.0, 0.0
        theta_h = 0.0
        theta_v = 0.0
        elems, positions, rotations = [], [], []
        cumulative_R = np.eye(3)

        for elem in elements:
            if (
                "bend" not in str(type(elem)).lower()
                or abs(getattr(elem, "angle", 0.0)) < 1e-9
            ):
                # --- Drift ---
                L = elem.l
                # Direction vector
                dx = L * np.cos(theta_v) * np.cos(theta_h)
                dy = L * np.sin(theta_v)
                dz = L * np.cos(theta_v) * np.sin(theta_h)

                # Midpoint is halfway along the segment
                mid_x = x + dx / 2
                mid_y = y + dy / 2
                mid_z = z + dz / 2

                # Store midpoint
                euler_angles = Rotation.from_matrix(cumulative_R).as_euler(
                    "zyx", degrees=False
                )
                elems.append(elem)
                positions.append(np.array([mid_x, mid_y, mid_z]))
                rotations.append(euler_angles)

                # Move to exit for next element
                x += dx
                y += dy
                z += dz

            else:
                # --- Dipole Bend ---
                L, phi, tilt = elem.l, elem.angle, elem.tilt

                if np.isclose(tilt, 0):  # Horizontal bend (x-z plane)
                    R_bend = Rotation.from_euler("y", phi).as_matrix()
                    R_half = Rotation.from_euler("y", phi / 2).as_matrix()

                    R_geom = L / phi  # bending radius

                    # Center of curvature
                    cx = x - R_geom * np.sin(theta_h)
                    cz = z + R_geom * np.cos(theta_h)

                    # Midpoint (half of bend angle)
                    theta_mid = theta_h + phi / 2
                    mid_x = cx + R_geom * np.sin(theta_mid)
                    mid_y = y
                    mid_z = cz - R_geom * np.cos(theta_mid)

                    # Rotation halfway through bend
                    R_mid = cumulative_R @ R_half

                    euler_angles = Rotation.from_matrix(R_mid).as_euler(
                        "zyx", degrees=False
                    )
                    elems.append(elem)
                    positions.append(np.array([mid_x, mid_y, mid_z]))
                    rotations.append(euler_angles)

                    # Update to exit of element
                    theta_h += phi
                    x = cx + R_geom * np.sin(theta_h)
                    z = cz - R_geom * np.cos(theta_h)
                    cumulative_R = cumulative_R @ R_bend

                elif np.isclose(tilt, np.pi / 2):  # Vertical bend (x-y plane)
                    R_bend = Rotation.from_euler("x", -phi).as_matrix()
                    R_half = Rotation.from_euler("x", -phi / 2).as_matrix()
                    R_geom = L / phi

                    cy = y - R_geom * np.cos(theta_v)

                    # Midpoint
                    theta_mid = theta_v + phi / 2
                    mid_y = cy + R_geom * np.cos(theta_mid)
                    mid_x = x
                    mid_z = z
                    R_mid = cumulative_R @ R_half

                    euler_angles = Rotation.from_matrix(R_mid).as_euler(
                        "zyx", degrees=False
                    )
                    elems.append(elem)
                    positions.append(np.array([mid_x, mid_y, mid_z]))
                    rotations.append(euler_angles)

                    # Exit of element
                    theta_v += phi
                    y = cy + R_geom * np.cos(theta_v)
                    cumulative_R = cumulative_R @ R_bend

                else:
                    raise ValueError(f"Unrecognized tilt angle {tilt} for {elem.id}")

        positions_and_rotations = [
            (p, r) for p, r in zip(np.array(positions), np.array(rotations))
        ]
        return {e: pr for e, pr in zip(elems, positions_and_rotations)}
