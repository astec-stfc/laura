from typing import Dict, Any, TYPE_CHECKING
from laura.models.elementList import MachineModel
from .converter import translate_elements
from .layout import MachineLayoutTranslator, wrap_lattice_line
from ..utils.functions import elegant_functional_definitions, sanitize_string

if TYPE_CHECKING:
    from ocelot.cpbd.magnetic_lattice import MagneticLattice
    from cheetah import Segment


class MachineModelTranslator(MachineModel):
    directory: str = "."

    @classmethod
    def from_machine(cls, machine: MachineModel) -> "MachineModelTranslator":
        return cls.model_validate(
            {
                "layout": machine.model_copy().layout,
                "section": machine.model_copy().section,
                "elements": machine.model_copy().elements,
                "sections": machine.model_copy().sections,
                "lattices": machine.model_copy().lattices,
                "master_lattice": machine.model_copy().master_lattice,
                "functional_definitions": machine.functional_definitions,
                "resolve_functional": machine.resolve_functional,
                "revolution_frequency": machine.revolution_frequency,
            }
        )

    def _layout_translator(self, layout) -> MachineLayoutTranslator:
        """
        Build a :class:`MachineLayoutTranslator` for ``layout``, falling back
        to this machine's own ``revolution_frequency`` if the layout does not
        define its own.
        """
        translator = MachineLayoutTranslator.from_layout(layout)
        if translator.revolution_frequency is None:
            translator.revolution_frequency = self.revolution_frequency
        return translator

    def to_astra(self) -> Dict[str, Dict[str, str]]:
        model = {}
        for name, latt in self.lattices.items():
            model.update({name: self._layout_translator(latt).to_astra()})
        return model

    def to_rftrack(self, P_Q: float = float("nan"), save: bool = False) -> Dict[str, Dict[str, object]]:
        """
        Create one RF-Track ``Lattice`` per section, grouped by layout.

        Parameters
        ----------
        P_Q: float
            Beam reference momentum-over-charge [MV/c], forwarded to every
            layout's ``to_rftrack(P_Q=...)``.
        save: bool
            Forwarded to every layout's ``to_rftrack(save=...)``; see
            ``SectionLatticeTranslator.to_rftrack``.

        Returns
        -------
        Dict[str, Dict[str, object]]
            ``{layout_name: {section_name: RF_Track.Lattice, ...}, ...}``
        """
        model = {}
        for name, latt in self.lattices.items():
            model.update(
                {name: self._layout_translator(latt).to_rftrack(P_Q=P_Q, save=save)}
            )
        return model

    def to_elegant(self, string: str = "", charge: float = None) -> str:
        lstring = ""
        for latt in self.lattices.values():
            for section in latt.sections.values():
                section_with_drifts = section.createDrifts()
                elem_dict = translate_elements(
                    section_with_drifts.values(),
                    master_lattice=self.master_lattice,
                    directory=self.directory,
                )
                if charge:
                    string += f"{section.name}_Q: CHARGE, TOTAL = {charge};\n"

                for d in elem_dict.values():
                    string += d.to_elegant()

                line = f"{section.name}: LINE = ("
                if charge:
                    line += f"{section.name}_Q, "
                line += ", ".join(section_with_drifts.keys()) + ")"
                lstring += "\n" + wrap_lattice_line(line) + "\n\n\n"

        for name, latt in self.lattices.items():
            line = f"{name}: LINE = (" + ", ".join(latt.keys()) + ")"
            lstring += wrap_lattice_line(line) + "\n\n"
        return elegant_functional_definitions(self.functional_definitions) + string + lstring

    def to_genesis(self, string: str = "") -> str:
        for latt in self.lattices.values():
            for section in latt.sections.values():
                section_with_drifts = section.createDrifts()
                elem_dict = translate_elements(
                    section_with_drifts.values(),
                    master_lattice=self.master_lattice,
                    directory=self.directory,
                )

                for i, d in enumerate(elem_dict.values()):
                    string += d.to_genesis(index=i)

                string += f"\n{section.name}: LINE = " + "{"
                string += ", ".join(section_with_drifts.keys()) + "};\n\n\n"

        for name, latt in self.lattices.items():
            string += f"{name}: LINE = " + "{"
            string += ", ".join(latt.keys()) + "};\n\n"
        return string

    def to_ocelot(self, save=False) -> Dict[str, Dict[str, "MagneticLattice"]]:
        model = {}
        for name, latt in self.lattices.items():
            model.update(
                {name: self._layout_translator(latt).to_ocelot(save=save)}
            )
        return model

    def to_cheetah(self, save=False) -> Dict[str, Dict[str, "Segment"]]:
        model = {}
        for name, latt in self.lattices.items():
            model.update(
                {name: self._layout_translator(latt).to_cheetah(save=save)}
            )
        return model

    def to_xsuite(
        self, beam_length: int, env: Any = None, particle_ref: Any = None, save=False
    ) -> Dict[str, Dict[str, object]]:
        model = {}
        for name, latt in self.lattices.items():
            model.update(
                {
                    name: self._layout_translator(latt).to_xsuite(
                        beam_length=beam_length,
                        env=env,
                        particle_ref=particle_ref,
                        save=save,
                    )
                }
            )
        return model

    def to_madx(
        self,
        beam: Dict[str, Dict[str, Dict[str, Any]]] | None = None,
        refer: str = "entry",
    ) -> Dict[str, Dict[str, str]]:
        """
        Create one MAD-X ``SEQUENCE`` per section, grouped by layout.

        Parameters
        ----------
        beam: dict
            ``{layout_name: {section_name: beam_dict}}``, forwarded to each
            layout's :meth:`MachineLayoutTranslator.to_madx`.
        refer: str
            Element reference position, forwarded to every layout.

        Returns
        -------
        Dict[str, Dict[str, str]]
            ``{sanitised_layout_name: {sanitised_section_name: sequence, ...}, ...}``
        """
        model = {}
        for name, latt in self.lattices.items():
            b = beam.get(name) if isinstance(beam, dict) else None
            model.update(
                {
                    sanitize_string(name): self._layout_translator(latt).to_madx(
                        beam=b, refer=refer
                    )
                }
            )
        return model
