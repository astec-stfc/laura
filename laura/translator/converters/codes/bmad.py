from pydantic import BaseModel, model_validator
from typing import Dict, Any, List, Literal, Optional, Union
from collections import Counter
from warnings import warn
from . import magnetic_orders
import laura.models.element as LAURA_elements
from laura.models.elementList import SectionLattice, MachineLayout, ElementList
from laura.models.element import (
    Element,
    Combined_Corrector,
    Vertical_Corrector,
    Horizontal_Corrector,
)
from ....Exporters.YAML import export_machine_combined_file, PositionMode
import math
import re
from pathlib import Path

_SILENTLY_SKIPPED_TYPES = ("Drift", "Beginning_Ele")

_CAVITY_TYPES = ("Lcavity", "RFCavity")

_COLLIMATOR_TYPES = ("ECollimator", "RCollimator")


def norm(v):
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if n == 0:
        return (0.0, 0.0, 0.0)
    return (v[0] / n, v[1] / n, v[2] / n)


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def deg(r):
    return math.degrees(r)


def rotation_angles(forward):
    f = norm(forward)
    # yaw (heading around Y): atan2(x, z)
    yaw = math.atan2(f[0], f[2])

    # pitch (elevation): atan2(y, sqrt(x^2+z^2))
    pitch = math.atan2(f[1], math.sqrt(f[0] * f[0] + f[2] * f[2]))

    # build a local right/up so we can compute roll.
    # choose world_up = (0,1,0)
    world_up = (0.0, 1.0, 0.0)

    right = norm(cross(world_up, f))
    up = cross(f, right)  # orthogonal up for the object frame

    # roll = signed angle around forward that rotates object's up -> world_up
    cr = cross(up, world_up)
    roll = math.atan2(dot(cr, f), dot(up, world_up))
    return pitch, roll, yaw


