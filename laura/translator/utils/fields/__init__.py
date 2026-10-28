"""
Electromagnetic field maps (RF structures, wakefields and magnets), with readers
for existing files and writers for code-specific formats.

Classes:
    - :class:`~laura.translator.utils.fields.FieldMap`: Generic field definition.
    - :class:`~laura.translator.utils.fields.field_parameter.FieldParameter`: Field parameter with a
      name and a :class:`~laura.translator.utils.units.UnitValue` associated with it.
"""

import os
import warnings
import numpy as np
from .field_parameter import FieldParameter, FIELD_NAMES
from laura.models.constants import speed_of_light
from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
)
from typing import Literal, List
from . import astra  # noqa E402
from . import bmad  # noqa E402
from . import gdf  # noqa E402
from . import hdf5  # noqa E402
from . import sdds  # noqa E402
from . import opal  # noqa E402
from . import rftrack  # noqa E402

allowed_fields = [
    "1DElectroStatic",
    "1DMagnetoStatic",
    "1DElectroDynamic",
    "2DElectroStatic",
    "2DMagnetoStatic",
    "2DElectroDynamic",
    "3DElectroStatic",
    "3DMagnetoStatic",
    "3DElectroDynamic",
    "LongitudinalWake",
    "TransverseWake",
    "3DWake",
    "1DQuadrupole",
]

fieldtype = Literal[tuple(allowed_fields)]

cavitytype = Literal[
    "StandingWave",
    "TravellingWave",
]


