import numpy as np

from ..units import UnitValue

from .FieldParameter import FieldParameter
from warnings import warn
from ..SDDSFile import SDDSFile, SDDS_Types

SDDS_FIELD_NAMES = (
    "x",
    "y",
    "z",
    "r",
    "t",
    "Ex",
    "Ey",
    "Ez",
    "Er",
    "Bx",
    "By",
    "Bz",
    "Br",
    "Wx",
    "Wy",
    "Wz",
    "Wr",
    "G",
)


def write_SDDS_field_file(self, sddsindex: int = 0, ascii: bool = False) -> str:
    """
    Generate the field data in a format that is suitable for SDDS, based on the
    :class:`~laura.translatoru.utils.fields.field` object provided.
    This is then written to an SDDS file.
    The `field_type` parameter determines the format of the file.

    A warning is raised if the field type is not supported (perhaps elevate to a `NotImplementedError`?)

    Parameters
    ----------
    self: :class:`~laura.translator.utils.fields.field`
        The field object
    sddsindex: int
        Must be provided for :class:`~laura.translator.utils.SDDSFile.SddsFile` class
    ascii: bool, optional
        Convert to ascii?

    Returns
    -------
    str:
        The name of the SDDS field file.
    """
    sdds_filename = self._output_filename(extension=".sdds")
    sddsfile = SDDSFile(index=sddsindex, ascii=ascii)
    zdata = self.z_values
    tdata = self.t_values
    if self.field_type == "LongitudinalWake":
        wzdata = self.Wz.value.val
        cnames = ["z", "t", "Wz"]
        cunits = ["m", "s", "V/C"]
        ccolumns = [
            zdata,
            tdata,
            wzdata,
        ]
    elif self.field_type == "TransverseWake":
        wxdata = self.Wx.value.val
        wydata = self.Wy.value.val
        ccolumns = np.array(
            [
                zdata,
                tdata,
                wxdata,
                wydata,
            ]
        )
        cnames = ["z", "t", "Wx", "Wy"]
        cunits = ["m", "s", "V/C/m", "V/C/m"]
    elif self.field_type == "3DWake":
        wxdata = self.Wx.value.val
        wydata = self.Wy.value.val
        wzdata = self.Wz.value.val
        ccolumns = np.array(
            [
                zdata,
                tdata,
                wxdata,
                wydata,
                wzdata,
            ]
        )
        cnames = ["z", "t", "Wx", "Wy", "Wz"]
        cunits = ["m", "s", "V/C/m", "V/C/m", "V/C"]
    elif self.field_type == "1DElectroDynamic":
        ezdata = self.Ez.value.val
        cnames = ["z", "Ez"]
        cunits = ["m", "V"]
        ccolumns = [
            zdata,
            ezdata,
        ]
    else:
        warn(f"Field type {self.field_type} not supported for SDDS")
        return
    if ccolumns is not None:
        ctypes = [SDDS_Types.SDDS_DOUBLE for _ in ccolumns]
        csymbols = ["" for _ in ccolumns]
        sddsfile.add_columns(cnames, ccolumns, ctypes, cunits, csymbols)
        sddsfile.write_file(sdds_filename)
    return sdds_filename


def read_SDDS_field_file(
    self,
    filename: str,
    field_type: str,
    column_map: dict[str, str] | None = None,
    **column_names: str | None,
) -> None:
    """
    Read SDDS columns into a :class:`laura.translator.utils.fields.field`.

    Columns named like a LAURA field attribute are mapped automatically,
    case-insensitively. Supported attributes are ``x``, ``y``, ``z``, ``r``,
    ``t``, ``Ex/Ey/Ez/Er``, ``Bx/By/Bz/Br``, ``Wx/Wy/Wz/Wr``, and ``G``.
    Non-standard SDDS names may be supplied either through ``column_map`` or
    ``<field>_column`` keyword arguments. For example, both
    ``column_map={"Wz": "W", "t": "T"}`` and
    ``wz_column="W", t_column="T"`` map the wake columns correctly.

    Unnamed legacy columns retain the established unit fallbacks: metres map
    to ``z``, seconds to ``t``, and volts/coulomb to ``Wz``. Ambiguous or
    unrecognised columns are ignored with a warning.

    Parameters
    ----------
    self: :class:`~laura.translator.utils.fields.field`
        The field object to be updated.
    filename: str
        The path to the SDDS field file
    field_type: str
        The name of the field, see :attr:`~laura.translator.utils.fields.allowed_fields`
    column_map: dict[str, str], optional
        Mapping from LAURA field attribute to SDDS column name.
    **column_names: str
        Per-field overrides named ``<field>_column``, such as
        ``ex_column="electricFieldX"`` or ``wz_column="W"``.

    Returns
    -------
    None

    ValueError
        If a column mapping names an unsupported LAURA field attribute.
    """
    fields = {name.lower(): name for name in SDDS_FIELD_NAMES}
    mapping = dict(column_map or {})
    for keyword, column in column_names.items():
        if not keyword.lower().endswith("_column"):
            raise ValueError(f"Unknown SDDS field option {keyword!r}")
        if column is not None:
            mapping[keyword[:-7]] = column
    invalid = sorted(name for name in mapping if name.lower() not in fields)
    if invalid:
        raise ValueError(f"Unsupported LAURA SDDS field(s): {', '.join(invalid)}")
    columns = {column.lower(): fields[name.lower()] for name, column in mapping.items()}

    self.reset_dicts()
    setattr(self, "field_type", field_type)
    try:
        elegantObject = SDDSFile(index=1, ascii=True)
    except Exception:
        elegantObject = SDDSFile(index=1, ascii=False)
    elegantObject.read_file(filename, page=-1)
    unit_fallbacks = {"m": "z", "s": "t", "V/C": "Wz"}
    for key, value in elegantObject._columns.items():
        target = columns.get(key.lower()) or fields.get(key.lower())
        target = target or unit_fallbacks.get(value.unit)
        if target is None:
            warn(
                f"Could not map SDDS column {key!r} ({value.unit}) in {filename}; "
                "use column_map or a <field>_column keyword"
            )
            continue
        setattr(
            self,
            target,
            FieldParameter(
                name=target,
                value=UnitValue(np.array(value.data), units=value.unit),
            ),
        )
