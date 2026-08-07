from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
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
}
_MAGNET_ORDERS = {
    "Bend": 0,
    "RBend": 0,
    "Quadrupole": 1,
    "Sextupole": 2,
    "Octupole": 3,
}
_LOSSY_CONVERSIONS = {
    "BeamPositionMonitor": "sampling and turn configuration was not represented",
    "BeamProfileMonitor": "sampling and profile-bin configuration was not represented",
    "BeamSizeMonitor": "beam-size statistics were reduced to a Screen",
    "BeamStatsMonitor": "weighted beam statistics were reduced to a Screen",
    "ParticlesMonitor": "particle-coordinate logging was reduced to a Screen",
    "LastTurnsMonitor": "particle-loss history was reduced to a Screen",
    "LimitRectEllipse": "the compound shape was reduced to its bounding size",
    "LimitRacetrack": "the racetrack shape was reduced to its bounding size",
    "LimitPolygon": "the polygon was reduced to its bounding size",
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

    source_file: Optional[str] = None
    """Xtrack ``Line``/``Environment`` JSON file, used instead of ``line``."""

    line_name: Optional[str] = None
    """Optional line selector for an Environment containing multiple lines."""

    functional_definitions: Dict[str, Union[int, float]] = {}

    position_mode: Literal["s", "survey"] = "s"
    """Use Xtrack's cumulative arc length by default, or its global survey."""

    elements: Dict = {}
    sections: Dict = {}
    layouts: Dict = {}
    initial_position: List[float] = [0, 0, 0]
    initial_rotation: List[float] = [0, 0, 0]
    _expressions: Dict[str, str] = PrivateAttr(default_factory=dict)
    _source_lines: Dict[str, Any] = PrivateAttr(default_factory=dict)

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
            self._source_lines = {name: self.line.lines[name] for name in names}
            object.__setattr__(self, "line", self._source_lines[names[0]])
        self._read_functional_definitions()
        return self

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
                return name
        return None

    def _physical(self, index: int, length: float, table, survey) -> dict:
        if self.position_mode == "s":
            return {
                "s": float(table.s_end[index]),
                "s_point": "end",
                "length": length,
            }

        start = np.array([survey.X[index], survey.Y[index], survey.Z[index]])
        end = np.array(
            [survey.X[index + 1], survey.Y[index + 1], survey.Z[index + 1]]
        )
        rotation = [
            float((survey.phi[index] + survey.phi[index + 1]) / 2),
            float((survey.psi[index] + survey.psi[index + 1]) / 2),
            float((survey.theta[index] + survey.theta[index + 1]) / 2),
        ]
        return {
            "middle": ((start + end) / 2).tolist(),
            "global_rotation": rotation,
            "length": length,
        }

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
                normal[0] = -float(getattr(native, "angle", normal[0]))
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
            magnetic = {
                "length": length,
                "multipoles": self._multipoles(element_name, native, length, native_type),
            }
            if native_type in {"Bend", "RBend"}:
                for source, target in {
                    "edge_entry_angle": "entrance_edge_angle",
                    "edge_exit_angle": "exit_edge_angle",
                    "edge_entry_fint": "edge_field_integral",
                    "edge_entry_hgap": "gap",
                }.items():
                    if hasattr(native, source):
                        value = self._symbol(element_name, source) or float(
                            getattr(native, source)
                        )
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
                    "phase": self._symbol(element_name, "lag") or float(native.lag),
                    "frequency": float(native.frequency),
                },
                "simulation": {
                    "field_amplitude": self._symbol(element_name, "voltage")
                    or float(native.voltage)
                },
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
        survey = None
        if self.position_mode == "survey":
            survey = self.line.survey(
                X0=self.initial_position[0],
                Y0=self.initial_position[1],
                Z0=self.initial_position[2],
                theta0=self.initial_rotation[0],
                phi0=self.initial_rotation[1],
                psi0=self.initial_rotation[2],
            )

        self.elements = {}
        stored_types = getattr(self.line, "metadata", {}).get(
            "laura_element_types", {}
        )
        for index, element_name in enumerate(self.line.element_names):
            native = self.line.element_dict[element_name]
            native_type = type(native).__name__
            if native_type == "Drift":
                continue
            stored_type = stored_types.get(element_name)
            laura_type = getattr(LAURA_elements, stored_type, None) if stored_type else None
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
            data = {
                "name": element_name,
                "machine_area": self.machine_area,
                "physical": self._physical(index, length, table, survey),
                **self._element_data(
                    element_name, native, native_type, length, stored_type
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


# Backwards-compatible public name used before the importer lifecycle was aligned.
XsuiteLatticeConverter = XsuiteLatticeImporter
