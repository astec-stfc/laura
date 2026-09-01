from laura.models.simulation import ApertureElement

from ..converters import elements_Elegant, elements_Madx
from ..utils.functions import sanitize_string
from .base import BaseElementTranslator


class ApertureTranslator(BaseElementTranslator):
    aperture: ApertureElement

    def to_bmad(self) -> str:
        """
        Generate a native Bmad collimator with symmetric aperture limits.

        Returns
        -------
        str
            String representation of the element for Bmad
        """
        shape = getattr(self.aperture.shape, "value", self.aperture.shape)
        etype = "ecollimator" if shape in ("elliptical", "circular") else "rcollimator"
        horizontal = self.aperture.radius or (self.aperture.horizontal_size or 0.0) / 2
        vertical = (
            self.aperture.radius
            or (self.aperture.vertical_size or 0.0) / 2
            or horizontal
        )
        return self._format_bmad(
            etype,
            {
                "l": self.length,
                "x1_limit": horizontal,
                "x2_limit": horizontal,
                "y1_limit": vertical,
                "y2_limit": vertical,
            },
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
        etype = self._convertType_Madx(self.hardware_type)
        if self.aperture.shape in ["elliptical", "circular"] and etype == "rcollimator":
            etype = "ecollimator"
        string = sanitize_string(self.name) + ": " + etype
        keys = []
        for key, value in self.full_dump(resolve=self._resolve_functional).items():
            if (
                not key == "name"
                and not key == "type"
                and not key == "commandtype"
                and self._convertKeyword_Madx(key) in elements_Madx[etype]
            ):
                if value is not None:
                    key = self._convertKeyword_Madx(key)
                    deferred = not self._resolve_functional and self.is_functional(
                        value
                    )
                    value = 1 if value is True else value
                    value = 0 if value is False else value
                    if key not in keys:
                        op = ":=" if deferred else "="
                        string += f", {key} {op} {value}"
                    keys.append(key)
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"

    def _write_ASTRA_Common(self, dic: dict) -> dict:
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

    def _write_ASTRA_Circular(self) -> dict:
        """
        Creates the part of the ASTRA element dictionary relevant to circular apertures in ASTRA

        Parameters
        ----------
        dic: dict
            Dictionary containing the parameters for the aperture

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
        return self._write_ASTRA_Common(dic)

    def _write_ASTRA_Planar(self, plane, width) -> dict:
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
        dic = dict()
        dic["File_Aperture"] = {"value": plane}
        dic["Ap_R"] = {"value": width}
        return self._write_ASTRA_Common(dic)

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

        Raises:
        -------
        ValueError
            If `shape` is not in the list of allowed values.
        """
        self.start_write()
        self.aperture.number_of_elements = 0
        if self.aperture.shape in ["elliptical", "circular"]:
            self.aperture.number_of_elements += 1
            dic = self._write_ASTRA_Circular()
            return self._write_ASTRA_dictionary(dic, n)
        elif self.aperture.shape in ["planar", "rectangular"]:
            text = ""
            if (
                self.aperture.horizontal_size is not None
                and self.aperture.horizontal_size > 0
            ):
                dic = self._write_ASTRA_Planar(
                    "Col_X", 1e3 * self.aperture.horizontal_size
                )
                text += self._write_ASTRA_dictionary(dic, n)
                self.aperture.number_of_elements += 1
            if (
                self.aperture.vertical_size is not None
                and self.aperture.vertical_size > 0
            ):
                dic = self._write_ASTRA_Planar(
                    "Col_Y", 1e3 * self.aperture.vertical_size
                )
                if self.aperture.number_of_elements > 0:
                    self.aperture.number_of_elements += 1
                    n = n + 1
                    text += "\n"
                text += self._write_ASTRA_dictionary(dic, n)
            return text
        elif self.aperture.shape == "scraper":
            text = ""
            if (
                self.aperture.horizontal_size is not None
                and self.aperture.horizontal_size > 0
            ):
                dic = self._write_ASTRA_Planar(
                    "Scr_X", 1e3 * self.aperture.horizontal_size
                )
                text += self._write_ASTRA_dictionary(dic, n)
                self.aperture.number_of_elements += 1
            if (
                self.aperture.vertical_size is not None
                and self.aperture.vertical_size > 0
            ):
                dic = self._write_ASTRA_Planar(
                    "Scr_Y", 1e3 * self.aperture.vertical_size
                )
                if self.aperture.number_of_elements > 0:
                    self.aperture.number_of_elements += 1
                    n = n + 1
                    text += "\n"
                text += self._write_ASTRA_dictionary(dic, n)
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
        wholestring = ""
        etype = self._convertType_Elegant(self.hardware_type)
        string = self.name + ": " + etype
        keys = []
        for key, value in self.full_dump().items():
            if (
                not key == "name"
                and not key == "type"
                and not key == "commandtype"
                and self._convertKeyword_Elegant(key) in elements_Elegant[etype]
            ):
                if value is not None:
                    key = self._convertKeyword_Elegant(key)
                    # if key == "dx":
                    #     value = self.physical.middle.x
                    # elif key == "dy":
                    #     value = self.physical.middle.y
                    value = 1 if value is True else value
                    value = 0 if value is False else value
                    if key not in keys:
                        tmpstring = ", " + key + " = " + str(value)
                        if len(string + tmpstring) > 76:
                            wholestring += string + ",&\n"
                            string = ""
                            string += tmpstring[2::]
                        else:
                            string += tmpstring
                    keys.append(key)
        wholestring += string + ";\n"
        return wholestring
