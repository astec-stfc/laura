from typing import Dict, Any, TYPE_CHECKING
from textwrap import wrap
from laura.models.elementList import MachineLayout
from .converter import translate_elements
from .section import SectionLatticeTranslator
from ..utils.functions import elegant_functional_definitions, sanitize_string

if TYPE_CHECKING:
    from ocelot.cpbd.magnetic_lattice import MagneticLattice
    from cheetah import Segment


class MachineLayoutTranslator(MachineLayout):
    directory: str = "."

    @classmethod
    def from_layout(cls, layout: MachineLayout) -> "MachineLayoutTranslator":
        return cls.model_validate(
            {
                "name": layout.model_copy().name,
                "sections": layout.model_copy().sections,
                "master_lattice": layout.model_copy().master_lattice,
                "functional_definitions": layout.functional_definitions,
                "resolve_functional": layout.resolve_functional,
                "revolution_frequency": layout.revolution_frequency,
            }
        )

    def _section_translator(self, section) -> SectionLatticeTranslator:
        """
        Build a :class:`SectionLatticeTranslator` for ``section``, falling back
        to this layout's own ``revolution_frequency`` if the section does not
        define its own.
        """
        translator = SectionLatticeTranslator.from_section(section)
        if translator.revolution_frequency is None:
            translator.revolution_frequency = self.revolution_frequency
        return translator

    def to_astra(self) -> Dict[str, str]:
        lattices = {}
        for section in self.sections.values():
            lattices.update(
                {
                    section.name: self._section_translator(section).to_astra()
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
        lstring = '&\n'.join(wrap(lstring, 80, break_long_words=False, break_on_hyphens=False))
        return elegant_functional_definitions(self.functional_definitions) + string + lstring

    def to_genesis(self, string: str = "") -> str:
        for section in self.sections.values():
            section_with_drifts = section.createDrifts()
            elem_dict = translate_elements(
                section_with_drifts.values(),
                master_lattice=self.master_lattice,
                directory=self.directory,
            )

            for i, d in enumerate(elem_dict.values()):
                string += d.to_genesis(index=i)

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
                    section.name: self._section_translator(section).to_ocelot(save=save)
                }
            )
        return lattices

    def to_rftrack(self, P_Q: float = float("nan"), save: bool = False) -> Dict[str, object]:
        """
        Create one RF-Track ``Lattice`` per section in this layout.

        Parameters
        ----------
        P_Q: float
            Beam reference momentum-over-charge [MV/c], forwarded to every
            section's ``to_rftrack(P_Q=...)``.
        save: bool
            Forwarded to every section's ``to_rftrack(save=...)``; see
            ``SectionLatticeTranslator.to_rftrack``.

        Returns
        -------
        Dict[str, object]
            ``{section_name: RF_Track.Lattice, ...}``
        """
        lattices = {}
        for section in self.sections.values():
            lattices.update(
                {
                    section.name: self._section_translator(section).to_rftrack(P_Q=P_Q, save=save)
                }
            )
        return lattices

    def to_cheetah(self, save=False) -> Dict[str, "Segment"]:
        lattices = {}
        for section in self.sections.values():
            lattices.update(
                {
                    section.name: self._section_translator(section).to_cheetah(save=save)
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
                    section.name: self._section_translator(section).to_xsuite(
                        beam_length=beam_length,
                        env=env,
                        particle_ref=particle_ref,
                        save=save,
                    )
                }
            )
        return lattices

    def to_madx(self, beam: Dict[str, Dict[str, Any]] | None = None) -> Dict[str, str]:
        lattices = {}
        for section in self.sections.values():
            b = beam[section.name] if isinstance(beam, Dict) and section.name in beam.keys() else None
            lattices.update(
                {
                    sanitize_string(section.name): SectionLatticeTranslator.from_section(
                        section
                    ).to_madx(beam=b)
                }
            )
        return lattices
