from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from ocelot.cpbd.magnetic_lattice import MagneticLattice
import laura.models.element as LAURA_elements
from laura.models.elementList import SectionLattice, MachineLayout, ElementList
from . import magnetic_orders
from .. import keyword_conversion_rules_ocelot as keyword_conversion_rules
from ...utils.functions import introspect_model_defaults, number_repeated_names
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
            "bend": "Dipole",
            "hcor": "Horizontal_Corrector",
            "marker": "Marker",
            "monitor": "Diagnostic",
            "rbend": "Dipole",
            "undulator": "Wiggler",
            "vcor": "Vertical_Corrector",
        }
    )
    return switch

ocelot_unsupported = [
    "Cleaner",
    "Scatter",
    "APContour",
    "Center",
    "Wakefield",
    "Laser",
    "Plasma",
    "MatrixTransform",
    "TwissMatch",
    "Decapole",
    "ActivePlasmaLens",
    "CrabCavity",
]


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

    initial_twiss: Optional[Any] = None
    """Optional Ocelot ``Twiss`` instance if found in the lattice file."""

    laura_elements: Dict = {}
    """Dictionary containing converted element objects"""

    def _default_name(self) -> str:
        return self.name

    def create_element_dictionary(self):
        return self.create_laura_element_dictionary()

    def create_laura_element_dictionary(self):
        from ...conversion_rules.codes.ocelot_conversion import (
            ocelot_conversion_rules,
        )

        self.laura_elements = {}
        switch_dict = _switch_dict(ocelot_conversion_rules)

        if self.initial_twiss is not None:
            twiss_name = getattr(self.initial_twiss, "id", "") or "initial_twiss"
            self.laura_elements[twiss_name] = LAURA_elements.TwissMatch(
                name=twiss_name,
                machine_area=self.machine_area,
                physical={"s": 0.0, "s_point": "end", "length": 0.0},
                simulation={
                    "beta_x": self.initial_twiss.beta_x,
                    "beta_y": self.initial_twiss.beta_y,
                    "alpha_x": self.initial_twiss.alpha_x,
                    "alpha_y": self.initial_twiss.alpha_y,
                    "eta_x": self.initial_twiss.Dx,
                    "eta_y": self.initial_twiss.Dy,
                    "eta_xp": self.initial_twiss.Dxp,
                    "eta_yp": self.initial_twiss.Dyp,
                    "from_beam": False,
                },
            )

        sequence = list(self.magnetic_lattice.sequence)
        numbered_ids = number_repeated_names([elem.id for elem in sequence])

        cumulative_s = 0.0
        for elem, numbered_id in zip(sequence, numbered_ids):
            length = float(getattr(elem, "l", 0.0))
            cumulative_s += length
            phys_common = {"s": cumulative_s, "s_point": "end", "length": length}

            typeconv = type(elem).__name__.lower()
            if typeconv == "drift":
                continue
            sftype = switch_dict.get(typeconv)
            if not sftype:
                warn(
                    f"Could not parse Ocelot element type {type(elem)} for "
                    f"{numbered_id!r}; skipping."
                )
                continue
            newobj = {
                "name": numbered_id,
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
                warn(f"Ocelot type {sftype!r} for {numbered_id!r} not recognized; skipping.")
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
                            if oceparam == "angle":
                                order, kl_value = 0, elem.element.angle
                            else:
                                order = int(oceparam[1:])
                                kl_value = getattr(elem.element, oceparam) * length
                            newobj["magnetic"].setdefault("multipoles", {})[
                                f"K{order}L"
                            ] = {"normal": kl_value, "order": order}
                        if oceparam == "angle" and newobj["hardware_type"] in (
                            "Horizontal_Corrector",
                            "Vertical_Corrector",
                        ):
                            if "magnetic" not in newobj:
                                newobj["magnetic"] = {}
                            key = (
                                "horizontal_kick"
                                if newobj["hardware_type"] == "Horizontal_Corrector"
                                else "vertical_kick"
                            )
                            newobj["magnetic"][key] = elem.element.angle
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
                {numbered_id: getattr(LAURA_elements, newobj["hardware_type"])(**newobj)}
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
