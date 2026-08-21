from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from warnings import warn

import numpy as np
from pydantic import BaseModel, ConfigDict, PrivateAttr, model_validator

import laura.models.element as LAURA_elements
from laura.models.elementList import ElementList, MachineLayout, SectionLattice
from ....Exporters.YAML import PositionMode, export_machine_combined_file

xsuite_unsupported = [
    "Laser",
    "Wakefield",
    "ActivePlasmaLens",
]

_TYPE_MAP = {
    "Bend": LAURA_elements.Dipole,
    "RBend": LAURA_elements.Dipole,
    "DipoleEdge": LAURA_elements.Marker,
    "Quadrupole": LAURA_elements.Quadrupole,
    "Sextupole": LAURA_elements.Sextupole,
    "Octupole": LAURA_elements.Octupole,
    "Multipole": LAURA_elements.Magnet,
    "Magnet": LAURA_elements.Magnet,
    "Solenoid": LAURA_elements.Solenoid,
    "UniformSolenoid": LAURA_elements.Solenoid,
    "Cavity": LAURA_elements.RFCavity,
    "NonLinearLens": LAURA_elements.NonLinearLens,
    "Marker": LAURA_elements.Marker,
    "BeamPositionMonitor": LAURA_elements.Beam_Position_Monitor,
    "BeamProfileMonitor": LAURA_elements.Screen,
    "BeamSizeMonitor": LAURA_elements.Screen,
    "BeamStatsMonitor": LAURA_elements.Screen,
    "ParticlesMonitor": LAURA_elements.Screen,
    "LastTurnsMonitor": LAURA_elements.Screen,
    "LimitEllipse": LAURA_elements.Collimator,
    "LimitRect": LAURA_elements.Collimator,
    "LimitRectEllipse": LAURA_elements.Collimator,
    "LimitRacetrack": LAURA_elements.Collimator,
    "LimitPolygon": LAURA_elements.Collimator,
    "SecondOrderTaylorMap": LAURA_elements.MatrixTransform,
    "CrabCavity": LAURA_elements.CrabCavity,
    "Wire": LAURA_elements.Wire,
    "RFMultipole": LAURA_elements.RFMultipole,
    "BeamBeamBiGaussian2D": LAURA_elements.BeamBeam,
}
_AC_DIPOLE_PLANES = {
    "h": LAURA_elements.Horizontal_AC_Dipole,
    "v": LAURA_elements.Vertical_AC_Dipole,
}
# Xtrack fields holding a strength *per metre*, which LAURA stores integrated.
_PER_METRE_FIELDS = (
    tuple(f"k{order}" for order in range(5))
    + tuple(f"k{order}s" for order in range(5))
    + ("ks",)
)
_MAGNET_ORDERS = {
    "Bend": 0,
    "RBend": 0,
    "Quadrupole": 1,
    "Sextupole": 2,
    "Octupole": 3,
}
_ORDER_TYPES = {
    0: LAURA_elements.Dipole,
    1: LAURA_elements.Quadrupole,
    2: LAURA_elements.Sextupole,
    3: LAURA_elements.Octupole,
}
_LOSSY_CONVERSIONS = {
    "DipoleEdge": "no adjacent Bend/RBend was found, so its edge-focusing "
    "parameters (e1, hgap, fint) were not represented",
    "BeamPositionMonitor": "sampling and turn configuration was not represented",
    "BeamProfileMonitor": "sampling and profile-bin configuration was not represented",
    "BeamSizeMonitor": "beam-size statistics were reduced to a Screen",
    "BeamStatsMonitor": "weighted beam statistics were reduced to a Screen",
    "ParticlesMonitor": "particle-coordinate logging was reduced to a Screen",
    "LastTurnsMonitor": "particle-loss history was reduced to a Screen",
    "LimitRectEllipse": "the compound shape was reduced to its bounding size",
    "LimitRacetrack": "the racetrack shape was reduced to its bounding size",
    "LimitPolygon": "the polygon was reduced to its bounding size",
    "ACDipole": "Xtrack's freq is a tune-like quantity (2*pi per turn) and was "
    "stored as-is in simulation.frequency, which LAURA holds in Hz; multiply by "
    "the ring's revolution_frequency to convert",
    "BeamBeamBiGaussian2D": "the thin single-slice weak-strong model carries no "
    "bunch length, so simulation.width was not set",
    "SecondOrderTaylorMap": "Xtrack has no 3rd-order term, so simulation.u_matrix "
    "and spin_taylor were not set",
}


