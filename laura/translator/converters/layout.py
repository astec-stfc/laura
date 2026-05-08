from typing import Dict, Any
from textwrap import wrap
from laura.models.elementList import MachineLayout
from .converter import translate_elements
from .section import SectionLatticeTranslator


class MachineLayoutTranslator(MachineLayout):
    directory: str = "."

    @classmethod
    def from_layout(cls, layout: MachineLayout) -> "MachineLayoutTranslator":
        return cls.model_validate(
            {
                "name": layout.model_copy().name,
                "sections": layout.model_copy().sections,
                "master_lattice": layout.model_copy().master_lattice,
            }
        )

    def to_astra(self) -> Dict[str, str]:
        lattices = {}
        for section in self.sections.values():
            lattices.update(
                {
                    section.name: SectionLatticeTranslator.from_section(
                        section
                    ).to_astra()
                }
            )
        return lattices

    def to_elegant(self, string: str = "", charge: float = None) -> str:
        for section in self.sections.values():
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

            lstring = f"\n{section.name}: LINE = ("
            if charge:
                lstring += f"{section.name}_Q, "
            for elem in section_with_drifts.keys():
                lstring += f"{elem}, "
            lstring = f"{lstring[:-2]})" + "\n\n\n"
        lstring = "&\n".join(
            wrap(lstring, 80, break_long_words=False, break_on_hyphens=False)
        )
        return string + lstring

    def to_genesis(self, string: str = "") -> str:
        for section in self.sections.values():
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
            string = f"{string[:-2]}" + "};\n\n\n"
        return string

    def to_ocelot(self, save=False) -> Dict[str, "MagneticLattice"]:
        lattices = {}
        for section in self.sections.values():
            lattices.update(
                {
                    section.name: SectionLatticeTranslator.from_section(
                        section
                    ).to_ocelot(save=save)
                }
            )
        return lattices

    def to_cheetah(self, save=False) -> Dict[str, "Segment"]:
        lattices = {}
        for section in self.sections.values():
            lattices.update(
                {
                    section.name: SectionLatticeTranslator.from_section(
                        section
                    ).to_cheetah(save=save)
                }
            )
        return lattices

    def to_bdsim(self, save=False) -> Dict[str, "Machine"]:
        lattices = {}
        for section in self.sections.values():
            lattices.update(
                {
                    section.name: SectionLatticeTranslator.from_section(
                        section
                    ).to_bdsim(save=save)
                }
            )
        return lattices

    def to_xsuite(
        self, beam_length: int, env: Any = None, particle_ref: Any = None, save=False
    ) -> Dict[str, object]:
        lattices = {}
        for section in self.sections.values():
            lattices.update(
                {
                    section.name: SectionLatticeTranslator.from_section(
                        section
                    ).to_xsuite(
                        beam_length=beam_length,
                        env=env,
                        particle_ref=particle_ref,
                        save=save,
                    )
                }
            )
        return lattices
