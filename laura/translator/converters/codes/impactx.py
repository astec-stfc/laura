"""ImpactX: the importer, from the element dicts ``to_dict()`` writes or an
inputs file."""

import json
import re
import subprocess
import sys
import tempfile
from math import copysign, pi, radians, sqrt
from pathlib import Path
from typing import Any, Dict, Optional
from warnings import warn

import numpy as np
from pydantic import ConfigDict, model_validator

import laura.models.element as laura_elements
from laura.utils.naming import number_repeated_names

from ...conversion_rules.codes.impactx_conversion import reference
from .importer import LatticeImporter, apply_misalignment

_DRIFTS = ("Drift", "ChrDrift", "ExactDrift")
_BENDS = ("Sbend", "ExactSbend", "CFbend", "ExactCFbend")
_ORDERS = {
    1: laura_elements.Quadrupole,
    2: laura_elements.Sextupole,
    3: laura_elements.Octupole,
}
_HWANG_LEE = {"K0": pi**2 / 6, "K1": 0.0, "K3": 1 / 6, "K4": 0.0, "K5": 0.0, "K6": 0.0}
"""``DipEdge``'s Hwang-Lee coefficients and their ImpactX defaults."""

_READ_INPUTS = Path(__file__).with_name("impactx_inputs.py")


def _stem(name: str) -> str:
    """``name`` without the suffix the exporter gives a part of an element."""
    return re.sub(r"_(in|out|entry|exit|m\d+)$", "", name or "")


def _parts(dicts: list, i: int) -> int:
    """How many dicts from ``dicts[i]`` make one element: the exporter's
    ``X_in``/kick/``X_out``, ``X_entry``/``X``/``X_exit`` aperture and
    ``X_m1``... thin multipoles, or a bend body with its ``DipEdge``\\ s."""
    names = [d.get("name") or "" for d in dicts[i : i + 3]]
    types = [d["type"] for d in dicts[i : i + 3]]
    stem = _stem(names[0])
    if names == [f"{stem}_in", stem, f"{stem}_out"] and not dicts[i + 1].get("ds"):
        return 3
    if names == [f"{stem}_entry", stem, f"{stem}_exit"] and types[0] == "Aperture":
        return 3
    if types[0] == "Multipole" and names[0] != stem:
        run = 1
        while (
            run < len(dicts) - i
            and dicts[i + run]["type"] == "Multipole"
            and _stem(dicts[i + run].get("name")) == stem
        ):
            run += 1
        return run
    edges = types[0] == "DipEdge"
    if types[edges : edges + 1] and types[edges] in _BENDS:
        return edges + 1 + (types[edges + 1 : edges + 2] == ["DipEdge"])
    return 1


