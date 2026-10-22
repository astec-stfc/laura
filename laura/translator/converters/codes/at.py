"""Accelerator Toolbox (pyAT): what the exporter cannot write, and the importer."""

from copy import deepcopy
from math import degrees
from typing import Any, Dict, Optional
from warnings import warn

import numpy as np
from pydantic import ConfigDict, model_validator

import laura.models.element as laura_elements

from ...utils.ac_dipole import MV_PER_VOLT
from ...utils.alignment import from_frame
from ...utils.at import (
    AT_FRAME,
    CLIGHT,
    at_matrices,
    at_pivot,
    cavity_phase,
    integrated,
)
from ...utils.functions import number_repeated_names
from .importer import LatticeImporter, apply_misalignment

at_unsupported = [
    "CombinedSolenoidQuadrupole",
    "FEL_Modulator",
    "RFMultipole",
    "NonLinearLens",
    "TwissMatch",
    "ElectrostaticSeparator",
    "Wire",
    "BeamBeam",
    "Wakefield",
    "Laser",
    "Plasma",
    "ActivePlasmaLens",
    "Charge",
    "Scatter",
]

_CLASSES = {
    "Marker": laura_elements.Marker,
    "Monitor": laura_elements.BeamPositionMonitor,
    "Dipole": laura_elements.Dipole,
    "Quadrupole": laura_elements.Quadrupole,
    "Sextupole": laura_elements.Sextupole,
    "Octupole": laura_elements.Octupole,
    "Corrector": laura_elements.CombinedCorrector,
    "RFCavity": laura_elements.RFCavity,
    "CrabCavity": laura_elements.CrabCavity,
    "Wiggler": laura_elements.Wiggler,
    "M66": laura_elements.MatrixTransform,
    "VariableThinMultipole": laura_elements.HorizontalACDipole,
}
"""AT class name -> LAURA class; ``Multipole``/``ThinMultipole`` go by order."""

_PASS_METHODS = {
    "SolenoidLinearPass": laura_elements.Solenoid,
    "MatrixTijkPass": laura_elements.MatrixTransform,
}
"""PassMethod -> LAURA class, for the plain ``Element``\\ s the exporter builds."""

_ORDERS = {
    1: laura_elements.Quadrupole,
    2: laura_elements.Sextupole,
    3: laura_elements.Octupole,
}


def _misalignment(elem: Any, length: float) -> Dict[str, float]:
    """Invert :func:`~laura.translator.conversion_rules.codes.at_conversion.misalign`,
    as :func:`apply_misalignment` arguments."""
    get = lambda key: float(getattr(elem, key, 0.0))  # noqa: E731
    angle, frame = get("BendingAngle"), get("tilt_frame")
    keys = ("dx", "dy", "dz", "pitch", "yaw", "tilt")
    if frame and any(get(k) for k in keys) and _pyat_frame(elem):
        warn(
            f"{elem.FamName}: pyAT's own tilt_frame applies the alignment errors "
            "before the roll, which no LAURA misalignment reproduces; imported "
            "as if LAURA had written it."
        )
    errors = from_frame(
        (get("dx"), get("dy"), get("dz")),
        (get("pitch"), get("yaw"), get("tilt")),
        tilt=frame,
        **at_pivot(length, angle),
    )
    if not angle:  # the body roll is the whole tilt
        frame, errors["dz_rot"] = frame + errors["dz_rot"], 0.0
    return {"roll": frame, **errors}


def _pyat_frame(elem: Any) -> bool:
    """Whether pyAT's ``transform_elem`` built ``elem``'s frame roll, rather
    than :func:`~laura.translator.conversion_rules.codes.at_conversion.misalign`."""
    import at

    native = deepcopy(elem)
    at.transform_elem(
        native,
        *(getattr(elem, k) for k in ("dx", "dy", "dz", "tilt", "pitch", "yaw")),
        tilt_frame=elem.tilt_frame,
        reference=elem.ReferencePoint,
    )
    return all(
        np.allclose(getattr(native, k), getattr(elem, k, np.nan))
        for k in ("R1", "T1", "R2", "T2")
    )


