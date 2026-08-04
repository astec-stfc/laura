from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict
from pydantic_core import PydanticUndefinedType
from typing import Any, Dict, List, TYPE_CHECKING
try:
    import xtrack as xt
    from xtrack.beam_elements.elements import _HasKnlKsl
    _XTRACK_AVAILABLE = True
except ImportError as _err:
    _XTRACK_AVAILABLE = False
    xt = None  # type: ignore[assignment]
    _HasKnlKsl = object  # type: ignore[misc, assignment]

if TYPE_CHECKING:
    import xtrack as xt  # type: ignore[no-redef]
    from xtrack.beam_elements.elements import _HasKnlKsl  # type: ignore[no-redef]
from laura.models.elementList import (
    SectionLattice,
    MachineLayout,
    ElementList,
)
from . import magnetic_orders
from .. import keyword_conversion_rules_xsuite as keyword_conversion_rules
from ...utils.functions import introspect_model_defaults
from ...conversion_rules.codes import xsuite_conversion
from warnings import warn

xsuite_unsupported = [
    "Laser",
    "Wakefield",
    "ActivePlasmaLens",
]

type_conversion_rules_xsuite_reversed = (
    xsuite_conversion.xsuite_conversion_rules_reverse
)


class XsuiteLatticeConverter(BaseModel):

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    name: str = "Lattice"

    machine_area: str = "Lattice"

    line: Any
    """Xsuite line"""

    elements: Dict = {}
    """Dictionary containing converted element objects"""

    sections: Dict = {}

    layouts: Dict = {}

    initial_position: List[float] = [0, 0, 0]

    initial_rotation: List[float] = [0, 0, 0]

    def rotation_matrix_from_survey(self, row):
        """Builds rotation matrix (local→global) from survey row."""
        R = np.array(
            [
                [row["ex"][0], row["ex"][1], row["ex"][2]],
                [row["ey"][0], row["ey"][1], row["ey"][2]],
                [row["ez"][0], row["ez"][1], row["ez"][2]],
            ]
        )
        return R

    def Ry(self, angle):
        """Rotation matrix about local y axis."""
        c, s = np.cos(angle), np.sin(angle)
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

    def rotation_about_axis(self, axis, angle):
        """
        Rodrigues rotation formula.
        axis must be unit vector (local coordinates).
        """
        axis = axis / np.linalg.norm(axis)
        c = np.cos(angle)
        s = np.sin(angle)
        C = 1 - c
        x, y, z = axis

        return np.array([
            [c + x * x * C, x * y * C - z * s, x * z * C + y * s],
            [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
            [z * x * C - y * s, z * y * C + x * s, c + z * z * C]
        ])

    def compute_element_center(self, P0, R0, L, theta=0.0, tilt=0.0):
        """
        tilt = rotation around local z axis (radians)
        theta = bending angle
        """

        # ---- midpoint in canonical x-z bending plane ----
        if abs(theta) < 1e-12:
            local_mid = np.array([0.0, 0.0, L / 2])
        else:
            Rbend = L / theta
            phi = theta / 2
            local_mid = np.array([
                Rbend * (1 - np.cos(phi)),
                0.0,
                Rbend * np.sin(phi)
            ])

        # ---- rotate midpoint by tilt ----
        if abs(tilt) > 1e-12:
            Rtilt = self.rotation_about_axis(np.array([0, 0, 1]), tilt)
            local_mid = Rtilt @ local_mid

        # ---- global midpoint ----
        Pcenter = P0 + R0 @ local_mid

        # ---- orientation at midpoint ----
        if abs(theta) < 1e-12:
            Rcenter_local = np.eye(3)
        else:
            # bending axis = rotated y-axis
            bend_axis = np.array([0, 1, 0])
            if abs(tilt) > 1e-12:
                bend_axis = Rtilt @ bend_axis

            Rcenter_local = self.rotation_about_axis(bend_axis, theta / 2)

        Rcenter = R0 @ Rcenter_local

        return Pcenter, Rcenter

    # Example for a batch of elements:
    def midpoints_for_line(self, element_and_survey, local_axes_map=None):
        """
        Compute midpoints for many elements.

        Inputs:

        - ``survey_positions``: (N,3) array of start positions P0 for each element
        - ``survey_rotations``: (N,3,3) array of rotations R0 for each element
          (R0 maps local->global)
        - ``elements``: sequence of element-objects or dicts, each must provide:

          - ``length``: float
          - ``angle``: float (bending angle in radians; if absent treated as 0)

          Accepts any object where ``getattr(el,'length')`` and ``getattr(el,'angle',0.0)`` work,
          or dict-like with keys ``'length'`` and ``'angle'``.

        - ``local_axes_map``: see ``element_midpoint_global``

        Returns:

        - ``mids``: (N,3) ndarray of midpoint positions
        """
        elem_pos = {}
        yhat = np.array([0, 1, 0])  # assuming horizontal bending plane

        for i, survey in enumerate(element_and_survey.values()):
            el = self.line.elements[i]
            # try several common attribute names for angle (xtrack names vary)
            L = getattr(el, "length", getattr(el, "L", 0.0))
            theta = getattr(el, "angle", getattr(el, "bending_angle", 0.0))
            tilt = getattr(el, "tilt", getattr(el, "rot_s_rad", 0.0))
            P0 = np.array([survey["x"], survey["y"], survey["z"]])
            R0 = self.rotation_matrix_from_survey(survey)
            print(list(element_and_survey.keys())[i], tilt)

            Pmid, Rmid = self.compute_element_center(P0, R0, L, theta=theta, tilt=tilt)
            ex, ey, ez = Rmid[:, 0], Rmid[:, 1], Rmid[:, 2]

            elem_pos.update(
                {
                    list(element_and_survey.keys())[i]: {
                        "x": Pmid[0],
                        "y": Pmid[1],
                        "z": Pmid[2],
                        "phi": survey["phi"],
                        "psi": survey["psi"],
                        "theta": survey["theta"],
                    }
                }
            )
        print(elem_pos["ivd1"])
        return elem_pos

    def create_element_dictionary(self):
        s = self.line.survey()._data
        elems = {k: v for k, v in zip(s["name"], self.line.elements)}
        survey = {
            s["name"][i]: {
                "x": s["X"][i] + self.initial_position[0],
                "y": s["Y"][i] + self.initial_position[1],
                "z": s["Z"][i] + self.initial_position[2],
                "ex": s["ex"][i] + self.initial_rotation[0],
                "ey": s["ey"][i] + self.initial_rotation[1],
                "ez": s["ez"][i] + self.initial_rotation[2],
                "phi": (s["phi"][i] + np.pi) % (2 * np.pi) - np.pi,
                "psi": (s["psi"][i] + np.pi) % (2 * np.pi) - np.pi,
                "theta": (s["theta"][i] + np.pi) % (2 * np.pi) - np.pi,
            }
            for i in range(len(s["X"][:-1]))
        }
        survey = self.midpoints_for_line(survey)
        for k, v in elems.items():
            machine_area = self.machine_area
            length = 0
            if hasattr(v, "length"):
                length = v.length
            pos = [float(x) for x in [survey[k]["x"], survey[k]["y"], survey[k]["z"]]]
            rot = [
                float(x)
                for x in [survey[k]["phi"], survey[k]["psi"], survey[k]["theta"]]
            ]
            phys = {"middle": pos, "global_rotation": rot, "length": length}

            if type(v) in type_conversion_rules_xsuite_reversed:
                p_obj = type_conversion_rules_xsuite_reversed[type(v)]
                model_fields = introspect_model_defaults(p_obj)
                hardware_class = p_obj.model_fields["hardware_class"].default
                if (
                    not type(p_obj.model_fields["hardware_type"].default)
                    == PydanticUndefinedType
                ):
                    hardware_type = p_obj.model_fields["hardware_type"].default
                else:
                    hardware_type = hardware_class
                if type(hardware_class) == PydanticUndefinedType:
                    hardware_class = hardware_type
                newobj = {
                    "name": k,
                    "hardware_type": hardware_type,
                    "hardware_class": hardware_class,
                    "machine_area": machine_area,
                    "physical": phys,
                }
                try:
                    merged = (
                        keyword_conversion_rules[hardware_type.lower()]
                        | keyword_conversion_rules["general"]
                    )
                except KeyError:
                    merged = keyword_conversion_rules["general"]
                except TypeError:
                    merged = keyword_conversion_rules["general"]
                for subk in ["magnetic", "cavity", "simulation", "diagnostic"]:
                    if subk in model_fields:
                        newobj.update({subk: {}})
                kwele = {y: x for x, y in merged.items()}
                exclude = ["order"]
                for name in dir(v):
                    for subk in model_fields:
                        if isinstance(model_fields[subk], dict) and name not in exclude:
                            if name in ["k1", "k2", "k3", "angle"] and isinstance(
                                v, _HasKnlKsl
                            ):
                                if "magnetic" not in newobj:
                                    newobj.update({"magnetic": {"length": length}})
                                try:
                                    newobj["magnetic"]["kl"] = (
                                        getattr(
                                            v,
                                            f"k{magnetic_orders[newobj['hardware_type']]}",
                                        )
                                        * v.length
                                    )
                                except AttributeError as e:
                                    print(e)
                                    newobj["magnetic"]["kl"] = getattr(v, name)
                                newobj["magnetic"].update({name: getattr(v, name)})
                                if name == "angle":
                                    newobj["magnetic"]["kl"] = (
                                        newobj["magnetic"]["kl"] * -1
                                    )
                                newobj["hardware_class"] = "Magnet"
                            if name in ["ks"]:
                                newobj.update(
                                    {"magnetic": {"ks": v.ks, "length": v.length}}
                                )
                            if name in model_fields[subk]:
                                newobj[subk].update({name: getattr(v, name)})
                            elif name in kwele:
                                if kwele[name] in model_fields[subk]:
                                    if (
                                        not isinstance(
                                            model_fields[subk][kwele[name]], str
                                        )
                                        or model_fields[subk][kwele[name]]
                                    ):
                                        try:
                                            newobj[subk].update(
                                                {kwele[name]: getattr(v, name)}
                                            )
                                        except KeyError as e:
                                            print(e)
                                        except AttributeError as e:
                                            print(e)
                if "angle" in newobj["physical"]:
                    newobj["physical"].update(
                        {"angle": newobj["physical"]["angle"] * -1}
                    )
                # if not newobj["hardware_class"] == "Drift":
                self.elements.update({k: p_obj(**newobj)})
            else:
                warn(f"Type conversion {type(v)} not implemented")

    def create_section(
        self, start: str, end: str, name: str
    ) -> Dict[str, SectionLattice]:
        if not self.elements:
            self.create_element_dictionary()
        appending = False
        order = []
        elems = {}
        if any([start not in self.elements.keys(), end not in self.elements.keys()]):
            raise KeyError(
                f"Could not find {start} or {end} in lattice; please check names"
            )
        for name, elem in self.elements.items():
            if name == start:
                appending = True
            if appending:
                order.append(name)
                elems.update({name: elem})
            if name == end:
                appending = False
        if not elems:
            raise ValueError(
                f"Could not create list of elements; check {start} is before {end}"
            )
        seclat = SectionLattice(
            order=order, elements=ElementList(elements=elems), name=name
        )
        self.sections.update({name: seclat})
        return {name: seclat}

    def create_layout(self, name: str, sections: List[Dict]) -> MachineLayout:
        if not self.elements:
            self.create_element_dictionary()
        layout_sections = {}
        for sec in sections:
            assert "name" in sec and "start" in sec and "end" in sec
            layout_sections.update(
                self.create_section(
                    start=sec["start"],
                    end=sec["end"],
                    name=sec["name"],
                )
            )
        layout = MachineLayout(
            name=name,
            sections={
                k: v
                for k, v in zip(
                    list(layout_sections.keys()), list(layout_sections.values())
                )
            },
        )
        self.layouts.update({name: layout})
        return layout
