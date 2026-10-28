from laura.models.rf import WakefieldElement
from laura.models.simulation import WakefieldSimulationElement

from ..utils.fields import FieldMap
from .base import BaseElementTranslator


class WakefieldTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.Wakefield` instance into a string or
    object that can be understood by various simulation codes.
    """

    cavity: WakefieldElement
    """Wakefield element."""

    simulation: WakefieldSimulationElement
    """Wakefield simulation attributes."""

    def to_bmad(self) -> str:
        """
        Generate a drift carrying a short-range wake for Bmad.

        Returns
        -------
        str
            String representation of the element for Bmad
        """
        self.start_write()
        parameters = self._bmad_sr_wake(self._bmad_parameters("drift"))
        return self._format_bmad("drift", parameters)

    def to_elegant(self) -> str:
        """
        Writes the wakefield element string for ELEGANT, as an ``rfcw`` with no voltage:
        ELEGANT's ``wake`` element has no length, and ``rfcw`` scales the per-cell wake
        by ``l / cell_length``, so it is applied once per cell, as in ASTRA and GPT.

        Returns
        -------
        str
            String representation of the element for ELEGANT
        """
        self.start_write()
        length = self.physical.length
        wake = self.simulation.wakefield_definition
        if not (
            isinstance(wake, FieldMap)
            and self.simulation.scale_kick > 0
            and getattr(self.simulation, "wakefield_enable", True)
        ):
            return f"{self.name}: drift, l = {length};\n"
        if not length:
            raise ValueError(f"Wakefield {self.name} has no length")
        filename = self.generate_field_file_name(wake, code="elegant")
        columns = [
            col
            for col in ("Wx", "Wy", "Wz")
            if getattr(getattr(wake, col, None), "value", None) is not None
        ]
        wakefile = (
            "zwakefile"
            if columns == ["Wz"]
            else "wakefile"
            if "Wz" in columns
            else "trwakefile"
        )
        return (
            f"{self.name}: rfcw, l = {length}, volt = 0, cell_length = {length / self.cavity.n_cells},&\n"
            f' {wakefile} = "{filename}", tcolumn = "t", '
            + ", ".join(f'{col.lower()}column = "{col}"' for col in columns)
            + ", n_bins = 0;\n"
        )

    def to_astra(self, n: int = 0, **kwargs: dict) -> str:
        """
        Writes the wakefield element string for ASTRA;
        see :func:`~_write_astra`.

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
        return self._write_astra(n=n)

    @property
    def astra_wake_spacing(self) -> tuple[float, int]:
        """
        How far apart to place the ``&WAKE`` entries, and how many to write.

        ASTRA applies a wake file in full at every position it is placed, so the
        number of copies has to match the length the wake was tabulated over.

        Returns
        -------
        tuple[float, int]
            Spacing between consecutive wakes [m], and the number to write.
        """
        wake_length = getattr(
            self.simulation.wakefield_definition, "reference_length", None
        )
        if not wake_length:
            return self.cavity.cell_length, int(self.cavity.n_cells)
        return wake_length, max(1, round(self.physical.length / wake_length))

    def _write_astra(self, n: int = 0, **kwargs: dict) -> str:
        """
        Writes the wakefield element string for ASTRA, one &WAKE element per
        length of structure the wake file covers; see
        :func:`~astra_wake_spacing`.

        Parameters
        ----------
        n: int
            Index of this cavity's first wake among all the wakes in the deck

        Returns
        -------
        str
            String representation of the element for ASTRA
        """
        field_file_name = self.generate_field_file_name(
            self.simulation.wakefield_definition, code="astra"
        )
        output = ""
        if self.simulation.wakefield_definition.field_type == "LongitudinalWake":
            waketype = "Monopole_Method_F"
        elif self.simulation.wakefield_definition.field_type == "TransverseWake":
            waketype = "Dipole_Method_F"
        else:
            waketype = "Taylor_Method_F"
        # scale_kick alone is not enough: wakefields also have to be
        # switched off when the section asks for it via wakefield_enable.
        if self.simulation.scale_kick > 0 and getattr(
            self.simulation, "wakefield_enable", True
        ):
            spacing, n_wakes = self.astra_wake_spacing
            for i in range(n_wakes):
                output += self._write_astra_dictionary(
                    {
                        "Wk_Type": {
                            "value": f'"{waketype}"',
                            "default": "'Taylor_Method_F'",
                        },
                        "Wk_filename": {"value": f"'{field_file_name}'", "default": ""},
                        "Wk_x": {"value": self.dx, "default": 0},
                        "Wk_y": {"value": self.dy, "default": 0},
                        "Wk_z": {"value": self.physical.start.z + (0.5 + i) * spacing},
                        "Wk_ex": {
                            "value": self.simulation.scale_field_ex,
                            "default": 0,
                        },
                        "Wk_ey": {
                            "value": self.simulation.scale_field_ey,
                            "default": 0,
                        },
                        "Wk_ez": {
                            "value": self.simulation.scale_field_ez,
                            "default": 1,
                        },
                        "Wk_hx": {
                            "value": self.simulation.scale_field_hx,
                            "default": 1,
                        },
                        "Wk_hy": {
                            "value": self.simulation.scale_field_hy,
                            "default": 0,
                        },
                        "Wk_hz": {
                            "value": self.simulation.scale_field_hz,
                            "default": 0,
                        },
                        "Wk_equi_grid": {
                            "value": self.simulation.equal_grid,
                            "default": 0.66,
                        },
                        "Wk_N_bin": {"value": 10, "default": 100},
                        "Wk_ip_method": {
                            "value": self.simulation.interpolation_method,
                            "default": 2,
                        },
                        "Wk_smooth": {"value": self.simulation.smooth, "default": 0.25},
                        "Wk_sub": {"value": self.simulation.subbins, "default": 10},
                        "Wk_scaling": {
                            "value": 1 * self.simulation.scale_kick,
                            "default": 1,
                        },
                    },
                    n + i,
                )
                output += "\n"
            output += "\n"
        return output

    def to_gpt(self, Brho: float = 0.0, *args, **kwargs) -> str:
        """
        Write a string representation of the wakefield for GPT.

        Parameters
        ----------
        Brho: float
            Magnetic rigidity.

        Returns
        -------
        str
            String representation of the wakefield for GPT.
        """
        self.start_write()
        field_ref_pos = self.get_field_reference_position()
        field_file_name = self.generate_field_file_name(
            self.simulation.wakefield_definition, code="gpt"
        )
        fringe_field_coefficient = 3.0 / self.cavity.cell_length
        output = ""
        # scale_kick alone is not enough: wakefields also have to be
        # switched off when the section asks for it via wakefield_enable.
        if self.simulation.scale_kick > 0 and getattr(
            self.simulation, "wakefield_enable", True
        ):
            zcolumn = "z"
            wake = self.simulation.wakefield_definition
            wxcolumn, wycolumn, wzcolumn = (
                col
                if getattr(getattr(wake, col, None), "value", None) is not None
                else ""
                for col in ("Wx", "Wy", "Wz")
            )
            # GPT takes wakes per metre over L, and a positive Wz accelerates;
            # LAURA's are per cell, with a positive Wz an energy loss
            factors = "".join(
                f', "FieldFactor{col}", {sign / self.cavity.cell_length}'
                for col, sign in ((wxcolumn, 1), (wycolumn, 1), (wzcolumn, -1))
                if col
            )
            for n in range(int(self.cavity.n_cells)):
                # GPT's wakefield() spans -L/2 < z < L/2, so each is centred on its cell
                ccs_label, value_text = self.ccs.ccs_text(
                    [
                        field_ref_pos[0],
                        field_ref_pos[1],
                        field_ref_pos[2]
                        + self.cavity.coupling_cell_length
                        + (n + 0.5) * self.cavity.cell_length,
                    ],
                    list(self.physical.rotation.model_dump().values()),
                )
                output += f'wakefield("{self.ccs.name}", {ccs_label}, {value_text}, {self.cavity.cell_length!s}, {fringe_field_coefficient!s}, "{field_file_name!s}", "{zcolumn}", "{wxcolumn}", "{wycolumn}", "{wzcolumn}"{factors});\n'
        return output
