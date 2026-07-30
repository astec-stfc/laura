from copy import deepcopy
from typing import Dict, Any
from warnings import warn
from textwrap import wrap
import numpy as np
from pydantic import PositiveInt

from ...models.elementList import SectionLattice
from ...models.RF import WakefieldElement
from ...models.simulation import WakefieldSimulationElement, DiagnosticSimulationElement
from .cavity import RFCavityTranslator
from .converter import translate_elements
from .diagnostic import DiagnosticTranslator
from .wake import WakefieldTranslator
from .codes.gpt import gpt_ccs, gpt_Zminmax, gpt_dtmint
from ..utils.functions import (
    tw_cavity_energy_gain,
    elegant_functional_definitions,
    madx_functional_definitions,
)
from ..utils.fields import field
from ...models.baseModels import IgnoreExtra
from ..utils.functions import sanitize_string


class SectionLatticeTranslator(SectionLattice):
    """
    Translator class for converting a :class:`~laura.models.elementList.SectionLattice` instance into a string or
    object that can be understood by various simulation codes.
    """

    directory: str = "."
    """Directory to which files will be written."""

    astra_headers: Dict = {}
    """Headers for ASTRA input file; see :class:`~laura.translator.converters.codes.astra.astra_header`
    and its child classes."""

    csrtrack_headers: Dict = {}
    """Headers for CSRTrack input file; see :class:`~laura.translator.converters.codes.csrtrack.csrtrack_element`
    and its child classes.."""

    gpt_headers: Dict = {}
    """Headers for GPT input file; see :class:`~laura.translator.converters.codes.astra.gpt_element`
    and its child classes.."""

    opal_headers: Dict = {}
    """Headers for OPAL input file; see :class:`~laura.translator.converters.codes.opal.opal_header`
    and its child classes..
    
    WARNING: OPAL not fully benchmarked / tested.
    """

    csr_enable: bool = True
    """Flag to enable calculation of CSR in drifts."""

    lsc_enable: bool = True
    """Flag to enable calculation of LSC in drifts."""

    wakefield_enable: bool = True
    """Flag to enable structure wakefields on accelerating cavities."""

    opal_version: str = "202210"
    """Version of OPAL to write for; propagated to the elements, which use it
    where classic OPAL and OPAL-X take different conventions."""

    lsc_bins: PositiveInt = 20
    """Number of LSC bins for drifts."""

    @classmethod
    def from_section(cls, section: SectionLattice) -> "SectionLatticeTranslator":
        """
        Method for creating an instance of this class based on an existing
        :class:`~laura.models.elementList.SectionLattice`.

        Parameters
        ----------
        section: SectionLattice
            The existing :class:`~laura.models.elementList.SectionLattice`

        Returns
        -------
        :class:`~laura.translator.converters.section.SectionLatticeTranslator`
            An instance of this class.

        """
        return cls.model_validate(
            {
                "name": section.model_copy().name,
                "order": section.model_copy().order,
                "elements": section.model_copy().elements,
                "master_lattice": section.model_copy().master_lattice,
                "functional_definitions": section.functional_definitions,
                "resolve_functional": section.resolve_functional,
            }
        )

    def to_astra(self) -> str:
        """
        Create an ASTRA-compatible input file based on the lattice information and
        the settings provided in :attr:`~astra_headers`.

        Returns
        -------
        str
            An ASTRA-compatible input file.
        """
        from .codes.astra import section_header_text_ASTRA

        headers = [
            "&APERTURE",
            "&CAVITY",
            "&SOLENOID",
            "&QUADRUPOLE",
            "&DIPOLE",
            "&WAKE",
        ]
        counter = {k: 1 for k in headers}
        written = []
        element_headers = {h: "" for h in headers}
        elem_dict = translate_elements(
            list(self.elements.elements.values()),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        astrastr = ""
        for h in self.astra_headers.values():
            astrastr += h.write_ASTRA()
        for e in elem_dict.values():
            for key, count in counter.items():
                if (
                    "&" + e.hardware_type.upper().replace("RF", "").replace("FIELD", "")
                    == key
                ):
                    if key not in written:
                        element_headers[
                            key
                        ] += f"{section_header_text_ASTRA[key]} = True\n"
                        written.append(key)
                    element_headers[key] += e.to_astra(n=count)
                    counter[key] += 1
                    if (
                        hasattr(e.simulation, "wakefield_definition")
                        and isinstance(e.simulation.wakefield_definition, (str, field))
                        and getattr(e.simulation, "wakefield_enable", True)
                    ):
                        w = WakefieldTranslator(
                            name=e.name + "_wake",
                            hardware_class="Wakefield",
                            hardware_type="Wakefield",
                            machine_area=e.machine_area,
                            physical=e.physical,
                            cavity=WakefieldElement(
                                cell_length=e.cavity.cell_length,
                                n_cells=e.cavity.n_cells,
                            ),
                            simulation=WakefieldSimulationElement(
                                wakefield_definition=e.simulation.wakefield_definition
                            ),
                            directory=e.directory,
                        )
                        if "&WAKE" not in written:
                            element_headers[
                                "&WAKE"
                            ] += f"{section_header_text_ASTRA['&WAKE']} = True\n"
                            written.append("&WAKE")
                        element_headers["&WAKE"] += w.to_astra(n=counter["&WAKE"])
                        counter["&WAKE"] += e.cavity.n_cells
                else:
                    cond = (
                        "&"
                        + e.hardware_type.upper().replace("RF", "").replace("FIELD", "")
                        in headers
                    )
                    # if not e.hardware_class == "Diagnostic" and not cond:
                    #     warn(
                    #         f"Element of type {e.hardware_type} not supported for ASTRA"
                    #     )
        for k, v in element_headers.items():
            astrastr += k + "\n"
            astrastr += v + "\n"
            astrastr += "/ \n"
        return astrastr

    def to_gpt(
            self,
            startz: float,
            endz: float,
            Brho: float = 0.0,
            dtmin: float | None = None,
            charge_sign: int = -1,
    ) -> str:
        """
        Create a GPT-compatible input file based on the lattice information and
        the settings provided in :attr:`~gpt_headers`.

        Note that, for sections with accelerating sections, the magnetic rigidity `Brho` may not
        be updated correctly, which may affect the accuracy of tracking through dipoles.

        Parameters
        ----------
        startz: float
            Start longitudinal location of the lattice.
        endz: float
            End longitudinal location of the lattice.
        Brho: float
            Magnetic rigidity.
        dtmin: float, optional
            Minimum time step size for integration
        charge_sign: int, optional
            Particle charge sign

        Returns
        -------
        str
            A GPT-compatible input file.
        """
        fulltext = ""
        for header in self.gpt_headers.values():
            fulltext += header.write_GPT()
        elem_dict = translate_elements(
            list(self.elements.elements.values()),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        self._apply_wakefield_enable(elem_dict)
        kwargs = {"charge_sign": charge_sign}
        for i, element in enumerate(list(elem_dict.values())):
            if i == 0:
                ccs = gpt_ccs(
                    name="wcs",
                    position=list(element.physical.start.model_dump().values()),
                    rotation=list(element.physical.global_rotation.model_dump().values()),
                )
            element.ccs = ccs
            fulltext += element.to_gpt(Brho, **kwargs)
            # The wakefield translator is built fresh here, so it does not
            # inherit the cavity's wakefield_enable -- gate on the cavity's own
            # flag instead, which _apply_wakefield_enable has already set.
            if (
                element.hardware_type.lower() == "rfcavity"
                and isinstance(element.simulation.wakefield_definition, field)
                and getattr(element.simulation, "wakefield_enable", True)
            ):
                w = WakefieldTranslator(
                    name=element.name + "_wake",
                    hardware_class="Wakefield",
                    hardware_type="Wakefield",
                    machine_area=element.machine_area,
                    physical=element.physical,
                    cavity=WakefieldElement(
                        cell_length=element.cavity.cell_length,
                        n_cells=element.cavity.n_cells,
                    ),
                    simulation=WakefieldSimulationElement(
                        wakefield_definition=element.simulation.wakefield_definition,
                    ),
                    directory=element.directory,
                )
                fulltext += w.to_gpt(Brho, **kwargs)
            new_ccs = deepcopy(element.ccs)
            if not new_ccs.name == ccs.name:
                relpos, relrot = ccs.relative_position(
                    list(element.physical.middle.model_dump().values()),
                    list(element.physical.global_rotation.model_dump().values()),
                )
            else:
                relpos = list(element.physical.middle.model_dump().values())
            screen0pos = 0
            ccs = deepcopy(new_ccs)
            if element.hardware_class.lower() == "diagnostic" or element.hardware_type.lower() == "marker":
                fulltext += f'screen({ccs.name_as_str}, "I", {str(relpos[2]+0.001)}, {ccs.name_as_str});\n'
                # if self.gpt_headers["setfile"].particle_definition == "laser":
        lastelem = list(elem_dict.values())[-1]
        lastscreen = DiagnosticTranslator(
            name="end_screen",
            hardware_class="Diagnostic",
            hardware_type="Diagnostic",
            machine_area=lastelem.machine_area,
            simulation=DiagnosticSimulationElement(
                output_filename=f"{self.name}_out.gdf"
            ),
            physical=lastelem.physical,
        )
        fulltext += lastscreen.to_gpt(Brho, output_ccs="wcs")
        relpos, relrot = ccs.relative_position(
            list(lastelem.physical.end.model_dump().values()),
            list(lastelem.physical.global_rotation.model_dump().values()),
        )
        fulltext += (
            f'screen("wcs", "I", {lastelem.physical.end.z}, "wcs");\n'
        )
        zminmax = gpt_Zminmax(
            ECS='"wcs", "I"',
            zmin=startz - 0.1,
            zmax=endz + 1,
        )
        fulltext += zminmax.write_GPT()
        if dtmin is not None:
            dtmint = gpt_dtmint(dtmin=dtmin)
            fulltext += dtmint.write_GPT()
        return fulltext

    def to_opal(self, energy: float = 0, breakstr: str = "") -> str:
        """
        Create an OPAL-compatible input file based on the lattice information and
        the settings provided in :attr:`~opal_headers`.

        Note that, for sections with accelerating sections, the beam energy `energy` may not
        be updated correctly, which may affect the accuracy of tracking through dipoles.

        Parameters
        ----------
        energy: float
            Beam energy
        breakstr: str
            String for separating sections in the lattice file.

        Returns
        -------
        str
            An OPAL-compatible input file.
        """
        check_dict = [
            "option",
            "distribution",
            "fieldsolver",
            "beam",
            "track",
            "run",
        ]
        for k in check_dict:
            if k not in self.opal_headers:
                raise KeyError(f"Header {k} must be defined for OPAL.")
        fulltext = ""
        fulltext += self.opal_headers["option"].write_Opal()
        fulltext += f"{breakstr}\n// LATTICE\n"
        zstops = []
        elem_dict = translate_elements(
            list(self.elements.elements.values()),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        written = []
        order = [n for n in self.order if n in elem_dict]
        start_z = elem_dict[order[0]].physical.start.z if order else 0.0
        for d in elem_dict.values():
            d.opal_version = self.opal_version
            if isinstance(d, RFCavityTranslator):
                if d.structure_type.lower() == "travellingwave":
                    energy += tw_cavity_energy_gain(d)
                else:
                    energy += d.field_amplitude * np.cos(np.pi * d.phase / 180)
            sval = d.physical.start.z - start_z
            stnew = d.to_opal(sval=sval, designenergy=energy)
            if len(stnew) > 0:
                written.append(d.name)
                fulltext += d.to_opal(sval=sval, designenergy=energy)
            zstops.append(d.physical.end.z)
        zstop = max(zstops)
        self.opal_headers["track"].ZSTOP = zstop
        fulltext += "\n" + self.name + ": LINE=("
        for e, element in list(elem_dict.items()):
            if len((fulltext + e).splitlines()[-1]) > 60:
                fulltext += "\n"
            if element.name in written:
                fulltext += e.replace("-", "_") + ", "
        fulltext = fulltext[:-2] + ");\n"

        fulltext += self.opal_headers["distribution"].write_Opal()
        fulltext += self.opal_headers["fieldsolver"].write_Opal()
        fulltext += self.opal_headers["beam"].write_Opal()
        fulltext += self.opal_headers["track"].write_Opal()
        fulltext += self.opal_headers["run"].write_Opal()
        fulltext += "ENDTRACK;\n\n Quit;\n"
        return fulltext

    def format_string(seld, string: str):
        fulltext = ""
        for s in string.strip().split(', '):
            if len((fulltext + s).splitlines()[-1]) > 60:
                fulltext += "&\n"
            fulltext += s + ", "
        return fulltext[:-2] + "\n"

    def _apply_wakefield_enable(self, elem_dict: dict) -> None:
        """
        Switch structure wakefields off on the translated elements when
        :attr:`~wakefield_enable` is False.

        Only ever turns wakefields off, so a per-element
        ``simulation.wakefield_enable`` set by the caller is still respected
        when the section-level flag is left on. The translated elements are
        throwaway copies, so the underlying lattice definition is unchanged.

        Parameters
        ----------
        elem_dict: dict
            The translated elements about to be written
        """
        if self.wakefield_enable:
            return
        for d in elem_dict.values():
            sim = getattr(d, "simulation", None)
            if sim is not None and hasattr(sim, "wakefield_enable"):
                sim.wakefield_enable = False

    def to_elegant(self, charge: float = None) -> str:
        """
        Create an ELEGANT-compatible input file based on the lattice information.

        Parameters
        ----------
        charge: float
            Bunch charge

        Returns
        -------
        str
            An ELEGANT-compatible lattice file.
        """
        section_with_drifts = self.createDrifts(
            csr_enable=self.csr_enable,
            lsc_enable=self.lsc_enable,
            lsc_bins=self.lsc_bins,
        )
        # (wakefields are applied to the translated elements below)
        elem_dict = translate_elements(
            section_with_drifts.values(),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        self._apply_wakefield_enable(elem_dict)
        string = ""
        if charge:
            string += f"{self.name}_Q: CHARGE, TOTAL = {charge};\n"

        for d in elem_dict.values():
            string += self.format_string(d.to_elegant())

        lstring = f"{self.name}: LINE = ("
        if charge:
            lstring += f"{self.name}_Q, "
        for elem in section_with_drifts.keys():
            lstring += f"{elem}, "
        lstring = f"{lstring[:-2]})" + "\n"
        lstring = '&\n'.join(wrap(lstring, 80, break_long_words=False, break_on_hyphens=False))
        return elegant_functional_definitions(self.functional_definitions) + string + lstring

    def to_genesis(self, split_element: str | None = None, chicanes: Dict | None = None) -> str:
        """
        Create a Genesis-compatible input file based on the lattice information.

        Parameters
        ----------
        split_element: str, optional
            Name of the element at which to split the lattice into two sections for Genesis
            (e.g., for simulating a two-stage FEL). If `None`, no split is performed.
        chicanes: Dict, optional
            Dictionary defining chicane parameters to be added to the lattice.
            Keys are chicane element names, and values contain `start`, `end`, `r56`, `dipole_length`, `drift_length`,
            with the last of these being the drift length between the first and second dipoles.

        Returns
        -------
        str
            A Genesis-compatible lattice file (v4).
        """
        section_with_drifts = self.createDrifts()
        elem_dict = translate_elements(
            section_with_drifts.values(),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        string = ""
        starts = []
        ends = []
        if isinstance(chicanes, dict):
            for chic in chicanes.values():
                self.check_chicane(chic)
                starts.append(chic["start"])
                ends.append(chic["end"])
            elem_dict_upd = deepcopy(elem_dict)
            chicane = False
            chicane_index = 1
            chicane_done = False
            for k, v in elem_dict.items():
                if k in starts:
                    chicane = True
                    chicane_done = False
                if not chicane:
                    elem_dict_upd.update({k: v})
                else:
                    if not chicane_done:
                        cstr = f"{chicane_index}{starts[chicane_index-1]}: CHICANE = " + "{"
                        chicname = list(chicanes.keys())[chicane_index - 1]
                        cstr += f"l = {chicanes[chicname]['length']}, "
                        cstr += f"delay = {2 * chicanes[chicname]['r56']}, "
                        cstr += f"lb = {chicanes[chicname]['dipole_length']}, "
                        cstr += f"ld = {chicanes[chicname]['drift_length']}" + "};\n"
                        elem_dict_upd.update({f"{starts[chicane_index-1]}": cstr})
                        chicane_index += 1
                        chicane_done = True
                if k in ends:
                    chicane = False
            elem_dict = elem_dict_upd

        for i, d in enumerate(elem_dict.values()):
            if isinstance(d , str):
                string += d
            else:
                string += d.to_genesis(index=i)
        string += f"{self.name}: LINE = " + "{"
        for i, elem in enumerate(elem_dict.keys()):
            if elem in starts:
                string += f"{elem_dict[starts[starts.index(elem)]][0]}{starts[starts.index(elem)]}, "
            else:
                string += f"{i}{elem}, "
        string = f"{string[:-2]}" + "};\n"
        if isinstance(split_element, str):
            if split_element in elem_dict.keys():
                string += f"{self.name}_SPLIT_1: LINE = " + "{"
                for i, elem in enumerate(elem_dict.keys()):
                    if elem == split_element:
                        break
                    else:
                        if elem in starts:
                            string += f"{elem_dict[starts[starts.index(elem)]][0]}{starts[starts.index(elem)]}, "
                        else:
                            string += f"{i}{elem}, "
                string = f"{string[:-2]}" + "};\n"
                string += f"{self.name}_SPLIT_2: LINE = " + "{"
                add = False
                for i, elem in enumerate(elem_dict.keys()):
                    if elem == split_element:
                        add = True
                    if add:
                        if elem in starts:
                            string += f"{elem_dict[starts[starts.index(elem)]][0]}{starts[starts.index(elem)]}, "
                        else:
                            string += f"{i}{elem}, "
                string = f"{string[:-2]}" + "};\n"
            else:
                warn(f"Element {split_element} not found in section {self.name} for GENESIS split.")
        return string


    def to_ocelot(self, save=False) -> "MagneticLattice":
        """
        Create an Ocelot-compatible magnetic lattice object based on the lattice information.

        Parameters
        ----------
        save: bool
            Flag to indicate whether to save the lattice to a file.

        Returns
        -------
        MagneticLattice
            An Ocelot `MagneticLattice` object.
        """
        from ocelot.cpbd.magnetic_lattice import MagneticLattice
        from ocelot.cpbd.transformations.second_order import SecondTM
        from ocelot.cpbd.transformations.kick import KickTM
        from ocelot.cpbd.transformations.runge_kutta import RungeKuttaTM
        from ocelot.cpbd.elements import Octupole, Undulator, Marker, Drift

        method = {"global": SecondTM, Octupole: KickTM, Undulator: RungeKuttaTM}
        section_with_drifts = self.createDrifts()
        elem_dict = translate_elements(
            section_with_drifts.values(),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        elements = []

        for d in elem_dict.values():
            obj = d.to_ocelot()
            objs = list(obj) if isinstance(obj, (list, tuple)) else [obj]
            # e.g. a Combined_Corrector split into an Hcor + Vcor pair.
            elements.extend(objs)
            # Some finite-length elements (e.g. collimators) map to zero-length
            # Ocelot elements (Aperture takes no length).
            # Pad the difference with a drift so the total length is preserved.
            oce_len = sum(getattr(o, "l", 0.0) or 0.0 for o in objs)
            gap = d.physical.length - oce_len
            if gap > 1e-9:
                elements.append(Drift(l=gap, eid=f"{d.name}_len"))

        maglat = MagneticLattice(elements, method=method)
        if save:
            maglat.save_as_py_file(f"{self.directory}/{self.name}.py")

        return maglat

    def to_cheetah(self, save=False) -> "Segment":
        """
        Create a Cheetah-compatible lattice segment object based on the lattice information.

        Parameters
        ----------
        save: bool
            Flag to indicate whether to save the lattice to a file.

        Returns
        -------
        Segment
            A Cheetah `Segment` object.
        """
        from cheetah import Segment

        section_with_drifts = self.createDrifts()
        elem_dict = translate_elements(
            section_with_drifts.values(),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        segment = []
        segments = False
        for element in elem_dict.values():
            if not element.subelement:
                elem = element.to_cheetah()
                if elem is not None:
                    segment.append(elem)
                    segments = True
        if segments:
            full_segment = Segment(elements=segment, name=self.name)
        else:
            raise ValueError(f"No cheetah elements added for {self.name}")

        if save:
            full_segment.to_lattice_json(filepath=f"{self.directory}/{self.name}.json")

        return full_segment

    def to_xsuite(
        self, beam_length: int, env: Any = None, particle_ref: Any = None, save=True
    ) -> "Line":
        """
        Create an Xsuite-compatible lattice line object based on the lattice information.

        Parameters
        ----------
        beam_length: int
            Number of particles in the beam
        env: xtrack.Environment
            xtrack Environment object; if `None`, it will be created
        particle_ref: xtrack.Particles
            xtrack Particles object
        save: bool
            Flag to indicate whether to save the `Line` to JSON.

        Returns
        -------
        Segment
            A Xsuite `Line` object.
        """
        import xtrack as xt

        if not isinstance(env, xt.Environment):
            env = xt.Environment()
        if not IgnoreExtra.resolve_functional:
            for name, value in (
                self.functional_definitions or IgnoreExtra.functional_definitions
            ).items():
                env[name] = value
        section_with_drifts = self.createDrifts()
        elem_dict = translate_elements(
            section_with_drifts.values(),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        def _is_symbolic(value: Any) -> bool:
            if isinstance(value, str):
                return True
            if isinstance(value, (list, tuple)):
                return any(isinstance(v, str) for v in value)
            return False

        line = env.new_line()
        for i, element in enumerate(list(elem_dict.values())):
            if not element.subelement:
                name, component, properties = element.to_xsuite(beam_length=beam_length)
                if any(_is_symbolic(v) for v in properties.values()):
                    env.new(element.name, component, **properties)
                    line.append(element.name)
                else:
                    line.append(element.name, component(**properties))
        if isinstance(particle_ref, xt.Particles):
            line.particle_ref = particle_ref
        if save:
            line.to_json(f"{self.directory}/{self.name}.json")
        return line

    def to_csrtrack(self) -> str:
        """
        Create a CSRTrack-compatible input file based on the lattice information and
        the settings provided in :attr:`~csrtrack_headers`.

        Returns
        -------
        str
            A CSRTrack-compatible lattice file.
        """
        headers = ["dipole", "quadrupole", "screen"]
        counter = {k: 1 for k in headers}
        elem_dict = translate_elements(
            list(self.elements.elements.values()),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        csrtrackstr = "io_path{logfile = log.txt}\nlattice{\n"
        for e in elem_dict.values():
            for key, count in counter.items():
                if e.hardware_type.lower() == key:
                    csrtrackstr += e.to_csrtrack(n=count)
                    counter[key] += 1
                else:
                    if not e.hardware_class == "Diagnostic":
                        warn(
                            f"Element of type {e.hardware_type} not supported for CSRTrack"
                        )
        lastelem = list(elem_dict.values())[-1]
        lastscreen = DiagnosticTranslator(
            name="end_screen",
            hardware_class="Diagnostic",
            hardware_type="Diagnostic",
            machine_area=lastelem.machine_area,
            simulation=DiagnosticSimulationElement(
                output_filename="end_screen.csrtrack"
            ),
            physical=lastelem.physical,
        )
        csrtrackstr += lastscreen.to_csrtrack(n=counter["screen"])
        csrtrackstr += "}\n"
        self.csrtrack_headers["tracker"].end_time_marker = (
            "screen" + str(counter["screen"]) + "b"
        )
        for h in self.csrtrack_headers.values():
            csrtrackstr += h.write_CSRTrack()
        return csrtrackstr

    def to_madx(
        self, beam: Dict[str, Any] | None = None, refer: str = "entry"
    ) -> str:
        """
        Create a MAD-X-compatible ``SEQUENCE`` definition based on the lattice
        information, suitable for :meth:`cpymad.madx.Madx.input` (see the
        `MAD-X User Guide <https://madx.web.cern.ch/webguide/manual.html>`_).

        Elements are placed at their entrance s-position (``refer=entry``, the
        default) or, when ``refer`` is ``"centre"``/``"center"``, at their centre
        (required before a MAD-X ``MAKETHIN``/``TRACK``).
        Explicit ``drift`` elements are inserted between elements via
        :meth:`createDrifts` and written into the sequence like any other
        element, which is the standard way of constructing a MAD-X lattice
        (rather than relying on MAD-X's implicit gap-filling between elements
        placed without a contiguous ``at=``).

        Parameters
        ----------
        beam: dict
            A dictionary describing a beam distribution with the keys as defined in the
            `Beam Section of the MAD-X User Guide <https://madx.web.cern.ch/webguide/manual.html#Ch7.S1>`_
        refer: str
            Gives a reference position for element placement, related to the ``at=`` parameter.

        Returns
        -------
        str
            A MAD-X-compatible ``SEQUENCE`` definition, prefixed with variable
            declarations for any functional definitions used symbolically by
            the lattice's elements.
        """
        section_with_drifts = self.createDrifts()
        elem_dict = translate_elements(
            section_with_drifts.values(),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        svals = self.get_s_values(as_dict=True, at_entrance=True)
        exit_svals = self.get_s_values(as_dict=True, at_entrance=False)
        length = max(exit_svals.values()) if exit_svals else 0.0
        centre = str(refer).lower() in ("centre", "center")
        refer = "centre" if centre else "entry"
        fulltext = ""
        for d in elem_dict.values():
            at = d.physical.start.z if d.subelement else svals[d.name]
            if centre:
                at += d.physical.length / 2
            fulltext += d.to_madx(at=at)

        seqstring = madx_functional_definitions(self.functional_definitions)
        has_beam = isinstance(beam, Dict)
        if has_beam:
            beamstr = "BEAM"
            for k, v in beam.items():
                beamstr += f", {k.upper()}={v}"
            beamstr += f", SEQUENCE = {sanitize_string(self.name)};\n"
            seqstring += beamstr
        seqstring += f"{sanitize_string(self.name)}: SEQUENCE, refer={refer}, l = {length};\n"
        seqstring += fulltext
        seqstring += "ENDSEQUENCE;\n"
        if has_beam:
            # USE is only meaningful once a BEAM has been declared for the
            # sequence -- MAD-X aborts with "USE - sequence without beam"
            # otherwise. Without a beam this is a plain sequence definition,
            # to be USEd by the caller after it issues its own BEAM.
            seqstring += f"USE, PERIOD={sanitize_string(self.name)};"
        return seqstring

    def to_wake_t(self) -> "Beamline":
        """
        Create a Wake-T-compatible beamline object based on the lattice information.

        Returns
        -------
        Segment
            A Wake-T `Beamline` object.
        """
        from wake_t import Beamline

        section_with_drifts = self.createDrifts()
        elem_dict = translate_elements(
            section_with_drifts.values(),
            master_lattice=self.master_lattice,
            directory=self.directory,
        )
        beamline = []
        for element in elem_dict.values():
            if not element.subelement:
                # try:
                if element.length > 0:
                    beamline.append(element.to_wake_t())
                # except Exception as e:
                #     print('Wake-T writeElements error:', element.name, e)
        return Beamline(beamline)