class ImpactXLatticeImporter(LatticeImporter):
    """Import an ImpactX lattice into LAURA's common lattice lifecycle.

    Inverts :mod:`~laura.translator.conversion_rules.codes.impactx_conversion`,
    regrouping the parts it splits one element into; a ``DipEdge`` merges
    into the bend beside it.
    """

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    name: str = "Lattice"

    machine_area: str = "Lattice"

    lattice: Any = None
    """ImpactX element dicts, as ``to_dict()`` writes them, or a
    ``KnownElementsList``."""

    source_file: Optional[str] = None
    """ImpactX inputs file (``.in``)."""

    energy: Optional[float] = None
    """Total energy [eV] of the reference particle, which ImpactX keeps on the
    beam."""

    particle: str = "electron"

    elements: Dict = {}

    @model_validator(mode="after")
    def _load_source(self):  # noqa: N804
        if (self.lattice is None) == (self.source_file is None):
            raise ValueError("Give exactly one of lattice or source_file.")
        if self.source_file:
            source = Path(self.source_file).resolve()
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp, "lattice.json")
                read = subprocess.run(
                    [sys.executable, "-I", str(_READ_INPUTS), str(source), str(out)],
                    cwd=source.parent,
                    capture_output=True,
                    text=True,
                )
                if read.returncode:
                    raise RuntimeError(
                        f"ImpactX could not read {self.source_file}:\n{read.stderr}"
                    )
                loaded = json.loads(out.read_text())
            particle = loaded["particle"] or self.particle
            object.__setattr__(self, "lattice", loaded["elements"])
            object.__setattr__(self, "particle", particle)
            if (
                loaded["kin_energy"] is not None
            ):  # a restart reads it from the beam file
                mass = reference(None, particle)["mass"]
                energy = mass + loaded["kin_energy"] * 1e6
                object.__setattr__(self, "energy", energy)
            object.__setattr__(self, "source_file", None)
        if hasattr(self.lattice, "to_dicts"):
            object.__setattr__(self, "lattice", self.lattice.to_dicts())
        return self

    def _default_name(self) -> str:
        return self.name

    def _reference_energy(self) -> Optional[float]:
        return self.energy

    def _ref(self, key: str, name: str) -> float:
        """``key`` of the reference particle, which ``name`` needs."""
        ref = reference(self.energy, self.particle)
        if key not in ref:
            raise ValueError(f"{name}: give the energy to import it.")
        return ref[key]

    def create_laura_element_dictionary(self) -> Dict:
        dicts, built, s, i = list(self.lattice), [], 0.0, 0
        while i < len(dicts):
            count = _parts(dicts, i)
            group, i = dicts[i : i + count], i + count
            length = sum(float(d.get("ds", 0.0)) for d in group)
            if length < 0:
                raise ValueError(
                    f"{group[0].get('name')}: LAURA has no negative lengths, "
                    "as in ImpactX's inverse elements."
                )
            s += length
            body = next(
                (d for d in group if d["type"] not in ("DipEdge", *_DRIFTS)), group[0]
            )
            if body["type"] in _DRIFTS:
                continue
            name = _stem(body.get("name")) if count > 1 else body.get("name")
            data = {
                "name": name or body["type"].lower(),
                "machine_area": self.machine_area,
                "physical": {"s": s, "s_point": "end", "length": length},
            }
            laura_type = self._fill(data, body, group, length)
            if laura_type is None:
                warn(
                    f"Could not import ImpactX element type {body['type']!r} "
                    f"for {data['name']!r}; skipping."
                )
                continue
            if laura_type not in (laura_elements.Aperture, laura_elements.Marker):
                rotation = radians(float(body.get("rotation", 0.0)))
                apply_misalignment(
                    data, laura_type, body.get("dx", 0.0), body.get("dy", 0.0), rotation
                )
            bore = body.get("aperture_x", 0.0), body.get("aperture_y", 0.0)
            if any(bore) and laura_type is not laura_elements.Aperture:
                data["aperture"] = {
                    "shape": "circular" if bore[0] == bore[1] else "elliptical",
                    "horizontal_size": bore[0],
                    "vertical_size": bore[1],
                }
            built.append((laura_type, data))
        names = number_repeated_names([data["name"] for _, data in built])
        self.elements = {}
        for (laura_type, data), name in zip(built, names):
            self.elements[name] = laura_type(**{**data, "name": name})
        return self.elements

    def _fill(self, data: dict, d: dict, group: list, length: float) -> type | None:
        """Add the type's own fields to ``data``; return the class to build."""
        kind, name = d["type"], data["name"]
        # unit 1 strengths are fields, in T/m^n or T m
        scale = 1 / self._ref("brho", name) if d.get("unit") in (1, "T-m") else 1.0
        if kind in _BENDS:
            return self._dipole(data, d, group, length, scale)
        if kind in ("Quad", "ChrQuad", "ExactQuad"):
            normal, skew = [0.0, d["k"] * scale * length], []
        elif kind == "ExactMultipole":
            normal = [k * scale * length for k in d["k_normal"]]
            skew = [k * scale * length for k in d["k_skew"]]
        elif kind == "Multipole":
            normal = [0.0] * max(m["multipole"] for m in group)
            skew = list(normal)
            for m in group:
                normal[m["multipole"] - 1] = m["K_normal"]
                skew[m["multipole"] - 1] = m["K_skew"]
        elif kind == "Kicker":
            data["magnetic"] = {
                "horizontal_kick": d["xkick"] * scale,
                "vertical_kick": d["ykick"] * scale,
            }
            return laura_elements.CombinedCorrector
        elif kind == "Sol" or (kind == "ChrAcc" and not d["ez"]):
            ks = d["ks"] if kind == "Sol" else d["bz"] / self._ref("beta_gamma", name)
            data["magnetic"] = {
                "length": length,
                "fields": {"S0L": ks * length * self._ref("brho", name)},
            }
            return laura_elements.Solenoid
        elif kind == "ShortRF":
            ref = reference(None, self.particle)
            data["cavity"] = {"frequency": d["freq"], "phase": -d["phase"]}
            data["simulation"] = {
                "field_amplitude": d["V"] * ref["mass"] / abs(ref["charge"])
            }
            return laura_elements.RFCavity
        elif kind == "NonlinearLens":
            data["magnetic"] = {
                "length": length,
                "integrated_strength": d["knll"],
                "dimensional_parameter": d["cnll"],
            }
            return laura_elements.NonLinearLens
        elif kind == "Aperture":
            if (
                d.get("action", "transmit") != "transmit"
                or d.get("repeat_x")
                or d.get("repeat_y")
            ):
                warn(
                    f"{name}: an absorbing or repeating aperture was imported as a plain one."
                )
            data["aperture"] = {
                "shape": d.get("shape", "rectangular"),
                "horizontal_size": d["aperture_x"],
                "vertical_size": d["aperture_y"],
                "horizontal_offset": d.get("dx", 0.0),
                "vertical_offset": d.get("dy", 0.0),
            }
            return laura_elements.Aperture
        elif kind == "LinearMap":
            beta = 1.0
            if self.energy:
                beta_gamma = self._ref("beta_gamma", name)
                beta = beta_gamma / sqrt(1 + beta_gamma**2)
            else:
                warn(
                    f"{name}: no energy given; the longitudinal terms assume beta = 1."
                )
            r = d["R"].to_numpy() if hasattr(d["R"], "to_numpy") else d["R"]
            frame = np.array([1, 1, 1, 1, -1 / beta, -beta])
            data["simulation"] = {
                "r_matrix": np.asarray(r, dtype=float) * frame / frame[:, None]
            }
            return laura_elements.MatrixTransform
        elif kind in ("Marker", "BeamMonitor"):
            return laura_elements.Marker
        else:
            return None
        multipoles = self._multipoles(name, normal, skew)
        data["magnetic"] = {"length": length, "multipoles": multipoles}
        orders = [m["order"] for m in multipoles.values()]
        return _ORDERS.get(max(orders, default=1), laura_elements.Magnet)

    @staticmethod
    def _multipoles(name: str, normal: list, skew: list) -> dict:
        """LAURA's ``K{n}L`` from integrated strengths indexed by order."""
        skew = list(skew) + [0.0] * (len(normal) - len(skew))
        strengths = [
            (n, kn, ks) for n, (kn, ks) in enumerate(zip(normal, skew)) if kn or ks
        ]
        if any(n > 4 for n, _, _ in strengths):
            warn(
                f"{name}: LAURA stores multipoles only through K4L; higher orders were skipped."
            )
        return {
            f"K{n}L": {"order": n, "normal": float(kn), "skew": float(ks)}
            for n, kn, ks in strengths
            if n <= 4
        }

    def _dipole(
        self, data: dict, d: dict, group: list, length: float, scale: float
    ) -> type:
        kind = d["type"]
        normal, skew = [0.0], []
        if kind == "ExactSbend":
            angle = radians(d["phi"])
            if d.get("B"):  # B sets the radius and only the sign of the angle
                angle = copysign(angle, d["B"] / self._ref("brho", data["name"]))
        elif kind == "ExactCFbend":
            normal = [k * scale * length for k in d["k_normal"]]
            skew = [k * scale * length for k in d["k_skew"]]
            angle = normal[0]
        else:
            angle = length / d["rc"] if d["rc"] else 0.0  # rc = 0 is no field
            if kind == "CFbend":
                normal = [0.0, d["k"] * length]
        normal[0] = angle
        magnetic = {
            "length": length,
            "multipoles": self._multipoles(data["name"], normal, skew),
        }
        simulation = {}
        body = group.index(d)
        for edge, location in ((group[:body], "entrance"), (group[body + 1 :], "exit")):
            plane = "1" if location == "entrance" else "2"
            if not edge:
                simulation[f"edge{plane}_effects"] = False
                continue
            edge = edge[0]
            magnetic[f"{location}_edge_angle"] = edge["psi"]
            if edge.get("g"):
                magnetic["gap" if location == "entrance" else "exit_gap"] = edge["g"]
                magnetic[f"edge_field_integral_{location}"] = edge.get("K2", 0.0)
            if edge.get("model") == "nonlinear_hwang_lee":
                for k, default in _HWANG_LEE.items():
                    if edge.get(k, default) != default:
                        magnetic[f"fringe_{k.lower()}"] = edge[k]
        data["magnetic"] = magnetic
        if simulation:
            data["simulation"] = simulation
        return laura_elements.Dipole
