import math
from typing import Dict
from warnings import warn

from laura.models.simulation import ApertureElement

from ..converters import elements_elegant, elements_madx
from ..utils.functions import sanitize_string
from .base import BaseElementTranslator, bmad_limits, elegant_line


class ApertureTranslator(BaseElementTranslator):
    """Apertures and collimators. Every code gets a local aperture of the
    LAURA shape; a code with only thin apertures gets one at each end of a
    drift, which is exact for a convex aperture."""

    aperture: ApertureElement

    @property
    def _elliptical(self) -> bool:
        shape = getattr(self.aperture.shape, "value", self.aperture.shape)
        return shape in ("elliptical", "circular")

    def _offsets(self) -> tuple:
        return self.aperture.horizontal_offset, self.aperture.vertical_offset

    def _warn_dropped_offset(self, code: str) -> None:
        if any(self._offsets()):
            warn(
                f"{code} apertures are centred; the offset of {self.name!r} was dropped."
            )

    def _convert_type_madx(self, etype: str) -> str:
        return "ecollimator" if self._elliptical else "rcollimator"

    def _convert_type_elegant(self, etype: str) -> str:
        return "ecol" if self._elliptical else "rcol"

    def _convert_type_opal(self, etype: str) -> str:
        return "ecollimator" if self._elliptical else "rcollimator"

    def to_bmad(self) -> str:
        """
        Generate a native Bmad collimator.

        Returns
        -------
        str
            String representation of the element for Bmad
        """
        etype = "ecollimator" if self._elliptical else "rcollimator"
        horizontal, vertical = self._half_sizes()
        return self._format_bmad(
            etype,
            {"l": self.length}
            | bmad_limits(self.name, self.aperture, horizontal, vertical),
        )

    def to_madx(self, at: float = None) -> str:
        """
        Generates a string representation of the object's properties in the MAD-X
        format.

        An elliptical or circular aperture (``aperture.shape in ["elliptical",
        "circular"]``) is written as a MAD-X ``ECOLLIMATOR`` rather than the
        default ``RCOLLIMATOR``.

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
        string = sanitize_string(self.name) + ": " + etype
        for key, value in self._dump_items(
            self._convert_keyword_madx,
            elements_madx[etype],
            resolve=self._resolve_functional,
        ):
            deferred = not self._resolve_functional and self.is_functional(value)
            string += f", {key} {':=' if deferred else '='} {self._flag(value)}"
        horizontal, vertical = self._half_sizes()
        if horizontal:
            apertype = "ellipse" if etype == "ecollimator" else "rectangle"
            string += (
                f", apertype = {apertype}, aperture = {{{horizontal}, {vertical}}}"
            )
        if any(self._offsets()):
            ox, oy = self._offsets()
            string += f", aper_offset = {{{ox}, {oy}}}"
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"

    def _half_sizes(self) -> tuple:
        """Horizontal and vertical half apertures; a missing vertical copies the horizontal."""
        horizontal = self.aperture.radius or self.aperture.horizontal_size or 0.0
        vertical = self.aperture.radius or self.aperture.vertical_size or horizontal
        return horizontal, vertical

    def _write_astra_common(self, dic: dict) -> dict:
        """
        Creates the part of the ASTRA element dictionary common to all apertures in ASTRA

        Parameters
        ----------
        dic: dict
            Dictionary containing the parameters for the aperture

        Returns
        -------
        dict
            ASTRA dictionary with parameters and values
        """
        if self.aperture.negative_extent is not None:
            dic["Ap_Z1"] = {"value": self.aperture.negative_extent, "default": 0}
            dic["a_pos"] = {"value": self.physical.start.z}
        else:
            dic["Ap_Z1"] = {"value": self.physical.start.z + self.dz, "default": 0}
        if self.aperture.positive_extent is not None:
            dic["Ap_Z2"] = {"value": self.aperture.positive_extent, "default": 0}
            dic["a_pos"] = {"value": self.physical.start.z}
        else:
            end = (
                self.physical.end.z + self.dz
                if self.physical.end.z >= (self.physical.start.z + 1e-3)
                else self.physical.start.z + self.dz + 1e-3
            )
            dic["Ap_Z2"] = {"value": end, "default": 0}
        ox, oy = self._offsets()
        dic["A_xoff"] = {"value": self.dx + ox, "default": 0, "type": "not_zero"}
        dic["A_yoff"] = {"value": self.dy + oy, "default": 0, "type": "not_zero"}
        dic["A_xrot"] = {
            "value": self._astra_rotation("x"),
            "default": 0,
            "type": "not_zero",
        }
        dic["A_yrot"] = {
            "value": self._astra_rotation("y"),
            "default": 0,
            "type": "not_zero",
        }
        dic["A_zrot"] = {
            "value": self._astra_rotation("z"),
            "default": 0,
            "type": "not_zero",
        }
        return dic

    def _write_astra_circular(self) -> dict:
        """
        Creates the part of the ASTRA element dictionary relevant to circular apertures in ASTRA

        Returns
        -------
        dict
            ASTRA dictionary with parameters and values
        """
        dic = dict()
        dic["File_Aperture"] = {"value": "RAD"}
        if self.aperture.radius is not None:
            radius = self.aperture.radius
        elif self.aperture.horizontal_size > 0 and self.aperture.vertical_size > 0:
            radius = min([self.aperture.horizontal_size, self.aperture.vertical_size])
        elif self.aperture.horizontal_size > 0:
            radius = self.aperture.horizontal_size
        elif self.aperture.vertical_size > 0:
            radius = self.aperture.vertical_size
        else:
            radius = 1
        dic["Ap_R"] = {"value": 1e3 * radius}
        return self._write_astra_common(dic)

    def _write_astra_planar(self, plane, width) -> dict:
        """
        Creates the ASTRA element dictionary for one plane of a planar aperture.

        Parameters
        ----------
        plane: str
            ASTRA ``File_Aperture`` value, ``"Col_X"`` or ``"Col_Y"``
        width: float
            Aperture half-width written as ``Ap_R`` [mm]

        Returns
        -------
        dict
            ASTRA dictionary with parameters and values
        """
        dic = dict()
        dic["File_Aperture"] = {"value": plane}
        dic["Ap_R"] = {"value": width}
        return self._write_astra_common(dic)

    def to_astra(self, n: int = 0, **kwargs: dict) -> str:
        """
        Writes the aperture element string for ASTRA

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

        Raises
        ------
        ValueError
            If `shape` is not in the list of allowed values.
        """
        self.start_write()
        self.aperture.number_of_elements = 0
        if self.aperture.shape in ["elliptical", "circular"]:
            self.aperture.number_of_elements += 1
            dic = self._write_astra_circular()
            return self._write_astra_dictionary(dic, n)
        elif self.aperture.shape in ["planar", "rectangular"]:
            text = ""
            if (
                self.aperture.horizontal_size is not None
                and self.aperture.horizontal_size > 0
            ):
                dic = self._write_astra_planar(
                    "Col_X", 1e3 * self.aperture.horizontal_size
                )
                text += self._write_astra_dictionary(dic, n)
                self.aperture.number_of_elements += 1
            if (
                self.aperture.vertical_size is not None
                and self.aperture.vertical_size > 0
            ):
                dic = self._write_astra_planar(
                    "Col_Y", 1e3 * self.aperture.vertical_size
                )
                if self.aperture.number_of_elements > 0:
                    self.aperture.number_of_elements += 1
                    n = n + 1
                    text += "\n"
                text += self._write_astra_dictionary(dic, n)
            return text
        elif self.aperture.shape == "scraper":
            text = ""
            if (
                self.aperture.horizontal_size is not None
                and self.aperture.horizontal_size > 0
            ):
                dic = self._write_astra_planar(
                    "Scr_X", 1e3 * self.aperture.horizontal_size
                )
                text += self._write_astra_dictionary(dic, n)
                self.aperture.number_of_elements += 1
            if (
                self.aperture.vertical_size is not None
                and self.aperture.vertical_size > 0
            ):
                dic = self._write_astra_planar(
                    "Scr_Y", 1e3 * self.aperture.vertical_size
                )
                if self.aperture.number_of_elements > 0:
                    self.aperture.number_of_elements += 1
                    n = n + 1
                    text += "\n"
                text += self._write_astra_dictionary(dic, n)
            return text
        else:
            raise ValueError(
                "shape must be in ['elliptical', 'planar', 'circular', 'rectangular', 'scraper']"
            )

    def to_elegant(self) -> str:
        """
        Generates a string representation of the object's properties in the Elegant format.

        Returns
        -------
        str
            A formatted string representing the object's properties in Elegant format.
        """
        self.start_write()
        etype = self._convert_type_elegant(self.hardware_type)
        horizontal, vertical = self._half_sizes()
        ox, oy = self._offsets()
        # elegant's DX/DY move the collimator, which is the aperture offset too
        overrides = {
            "x_max": horizontal,
            "y_max": vertical,
            "dx": self.dx + ox,
            "dy": self.dy + oy,
        }
        terms = [
            f"{key} = {self._flag(value)}"
            for key, value in self._dump_items(
                self._convert_keyword_elegant,
                elements_elegant[etype],
                overrides=overrides,
            )
        ]
        return elegant_line(self.name + ": " + etype, terms)

    def _opal_alignment(self) -> Dict[str, float]:
        """The OPAL alignment with the aperture offset added, plus the sizes."""
        alignment = super()._opal_alignment()
        horizontal, vertical = self._half_sizes()
        ox, oy = self._offsets()
        return alignment | {
            "dx": alignment["dx"] + ox,
            "dy": alignment["dy"] + oy,
            "xsize": horizontal,
            "ysize": vertical,
        }

    def to_ocelot(self) -> object:
        """An OCELOT ``Aperture``, or a drift between two for a thick element."""
        from ocelot.cpbd.elements import Aperture, Drift

        self.start_write()
        horizontal, vertical = self._half_sizes()
        ox, oy = self._offsets()

        def aperture(eid):
            # OCELOT's dx/dy place the aperture centre: offset plus misalignment
            return Aperture(
                xmax=horizontal or math.inf,
                ymax=vertical or math.inf,
                dx=self.dx + ox,
                dy=self.dy + oy,
                type="ellipt" if self._elliptical else "rect",
                eid=eid,
            )

        if not self.length:
            return aperture(self.name)
        return [
            aperture(f"{self.name}_entry"),
            Drift(l=self.length, eid=self.name),
            aperture(f"{self.name}_exit"),
        ]

    def to_cheetah(self) -> object:
        """A Cheetah ``Aperture``, or a drift between two for a thick element."""
        from cheetah.accelerator import Aperture, Drift, Segment
        from torch import float64, tensor

        self.start_write()
        self._warn_dropped_offset("Cheetah")
        horizontal, vertical = self._half_sizes()

        def aperture(name):
            return Aperture(
                x_max=tensor(horizontal or math.inf, dtype=float64),
                y_max=tensor(vertical or math.inf, dtype=float64),
                shape="elliptical" if self._elliptical else "rectangular",
                name=name,
                sanitize_name=True,
                dtype=float64,
            )

        if not self.length:
            return aperture(self.name)
        drift = Drift(
            length=tensor(self.length, dtype=float64),
            name=f"{self.name}_drift",
            sanitize_name=True,
            dtype=float64,
        )
        return Segment(
            elements=[
                aperture(f"{self.name}_entry"),
                drift,
                aperture(f"{self.name}_exit"),
            ],
            name=self.name,
            sanitize_name=True,
        )

    def to_xsuite(self, beam_length: int) -> tuple | list:
        """An Xtrack limit, or a drift between two for a thick element."""
        import xtrack as xt

        self.start_write()
        horizontal, vertical = self._half_sizes()
        ox, oy = self._offsets()
        # an unset plane is open; 1e10 is xtrack's own "unlimited"
        horizontal, vertical = horizontal or 1e10, vertical or 1e10
        if self._elliptical:
            component = xt.LimitEllipse
            properties = {"a": horizontal, "b": vertical, "shift_x": ox, "shift_y": oy}
        else:
            component = xt.LimitRect
            properties = {
                "min_x": ox - horizontal,
                "max_x": ox + horizontal,
                "min_y": oy - vertical,
                "max_y": oy + vertical,
            }
        if not self.length:
            return self.name, component, properties
        return [
            (f"{self.name}_entry", component, dict(properties)),
            (self.name, xt.Drift, {"length": self.length}),
            (f"{self.name}_exit", component, dict(properties)),
        ]
