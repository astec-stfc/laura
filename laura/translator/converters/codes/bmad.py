from pydantic import BaseModel, Field, PrivateAttr, model_validator
from typing import Dict, Any, List, Optional, Union
from warnings import warn
from . import magnetic_orders
import laura.models.element as LAURA_elements
from laura.models.elementList import (
    SectionLattice,
    MachineLayout,
    MachineModel,
    ElementList,
)
from laura.models.element import (
    Element,
    Combined_Corrector,
    Vertical_Corrector,
    Horizontal_Corrector,
)
from ....Exporters.YAML import export_machine_combined_file, PositionMode
from .. import keyword_conversion_rules_bmad, type_conversion_rules_Bmad
from ...utils.functions import number_repeated_names, merge_layout_elements
import math
from itertools import permutations
import numpy as np
import re
import tempfile
from pathlib import Path

_SILENTLY_SKIPPED_TYPES = ("Drift", "Pipe")

_CAVITY_TYPES = ("Lcavity", "RFCavity", "Crab_Cavity", "E_Gun")

_COLLIMATOR_TYPES = ("ECollimator", "RCollimator")

_MULTIPOLE_TYPES = ("Multipole", "AB_multipole", "Thick_Multipole", "Sad_Mult")

_ORDER_TYPES = {0: "Dipole", 1: "Quadrupole", 2: "Sextupole", 3: "Octupole"}


def _switch_dict() -> Dict[str, str]:
    """Bmad element key -> LAURA hardware type."""
    switch = {
        native_type.lower(): laura_type
        for laura_type, native_type in type_conversion_rules_Bmad.items()
    }
    switch.update(
        {
            "lcavity": "RFCavity",
            "match": "MatrixTransform",
            "rbend": "Dipole",
            "rcollimator": "Collimator",
            "undulator": "Wiggler",
            "e_gun": "RFCavity",
            "beambeam": "BeamBeam",
        }
    )
    return switch


