from typing import List
import numpy as np
import easygdf
from warnings import warn
from .field_parameter import require_rf, set_field
from laura.models.constants import speed_of_light

# field_type: (block names, drop repeated z samples via union)
_GDF_BLOCKS = {
    "LongitudinalWake": (("z", "Wz"), True),
    "TransverseWake": (("z", "Wx", "Wy"), False),
    "3DWake": (("z", "Wx", "Wy", "Wz"), False),
    "1DMagnetoStatic": (("z", "Bz"), True),
    "3DMagnetoStatic": (("x", "y", "z", "Bx", "By", "Bz"), False),
}
_GDF_WAKES = {
    "LongitudinalWake": ("Wz",),
    "TransverseWake": ("Wx", "Wy"),
    "3DWake": ("Wx", "Wy", "Wz"),
}


def write_gdf_field_file(self) -> str:
    """
    Write the field data of a :class:`~laura.translator.utils.fields.FieldMap`
    to a GPT GDF file, in a format set by `field_type`. Unsupported field
    types raise a warning.

    Parameters
    ----------
    self: :class:`~laura.translator.utils.fields.FieldMap`
        The field object

    Returns
    -------
    str:
        The name of the GDF field file.
    """
    gdf_file = self._output_filename(extension=".gdf")
    blocks = None
    zdata = self.z.value.val
    if self.field_type in _GDF_BLOCKS:
        names, unique_z = _GDF_BLOCKS[self.field_type]
        blocks = [{"name": n, "value": getattr(self, n).value.val} for n in names]
        if unique_z:
            blocks = union(blocks)
    elif self.field_type == "1DElectroDynamic":
        ezdata = self.Ez.value.val
        fielddata = np.array([zdata, ezdata]).transpose()
        if self.cavity_type == "TravellingWave":
            startpos = list(zdata).index(self.start_cell_z)
            halfcell1 = 1.0 * fielddata[:startpos]
            halfcell2 = 1.0 * halfcell1[::-1]
            halfcell1[:, 1] /= max(halfcell1[:, 1])
            halfcell2[:, 0] = halfcell2[:, 0][::-1]
            halfcell2[:, 1] /= max(halfcell2[:, 1])
            halfcell1end = halfcell1[-1, 0]
            zstep = zdata[1] - zdata[0]
            lambda_rf = speed_of_light / self.frequency
            ncells = (self.n_cells - 1) * self.mode_numerator / self.mode_denominator
            nsteps = int(np.floor((ncells) * lambda_rf / zstep))
            middle_rf = np.array(
                [
                    [
                        (x * zstep + halfcell1end + zstep),
                        np.cos((2 * np.pi / lambda_rf) * (x * zstep)),
                    ]
                    for x in range(0, nsteps + 1)
                ]
            )
            halfcell2[:, 0] += middle_rf[-1, 0] + zstep
            zdata, ezdata = np.concatenate([halfcell1, middle_rf, halfcell2]).transpose()
        blocks = union(
            [
                {"name": "z", "value": zdata},
                {"name": "Ez", "value": ezdata},
            ]
        )
    else:
        warn(f"Field type {self.field_type} not supported for GPT")
    if blocks is not None:
        easygdf.save(gdf_file, blocks)
    return gdf_file


def union(blocks: List) -> List:
    """
    Update the field data into a format compatible for easyGDF

    Parameters
    ----------
    blocks: List[Dict]
        The field parameters, keyed by name

    Returns
    -------
    List:
        A list of easyGDF-compatible dictionaries
    """
    names = [b["name"] for b in blocks]
    if "z" in names:
        zidx = names.index("z")
        _, indices = np.unique(
            np.round(blocks[zidx]["value"], decimals=6), return_index=True
        )
        blocks = [{"name": b["name"], "value": b["value"][indices]} for b in blocks]
        return blocks
    return blocks


def _block(fdat: List, name: str):
    """Return the value of the first GDF block called `name` (case-insensitive)."""
    return [k["value"] for k in fdat if k["name"].lower() == name.lower()][0]


def read_gdf_field_file(
    self,
    filename: str,
    field_type: str,
    cavity_type: str | None = None,
    frequency: float | None = None,
    normalize_b: bool = True,
):
    """
    Read a GDF field file into a :class:`~laura.translator.utils.fields.FieldMap` object.

    Parameters
    ----------
    self: :class:`~laura.translator.utils.fields.FieldMap`
        The field object to be updated.
    filename: str
        The path to the GDF field file
    field_type: str
        The name of the field, see :attr:`~laura.translator.utils.fields.allowed_fields`
    cavity_type: str, optional
        The type of RF cavity, see :attr:`~laura.translator.utils.fields.hdf5.allowed_cavities`
    frequency: float, optional
        The frequency of the RF cavity.
    normalize_b: bool, optional
        Normalize Bx and By with respect to Bz (True by default)

    Returns
    -------
    None

    Raises
    ------
    ValueError:
        if the cavity `field_type` contains the string `Electro` and `cavity_type` is not provided
    ValueError:
        if the cavity `field_type` contains the string `Electro` and `frequency` is not provided
    NotImplementedError:
        if a given `field_type` is not implemented
    """
    self.reset_dicts()
    setattr(self, "field_type", field_type)
    require_rf(self, field_type, cavity_type, frequency)
    fdat = easygdf.load(filename)["blocks"]
    try:
        zval = _block(fdat, "z")
    except Exception:
        zval = _block(fdat, "t") * speed_of_light
    if field_type == "1DMagnetoStatic":
        bzval = _block(fdat, "Bz")
        set_field(self, "z", zval, "m")
        set_field(self, "Bz", bzval / np.max(bzval), "T")
    elif field_type == "3DMagnetoStatic":
        xval, yval, bxval, byval, bzval = (
            _block(fdat, n) for n in ("x", "y", "Bx", "By", "Bz")
        )
        # Normalise by the maximum *on-axis* Bz field
        if normalize_b:
            norm_bz = max(
                [
                    abs(Bz)
                    for x, y, Bz in zip(xval, yval, bzval)
                    if x == 0.0 and y == 0.0
                ]
            )
        else:
            norm_bz = 1
        set_field(self, "x", xval, "m")
        set_field(self, "y", yval, "m")
        set_field(self, "z", zval, "m")
        set_field(self, "Bx", bxval / norm_bz, "T")
        set_field(self, "By", byval / norm_bz, "T")
        set_field(self, "Bz", bzval / norm_bz, "T")
    elif field_type == "1DElectroDynamic":
        if cavity_type == "StandingWave":
            ezval = _block(fdat, "Ez")
            set_field(self, "z", zval, "m")
            set_field(self, "Ez", ezval / np.max(ezval), "V/m")
        elif cavity_type == "TravellingWave":
            raise NotImplementedError(f"{cavity_type} not implemented for GDF files")
    elif field_type in _GDF_WAKES:
        names = _GDF_WAKES[field_type]
        values = [_block(fdat, n) for n in names]
        set_field(self, "z", zval, "m")
        for name, value in zip(names, values):
            set_field(self, name, value, "V/C" if name == "Wz" else "V/C/m")
    else:
        raise NotImplementedError(f"{field_type} loading not implemented for GDF files")