class FieldMap(BaseModel):
    """
    Electromagnetic field map (RF structure, wakefield or magnet), read from and
    written to ASTRA, SDDS, GDF, OPAL, HDF5 and Bmad formats.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    x: FieldParameter = None
    """X position or coordinate of the field."""

    y: FieldParameter = None
    """Y position or coordinate of the field."""

    z: FieldParameter = None
    """Z position or coordinate of the field."""

    r: FieldParameter = None
    """Radial position or coordinate of the field."""

    t: FieldParameter = None
    """Time parameter of the field."""

    Ex: FieldParameter = None
    """Electric field component in the X direction."""

    Ey: FieldParameter = None
    """Electric field component in the Y direction."""

    Ez: FieldParameter = None
    """Electric field component in the Z direction."""

    Er: FieldParameter = None
    """Radial electric field component."""

    Bx: FieldParameter = None
    """Magnetic field component in the X direction."""

    By: FieldParameter = None
    """Magnetic field component in the Y direction."""

    Bz: FieldParameter = None
    """Magnetic field component in the Z direction."""

    Br: FieldParameter = None
    """Radial magnetic field component."""

    Wx: FieldParameter = None
    """Wakefield component in the X direction."""

    Wy: FieldParameter = None
    """Wakefield component in the Y direction."""

    Wz: FieldParameter = None
    """Wakefield component in the Z direction."""

    Wr: FieldParameter = None
    """Radial wakefield component."""

    G: FieldParameter = None
    """Magnetic gradient."""

    filename: str | None = None
    """Filename of the field file."""

    field_type: fieldtype | None = None
    """Type of the field, e.g., '1DElectroStatic', '1DMagnetoStatic', etc."""

    origin_code: str | None = None
    """Code that generated the field, e.g., 'ASTRA', 'SDDS', etc."""

    norm: float = 1.0
    """Normalization factor for the field."""

    read: bool = False
    """Flag indicating whether the field file has been read."""

    length: int | float | np.float64 | None = None
    """Length of the field, if applicable. Note that the HDF5 reader only keeps
    a physical length here for a 2DElectroDynamic map; for every other field it
    overwrites this with the number of samples."""

    reference_length: float | None = None
    """Length of machine the field describes [m], where the file says so."""

    frequency: float | np.int64 | np.float64 | None = None
    """Frequency of the field, if applicable."""

    radius: float | None = (
        None  # MAGIC NUMBER FOR SOLENOID RADIUS, DEFAULTS TO 10cm in write_opal_field_file
    )
    """Radius of the field, if applicable, defaults TO 10cm in write_opal_field_file."""

    fourier: int | np.int64 = 100
    """Number of Fourier modes for the field, default is 100."""

    cavity_type: cavitytype | None = None
    """Type of the cavity, e.g., 'StandingWave', 'TravellingWave'."""

    start_cell_z: float | None = None
    """Starting position of the cell in the Z direction, required for TravellingWave cavities."""

    end_cell_z: float | None = None
    """Ending position of the cell in the Z direction, required for TravellingWave cavities."""

    mode_numerator: float | None = None
    """Numerator for the mode of the TravellingWave cavity. 
    For TW linacs in ASTRA, the mode is 2π mode_numerator / mode_denominator"""

    mode_denominator: float | None = None
    """Denominator for the mode of the TravellingWave cavity. 
    For TW linacs in ASTRA, the mode is 2π mode_numerator / mode_denominator"""

    orientation: str | None = None
    """Orientation of the field, e.g., 'horizontal', 'vertical', etc."""

    n_cells: int | float | None = None
    """Number of cells in the field, if applicable."""

    # For TW linacs in ASTRA, the mode is 2π mode_numerator / mode_denominator

    def __init__(
        self,
        filename=None,
        field_type=None,
        frequency=None,
        cavity_type=None,
        *args,
        **kwargs,
    ):
        super(
            FieldMap,
            self,
        ).__init__(
            filename=filename,
            field_type=field_type,
            frequency=frequency,
            cavity_type=cavity_type,
            *args,
            **kwargs,
        )
        if filename is not None:
            reader_options = {
                name: value
                for name, value in kwargs.items()
                if name in ("column_map", "normalize_b") or name.lower().endswith("_column")
            }
            self.read_field_file(
                filename,
                field_type=field_type,
                frequency=frequency,
                cavity_type=cavity_type,
                **reader_options,
            )

    @model_validator(mode="before")
    def validate_fields(cls, values):
        return values

    def reset_dicts(self) -> None:
        """
        Reset the field parameters to their default values.
        """
        self.origin_code = None
        self.field_type = None
        self.norm = 1.0
        for par in FIELD_NAMES:
            setattr(self, par, FieldParameter(name=par))
        self.read = False

    @property
    def z_values(self) -> List[float] | None:
        """
        Returns the Z values of the field.
        If the time parameter is set and Z is not, it calculates Z based on the time and speed of light.

        Returns
        -------
        List[float] | None:
            A list of Z values if available, otherwise None.
        """
        if isinstance(self.z, FieldParameter) and self.z.value is not None:
            return self.z.value.val
        elif isinstance(self.t, FieldParameter) and self.t.value is not None:
            return -1 * abs(self.t.value.val * speed_of_light)
        else:
            raise ValueError("Neither t nor z are defined")

    @property
    def t_values(self) -> List[float] | None:
        """
        Returns the time values of the field.
        If the Z parameter is set and time is not, it calculates time based on Z and speed of light.

        Returns
        -------
        List[float] | None:
            A list of time values if available, otherwise None.
        """
        if isinstance(self.t, FieldParameter) and self.t.value is not None:
            return self.t.value.val
        elif isinstance(self.z, FieldParameter) and self.z.value is not None:
            return abs(self.z.value.val / speed_of_light)
        else:
            raise ValueError("Neither t nor z are defined")

    def read_field_file(
        self,
        filename: str,
        field_type: str | None = None,
        cavity_type: str | None = None,
        frequency: float | None = None,
        normalize_b: bool = True,
        **kwargs,
    ) -> None:
        """
        Read a field file, dispatching on its extension (HDF5, ASTRA, SDDS,
        GDF or OPAL).

        Parameters
        ----------
        filename: str
            The path to the field file to be read.
        field_type: fieldtype | None
            The type of the field, e.g., '1DElectroStatic', '1DMagnetoStatic', etc.
        cavity_type: cavitytype | None
            The type of the cavity, e.g., 'StandingWave', 'TravellingWave'.
        frequency: float | None
            The frequency of the field, if applicable.
        normalize_b: bool
            Normalize Bx and By with respect to Bz (True by default)
        **kwargs
            Format-specific reader options. For SDDS files, columns matching
            LAURA field names are loaded automatically. Use
            ``column_map={"Wz": "W"}`` or per-field overrides such as
            ``wz_column="W"`` and ``t_column="T"`` for non-standard names.
            SDDS supports coordinates, electric and magnetic components,
            wake components, and gradient; see
            :func:`~laura.translator.utils.fields.sdds.read_sdds_field_file`.

        Returns
        -------
        None:
            The method modifies the field object in place, populating its parameters based on the file content.
        """
        fext = os.path.splitext(os.path.basename(filename))[-1]
        if fext == ".hdf5":
            hdf5.read_hdf5_field_file(self, filename)
        else:
            if fext.lower() in [".astra", ".dat"]:
                astra.read_astra_field_file(
                    self,
                    filename,
                    field_type=field_type,
                    cavity_type=cavity_type,
                    frequency=frequency,
                )
            elif fext.lower() in [".sdds"]:
                sdds.read_sdds_field_file(self, filename, field_type=field_type, **kwargs)
            elif fext.lower() in [".gdf"]:
                gdf.read_gdf_field_file(
                    self,
                    filename,
                    field_type=field_type,
                    cavity_type=cavity_type,
                    frequency=frequency,
                    normalize_b=normalize_b,
                )
            elif fext.lower() in [".opal"]:
                opal.read_opal_field_file(
                    self,
                    filename,
                    field_type=field_type,
                    cavity_type=cavity_type,
                    frequency=frequency,
                )
            self.read = True

    def _output_filename(
        self, extension: str = ".hdf5", location: str | None = None
    ) -> str:
        """
        Return the output path ``<field-file stem><extension>`` in the
        directory of `location`, or else the default output directory.

        Parameters
        ----------
        extension: str:
            The file extension to be used for the output file. Default is ".hdf5".
        location: str | None:
            Optional; if provided, it specifies the directory where the output file will be saved.

        Returns
        -------
        str:
            The relative path to the output file, constructed from the
            specified location or the current field file's directory.
        """
        if location is not None:
            _output_location = os.path.dirname(os.path.abspath(location))
        else:
            if not hasattr(self, "_output_location"):
                _output_location = os.path.dirname(os.path.dirname(self.filename))
            else:
                _output_location = self._output_location
        basefilename = os.path.basename(self.filename)
        pre, _ = os.path.splitext(basefilename)
        path = os.path.join(_output_location, pre + extension)
        try:
            return os.path.relpath(path)
        except ValueError:  # Windows: path and cwd on different drives
            return os.path.abspath(path)

    def get_field_data(self, code: str) -> np.ndarray | None:
        """
        Generate field data for `code` ('astra' or 'ocelot'); warn and
        return None if the field file has not been read.

        Parameters
        ----------
        code: str:
            The code for which the field data is to be generated.
            Supported codes are 'astra' and 'ocelot'.

        Returns
        -------
        np.ndarray | None:
            The generated field data in the format required by the specified code,
            or None if the field file has not been read.
        """
        if not self.read:
            warnings.warn(
                "Field file not read in. Use read_field_file to load in an hdf5 field file."
            )
            return
        if code.lower() in ["astra", "ocelot"]:
            return astra.generate_astra_field_data(self)
        return None

    def write_field_file(
        self, code: str, location: str | None = None, **kwargs
    ) -> str | None:
        """
        Write the field data in the format of `code`; warn and return None if
        the field file has not been read.

        Parameters
        ----------
        code: str:
            The code for which the field data is to be written.
            Supported codes are 'astra'/'ocelot', 'sdds'/'elegant',
            'gdf'/'gpt', 'opal', 'hdf5' and 'bmad'.
        location: str | None:
            Optional; if provided, it specifies the directory where the output file will be saved.
        **kwargs
            Passed to :func:`~laura.translator.utils.fields.bmad.write_bmad_field_file`.

        Returns
        -------
        str | None:
            The path to the written field file, or None if the field file has not been read.
        """
        if not self.read:
            warnings.warn(
                "Field file not read in. Use read_field_file to load in an hdf5 field file."
            )
            return
        if location is not None:
            self._output_location = os.path.dirname(os.path.abspath(location))
        else:
            self._output_location = os.path.dirname(os.path.dirname(self.filename))
        if code.lower() in ["astra", "ocelot"]:
            return astra.write_astra_field_file(self)
        elif code.lower() in ["sdds", "elegant"]:
            return sdds.write_sdds_field_file(self)
        elif code.lower() in ["gdf", "gpt"]:
            return gdf.write_gdf_field_file(self)
        elif code.lower() == "opal":
            return opal.write_opal_field_file(
                self,
                frequency=self.frequency,
                radius=self.radius,
                fourier=self.fourier,
                orientation=self.orientation,
            )
        elif code.lower() == "hdf5":
            return hdf5.write_hdf5_field_file(self)
        elif code.lower() == "bmad":
            return bmad.write_bmad_field_file(self, **kwargs)


from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "field": "FieldMap",
    },
)