def _floor_to_physical(floor: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Convert a Tao ``ele_floor`` record to LAURA ``datum``/``global_rotation``.
    Bmad's ``theta`` (vertical) corresponds to LAURA's ``psi``, so
    these are switched over.
    """
    reference = floor.get("Reference")
    if reference is None or len(reference) < 6:
        return {}
    x, y, z, theta, phi, psi = (float(v) for v in reference[:6])
    return {
        "datum": {"x": x, "y": y, "z": z},
        "global_rotation": {"phi": phi, "psi": theta, "theta": psi},
    }


def _misalignment(parameters: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Convert an element's Bmad misalignment attributes to LAURA's
    ``physical.error``. See :func:`_floor_to_physical` --
    angle names are swapped around.
    """
    position = {
        axis: float(parameters.get(f"{axis.upper()}_OFFSET", 0.0) or 0.0)
        for axis in ("x", "y", "z")
    }
    rotation = {
        "phi": float(parameters.get("Y_PITCH", 0.0) or 0.0),
        "psi": float(parameters.get("X_PITCH", 0.0) or 0.0),
        "theta": 0.0,
    }
    if not any(position.values()) and not any(rotation.values()):
        return {}
    return {"error": {"position": position, "rotation": rotation}}


def _aperture(parameters: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Convert an element's Bmad aperture limits to a LAURA ``aperture`` dict."""
    limits = {
        key: float(parameters.get(key, 0.0) or 0.0)
        for key in ("X1_LIMIT", "X2_LIMIT", "Y1_LIMIT", "Y2_LIMIT")
    }
    if not any(limits.values()):
        return {}
    shape = str(parameters.get("aperture_type", "rectangular")).lower()
    return {
        "aperture": {
            "horizontal_size": limits["X1_LIMIT"] + limits["X2_LIMIT"],
            "vertical_size": limits["Y1_LIMIT"] + limits["Y2_LIMIT"],
            "shape": shape if shape in ("rectangular", "elliptical", "circular") else "rectangular",
        }
    }


def _native_keyword(hardware_type: str, laura_field: str) -> str:
    """Return the Tao/Bmad spelling for a LAURA field."""
    rules = keyword_conversion_rules_bmad["general"]
    key = hardware_type.lower()
    if key in keyword_conversion_rules_bmad:
        rules = keyword_conversion_rules_bmad[key] | rules
    return rules.get(laura_field, laura_field).upper()


def _read_lattice_text(path: Path, _seen: Optional[set] = None) -> str:
    """Read a Bmad lattice file, inlining any ``call, file = ...`` statements
    it contains.

    Bmad resolves a ``call``'d filename relative to the directory of the file
    containing the ``call`` -- mirror that here so functional parameter
    definitions declared in a called file are still found.
    """
    seen = _seen if _seen is not None else set()
    path = path.resolve()
    if path in seen:
        return ""
    seen.add(path)
    text = re.sub(r"!.*", "", path.read_text())

    def _inline(match: "re.Match") -> str:
        called = (path.parent / match.group(1).strip("'\"")).resolve()
        if not called.is_file():
            return match.group(0)
        return _read_lattice_text(called, seen)

    return re.sub(r"(?im)^\s*call\s*,\s*file\s*=\s*([^\s;]+)\s*;?\s*$", _inline, text)


def _ac_kicker_data(tao, element_id: str) -> Dict[str, list]:
    # pytao cannot parse the nested ele:ac_kicker response in current releases.
    result = {"frequencies": [], "amp_vs_time": []}
    section = None
    for line in tao.cmd(f"pipe ele:ac_kicker {element_id}|model"):
        if line.startswith("has#"):
            section = line.partition("#")[2].lower()
        elif section in result:
            result[section].append(
                tuple(float(value) for value in line.split(";")[1:])
            )
    return result


def _taylor_matrices(taylor: Dict[str, Any]):
    """Convert a Bmad orbital Taylor map of order <= 3 to C/R/T/U arrays."""
    c_matrix = np.zeros(6)
    r_matrix = np.zeros((6, 6))
    t_matrix = np.zeros((6, 6, 6))
    u_matrix = np.zeros((6, 6, 6, 6))
    ref = np.zeros(6)
    for section in taylor["data"]:
        ref[section["index"] - 1] = section["ref"]

    for section in taylor["data"]:
        output = section["index"] - 1
        for term in section["data"]:
            powers = [int(term[f"exp{i}"]) for i in range(1, 7)]
            degree = sum(powers)
            coefficient = term["coef"]
            if degree > 3:
                raise ValueError(f"contains an orbital term of order {degree}")
            indices = [index for index, power in enumerate(powers) for _ in range(power)]
            if degree == 0:
                c_matrix[output] += coefficient
            elif degree == 1:
                r_matrix[output, indices[0]] += coefficient
            else:
                unique_indices = set(permutations(indices))
                tensor = t_matrix if degree == 2 else u_matrix
                for tensor_indices in unique_indices:
                    tensor[(output, *tensor_indices)] += coefficient / len(unique_indices)

    t_feeddown = np.einsum("ijk,k->ij", t_matrix, ref)
    u_feeddown = np.einsum("ijkl,l->ijk", u_matrix, ref)
    c_matrix = (
        c_matrix
        - r_matrix @ ref
        + t_feeddown @ ref
        - np.einsum("ijkl,j,k,l->i", u_matrix, ref, ref, ref)
    )
    r_matrix = (
        r_matrix
        - 2 * t_feeddown
        + 3 * np.einsum("ijkl,k,l->ij", u_matrix, ref, ref)
    )
    t_matrix = t_matrix - 3 * u_feeddown
    return c_matrix, r_matrix, t_matrix, u_matrix


class BmadTaoInit(BaseModel):
    """Minimal Tao init file for one Bmad lattice and optional line selections."""

    lattice_file: str
    lines: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_lines(self):
        if any(not line.strip() for line in self.lines):
            raise ValueError("Bmad line names cannot be empty.")
        return self

    def render(self) -> str:
        targets = [
            f"{self.lattice_file}@{line}" for line in self.lines
        ] or [self.lattice_file]
        entries = "\n".join(
            "  design_lattice({})%file = '{}'".format(
                index, target.replace("'", "''")
            )
            for index, target in enumerate(targets, 1)
        )
        return (
            "&tao_design_lattice\n"
            f"  n_universes = {len(targets)}\n"
            f"{entries}\n"
            "/\n"
        )

    def write(self, path: str | Path) -> Path:
        path = Path(path)
        path.write_text(self.render())
        return path


class BmadLatticeImporter(BaseModel):

    machine_area: str = "Lattice"

    tao_init: Optional[str] = None
    """Name of Tao init file which produces."""

    lattice_file: Optional[str] = None
    """Original BMAD lattice file, used instead of ``tao_init``."""

    lines: List[str] = Field(default_factory=list)
    """Bmad lines to load as separate Tao universes from ``lattice_file``."""

    libtao: Optional[str] = None
    """libtao.so file"""

    elements: Dict = {}
    """Dictionary containing converted LAURA element objects"""

    functional_definitions: Dict[str, Union[int, float]] = {}

    n_universes: int = 1

    names: Dict[int, Dict[str, List[str]]] = {}

    names_numbered: Dict[int, Dict[str, List[str]]] = {}

    types: Dict[int, Dict[str, List[str]]] = {}

    lengths: Dict[int, Dict[str, List[float]]] = {}

    spos: Dict[int, Dict[str, List[float]]] = {}
    """Cumulative arc-length at the *exit* of each element (Bmad's ``ele.s``)."""

    params: Dict[int, Dict[str, List[Dict[str, Any]]]] = {}

    branch_params: Dict[int, Dict[str, Dict[str, Any]]] = {}
    """Tao ``branch1`` records, holding ``param_geometry`` and ``param_particle``."""

    laura_elems: Dict[int, Dict[str, Dict[str, Element]]] = {}

    branches: Dict[int, List[str]] = {}

    deferred_parameters: Dict[str, Dict[str, str]] = {}

    _generated_tao_init: Any = PrivateAttr(default=None)

    @model_validator(mode="after")
    def _check_input(self):
        if (self.tao_init is None) == (self.lattice_file is None):
            raise ValueError("Give exactly one of tao_init or lattice_file.")
        if self.tao_init and self.lines:
            raise ValueError("lines can only be used with lattice_file.")
        return self

    def _tao_init_path(self) -> str:
        if self.tao_init:
            return self.tao_init
        self._generated_tao_init = tempfile.TemporaryDirectory(prefix="laura-bmad-")
        path = Path(self._generated_tao_init.name) / "tao.init"
        return str(
            BmadTaoInit(
                lattice_file=str(Path(self.lattice_file).resolve()), lines=self.lines
            ).write(path)
        )

    def _read_functional_definitions(self) -> None:
        if not self.lattice_file:
            return
        text = _read_lattice_text(Path(self.lattice_file))
        text = text.replace("&\n", " ")
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

        tao = Tao(f"-init {self._tao_init_path()} -noplot", so_lib=self.libtao)
        while True:
            try:
                tao.universe(str(self.n_universes))
            except TaoCommandError as e:
                print(f"TaoCommandError when loading universe; {e}")
                break
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
            self.params.update({self.n_universes: {}})
            self.branch_params.update({self.n_universes: {}})
            self.laura_elems.update({self.n_universes: {}})
            for ind, b in enumerate(self.branches[self.n_universes]):
                kwa = {
                    "ix_uni": str(self.n_universes),
                    "ix_branch": str(ind),
                }
                self.branch_params[self.n_universes][b] = tao.branch1(
                    ix_uni=self.n_universes, ix_branch=ind
                )
                names = [i for i in tao.lat_list("*", "ele.name", **kwa)]
                names_numbered = number_repeated_names(names)
                types = [i for i in tao.lat_list("*", "ele.key", **kwa)]
                lengths = [i for i in tao.lat_list("*", "ele.l", **kwa)]
                spos = [i for i in tao.lat_list("*", "ele.s", **kwa)]
                params = []
                for i, etype in enumerate(types):
                    element_id = f"{self.n_universes}@{ind}>>{i}"
                    attributes = tao.ele_gen_attribs(element_id)
                    if etype == "Match":
                        matrix = tao.ele_mat6(element_id, who="mat6")
                        attributes["_MAT6"] = [
                            matrix[str(row)] for row in range(1, 7)
                        ]
                        attributes["_VEC0"] = tao.ele_mat6(
                            element_id, who="vec0"
                        )["vec0"]
                    elif etype == "Taylor":
                        attributes["_TAYLOR"] = tao.ele_taylor(element_id)
                        attributes["_SPIN_TAYLOR"] = tao.ele_spin_taylor(
                            element_id
                        )
                    elif etype in _MULTIPOLE_TYPES:
                        attributes["_MULTIPOLES"] = tao.ele_multipoles(element_id)
                    elif etype == "AC_Kicker":
                        attributes["_AC_KICKER"] = _ac_kicker_data(tao, element_id)
                    elif etype == "Beginning_Ele":
                        attributes["_TWISS"] = tao.ele_twiss(element_id)
                        attributes["_FLOOR"] = tao.ele_floor(element_id)
                        attributes["_COUPLING"] = tao.twiss_at_s(
                            ix_uni=self.n_universes,
                            ele=f"{ind}>>{i}",
                            s_offset=0.0,
                        )
                    params.append(attributes)
                self.names[self.n_universes].update({b: names})
                self.names_numbered[self.n_universes].update({b: names_numbered})
                self.types[self.n_universes].update({b: types})
                self.lengths[self.n_universes].update({b: lengths})
                self.spos[self.n_universes].update({b: spos})
                self.params[self.n_universes].update({b: params})
                self.laura_elems[self.n_universes].update({b: {}})
            self.n_universes += 1
        self.branches = {
            k: [f'{i["branch_name"]}_{k}' for i in tao.lat_branch_list(ix_uni=k)]
            for k in range(1, self.n_universes)
        }

    def _physical_common(self, universe: int, b: str, i: int) -> dict:
        """Build this element's shared ``physical`` sub-dict (position + length).

        Bmad's own cumulative arc-length is handed straight to LAURA as
        ``physical.s``/``s_point``, fed into ``resolve_positions()``.
        """
        return {
            "s": self.spos[universe][b][i],
            "s_point": "end",
            "length": float(self.lengths[universe][b][i]),
            **_misalignment(self.params[universe][b][i]),
        }

    def create_element_dictionary(self, universe: int) -> Dict[str, Dict[str, Element]]:
        return self.create_laura_element_dictionary(universe)

    def create_laura_element_dictionary(
        self, universe: int
    ) -> Dict[str, Dict[str, Element]]:
        switch_dict = _switch_dict()
        for b in self.names_numbered[universe].keys():
            for i, nam in enumerate(self.names_numbered[universe][b]):
                etype = self.types[universe][b][i]
                mapped_type = switch_dict.get(etype.lower())
                length = float(self.lengths[universe][b][i])
                phys_common = self._physical_common(universe, b, i)

                elem_data = {}
                parameters = self.params[universe][b][i]
                if etype == "Kicker":
                    hardware_type = mapped_type
                    horizontal = nam + "_H"
                    vertical = nam + "_V"
                    hkick = _native_keyword(hardware_type, "horizontal_kick")
                    vkick = _native_keyword(hardware_type, "vertical_kick")
                    hcor = {"length": length, "horizontal_kick": parameters[hkick]}
                    vcor = {"length": length, "vertical_kick": parameters[vkick]}
                    elem_data = {
                        "hardware_type": hardware_type,
                        "magnetic": {
                            "length": length,
                            "horizontal_kick": parameters[hkick],
                            "vertical_kick": parameters[vkick],
                        },
                    }
                    for attribute, target in (
                        (hkick, "horizontal_kick"),
                        (vkick, "vertical_kick"),
                    ):
                        symbol = self._symbol(nam.split(".", 1)[0], attribute)
                        if symbol:
                            elem_data["magnetic"][target] = symbol
                            (hcor if attribute == "HKICK" else vcor)[target] = symbol
                elif etype in ("HKicker", "VKicker"):
                    target = (
                        "horizontal_kick" if etype == "HKicker" else "vertical_kick"
                    )
                    kick = _native_keyword(mapped_type, target)
                    elem_data = {
                        "hardware_type": mapped_type,
                        "magnetic": {
                            "length": length,
                            target: self._symbol(
                                nam.split(".", 1)[0], kick
                            ) or parameters[kick],
                        },
                    }
                elif etype in magnetic_orders:
                    hardware_type = mapped_type
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
                            "entrance_edge_angle": parameters[
                                _native_keyword(hardware_type, "entrance_edge_angle")
                            ],
                            "exit_edge_angle": parameters[
                                _native_keyword(hardware_type, "exit_edge_angle")
                            ],
                        }
                    gap = _native_keyword(hardware_type, "gap")
                    if gap in parameters:
                        kl.update({"gap": parameters[gap]})
                    hgap = _native_keyword(hardware_type, "half_gap")
                    if hgap in parameters and parameters[hgap]:
                        kl["gap"] = 2 * parameters[hgap]
                    fint = _native_keyword(hardware_type, "edge_field_integral")
                    if fint in parameters:
                        kl["edge_field_integral"] = parameters[fint]
                    if parameters.get("TILT"):
                        kl["tilt"] = parameters["TILT"]
                    elem_data = {
                        "hardware_type": hardware_type,
                        "magnetic": {"order": order, "length": length, **kl},
                    }
                elif etype in _CAVITY_TYPES:
                    hardware_type = mapped_type
                    n_cells = parameters.get(
                        _native_keyword(hardware_type, "n_cells"), 1
                    ) or 1
                    elem_data = {
                        "hardware_type": hardware_type,
                        "cavity": {
                            "phase": parameters.get(
                                _native_keyword(hardware_type, "phase"), 0.0
                            ) * 360.0,
                            "frequency": parameters[
                                _native_keyword(hardware_type, "frequency")
                            ],
                            "n_cells": n_cells,
                            "cell_length": length / n_cells,
                            "structure_type": str(
                                parameters.get(
                                    _native_keyword(hardware_type, "structure_type"),
                                    "Standing_Wave",
                                )
                            ).replace("_", ""),
                        },
                        "simulation": {
                            "field_amplitude": parameters[
                                _native_keyword(hardware_type, "field_amplitude")
                            ]
                        },
                    }
                elif etype in ("Wiggler", "Undulator"):
                    b_max = parameters.get(
                        _native_keyword(mapped_type, "peak_magnetic_field"), 0.0
                    )
                    l_period = parameters.get(
                        _native_keyword(mapped_type, "period"), 0.0
                    )
                    elem_data = {
                        "hardware_type": mapped_type,
                        "magnetic": {
                            "length": length,
                            "peak_magnetic_field": b_max,
                            "period": l_period,
                            "num_periods": int(
                                parameters.get(
                                    _native_keyword(mapped_type, "num_periods"), 0
                                )
                            ),
                            "strength": 0.934 * b_max * (l_period * 100.0),
                        },
                    }
                elif etype == "Solenoid":
                    bs_field = parameters.get(
                        _native_keyword(mapped_type, "ks"), 0.0
                    )
                    elem_data = {
                        "hardware_type": mapped_type,
                        "magnetic": {
                            "length": length,
                            "fields": {"S0L": bs_field * length},
                        },
                    }
                elif etype == "Sol_Quad":
                    k1 = _native_keyword(mapped_type, "k1l")
                    bs_field = _native_keyword(mapped_type, "ks")
                    elem_data = {
                        "hardware_type": mapped_type,
                        "magnetic": {
                            "length": length,
                            "k1l": self._symbol(
                                nam.split(".", 1)[0], k1, length
                            ) or parameters.get(k1, 0.0) * length,
                            "solenoid_fields": {
                                "S0L": parameters.get(bs_field, 0.0) * length
                            },
                        },
                    }
                elif etype == "ELSeparator":
                    field = parameters.get(
                        _native_keyword(mapped_type, "field_amplitude"), 0.0
                    )
                    hkick = parameters.get(
                        _native_keyword(mapped_type, "horizontal_kick"), 0.0
                    )
                    vkick = parameters.get(
                        _native_keyword(mapped_type, "vertical_kick"), 0.0
                    )
                    kick = math.hypot(hkick, vkick)
                    if kick:
                        horizontal_field = field * hkick / kick
                        vertical_field = field * vkick / kick
                    else:
                        tilt = parameters.get("TILT", 0.0)
                        horizontal_field = field * math.sin(tilt)
                        vertical_field = field * math.cos(tilt)
                    elem_data = {
                        "hardware_type": mapped_type,
                        "simulation": {
                            "horizontal_field": horizontal_field,
                            "vertical_field": vertical_field,
                        },
                    }
                elif etype == "Match":
                    elem_data = {
                        "hardware_type": mapped_type,
                        "simulation": {
                            "apply": True,
                            "c_matrix": parameters["_VEC0"],
                            "r_matrix": parameters["_MAT6"],
                        },
                    }
                elif etype == "Taylor":
                    try:
                        c_matrix, r_matrix, t_matrix, u_matrix = _taylor_matrices(
                            parameters["_TAYLOR"]
                        )
                    except ValueError as exc:
                        warn(f"Could not import Bmad Taylor element {nam!r}: {exc}.")
                        continue
                    elem_data = {
                        "hardware_type": mapped_type,
                        "simulation": {
                            "apply": True,
                            "c_matrix": c_matrix,
                            "r_matrix": r_matrix,
                            "t_matrix": t_matrix,
                            "u_matrix": u_matrix,
                            "spin_taylor": parameters["_SPIN_TAYLOR"],
                        },
                    }
                elif etype in _COLLIMATOR_TYPES:
                    x1 = _native_keyword(mapped_type, "x1_limit")
                    x2 = _native_keyword(mapped_type, "x2_limit")
                    y1 = _native_keyword(mapped_type, "y1_limit")
                    y2 = _native_keyword(mapped_type, "y2_limit")
                    elem_data = {
                        "hardware_type": mapped_type,
                        "aperture": {
                            "horizontal_size": (
                                parameters.get(x1, 0.0)
                                + parameters.get(x2, 0.0)
                            ),
                            "vertical_size": (
                                parameters.get(y1, 0.0)
                                + parameters.get(y2, 0.0)
                            ),
                        },
                    }
                elif etype in _MULTIPOLE_TYPES:
                    poles = {}
                    for row in parameters.get("_MULTIPOLES", {}).get("data", []):
                        order = int(row["index"])
                        # An/Bn are the skew/normal coefficients. For an element
                        # written as KnL/Tn, Bmad supplies the equivalent pair
                        # rather than making us resolve the tilt ourselves.
                        # They relate to LAURA's integrated KnL by a factor n!.
                        normal = row.get("Bn", row.get("Bn (equiv)", 0.0)) or 0.0
                        skew = row.get("An", row.get("An (equiv)", 0.0)) or 0.0
                        if normal or skew:
                            scale = math.factorial(order)
                            poles[f"K{order}L"] = {
                                "order": order,
                                "normal": normal * scale,
                                "skew": skew * scale,
                            }
                    if not poles:
                        warn(
                            f"Bmad {etype} {nam!r} has no multipole content; skipping."
                        )
                    else:
                        highest = max(int(k[1:-1]) for k in poles)
                        hardware_type = _ORDER_TYPES.get(highest, "Magnet")
                        elem_data = {
                            "hardware_type": hardware_type,
                            "magnetic": {
                                "order": highest,
                                "length": length,
                                "multipoles": poles,
                            },
                        }
                elif etype == "AC_Kicker":
                    hkick = parameters.get("HKICK", 0.0) or 0.0
                    vkick = parameters.get("VKICK", 0.0) or 0.0
                    vertical = abs(vkick) > abs(hkick)
                    amplitude = vkick if vertical else hkick
                    simulation = {"field_amplitude": amplitude}
                    ac_data = parameters.get("_AC_KICKER", {})
                    frequencies = ac_data.get("frequencies", [])
                    if frequencies:
                        frequency, scale, phase = max(
                            frequencies, key=lambda row: abs(row[1])
                        )
                        simulation.update(
                            {
                                "field_amplitude": amplitude * scale,
                                "frequency": frequency,
                                "phase": phase * 360,
                            }
                        )
                        if len(frequencies) > 1:
                            warn(
                                f"Bmad AC_Kicker {nam!r} has multiple frequencies; "
                                "LAURA stores one, so the largest-amplitude component "
                                "was imported."
                            )
                    if ac_data.get("amp_vs_time"):
                        warn(
                            f"Bmad AC_Kicker {nam!r} uses amp_vs_time; LAURA has no "
                            "equivalent sampled-time waveform, so it was not imported."
                        )
                    elem_data = {
                        "hardware_type": (
                            "Vertical_AC_Dipole" if vertical else "Horizontal_AC_Dipole"
                        ),
                        "simulation": simulation,
                    }
                    if hkick and vkick:
                        warn(
                            f"Bmad AC_Kicker {nam!r} kicks in both planes "
                            f"(hkick={hkick}, vkick={vkick}); LAURA models a single "
                            "plane per element, so only the larger kick is imported."
                        )
                elif etype == "BeamBeam":
                    elem_data = {
                        "hardware_type": mapped_type,
                        "simulation": {
                            "n_particles": parameters.get("N_PARTICLE"),
                            "charge": parameters.get("CHARGE"),
                            "horizontal_sigma": parameters.get("SIG_X"),
                            "vertical_sigma": parameters.get("SIG_Y"),
                            "width": parameters.get("SIG_Z"),
                        },
                    }
                elif etype in ("Marker", "Monitor", "Instrument"):
                    markelem = {
                        "physical": dict(phys_common),
                        "name": nam,
                        "hardware_type": mapped_type,
                        "machine_area": getattr(self, "machine_area", "Lattice"),
                        **_aperture(parameters),
                    }
                    self.laura_elems[universe][b].update(
                        {nam: getattr(LAURA_elements, markelem["hardware_type"])(**markelem)}
                    )
                elif etype == "Beginning_Ele":
                    twiss = parameters.get("_TWISS", {})
                    if twiss:
                        self._warn_unsupported_coupling(twiss, parameters, nam)
                        physical = dict(phys_common)
                        physical.update(
                            _floor_to_physical(parameters.get("_FLOOR", {}))
                        )
                        markelem = {
                            "physical": physical,
                            "name": nam,
                            "hardware_type": "TwissMatch",
                            "machine_area": getattr(self, "machine_area", "Lattice"),
                            "simulation": {
                                "beta_x": twiss["beta_a"],
                                "beta_y": twiss["beta_b"],
                                "alpha_x": twiss["alpha_a"],
                                "alpha_y": twiss["alpha_b"],
                                "eta_x": twiss["eta_x"],
                                "eta_y": twiss["eta_y"],
                                "eta_xp": twiss["etap_x"],
                                "eta_yp": twiss["etap_y"],
                                "from_beam": False,
                            },
                        }
                        self.laura_elems[universe][b].update(
                            {nam: LAURA_elements.TwissMatch(**markelem)}
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
                            "machine_area": getattr(self, "machine_area", "Lattice"),
                            **_aperture(parameters),
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
                        hardware_type = elems[nam]["hardware_type"]
                        self.laura_elems[universe][b].update(
                            {nam: getattr(LAURA_elements, hardware_type)(**elems[nam])}
                        )
        return self.laura_elems[universe]

    def _reference_energy(self, universe: int, branch: str) -> float | None:
        """Reference total energy [eV] at the start of ``branch``.        """
        types = self.types.get(universe, {}).get(branch, [])
        for index, etype in enumerate(types):
            if etype == "Beginning_Ele":
                e_tot = self.params[universe][branch][index].get("E_TOT")
                return float(e_tot) if e_tot is not None else None
        return None

    def _warn_unsupported_coupling(self, twiss: Dict[str, Any], attributes: Dict[str, Any], name: str) -> None:
        """Warn that Bmad's transverse coupling description is not imported.        """
        if twiss.get("mode_flip") or attributes.get("MODE_FLIP"):
            warn(
                f"Bmad lattice has mode_flip=True at {name!r}: currently unsupported."
            )
        coupling = attributes.get("_COUPLING", {})
        cmat = [coupling.get(f"c_mat{ij}", 0.0) for ij in ("11", "12", "21", "22")]
        if any(cmat):
            warn(
                f"Bmad lattice has transverse coupling at {name!r} "
                f"(cmat = {cmat}, gamma_c = {coupling.get('gamma_c')}): "
                "currently unsupported."
            )

    def create_section(self, universe: int, branch: str) -> Dict[str, SectionLattice]:
        if not self.laura_elems[universe][branch]:
            self.create_laura_element_dictionary(universe)
        elems = self.laura_elems[universe][branch]
        self.elements = elems
        order = [n for n, e in elems.items() if not e.is_subelement()]
        branch_params = self.branch_params.get(universe, {}).get(branch, {})
        geometry = branch_params.get("param_geometry")
        seclat = SectionLattice(
            order=order, elements=ElementList(elements=elems), name=branch,
            functional_definitions=self.functional_definitions,
            geometry=str(geometry).lower() if geometry else None,
            reference_energy=self._reference_energy(universe, branch),
        )
        seclat.resolve_positions(elems)
        for name, elem in elems.items():
            if elem.is_subelement():
                parent = elems.get(elem.subelement)
                if parent is not None and parent.physical.middle is not None:
                    elem.physical.s = parent.physical.s
                    elem.physical.s_point = parent.physical.s_point
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
            particle=self._particle(universe),
        )

    def _particle(self, universe: int) -> str | None:
        """Design particle species."""
        for branch_params in self.branch_params.get(universe, {}).values():
            particle = branch_params.get("param_particle")
            if particle:
                return str(particle)
        return None

    def create_machine_model(self, min_section_length: int = 5) -> MachineModel:
        """Build a model with one layout per Tao universe.
        Branches become sections. Elements with the same name are given a
        ``name__layout`` copy when shared between branches because
        :class:`MachineModel` stores one placement per name.

        Parameters
        ----------
        min_section_length: int
            Sections are only created if they are longer than this value.

        Returns
        -------
        MachineModel
            The full machine model containing all branches and universes.
        """
        if min_section_length < 1:
            raise ValueError("min_section_length must be at least 1.")

        layout_names = {}
        if self.tao_init:
            text = Path(self.tao_init).read_text()
            layout_names = {
                int(universe): Path(filename).stem
                for universe, filename in re.findall(
                    r"design_lattice\((\d+)\)%file\s*=\s*['\"]([^'\"]+)['\"]",
                    text,
                    re.I,
                )
            }

        elements = {}
        section_definitions = {}
        layout_definitions = {}
        skipped_sections = []

        for universe in sorted(self.branches):
            default_name = (
                Path(self.lattice_file).stem if self.lattice_file else str(universe)
            )
            layout_name = layout_names.get(universe, default_name)
            if layout_name in layout_definitions:
                layout_name = f"{layout_name}_{universe}"
            layout = self.create_layout(universe, name=layout_name)
            layout_sections = []
            for source_name, section in layout.sections.items():
                if len(section.order) < min_section_length:
                    skipped_sections.append(f"{layout_name}/{source_name}")
                    continue
                section_name = source_name
                if section_name in section_definitions:
                    section_name = f"{layout_name}_{section_name}"
                merge_layout_elements(
                    elements,
                    section_definitions,
                    section_name,
                    section.elements.elements.items(),
                    section.order,
                    layout_name,
                )
                layout_sections.append(section_name)
            if layout_sections:
                layout_definitions[layout_name] = layout_sections

        if skipped_sections:
            warn(
                "Skipped BMAD branches shorter than min_section_length="
                f"{min_section_length}: {', '.join(skipped_sections)}"
            )
        if not layout_definitions:
            raise ValueError(
                "No BMAD layouts meet min_section_length="
                f"{min_section_length}."
            )

        source = self.tao_init or self.lattice_file
        return MachineModel(
            elements=elements,
            section={"sections": section_definitions},
            layout={
                "layouts": layout_definitions,
                "default_layout": next(iter(layout_definitions)),
            },
            master_lattice=str(Path(source).resolve().parent),
            functional_definitions=self.functional_definitions,
        )

    def export_yaml(
        self,
        path: str,
        source: Union[SectionLattice, MachineLayout, MachineModel],
        position_mode: PositionMode = "s",
    ) -> None:
        export_machine_combined_file(path, source, position_mode=position_mode)
