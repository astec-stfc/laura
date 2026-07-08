from typing import Dict, Any, TYPE_CHECKING
from textwrap import wrap
from laura.models.elementList import MachineModel
from .converter import translate_elements
from .layout import MachineLayoutTranslator

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
            }
        )

    def to_astra(self) -> Dict[str, Dict[str, str]]:
        model = {}
        for name, latt in self.lattices.items():
            model.update({name: MachineLayoutTranslator.from_layout(latt).to_astra()})
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
            model.update({name: MachineLayoutTranslator.from_layout(latt).to_rftrack(P_Q=P_Q, save=save)})
        return model

    def format_string(seld, string: str):
        fulltext = ""
        for s in string.split(', '):
            if len((fulltext + s).splitlines()[-1]) > 60:
                fulltext += "&\n"
            fulltext += s + ", "
        return fulltext

    def to_elegant(self, string: str = "", charge: float = None) -> str:
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
                    string += self.format_string(d.to_elegant())

                string += f"\n{section.name}: LINE = ("
                if charge:
                    string += f"{section.name}_Q, "
                for elem in section_with_drifts.keys():
                    string += f"{elem}, "
                string = f"{string[:-2]})" + "\n\n\n"

        for name, latt in self.lattices.items():
            lstring = f"{name}: LINE = ("
            for l in list(latt.keys()):
                lstring += f"{l}, "
            lstring = f"{lstring[:-2]})" + "\n\n"
        lstring = '&\n'.join(wrap(lstring, 80, break_long_words=False, break_on_hyphens=False))
        return string + lstring

    def to_genesis(self, string: str = "") -> str:
        for latt in self.lattices.values():
            for section in latt.sections.values():
                section_with_drifts = section.createDrifts()
                elem_dict = translate_elements(
                    section_with_drifts.values(),
                    master_lattice=self.master_lattice,
                    directory=self.directory,
                )

                for d in elem_dict.values():
                    string += d.to_genesis()

                string += f"\n{section.name}: LINE = " + "{"
                for elem in section_with_drifts.keys():
                    string += f"{elem}, "
                string = f"{string[:-2]}" + "}\n\n\n"

        for name, latt in self.lattices.items():
            string += f"{name}: LINE = " + "{"
            for l in list(latt.keys()):
                string += f"{l}, "
            string = f"{string[:-2]}" + "};\n\n"
        return string

    def to_ocelot(self, save=False) -> Dict[str, Dict[str, "MagneticLattice"]]:
        model = {}
        for name, latt in self.lattices.items():
            model.update(
                {name: MachineLayoutTranslator.from_layout(latt).to_ocelot(save=save)}
            )
        return model

    def to_cheetah(self, save=False) -> Dict[str, Dict[str, "Segment"]]:
        model = {}
        for name, latt in self.lattices.items():
            model.update(
                {name: MachineLayoutTranslator.from_layout(latt).to_cheetah(save=save)}
            )
        return model

    def to_xsuite(
        self, beam_length: int, env: Any = None, particle_ref: Any = None, save=False
    ) -> Dict[str, Dict[str, object]]:
        model = {}
        for name, latt in self.lattices.items():
            model.update(
                {
                    name: MachineLayoutTranslator.from_layout(latt).to_xsuite(
                        beam_length=beam_length,
                        env=env,
                        particle_ref=particle_ref,
                        save=save,
                    )
                }
            )
        return model