class BmadLatticeImporter(BaseModel):

    floorplan_init: Optional[str] = None
    """Name of Tao init file which produces floor coordinates"""

    lattice_file: Optional[str] = None
    """Original BMAD lattice file, used instead of ``floorplan_init``."""

    libtao: str = None
    """libtao.so file"""

    position_mode: Literal["s", "floor"] = "s"
    """How element positions are resolved from Tao:

    ``"s"`` (default): each element is given Bmad's own cumulative
    arc-length ``s`` and LAURA integrates the design orbit itself (see
    :meth:`~laura.models.elementList.SectionLattice._resolve_s_coordinates`)
    to produce global ``middle``/rotation. ``orbit.floor.x/y/z`` are still
    fetched and kept on :attr:`xpos`/:attr:`ypos`/:attr:`zpos`, purely so
    LAURA's own integration can be cross-checked against Tao's.

    ``"floor"``: the legacy behaviour -- each element's global ``middle``
    and rotation are derived directly from consecutive
    ``orbit.floor.x/y/z`` points, bypassing LAURA's trajectory integration.
    """

    elements: Dict = {}
    """Dictionary containing converted LAURA element objects"""

    functional_definitions: Dict[str, Union[int, float]] = {}

    n_universes: int = 1

    names: Dict[int, Dict[str, List[str]]] = {}

    names_numbered: Dict[int, Dict[str, List[str]]] = {}

    types: Dict[int, Dict[str, List[str]]] = {}

    lengths: Dict[int, Dict[str, List[float]]] = {}

    spos: Dict[int, Dict[str, List[float]]] = {}
    """Cumulative arc-length at the *exit* of each element (Bmad's ``ele.s``),
    used for ``position_mode="s"``."""

    xpos: Dict[int, Dict[str, List[float]]] = {}

    ypos: Dict[int, Dict[str, List[float]]] = {}

    zpos: Dict[int, Dict[str, List[float]]] = {}

    params: Dict[int, Dict[str, List[Dict[str, Any]]]] = {}

    laura_elems: Dict[int, Dict[str, Dict[str, Element]]] = {}

    branches: Dict[int, List[str]] = {}

    deferred_parameters: Dict[str, Dict[str, str]] = {}

    @model_validator(mode="after")
    def _check_input(self):
        if (self.floorplan_init is None) == (self.lattice_file is None):
            raise ValueError("Give exactly one of floorplan_init or lattice_file.")
        return self

    def _read_functional_definitions(self) -> None:
        if not self.lattice_file:
            return
        text = Path(self.lattice_file).read_text()
        text = re.sub(r"!.*", "", text).replace("&\n", " ")
        statements = [statement.strip() for statement in re.split(r";|\n", text)]
        values = {}
        deferred = {}
        for statement in statements:
            scalar = re.fullmatch(
                r"([A-Za-z_][\w.]*)\s*=\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)",
                statement,
            )
            if scalar:
                values[scalar.group(1)] = float(scalar.group(2))
                continue
            element = re.match(r"([^:]+):\s*[^,]+,(.*)", statement, re.S)
            if not element:
                continue
            for attribute, expression in re.findall(
                r"([A-Za-z_][\w.]*)\s*:=\s*([^,]+)", element.group(2)
            ):
                deferred.setdefault(element.group(1).strip().lower(), {})[
                    attribute.upper()
                ] = expression.strip()
        used = {
            token
            for parameters in deferred.values()
            for expression in parameters.values()
            for token in re.findall(r"[A-Za-z_][\w.]*", expression)
        }
        self.deferred_parameters = deferred
        self.functional_definitions = {
            name: value for name, value in values.items() if name in used
        }

    def _symbol(self, element: str, attribute: str, length=0.0) -> str | None:
        expression = self.deferred_parameters.get(element.lower(), {}).get(attribute)
        if not expression:
            return None
        compact = expression.lower().replace(" ", "").replace("(", "").replace(")", "")
        for name in self.functional_definitions:
            if compact == name.lower():
                return name
            if length and compact.startswith(name.lower() + "/"):
                try:
                    if math.isclose(float(compact.split("/", 1)[1]), length):
                        return name
                except ValueError:
                    pass
        return None

    def model_post_init(self, __context: Any) -> None:
        from pytao import Tao, TaoCommandError

        self._read_functional_definitions()

        tao = Tao(
            f"-{'lat' if self.lattice_file else 'init'} "
            f"{self.lattice_file or self.floorplan_init} -noplot",
            so_lib=self.libtao,
        )
        while True:
            try:
                tao.universe(str(self.n_universes))
                self.branches.update(
                    {
                        self.n_universes: [
                            f'{i["branch_name"]}_{self.n_universes}'
                            for i in tao.lat_branch_list(ix_uni=self.n_universes)
                        ]
                    }
                )
                self.names.update({self.n_universes: {}})
                self.names_numbered.update({self.n_universes: {}})
                self.types.update({self.n_universes: {}})
                self.lengths.update({self.n_universes: {}})
                self.spos.update({self.n_universes: {}})
                self.xpos.update({self.n_universes: {}})
                self.ypos.update({self.n_universes: {}})
                self.zpos.update({self.n_universes: {}})
                self.params.update({self.n_universes: {}})
                self.laura_elems.update({self.n_universes: {}})
                for ind, b in enumerate(self.branches[self.n_universes]):
                    kwa = {
                        "ix_uni": str(self.n_universes),
                        "ix_branch": b.replace(f"_{self.n_universes}", ""),
                    }
                    names = [i for i in tao.lat_list("*", "ele.name", **kwa)]
                    names_numbered = [
                        f"{x}.{(c := Counter(names[:i + 1]))[x]}"
                        for i, x in enumerate(names)
                    ]
                    types = [i for i in tao.lat_list("*", "ele.key", **kwa)]
                    lengths = [i for i in tao.lat_list("*", "ele.l", **kwa)]
                    spos = [i for i in tao.lat_list("*", "ele.s", **kwa)]
                    xpos = [i for i in tao.lat_list("*", "orbit.floor.x", **kwa)]
                    ypos = [i for i in tao.lat_list("*", "orbit.floor.y", **kwa)]
                    zpos = [i for i in tao.lat_list("*", "orbit.floor.z", **kwa)]
                    params = [
                        tao.ele_gen_attribs(f"{str(self.n_universes)}@{ind}>>{i}")
                        for i in range(len(names))
                    ]
                    self.names[self.n_universes].update({b: names})
                    self.names_numbered[self.n_universes].update({b: names_numbered})
                    self.types[self.n_universes].update({b: types})
                    self.lengths[self.n_universes].update({b: lengths})
                    self.spos[self.n_universes].update({b: spos})
                    self.xpos[self.n_universes].update({b: xpos})
                    self.ypos[self.n_universes].update({b: ypos})
                    self.zpos[self.n_universes].update({b: zpos})
                    self.params[self.n_universes].update({b: params})
                    self.laura_elems[self.n_universes].update({b: {}})
                self.n_universes += 1
            except TaoCommandError:
                break
        self.branches = {
            k: [f'{i["branch_name"]}_{k}' for i in tao.lat_branch_list(ix_uni=k)]
            for k in range(1, self.n_universes)
        }

    def _physical_common(self, universe: int, b: str, i: int) -> dict:
        """Build this element's shared ``physical`` sub-dict (position + length).

        ``"s"`` mode: Bmad's own cumulative arc-length
        is handed straight to LAURA as ``physical.s``/``s_point``,
        and LAURA's own trajectory integration produces global
        middle/rotation later, via ``resolve_positions()``.

        ``"floor"`` mode (legacy): global ``middle``/rotation are derived
        directly from consecutive ``orbit.floor.x/y/z`` points.
        """
        length = float(self.lengths[universe][b][i])
        if self.position_mode == "s":
            return {
                "s": self.spos[universe][b][i],
                "s_point": "end",
                "length": length,
            }

        end_x = self.xpos[universe][b][i]
        end_y = self.ypos[universe][b][i]
        end_z = self.zpos[universe][b][i]

        # Start position is the end of the previous element, or the origin
        # for the first element in the branch.
        if i > 0:
            start_x = self.xpos[universe][b][i - 1]
            start_y = self.ypos[universe][b][i - 1]
            start_z = self.zpos[universe][b][i - 1]
        else:
            start_x = start_y = start_z = 0.0

        middle = [
            (start_x + end_x) / 2.0,
            (start_y + end_y) / 2.0,
            (start_z + end_z) / 2.0,
        ]

        # Beam direction at the START of this element (i.e. the exit
        # direction of the previous element).
        if i > 1:
            forward = (
                self.xpos[universe][b][i - 1] - self.xpos[universe][b][i - 2],
                self.ypos[universe][b][i - 1] - self.ypos[universe][b][i - 2],
                self.zpos[universe][b][i - 1] - self.zpos[universe][b][i - 2],
            )
        elif i == 1:
            forward = (
                self.xpos[universe][b][0],
                self.ypos[universe][b][0],
                self.zpos[universe][b][0],
            )
        else:
            forward = (0.0, 0.0, 1.0)
        pitch, roll, yaw = rotation_angles(forward)

        return {
            "position": middle,
            "global_rotation": [pitch, roll, yaw],
            "length": length,
        }

    def create_element_dictionary(self, universe: int) -> Dict[str, Dict[str, Element]]:
        return self.create_laura_element_dictionary(universe)

    def create_laura_element_dictionary(
        self, universe: int
    ) -> Dict[str, Dict[str, Element]]:
        for b in self.names_numbered[universe].keys():
            for i, nam in enumerate(self.names_numbered[universe][b]):
                etype = self.types[universe][b][i]
                length = float(self.lengths[universe][b][i])
                phys_common = self._physical_common(universe, b, i)

                elem_data = {}
                parameters = self.params[universe][b][i]
                if etype == "Kicker":
                    hardware_type = "Combined_Corrector"
                    horizontal = nam + "_H"
                    vertical = nam + "_V"
                    hcor = {"length": length, "horizontal_kick": parameters["HKICK"]}
                    vcor = {"length": length, "vertical_kick": parameters["VKICK"]}
                    elem_data = {
                        "hardware_type": hardware_type,
                        "magnetic": {
                            "length": length,
                            "horizontal_kick": parameters["HKICK"],
                            "vertical_kick": parameters["VKICK"],
                        },
                    }
                    for attribute, target in (
                        ("HKICK", "horizontal_kick"),
                        ("VKICK", "vertical_kick"),
                    ):
                        symbol = self._symbol(nam.split(".", 1)[0], attribute)
                        if symbol:
                            elem_data["magnetic"][target] = symbol
                            (hcor if attribute == "HKICK" else vcor)[target] = symbol
                elif etype in magnetic_orders:
                    hardware_type = etype
                    order = magnetic_orders[hardware_type]
                    try:
                        normal = self._symbol(
                            nam.split(".", 1)[0], f"K{order}", length
                        ) or parameters[f"K{order}"] * length
                        kl = {
                            "multipoles": {
                                f"K{order}L": {
                                    "normal": normal,
                                    "order": order,
                                },
                            },
                        }
                    except KeyError:
                        angle = self._symbol(
                            nam.split(".", 1)[0], "ANGLE"
                        ) or parameters["ANGLE"]
                        kl = {
                            "multipoles": {
                                f"K{order}L": {
                                    "normal": angle,
                                    "order": order,
                                },
                            },
                            "entrance_edge_angle": parameters["E1"],
                            "exit_edge_angle": parameters["E2"],
                        }
                    if "GAP" in parameters:
                        kl.update({"gap": parameters["GAP"]})
                    elem_data = {
                        "hardware_type": hardware_type,
                        "magnetic": {"order": order, "length": length, **kl},
                    }
                elif etype in _CAVITY_TYPES:
                    n_cells = parameters.get("N_CELL", 1) or 1
                    elem_data = {
                        "hardware_type": "RFCavity",
                        "cavity": {
                            "phase": parameters.get("PHI0", 0.0) * 360.0,
                            "frequency": parameters["RF_FREQUENCY"],
                            "n_cells": n_cells,
                            "cell_length": length / n_cells,
                            "structure_type": str(
                                parameters.get("CAVITY_TYPE", "Standing_Wave")
                            ).replace("_", ""),
                        },
                        "simulation": {"field_amplitude": parameters["VOLTAGE"]},
                    }
                elif etype == "Wiggler":
                    b_max = parameters.get("B_MAX", 0.0)
                    l_period = parameters.get("L_PERIOD", 0.0)
                    elem_data = {
                        "hardware_type": "Wiggler",
                        "magnetic": {
                            "length": length,
                            "peak_magnetic_field": b_max,
                            "period": l_period,
                            "num_periods": int(parameters.get("N_PERIOD", 0)),
                            "strength": 0.934 * b_max * (l_period * 100.0),
                        },
                    }
                elif etype == "Solenoid":
                    bs_field = parameters.get("BS_FIELD", 0.0)
                    elem_data = {
                        "hardware_type": "Solenoid",
                        "magnetic": {
                            "length": length,
                            "fields": {"S0L": bs_field * length},
                        },
                    }
                elif etype in _COLLIMATOR_TYPES:
                    elem_data = {
                        "hardware_type": "Collimator",
                        "aperture": {
                            "horizontal_size": (
                                parameters.get("X1_LIMIT", 0.0)
                                + parameters.get("X2_LIMIT", 0.0)
                            ),
                            "vertical_size": (
                                parameters.get("Y1_LIMIT", 0.0)
                                + parameters.get("Y2_LIMIT", 0.0)
                            ),
                        },
                    }
                elif etype in ("Marker", "Monitor"):
                    markelem = {
                        "physical": dict(phys_common),
                        "name": nam,
                        "hardware_type": (
                            "Marker" if etype == "Marker" else "Beam_Position_Monitor"
                        ),
                        "machine_area": "test",
                    }
                    self.laura_elems[universe][b].update(
                        {nam: getattr(LAURA_elements, markelem["hardware_type"])(**markelem)}
                    )
                elif etype not in _SILENTLY_SKIPPED_TYPES:
                    warn(
                        f"Could not parse Bmad element type {etype!r} for "
                        f"{nam!r}; skipping."
                    )

                if elem_data:
                    elems = {
                        nam: {
                            "physical": dict(phys_common),
                            "name": nam,
                            "machine_area": "test",
                            **elem_data,
                        }
                    }
                    if etype == "Kicker":
                        helem = dict(elems[nam])
                        helem["physical"] = dict(phys_common)
                        helem.update(
                            {
                                "name": horizontal,
                                "hardware_type": "Horizontal_Corrector",
                                "magnetic": hcor,
                                "subelement": nam,
                            }
                        )
                        velem = dict(elems[nam])
                        velem["physical"] = dict(phys_common)
                        velem.update(
                            {
                                "name": vertical,
                                "hardware_type": "Vertical_Corrector",
                                "magnetic": vcor,
                                "subelement": nam,
                            }
                        )
                        comb = Combined_Corrector(**elems[nam])
                        hori = Horizontal_Corrector(**helem)
                        vert = Vertical_Corrector(**velem)
                        self.laura_elems[universe][b].update(
                            {
                                nam: comb,
                                horizontal: hori,
                                vertical: vert,
                            },
                        )
                    else:
                        if etype in ("RBend", "SBend"):
                            self.types[universe][b][i] = "Dipole"
                            elems[nam]["hardware_type"] = "Dipole"
                        hardware_type = elems[nam]["hardware_type"]
                        self.laura_elems[universe][b].update(
                            {nam: getattr(LAURA_elements, hardware_type)(**elems[nam])}
                        )
        return self.laura_elems[universe]

    def create_section(self, universe: int, branch: str) -> Dict[str, SectionLattice]:
        if not self.laura_elems[universe][branch]:
            self.create_laura_element_dictionary(universe)
        elems = self.laura_elems[universe][branch]
        self.elements = elems
        order = [n for n, e in elems.items() if not e.is_subelement()]
        seclat = SectionLattice(
            order=order, elements=ElementList(elements=elems), name=branch,
            functional_definitions=self.functional_definitions,
        )
        seclat.resolve_positions(elems)
        for name, elem in elems.items():
            if elem.is_subelement():
                parent = elems.get(elem.subelement)
                if parent is not None and parent.physical.middle is not None:
                    elem.physical.middle = parent.physical.middle
                    elem.physical.rotation = parent.physical.rotation
                    elem.physical.global_rotation = parent.physical.global_rotation
        return {branch: seclat}

    def create_layout(
        self, universe: int, name: Optional[str] = None
    ) -> MachineLayout:
        layout = {}
        for branch in list(self.names_numbered[universe].keys()):
            layout.update(self.create_section(universe, branch))
        return MachineLayout(
            name=name or str(universe), sections=layout,
            functional_definitions=self.functional_definitions,
        )

    def export_yaml(
        self,
        path: str,
        source: Union[SectionLattice, MachineLayout],
        position_mode: PositionMode = "s",
    ) -> None:
        export_machine_combined_file(path, source, position_mode=position_mode)