class XsuiteLatticeImporter(BaseModel):
    """Import an Xtrack line into LAURA's common lattice lifecycle."""

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    name: str = "Lattice"

    machine_area: str = "Lattice"

    line: Any = None
    """Xtrack line. Xtrack is only required when the importer is used."""

    initial_twiss: Optional[Any] = None
    """Optional ``xtrack.TwissInit`` instance."""

    source_file: Optional[str] = None
    """Xtrack ``Line``/``Environment`` JSON file, used instead of ``line``."""

    line_name: Optional[str] = None
    """Optional line selector for an Environment containing multiple lines."""

    use_sliced: bool = False
    """Import a sliced line's slices rather than the thick elements they came
    from. Off by default -- see :meth:`_unsliced`."""

    functional_definitions: Dict[str, Union[int, float]] = {}

    elements: Dict = {}
    sections: Dict = {}
    layouts: Dict = {}
    _expressions: Dict[str, str] = PrivateAttr(default_factory=dict)
    _source_lines: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _conflicting_symbols: set = PrivateAttr(default_factory=set)
    _raw_definitions: Dict[str, float] = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def _load_source(self):
        if (self.line is None) == (self.source_file is None):
            raise ValueError("Give exactly one of line or source_file.")
        if self.source_file:
            try:
                import xtrack as xt
            except ImportError as exc:
                raise ImportError(
                    "xsuite is not installed. Install with: "
                    'pip install "laura-accelerator[xsuite]"'
                ) from exc
            source_class = json.loads(Path(self.source_file).read_text()).get("__class__")
            loaded = (
                xt.Environment.from_json(
                    self.source_file, classes=(xt.ParticlesMonitor,)
                )
                if source_class == "Environment"
                else xt.Line.from_json(
                    self.source_file, classes=(xt.ParticlesMonitor,)
                )
            )
            object.__setattr__(self, "line", loaded)
            object.__setattr__(self, "source_file", None)
        if hasattr(self.line, "lines") and not hasattr(self.line, "element_names"):
            names = list(self.line.lines)
            if self.line_name:
                if self.line_name not in names:
                    raise KeyError(f"Xtrack line {self.line_name!r} was not found.")
                names = [self.line_name]
            self._source_lines = {
                name: self._unsliced(self.line.lines[name]) for name in names
            }
            object.__setattr__(self, "line", self._source_lines[names[0]])
        else:
            object.__setattr__(self, "line", self._unsliced(self.line))
        self._read_functional_definitions()
        return self

    @staticmethod
    def _multipole_type(native):
        """
        Resolve a thin ``Multipole`` to a specific magnet class.
        """
        orders = [
            order
            for values in (getattr(native, "knl", []), getattr(native, "ksl", []))
            for order, value in enumerate(values)
            if value
        ]
        if not orders:
            return LAURA_elements.Magnet
        return _ORDER_TYPES.get(max(orders), LAURA_elements.Magnet)

    @staticmethod
    def _acdipole_type(element_name: str, native):
        """Resolve an ``ACDipole`` to its horizontal or vertical LAURA class."""
        plane = str(getattr(native, "plane", "")).strip().lower()
        laura_type = _AC_DIPOLE_PLANES.get(plane)
        if laura_type is None:
            warn(
                f"Xtrack ACDipole {element_name!r} has plane {plane!r}, which is "
                "neither 'h' nor 'v'; importing it as a horizontal AC dipole."
            )
            laura_type = LAURA_elements.Horizontal_AC_Dipole
        return laura_type

    def _unsliced(self, line):
        """Prefer the thick line a sliced Xtrack line was built from.

        ``slice_thick_elements`` replaces each thick element with a sequence of
        ``ThinSlice*``/``DriftSlice*``. Xtrack keeps the pre-slicing view on
        ``_line_before_slicing`` (a shallow copy that shares this line's
        element dict and variable management), so import that instead.

        Set ``use_sliced=True`` to import the slices as they are.
        """
        if self.use_sliced:
            return line
        before = getattr(line, "_line_before_slicing", None)
        if before is None or line.element_names == before.element_names:
            return line
        warn(
            f"Xtrack line was sliced into {len(line.element_names)} elements; "
            f"importing the {len(before.element_names)} thick elements it was "
            "sliced from. Pass use_sliced=True to import the slices instead."
        )
        return before

    def _read_functional_definitions(self) -> None:
        """Keep independent Environment variables used by element expressions."""
        vars = getattr(self.line, "vars", None)
        if vars is None:
            return
        manager = self.line.env._var_management_to_dict().get("_var_manager", [])
        self._expressions = {
            target: expression
            for target, expression in manager
            if target.startswith("element_refs[")
        }
        names = {
            part.split("']", 1)[0]
            for expression in self._expressions.values()
            for part in expression.split("vars['")[1:]
        }
        definitions = dict(self.functional_definitions)
        definitions.update(
            getattr(self.line, "metadata", {}).get(
                "laura_functional_definitions", {}
            )
        )
        definitions.update({
            name: float(self.line.varval[name])
            for name in names
            if name not in {"t_turn_s", "__vary_default"}
        })
        object.__setattr__(self, "functional_definitions", definitions)
        self._raw_definitions = dict(definitions)

    def _bare_symbol(self, element_name: str, field: str) -> str | None:
        """The variable name when ``field`` is driven by a bare ``vars['x']``."""
        expr = self._expressions.get(f"element_refs['{element_name}'].{field}")
        if not expr:
            return None
        return next(
            (
                name
                for name in self.functional_definitions
                if expr == f"vars['{name}']"
            ),
            None,
        )

    def _rescale_strength_symbols(self) -> None:
        """Re-express per-metre strength variables as integrated strengths."""
        scaled: Dict[str, float] = {}
        conflicting: set = set()
        lines = list(self._source_lines.values()) or [self.line]
        for line in lines:
            for element_name in line.element_names:
                native = line.element_dict[element_name]
                native_type = type(native).__name__
                length = float(getattr(native, "length", 0.0) or 0.0)
                if not length:
                    continue
                for field in _PER_METRE_FIELDS:
                    symbol = self._bare_symbol(element_name, field)
                    if symbol is None or symbol not in self._raw_definitions:
                        continue
                    factor = (
                        -length
                        if field == "k0" and native_type in {"Bend", "RBend"}
                        else length
                    )
                    value = float(self._raw_definitions[symbol]) * factor
                    if symbol in scaled and not np.isclose(scaled[symbol], value):
                        conflicting.add(symbol)
                    scaled[symbol] = value

        self._conflicting_symbols = conflicting
        definitions = dict(self.functional_definitions)
        definitions.update(
            {
                name: value
                for name, value in scaled.items()
                if name not in conflicting
            }
        )
        object.__setattr__(self, "functional_definitions", definitions)

    def _symbol(self, element_name: str, field: str, length: float = 0.0) -> str | None:
        """Recognise expressions emitted by LAURA for a single scalar variable."""
        try:
            expr = self._expressions[f"element_refs['{element_name}'].{field}"]
        except KeyError:
            return None
        for name in self.functional_definitions:
            token = f"vars['{name}']"
            if expr == token or (
                length and expr.replace("(", "").replace(")", "").replace(" ", "")
                == f"{token}/{length}".replace(" ", "")
            ):
                if name in self._conflicting_symbols and expr == token:
                    return None
                return name
        return None

    def _physical(self, index: int, length: float, table) -> dict:
        return {
            "s": float(table.s_end[index]),
            "s_point": "end",
            "length": length,
        }

    def _rf_phase(self, element_name: str, native) -> str | float:
        # Xtrack phase is radians; its legacy lag is degrees and remains additive.
        phase = float(getattr(native, "phase", 0.0))
        lag = float(getattr(native, "lag", 0.0))
        phase_symbol = self._symbol(element_name, "phase")
        lag_symbol = self._symbol(element_name, "lag")
        if lag_symbol and not phase_symbol and phase == 0.0:
            return lag_symbol
        if phase_symbol or lag_symbol:
            name = f"{element_name}_laura_phase"
            self.functional_definitions[name] = float(np.degrees(phase) + lag)
            return name
        return float(np.degrees(phase) + lag)

    def _multipoles(self, element_name: str, native, length: float, native_type: str) -> dict:
        normal = [float(value) for value in getattr(native, "knl", [])]
        skew = [float(value) for value in getattr(native, "ksl", [])]
        if native_type in _MAGNET_ORDERS:
            order = _MAGNET_ORDERS[native_type]
            needed = 3 if native_type in {"Bend", "RBend"} else order + 1
            missing = needed - len(normal)
            normal.extend([0.0] * max(missing, 0))
            skew.extend([0.0] * max(order + 1 - len(skew), 0))
            if native_type in {"Bend", "RBend"}:
                k0 = getattr(native, "k0", None)
                if k0 is None or isinstance(k0, str):
                    normal[0] = -float(getattr(native, "angle", normal[0]))
                else:
                    normal[0] = -float(k0) * length
                for component_order in (1, 2):
                    normal[component_order] += (
                        float(getattr(native, f"k{component_order}", 0.0)) * length
                    )
            else:
                normal[order] += float(getattr(native, f"k{order}", 0.0)) * length
                skew[order] += float(getattr(native, f"k{order}s", 0.0)) * length

        highest = min(max(len(normal), len(skew)), 5)
        if any(value != 0 for value in normal[5:] + skew[5:]):
            warn(
                "LAURA stores multipoles only through K4L; "
                "higher Xtrack orders were skipped."
            )
        result = {
            f"K{order}L": {
                "order": order,
                "normal": float(normal[order]) if order < len(normal) else 0.0,
                "skew": float(skew[order]) if order < len(skew) else 0.0,
            }
            for order in range(highest)
        }
        for order in range(highest):
            symbol = self._symbol(element_name, f"k{order}", length)
            if symbol:
                result[f"K{order}L"]["normal"] = symbol
            symbol = self._symbol(element_name, f"k{order}s", length)
            if symbol:
                result[f"K{order}L"]["skew"] = symbol
        return result

    def _element_data(
        self,
        element_name: str,
        native,
        native_type: str,
        length: float,
        laura_type: str | None = None,
        edges: Dict[str, Any] | None = None,
    ) -> dict:
        if laura_type in {
            "Combined_Corrector",
            "Horizontal_Corrector",
            "Vertical_Corrector",
        }:
            normal = list(getattr(native, "knl", []))
            skew = list(getattr(native, "ksl", []))
            return {
                "magnetic": {
                    "length": length,
                    "horizontal_kick": -float(normal[0]) if normal else 0.0,
                    "vertical_kick": float(skew[0]) if skew else 0.0,
                }
            }
        if native_type in _MAGNET_ORDERS or native_type in {
            "Multipole",
            "Magnet",
        }:
            multipoles = self._multipoles(element_name, native, length, native_type)
            if native_type == "Multipole" and not any(
                component["normal"] or component["skew"]
                for component in multipoles.values()
            ):
                warn(
                    f"Xtrack Multipole {element_name!r} has no non-zero knl/ksl "
                    "component, so its order could not be determined; importing "
                    "it as a generic Magnet with all multipole orders left at zero."
                )
                return {"magnetic": {"length": length}}
            magnetic = {
                "length": length,
                "multipoles": multipoles,
            }
            if native_type in {"Bend", "RBend"}:
                entry_edge = (edges or {}).get("entry")
                exit_edge = (edges or {}).get("exit")
                field_map = {
                    "edge_entry_angle": ("entrance_edge_angle", "e1", entry_edge),
                    "edge_exit_angle": ("exit_edge_angle", "e1", exit_edge),
                    "edge_entry_fint": ("edge_field_integral", "fint", entry_edge or exit_edge),
                    "edge_entry_hgap": ("gap", "hgap", entry_edge or exit_edge),
                }
                for source, (target, edge_attr, fallback_edge) in field_map.items():
                    if hasattr(native, source):
                        value = self._symbol(element_name, source) or float(
                            getattr(native, source)
                        )
                        if value == 0.0 and fallback_edge is not None:
                            value = float(getattr(fallback_edge, edge_attr, 0.0))
                        magnetic[target] = 2 * value if target == "gap" else value
            return {"magnetic": magnetic}
        if native_type in {"Solenoid", "UniformSolenoid"}:
            strength = self._symbol(element_name, "ks", length)
            return {
                "magnetic": {
                    "length": length,
                    "fields": {
                        "S0L": strength or float(getattr(native, "ks", 0.0)) * length
                    },
                }
            }
        if native_type == "NonLinearLens":
            return {
                "magnetic": {
                    "length": length,
                    "integrated_strength": self._symbol(element_name, "knll")
                    or float(native.knll),
                    "dimensional_parameter": self._symbol(element_name, "cnll")
                    or float(native.cnll),
                }
            }
        if native_type == "Cavity":
            return {
                "cavity": {
                    "phase": self._rf_phase(element_name, native),
                    "frequency": float(native.frequency),
                },
                "simulation": {
                    "field_amplitude": self._symbol(element_name, "voltage")
                    or float(native.voltage)
                },
            }
        if native_type == "SecondOrderTaylorMap":
            return {
                "simulation": {
                    "c_matrix": np.array(native.k, dtype=float),
                    "r_matrix": np.array(native.R, dtype=float),
                    "t_matrix": np.array(native.T, dtype=float),
                }
            }
        if native_type == "CrabCavity":
            return {
                "cavity": {
                    "phase": self._rf_phase(element_name, native),
                    "frequency": float(native.frequency),
                },
                "simulation": {
                    "field_amplitude": self._symbol(element_name, "crab_voltage")
                    or float(native.crab_voltage)
                },
            }
        if native_type == "Wire":
            return {
                "simulation": {
                    "current": self._symbol(element_name, "current")
                    or float(native.current),
                    "interaction_length": float(native.L_int),
                    "horizontal_offset": float(native.xma),
                    "vertical_offset": float(native.yma),
                }
            }
        if native_type == "RFMultipole":
            return {
                "simulation": {
                    "field_amplitude": self._symbol(element_name, "voltage")
                    or float(native.voltage),
                    "frequency": float(native.frequency),
                    "phase": self._rf_phase(element_name, native),
                    "knl": [float(value) for value in native.knl],
                    "ksl": [float(value) for value in native.ksl],
                    "pnl": [float(value) for value in native.pn],
                    "psl": [float(value) for value in native.ps],
                }
            }
        if native_type == "BeamBeamBiGaussian2D":
            return {
                "simulation": {
                    "charge": float(native.other_beam_q0),
                    "n_particles": float(native.other_beam_num_particles),
                    "horizontal_offset": float(native.other_beam_shift_x),
                    "vertical_offset": float(native.other_beam_shift_y),
                    "horizontal_sigma": float(np.sqrt(native.other_beam_Sigma_11)),
                    "vertical_sigma": float(np.sqrt(native.other_beam_Sigma_33)),
                }
            }
        if native_type == "ACDipole":
            return {
                "simulation": {
                    "field_amplitude": self._symbol(element_name, "volt")
                    or float(native.volt),
                    "frequency": float(native.freq),
                    "phase": self._symbol(element_name, "lag") or float(native.lag),
                    "ramp": [float(value) for value in native.ramp],
                }
            }
        if native_type == "LimitEllipse":
            return {
                "aperture": {
                    "shape": "elliptical",
                    "horizontal_size": 2 * float(native.a),
                    "vertical_size": 2 * float(native.b),
                }
            }
        if native_type == "LimitRect":
            return {
                "aperture": {
                    "shape": "rectangular",
                    "horizontal_size": float(native.max_x - native.min_x),
                    "vertical_size": float(native.max_y - native.min_y),
                }
            }
        if native_type == "LimitRectEllipse":
            return {
                "aperture": {
                    "horizontal_size": 2
                    * min(float(native.max_x), float(np.sqrt(native.a_squ))),
                    "vertical_size": 2
                    * min(float(native.max_y), float(np.sqrt(native.b_squ))),
                }
            }
        if native_type == "LimitRacetrack":
            return {
                "aperture": {
                    "horizontal_size": float(native.max_x - native.min_x),
                    "vertical_size": float(native.max_y - native.min_y),
                }
            }
        if native_type == "LimitPolygon":
            return {
                "aperture": {
                    "horizontal_size": float(np.ptp(native.x_vertices)),
                    "vertical_size": float(np.ptp(native.y_vertices)),
                }
            }
        return {}

    def create_element_dictionary(self) -> Dict:
        return self.create_laura_element_dictionary()

    def create_laura_element_dictionary(self) -> Dict:
        try:
            import xtrack  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "xsuite is not installed. Install with: "
                'pip install "laura-accelerator[xsuite]"'
            ) from exc

        table = self.line.get_table()

        self.elements = {}
        if self.initial_twiss is not None:
            optics = getattr(self.initial_twiss, "_temp_optics_data", None)
            if optics is None:
                warn(
                    "initial_twiss has no readable optics data (already "
                    "consumed by line.twiss(), or built via W_matrix instead "
                    "of betx/alfx/...); skipping the TwissMatch marker."
                )
            else:
                twiss_name = (
                    getattr(self.initial_twiss, "element_name", None)
                    or "initial_twiss"
                )
                self.elements[twiss_name] = LAURA_elements.TwissMatch(
                    name=twiss_name,
                    machine_area=self.machine_area,
                    physical={"s": 0.0, "s_point": "end", "length": 0.0},
                    simulation={
                        "beta_x": optics["betx"],
                        "beta_y": optics["bety"],
                        "alpha_x": optics["alfx"],
                        "alpha_y": optics["alfy"],
                        "eta_x": optics["dx"],
                        "eta_y": optics["dy"],
                        "eta_xp": optics["dpx"],
                        "eta_yp": optics["dpy"],
                        "from_beam": False,
                    },
                )
        stored_types = getattr(self.line, "metadata", {}).get(
            "laura_element_types", {}
        )
        element_names = list(self.line.element_names)
        self._rescale_strength_symbols()
        absorbed_edges: Dict[str, Dict[str, Any]] = {}
        skip_indices: set = set()
        for index, element_name in enumerate(element_names):
            native = self.line.element_dict[element_name]
            if type(native).__name__ != "DipoleEdge":
                continue
            for neighbor_index in (index - 1, index + 1):
                if not (0 <= neighbor_index < len(element_names)):
                    continue
                neighbor = self.line.element_dict[element_names[neighbor_index]]
                if type(neighbor).__name__ in {"Bend", "RBend"}:
                    side = "entry" if str(getattr(native, "side", "entry")) == "entry" else "exit"
                    absorbed_edges.setdefault(element_names[neighbor_index], {})[side] = native
                    skip_indices.add(index)
                    break

        for index, element_name in enumerate(element_names):
            native = self.line.element_dict[element_name]
            native_type = type(native).__name__
            if native_type == "Drift":
                continue
            if index in skip_indices:
                continue
            stored_type = stored_types.get(element_name)
            laura_type = getattr(LAURA_elements, stored_type, None) if stored_type else None
            if laura_type is None and native_type == "Multipole":
                laura_type = self._multipole_type(native)
            if laura_type is None and native_type == "ACDipole":
                laura_type = self._acdipole_type(element_name, native)
            laura_type = laura_type or _TYPE_MAP.get(native_type)
            if laura_type is None:
                warn(
                    f"Could not parse Xtrack element type {native_type!r} for "
                    f"{element_name!r}; skipping."
                )
                continue

            warning = None if stored_type else _LOSSY_CONVERSIONS.get(native_type)
            if native_type == "LimitRect" and (
                not np.isclose(native.min_x, -native.max_x)
                or not np.isclose(native.min_y, -native.max_y)
            ):
                warning = "the off-centre aperture offset was not represented"
            if warning:
                warn(
                    f"Xtrack element type {native_type!r} for {element_name!r} "
                    f"was imported as {laura_type.__name__}; {warning}."
                )

            length = float(getattr(native, "length", 0.0))
            physical_length = length if getattr(native, "isthick", True) else 0.0
            data = {
                "name": element_name,
                "machine_area": self.machine_area,
                "physical": self._physical(index, physical_length, table),
                **self._element_data(
                    element_name,
                    native,
                    native_type,
                    length,
                    stored_type,
                    absorbed_edges.get(element_name),
                ),
            }
            self.elements[element_name] = laura_type(**data)
        return self.elements

    def create_section(
        self, section: Optional[Dict] = None
    ) -> Dict[str, SectionLattice]:
        if not self.elements:
            self.create_laura_element_dictionary()
        if section is None:
            names = list(self.elements)
            if not names:
                raise ValueError("No elements were imported; cannot build a section.")
            section = {self.name: [names[0], names[-1]]}
        if len(section) != 1:
            raise ValueError("A section definition must contain exactly one section.")
        section_name, bounds = next(iter(section.items()))
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

        elements = dict(list(self.elements.items())[first : last + 1])
        lattice = SectionLattice(
            order=list(elements),
            elements=ElementList(elements=elements),
            name=section_name,
            functional_definitions=self.functional_definitions,
        )
        lattice.resolve_positions(self.elements)
        self.sections[section_name] = lattice
        return {section_name: lattice}

    def create_layout(
        self, name: Optional[str] = None, sections: Optional[Dict] = None
    ) -> MachineLayout:
        if self._source_lines and sections is None:
            layout_sections = {}
            for line_name, line in self._source_lines.items():
                object.__setattr__(self, "line", line)
                self._read_functional_definitions()
                self.elements = {}
                self.create_laura_element_dictionary()
                names = list(self.elements)
                layout_sections.update(
                    self.create_section({line_name: [names[0], names[-1]]})
                )
        elif sections is None:
            layout_sections = self.create_section()
        else:
            layout_sections = {}
            for section_name, bounds in sections.items():
                layout_sections.update(self.create_section({section_name: bounds}))
        layout = MachineLayout(
            name=name or self.name,
            sections=layout_sections,
            functional_definitions=self.functional_definitions,
        )
        self.layouts[layout.name] = layout
        return layout

    def export_yaml(
        self,
        path: str,
        source: Union[SectionLattice, MachineLayout],
        position_mode: PositionMode = "s",
    ) -> None:
        export_machine_combined_file(path, source, position_mode=position_mode)


XsuiteLatticeConverter = XsuiteLatticeImporter
