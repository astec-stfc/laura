import numpy as np
from pydantic import computed_field, model_validator

from laura.models.rf import RFCavityElement
from laura.models.simulation import RFCavitySimulationElement
from laura.translator.utils.fields import FieldMap

from ..converters import (
    elements_bmad,
    elements_elegant,
    elements_madx,
    elements_opal,
)
from ..utils.functions import sanitize_string
from .base import BaseElementTranslator, ocelot_attributes


class RFCavityTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.RFCavity` element instance into a string or
    object that can be understood by various simulation codes.
    """

    cavity: RFCavityElement
    """Cavity element."""

    simulation: RFCavitySimulationElement
    """Cavity simulation element"""

    wakefile: str | None = None
    """Name of wakefile associated with the cavity."""

    trwakefile: str | None = None
    """Name of transverse wakefile associated with the cavity."""

    zwakefile: str | None = None
    """Name of longitudinal wakefile associated with the cavity."""

    bmad_geometry: str | None = None
    """Geometry of the branch this cavity is being written into, when known.

    Set to ``"closed"`` by :meth:`SectionLatticeTranslator.to_bmad` so the
    cavity can pick the form Bmad allows there; see :meth:`to_bmad`."""

    @model_validator(mode="before")
    @classmethod
    def preserve_cavity_subtype_and_madx_defaults(cls, data):
        """Rebuild the specialised cavity payload needed by each exporter.

        ``translate_elements`` passes a serialised element dictionary to its
        translators. MAD-X ``TWCAVITY`` does not use the ASTRA-only mode
        fraction, so supply its neutral value when the serialized payload has
        none. Deflecting versus accelerating output is selected from
        ``hardware_type``, not from the payload model class.
        """
        if not isinstance(data, dict) or not isinstance(data.get("cavity"), dict):
            return data

        payload = dict(data)
        cavity = dict(payload["cavity"])
        if str(cavity.get("structure_type", "")).lower() == "travellingwave":
            if cavity.get("mode_numerator") is None:
                cavity["mode_numerator"] = 1
            if cavity.get("mode_denominator") is None:
                cavity["mode_denominator"] = 1
            payload["cavity"] = RFCavityElement(**cavity)

        return payload

    @computed_field
    @property
    def structure_type(self) -> str:
        """
        The structure type, spelled the one way the rest of this class tests for.
        Works for US and British spelling (Travelling/Traveling wave)
        """
        value = str(getattr(self.cavity, "structure_type", "StandingWave"))
        return {
            "travellingwave": "TravellingWave",
            "travelingwave": "TravellingWave",
            "standingwave": "StandingWave",
        }.get(value.replace("_", "").lower(), value)

    @property
    def phase(self) -> float:
        """Cavity phase, resolving a functional definition if set symbolically."""
        return self.resolve(self.cavity.phase)

    @property
    def field_amplitude(self) -> float:
        """Cavity field amplitude, resolving a functional definition if set symbolically."""
        return self.resolve(self.simulation.field_amplitude)

    @computed_field
    @property
    def tcolumn(self) -> str | None:
        return f'"{self.simulation.t_column}"' if self.simulation.t_column else None

    @computed_field
    @property
    def zcolumn(self) -> str | None:
        return f'"{self.simulation.z_column}"' if self.simulation.z_column else None

    @computed_field
    @property
    def wxcolumn(self) -> str | None:
        return f'"{self.simulation.wx_column}"' if self.simulation.wx_column else None

    @computed_field
    @property
    def wycolumn(self) -> str | None:
        return f'"{self.simulation.wy_column}"' if self.simulation.wy_column else None

    @computed_field
    @property
    def wzcolumn(self) -> str | None:
        return f'"{self.simulation.wz_column}"' if self.simulation.wz_column else None

    def to_bmad(self) -> str:
        """
        Generate a Bmad RF or crab-cavity definition.

        Returns
        -------
        str
            String representation of the element for Bmad
        """
        self.start_write()
        etype = self._convert_type_bmad(self.hardware_type)
        if etype == "lcavity" and self.bmad_geometry == "closed":
            etype = "rfcavity"
        parameters = self._bmad_parameters(etype)
        phase = self.cavity.phase
        parameters["phi0"] = (
            f"-({phase}) / 360"
            if not self._resolve_functional and self.is_functional(phase)
            else -self.resolve(phase) / 360
        )
        voltage = parameters.get("voltage")
        if voltage is not None and self.structure_type == "TravellingWave":
            factor = abs(
                (self.get_cells() + 3.8) * self.cavity.cell_length * (1 / np.sqrt(2))
            )
            parameters["voltage"] = (
                f"({voltage}) * {factor}"
                if not self._resolve_functional and self.is_functional(voltage)
                else factor * self.resolve(voltage)
            )
        if "cavity_type" in elements_bmad[etype]:
            structure = str(self.structure_type).replace("_", "").lower()
            parameters["cavity_type"] = {
                "standingwave": "standing_wave",
                "travellingwave": "traveling_wave",
                "travelingwave": "traveling_wave",
            }.get(structure, structure)
        self._bmad_sr_wake(parameters)
        return self._format_bmad(etype, parameters)

    def set_wakefield_column_names(self, wakefield_file_name: str | None) -> None:
        """
        Set the column names for the wakefield file, based on ``wakefield_definition``.

        Parameters
        ----------
        wakefield_file_name: str or None
            Name of the wakefield file; nothing is set if there is no file
        """
        if wakefield_file_name is None:
            return
        if all([x is not None for x in [self.wxcolumn, self.wycolumn, self.wzcolumn]]):
            self.wakefile = f'"{wakefield_file_name}"'
            return
        elif self.wzcolumn is not None and all(
            [x is None for x in [self.wxcolumn, self.wycolumn]]
        ):
            self.zwakefile = f'"{wakefield_file_name}"'
            return
        elif self.wzcolumn is None and all(
            [x is not None for x in [self.wxcolumn, self.wycolumn]]
        ):
            self.trwakefile = f'"{wakefield_file_name}"'
            return

    def to_elegant(self) -> str:
        """
        Writes the cavity element string for ELEGANT.

        Returns
        -------
        str
            String representation of the element for ELEGANT
        """
        self.start_write()
        wholestring = ""
        etype = self._convert_type_elegant(self.hardware_type)
        if self.hardware_type == "RFCavity" and not self._wakefield_active():
            etype = "rfca"
        elif self._wakefield_active():
            wakefield_file_name = self.generate_field_file_name(
                self.simulation.wakefield_definition, code="elegant"
            )
            self.set_wakefield_column_names(wakefield_file_name)
        string = f"{self.name}: {etype}"
        preferred = {
            "n_kicks": (
                "simulation_n_kicks" if self.simulation.n_kicks else "cavity_n_cells"
            )
        }
        keys = []
        for output, direct, nested in (
            ("wakefile", "wakefile", "simulation_wakefile"),
            ("zwakefile", "zwakefile", "simulation_zwakefile"),
            ("trwakefile", "trwakefile", "simulation_trwakefile"),
            ("tcolumn", "tcolumn", "simulation_t_column"),
            ("zcolumn", "zcolumn", "simulation_z_column"),
            ("wxcolumn", "wxcolumn", "simulation_wx_column"),
            ("wycolumn", "wycolumn", "simulation_wy_column"),
            ("wzcolumn", "wzcolumn", "simulation_wz_column"),
        ):
            preferred[output] = direct if getattr(self, direct) is not None else nested
        emitted = set()
        # `_convert_keyword_elegant`, built once rather than per key
        convert = self._keyword_converter_elegant(
            self._convert_type_elegant(self.hardware_type)
        )
        for source_key, value in self.full_dump(
            resolve=self._resolve_functional
        ).items():
            converted_key = convert(source_key).lower()
            if preferred.get(converted_key, source_key) != source_key:
                continue
            if converted_key in emitted:
                continue
            if (
                source_key not in {"name", "type", "commandtype"}
                and converted_key in elements_elegant[etype]
                and value is not None
            ):
                key = converted_key
                emitted.add(key)
                # rftmez0 uses frequency instead of freq
                if etype == "rftmez0" and key == "freq":
                    key = "frequency"
                functional = self.is_functional(value)
                if self.hardware_type in [
                    "RFCavity",
                    "RFDeflectingCavity",
                    "CrabCavity",
                ]:
                    if key == "phase":
                        if etype == "rftmez0":
                            # If using rftmez0 or similar
                            if functional:
                                value = self._rpn(value, 360.0, "/", 2 * 3.14159, "*")
                            else:
                                value = (value / 360.0) * (2 * 3.14159)
                        else:
                            value = (
                                self._rpn(90, value, "-") if functional else 90 - value
                            )

                # In ELEGANT the voltages need to be compensated
                if key == "volt":
                    if self.structure_type == "TravellingWave":
                        factor = abs(
                            (self.get_cells() + 3.8)
                            * self.cavity.cell_length
                            * (1 / np.sqrt(2))
                        )
                        value = (
                            self._rpn(factor, value, "*")
                            if functional
                            else factor * value
                        )
                    elif functional:
                        value = self._elegant_value(value)
                elif key == "voltage" and functional:
                    value = self._elegant_value(value)
                # If using rftmez0 or similar
                if key == "ez_peak":
                    value = (
                        self._rpn(1e-3 / np.sqrt(2), value, "*", "abs")
                        if functional
                        else abs(1e-3 / (np.sqrt(2)) * value)
                    )

                if key == "wakefile":
                    value = value

                if key == "body_focus_model" and not self.length:
                    continue
                if (
                    key == "body_focus_model"
                    and self.structure_type == "TravellingWave"
                ):
                    value = "TW1"

                # In CAVITY NKICK = n_cells
                if (
                    key == "n_kicks"
                    and source_key == "cavity_n_cells"
                    and self.get_cells() > 1
                ):
                    value = 3 * self.get_cells()

                if key == "n_bins" and not functional and value > 0:
                    print(
                        "WARNING: Cavity n_bins is not zero - check log file to ensure correct behaviour!"
                    )
                value = 1 if value is True else value
                value = 0 if value is False else value
                if key not in keys:
                    string += f", {key} = {value!s}"
                keys.append(key)
        wholestring += f"{string};\n"
        return wholestring

    def to_ocelot(self) -> object:
        """
        Creates the cavity element for Ocelot.

        Returns
        -------
        object
            Ocelot Cavity object
        """
        from ..conversion_rules.codes import ocelot_conversion

        type_conversion_rules_ocelot = ocelot_conversion.ocelot_conversion_rules
        self.start_write()
        self.generate_field_file_name(
            self.simulation.wakefield_definition, code="astra"
        )
        obj = type_conversion_rules_ocelot[self.hardware_type](eid=self.name)
        attributes = ocelot_attributes(type(obj))
        convert = self._keyword_converter("ocelot")
        for key, value in self.full_dump().items():
            if (
                not key == "name"
                and not key == "type"
                and not key == "commandtype"
                and (value.size > 0 if isinstance(value, np.ndarray) else value)
                and convert(key) in attributes
            ):
                key = convert(key).lower()
                if self.hardware_type in ["RFCavity", "RFDeflectingCavity"]:
                    if key == "v":
                        if self.structure_type == "TravellingWave":
                            value = (
                                value
                                * 1e-9
                                * abs(
                                    (self.get_cells() + 3.8)
                                    * self.cavity.cell_length
                                    * (1 / np.sqrt(2))
                                )
                            )
                        else:
                            value = value * 1e-9
                setattr(obj, key, value)
        if not obj.l:
            obj.l = 1e-9
        return obj

    def to_cheetah(self) -> object:
        """
        Creates the cavity element for Cheetah.

        Returns
        -------
        object
            Cheetah Cavity object
        """
        from torch import float64, tensor

        from ..conversion_rules.codes import cheetah_conversion

        type_conversion_rules_cheetah = cheetah_conversion.cheetah_conversion_rules
        self.start_write()
        obj = type_conversion_rules_cheetah[self.hardware_type](
            name=self.name,
            length=tensor(self.physical.length, dtype=float64),
            sanitize_name=True,
        )
        buffers = obj.__class__(
            length=tensor(self.physical.length, dtype=float64)
        )._buffers
        for key, value in self.full_dump().items():
            if (key not in ["name", "type", "commandtype"]) and (
                self._convert_keyword_cheetah(key) in buffers
            ):
                key = self._convert_keyword_cheetah(key)
                value = (
                    getattr(self, key)
                    if hasattr(self, key) and getattr(self, key) is not None
                    else value
                )
                if key == "voltage":
                    if self.structure_type == "TravellingWave":
                        value = value * abs(
                            (self.get_cells() + 3.8)
                            * self.cavity.cell_length
                            * (1 / np.sqrt(2))
                        )
                    else:
                        value = value
                if isinstance(value, float):
                    dt = float64
                    setattr(
                        obj, self._convert_keyword_cheetah(key), tensor(value, dtype=dt)
                    )
                elif isinstance(value, int):
                    from torch import int64

                    dt = int64
                    setattr(
                        obj, self._convert_keyword_cheetah(key), tensor(value, dtype=dt)
                    )
        if hasattr(obj, "cavity_type"):
            if self.cavity.structure_type == "TravellingWave":
                obj.cavity_type = "traveling_wave"
            else:
                obj.cavity_type = "standing_wave"
        self._cheetah_float64(obj)
        return obj

    def to_astra(self, n: int = 0, **kwargs: dict) -> str:
        """
        Writes the cavity element string for ASTRA.

        Parameters
        ----------
        n: int
            Element index number
        **kwargs: dict
            Keyword args

        Returns
        -------
        str
            String representation of the element for ASTRA
        """
        self.start_write()
        field_ref_pos = self.get_field_reference_position()
        auto_phase = kwargs["auto_phase"] if "auto_phase" in kwargs else True
        crest = self.cavity.crest if not auto_phase else 0
        field_file_name = self.generate_field_file_name(
            self.simulation.field_definition, code="astra"
        )
        if field_file_name is None:
            raise ValueError(
                f"{self.name}: ASTRA cavities need a field map "
                "(simulation.field_definition)."
            )
        return self._write_astra_dictionary(
            {
                "C_pos": {"value": field_ref_pos[2] + self.dz, "default": 0},
                "FILE_EFieLD": {"value": f"'{field_file_name}'", "default": ""},
                "C_numb": {"value": self.get_cells()},
                "Nue": {
                    "value": float(self.cavity.frequency) / 1e9,
                    "default": 2998.5,
                },
                "MaxE": {
                    "value": float(self.field_amplitude) / 1e6,
                    "default": 0,
                },
                "Phi": {"value": crest - self.phase, "default": 0.0},
                "C_smooth": {"value": self.simulation.smooth, "default": None},
                "C_xoff": {
                    "value": field_ref_pos[0] + self.dx,
                    "default": None,
                    "type": "not_zero",
                },
                "C_yoff": {
                    "value": field_ref_pos[1] + self.dy,
                    "default": None,
                    "type": "not_zero",
                },
                "C_xrot": {
                    "value": self._astra_rotation("x"),
                    "default": None,
                    "type": "not_zero",
                },
                "C_yrot": {
                    "value": self._astra_rotation("y"),
                    "default": None,
                    "type": "not_zero",
                },
                "C_zrot": {
                    "value": self._astra_rotation("z"),
                    "default": None,
                    "type": "not_zero",
                },
            },
            n,
        )

    def to_xsuite(self, beam_length: int) -> tuple:
        """
        Generates an Xsuite object based on the element's properties and type.

        Parameters
        ----------
        beam_length: int
            Number of macroparticles in the beam

        Returns
        -------
        tuple
            (objectname, Xsuite object, properties[dict])
        """
        from ..conversion_rules.codes import xsuite_conversion

        type_conversion_rules_xsuite = xsuite_conversion.xsuite_conversion_rules
        self.start_write()
        obj = type_conversion_rules_xsuite[self.hardware_type]
        properties = {}
        for key, value in self.full_dump(resolve=self._resolve_functional).items():
            if (key not in ["name", "type", "commandtype"]) and (
                self._convert_keyword_xsuite(key) in list(obj.__dict__.keys())
            ):
                key = self._convert_keyword_xsuite(key)
                functional = self.is_functional(value)
                if key == "phase":
                    value = (
                        f"(90 - ({value})) * {np.pi / 180}"
                        if functional
                        else np.radians(90 - value)
                    )
                if key == "voltage" and not functional:
                    if self.structure_type == "TravellingWave":
                        value = value * abs(
                            (self.get_cells() + 3.8)
                            * self.cavity.cell_length
                            * (1 / np.sqrt(2))
                        )
                    else:
                        value = value
                if key == "num_kicks" and value is None and self.get_cells() > 1:
                    value = 3 * self.get_cells()
                if value is not None:
                    properties.update({key: value})
        return self.name, obj, properties

    def to_madx(self, at: float = None) -> str:
        """
        Writes the cavity element string for MAD-X.

        MAD-X ``VOLT`` is in MV and ``FREQ`` in MHz (LAURA stores volts and Hz),
        and ``LAG`` is the phase lag in fractions of a full RF cycle with the
        crest at ``LAG = 0.25`` (a sine convention), so LAURA's
        off-crest-is-zero ``phase`` [deg] is converted via
        ``lag = (90 - phase) / 360`` -- the same +90 degree convention used for
        ELEGANT, expressed as a fraction of 360 degrees rather than degrees.

        A travelling-wave cavity (``cavity.structure_type == "TravellingWave"``)
        is written as a MAD-X ``TWCAVITY`` rather than the standing-wave
        ``RFCAVITY``.

        Parameters
        ----------
        at: float, optional
            S-position at which to place the element inside a MAD-X ``SEQUENCE``;
            see :meth:`~laura.translator.converters.base.BaseElementTranslator.to_madx`.

        Returns
        -------
        str
            String representation of the element for MAD-X
        """
        self.start_write()
        etype = self._convert_type_madx(self.hardware_type)
        string = f"{sanitize_string(self.name)}: {etype}"
        for key, value in self._dump_items(
            self._convert_keyword_madx,
            elements_madx[etype],
            resolve=self._resolve_functional,
            unique=False,
        ):
            functional = self.is_functional(value) and not self._resolve_functional
            if key == "lag":
                value = (
                    f"(90 - ({value})) / 360" if functional else (90 - value) / 360.0
                )
            if key == "volt":
                if self.structure_type == "TravellingWave":
                    factor = abs(
                        (self.get_cells() + 3.8)
                        * self.cavity.cell_length
                        * (1 / np.sqrt(2))
                    )
                else:
                    factor = 1.0
                value = (
                    f"({value}) * {factor / 1e6}"
                    if functional
                    else factor * value / 1e6
                )
            if key == "freq" and not functional:
                value = value / 1e6
            string += f", {key} {':=' if functional else '='} {self._flag(value)}"
        if at is not None:
            string += f", at = {at}"
        return f"{string};\n"

    def to_opal(self, sval: float, designenergy: float | None = None) -> str:
        """
        Generates a string representation of the object's properties in the OPAL format.

        Parameters
        ----------
        sval: float
            S-position of the element
        designenergy: float, optional
            Beam energy at element in MeV

        Returns
        -------
        str
            A formatted string representing the object's properties in OPAL format.
        """
        self.start_write()
        etype = self._convert_type_opal(self.hardware_type)
        if self.structure_type == "TravellingWave":
            etype = "travelingwave"
        wholestring = f"{self.name.replace('-', '_')}: {etype}"
        if etype.lower() == "drift" or self.simulation.field_definition is None:
            return ""
        for key, value in self._dump_items(
            self._convert_keyword_opal, elements_opal[etype], unique=False
        ):
            if key == "lag":
                value = -value * np.pi / 180
            if key in ("freq", "volt"):
                value = value / 1e6
            wholestring += f", {key} = {self._flag(value)}"
        if isinstance(self.simulation.field_definition, FieldMap):
            wholestring += f', fmapfn = "{self.generate_field_file_name(self.simulation.field_definition, code="opal")}"'
            if self.structure_type == "TravellingWave":
                mode = float(self.simulation.field_definition.mode_numerator) / float(
                    self.simulation.field_definition.mode_denominator
                )
                wholestring += f", mode = {mode}"
        wholestring += f", ELEMEDGE = {sval};\n"
        return wholestring

    def get_cells(self) -> int:
        """
        Get the number of cavity cells.

        Returns
        -------
        int or None
            The number of cavity cells, or None if not defined.
        """
        if (
            self.cavity.n_cells == 0 or self.cavity.n_cells is None
        ) and self.cavity.cell_length > 0:
            cells = round(
                (self.physical.length - self.cavity.cell_length)
                / self.cavity.cell_length
            )
            cells = int(cells - (cells % 3))
        elif self.cavity.n_cells:
            if self.cavity.cell_length == self.physical.length:
                cells = 1
            else:
                cells = int(self.cavity.n_cells - (self.cavity.n_cells % 3))
        else:
            cells = 0
        return cells

    def to_gpt(self, Brho: float = 0.0, *args, **kwargs) -> str:
        """
        Write a string representation of the cavity for GPT

        #TODO note that not all possible ways of writing a cavity in GPT are currently supported.

        Parameters
        ----------
        Brho: float
            Magnetic rigidity; not used

        Returns
        -------
        str
            String representation of the cavity for GPT.
        """
        self.start_write()
        field_ref_pos = self.get_field_reference_position()
        ccs_label, value_text = self.ccs.ccs_text(
            field_ref_pos, list(self.physical.rotation.model_dump().values())
        )
        relpos, _ = self.ccs.relative_position(
            field_ref_pos, list(self.physical.global_rotation.model_dump().values())
        )
        field_file_name = self.generate_field_file_name(
            self.simulation.field_definition, code="gpt"
        )
        self.generate_field_file_name(self.simulation.wakefield_definition, code="gpt")
        """
        map1D_TM("wcs","z",linacposition,"mockup2m.gdf","Z","Ez",ffacl,phil,w);
        wakefield("wcs","z",  6.78904 + 4.06667 / 2, 4.06667, 50, "Sz5um10mm.gdf", "z","","","Wz", "FieldFactorWz", 10 * 122 / 4.06667) ;
        """
        subname = str(relpos[2]).replace(".", "")
        output = ""
        if field_file_name is not None:
            output = (
                f"f{subname} = {self.cavity.frequency!s};\n"
                f"w{subname} = 2*pi*f{subname};\n"
                f"phi{subname} = {(self.cavity.crest + 90 - self.phase + 0) % 360.0!s}/deg;\n"
            )
            if self.structure_type == "TravellingWave":
                output += f"ffac{subname} = 1.007 * {9.0 / (2.0 * np.pi) * self.field_amplitude!s};\n"
            else:
                output += f"ffac{subname} = {self.field_amplitude!s};\n"

            output += f'map1D_TM("{self.ccs.name}", {ccs_label}, {value_text}, "{field_file_name!s}", "z", "Ez", ffac{subname}, phi{subname}, w{subname});\n'
        else:
            output = ""
        return output