class ATLatticeImporter(LatticeImporter):
    """Import a pyAT ``Lattice`` into LAURA's common lattice lifecycle."""

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    name: Optional[str] = None
    """Section/layout name; defaults to the lattice's own."""

    machine_area: str = "Lattice"

    lattice: Any = None
    """``at.Lattice``. pyAT is only required when the importer is used."""

    source_file: Optional[str] = None
    """Any file ``at.load_lattice`` reads (``.m``, ``.mat``, ``.json``, ...),
    used instead of ``lattice``."""

    elements: Dict = {}

    @model_validator(mode="after")
    def _load_source(self):  # noqa: N804
        if (self.lattice is None) == (self.source_file is None):
            raise ValueError("Give exactly one of lattice or source_file.")
        if self.source_file:
            try:
                import at
            except ImportError as exc:
                raise ImportError(
                    "accelerator-toolbox is not installed. Install with: "
                    'pip install "laura-accelerator[at]"'
                ) from exc
            object.__setattr__(self, "lattice", at.load_lattice(self.source_file))
            object.__setattr__(self, "source_file", None)
        return self

    def _default_name(self) -> str:
        return self.name or getattr(self.lattice, "name", "") or "Lattice"

    def _reference_energy(self) -> Optional[float]:
        return float(self.lattice.energy)

    def create_laura_element_dictionary(self) -> Dict:
        ring = self.lattice
        rest_energy = ring.particle.rest_energy
        brho = (ring.energy**2 - rest_energy**2) ** 0.5 / CLIGHT
        names = number_repeated_names([e.FamName for e in ring])
        self.elements = {}
        s = 0.0
        for elem, name in zip(ring, names):
            length = float(getattr(elem, "Length", 0.0))
            s += length
            native = type(elem).__name__
            if native == "Drift":
                continue
            laura_type = _PASS_METHODS.get(elem.PassMethod) or _CLASSES.get(native)
            if native in ("Multipole", "ThinMultipole"):
                laura_type = self._multipole_type(elem)
            if laura_type is None:
                warn(
                    f"Could not import AT element type {native!r} for {name!r}; skipping."
                )
                continue
            data = {
                "name": name,
                "machine_area": self.machine_area,
                "physical": {"s": s, "s_point": "end", "length": length},
            }
            laura_type = self._fill(data, elem, laura_type, length, brho)
            if laura_type is not laura_elements.MatrixTransform:
                apply_misalignment(data, laura_type, **_misalignment(elem, length))
            if "aperture" in laura_type.model_fields:
                self._aperture(data, elem, name)
            self.elements[name] = laura_type(**data)
        return self.elements

    @staticmethod
    def _multipole_type(elem) -> type:
        """By highest order; a pure dipole kick is a corrector."""
        orders = [
            n
            for polynom in (elem.PolynomA, elem.PolynomB)
            for n, value in enumerate(polynom)
            if value
        ]
        if not orders or max(orders) == 0:
            return laura_elements.CombinedCorrector
        return _ORDERS.get(max(orders), laura_elements.Magnet)

    @staticmethod
    def _multipoles(elem, length: float) -> dict:
        normal = integrated(elem.PolynomB, length)
        skew = integrated(elem.PolynomA, length)
        if any(n > 4 for n in (*normal, *skew)):
            warn(
                f"{elem.FamName}: LAURA stores multipoles only through K4L; higher orders were skipped."
            )
        return {
            f"K{n}L": {
                "order": n,
                "normal": normal.get(n, 0.0),
                "skew": skew.get(n, 0.0),
            }
            for n in sorted({*normal, *skew})
            if n <= 4
        }

    def _fill(
        self, data: dict, elem, laura_type: type, length: float, brho: float
    ) -> type:
        """Add the type's own fields to ``data``; return the class to build,
        which an AC dipole's plane can change."""
        if laura_type is laura_elements.Dipole:
            multipoles = self._multipoles(elem, length)
            if multipoles.pop("K0L", {}).get("normal"):
                warn(
                    f"{elem.FamName}: AT's PolynomB[0] on a Dipole is a field error; not imported."
                )
            data["magnetic"] = {
                "length": length,
                "multipoles": {
                    "K0L": {"order": 0, "normal": float(elem.BendingAngle)},
                    **multipoles,
                },
                "entrance_edge_angle": float(elem.EntranceAngle),
                "exit_edge_angle": float(elem.ExitAngle),
                "gap": float(getattr(elem, "FullGap", 0.0)),
                "edge_field_integral_entrance": float(getattr(elem, "FringeInt1", 0.0)),
                "edge_field_integral_exit": float(getattr(elem, "FringeInt2", 0.0)),
            }
            if elem.PassMethod != "BndMPoleSymplectic4E2Pass":
                data["simulation"] = {
                    "edge1_effects": getattr(elem, "FringeBendEntrance", 1) != 0,
                    "edge2_effects": getattr(elem, "FringeBendExit", 1) != 0,
                }
        elif laura_type is laura_elements.CombinedCorrector:
            if hasattr(elem, "KickAngle"):
                h, v = (float(k) for k in elem.KickAngle)
            else:  # a thin multipole's PolynomB[0] kicks toward -x
                h, v = -float(elem.PolynomB[0]), float(elem.PolynomA[0])
            data["magnetic"] = {
                "length": length,
                "horizontal_kick": h,
                "vertical_kick": v,
            }
        elif laura_type in (*_ORDERS.values(), laura_elements.Magnet):
            data["magnetic"] = {
                "length": length,
                "multipoles": self._multipoles(elem, length),
            }
        elif laura_type in (laura_elements.RFCavity, laura_elements.CrabCavity):
            crab = laura_type is laura_elements.CrabCavity
            voltage = float(elem.Voltages[0]) if crab else float(elem.Voltage)
            if crab and elem.Voltages[1]:
                warn(
                    f"{elem.FamName}: LAURA's crab cavity is horizontal; the vertical voltage was not imported."
                )
            frequency = float(elem.Frequency)
            data["cavity"] = {
                "frequency": frequency,
                "phase": cavity_phase(
                    float(getattr(elem, "TimeLag", 0.0)),
                    frequency,
                    crest=-90.0 if crab else 90.0,
                ),
            }
            data["simulation"] = {"field_amplitude": voltage}
        elif laura_type is laura_elements.Wiggler:
            data["magnetic"] = {
                "length": length,
                "period": float(elem.Lw),
                "peak_magnetic_field": float(elem.Bmax),
                "num_periods": round(length / elem.Lw),
                "helical": int(getattr(elem, "NVharm", 0)) > 0,
            }
        elif laura_type is laura_elements.Solenoid:
            charge = self.lattice.particle.charge
            data["magnetic"] = {
                "length": length,
                "fields": {"S0L": float(elem.K) * length * brho * charge},
            }
        elif laura_type is laura_elements.MatrixTransform:
            c, r, t = at_matrices(
                getattr(elem, "T2", np.zeros(6)),
                elem.M66,
                getattr(elem, "Tijk", np.zeros((6, 6, 6))),
                AT_FRAME.T,
            )
            data["simulation"] = {"c_matrix": c, "r_matrix": r, "t_matrix": t}
        elif laura_type is laura_elements.HorizontalACDipole:
            vertical = getattr(elem, "AmplitudeB", None) is None
            plane = "A" if vertical else "B"
            kick = float(np.ravel(getattr(elem, f"Amplitude{plane}"))[0])
            data["simulation"] = {
                # see build_ac_dipole: the amplitude is a kick, PolynomB's toward -x
                "field_amplitude": kick * brho / MV_PER_VOLT * (1 if vertical else -1),
                "frequency": float(getattr(elem, f"Frequency{plane}")),
                "phase": degrees(float(getattr(elem, f"Phase{plane}", 0.0))),
                "ramp": [int(r) for r in getattr(elem, "Ramps", (0, 0, 0, 0))],
            }
            if vertical:
                return laura_elements.VerticalACDipole
        return laura_type

    @staticmethod
    def _aperture(data: dict, elem, name: str) -> None:
        if hasattr(elem, "EApertures"):
            rx, ry = (float(r) for r in elem.EApertures)
            shape = "circular" if rx == ry else "elliptical"
        elif hasattr(elem, "RApertures"):
            xmin, xmax, ymin, ymax = (float(r) for r in elem.RApertures)
            if xmin != -xmax or ymin != -ymax:
                warn(f"{name}: the off-centre aperture offset was not represented.")
            rx, ry, shape = (xmax - xmin) / 2, (ymax - ymin) / 2, "rectangular"
        else:
            return
        data["aperture"] = {
            "shape": shape,
            "horizontal_size": 2 * rx,
            "vertical_size": 2 * ry,
        }
