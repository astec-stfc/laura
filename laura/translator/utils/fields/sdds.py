import numpy as np

from .field_parameter import FIELD_NAMES, set_field
from warnings import warn
from ..sdds_file import SDDSFile, SddsTypes

SDDS_FIELD_NAMES = FIELD_NAMES

# field_type: (column names, column units)
_SDDS_COLUMNS = {
    "LongitudinalWake": (["z", "t", "Wz"], ["m", "s", "V/C"]),
    "TransverseWake": (["z", "t", "Wx", "Wy"], ["m", "s", "V/C/m", "V/C/m"]),
    "3DWake": (["z", "t", "Wx", "Wy", "Wz"], ["m", "s", "V/C/m", "V/C/m", "V/C"]),
    "1DElectroDynamic": (["z", "Ez"], ["m", "V"]),
}


def write_sdds_field_file(self, sddsindex: int = 0, ascii: bool = False) -> str:
    """
    Write the field data of a :class:`~laura.translator.utils.fields.FieldMap`
    to an SDDS file, in a format set by `field_type`. Unsupported field types
    raise a warning.

    Parameters
    ----------
    self: :class:`~laura.translator.utils.fields.FieldMap`
        The field object
    sddsindex: int
        Must be provided for the :class:`~laura.translator.utils.sdds_file.SDDSFile` class
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
    if self.field_type not in _SDDS_COLUMNS:
        warn(f"Field type {self.field_type} not supported for SDDS")
        return
    cnames, cunits = _SDDS_COLUMNS[self.field_type]
    data = {"z": zdata, "t": tdata}
    ccolumns = [data[n] if n in data else getattr(self, n).value.val for n in cnames]
    # Stacked as before, so ragged wake columns still raise
    if self.field_type in ("TransverseWake", "3DWake"):
        ccolumns = np.array(ccolumns)
    if ccolumns is not None:
        ctypes = [SddsTypes.SDDS_DOUBLE for _ in ccolumns]
        csymbols = ["" for _ in ccolumns]
        sddsfile.add_columns(cnames, ccolumns, ctypes, cunits, csymbols)
        sddsfile.write_file(sdds_filename)
    return sdds_filename


def read_sdds_field_file(
    self,
    filename: str,
    field_type: str,
    column_map: dict[str, str] | None = None,
    **column_names: str | None,
) -> None:
    """
    Read SDDS columns into a :class:`~laura.translator.utils.fields.FieldMap`.

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
    self: :class:`~laura.translator.utils.fields.FieldMap`
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

    Raises
    ------
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
        elegant_object = SDDSFile(index=1, ascii=True)
    except Exception:
        elegant_object = SDDSFile(index=1, ascii=False)
    elegant_object.read_file(filename, page=-1)
    unit_fallbacks = {"m": "z", "s": "t", "V/C": "Wz"}
    for key, value in elegant_object._columns.items():
        target = columns.get(key.lower()) or fields.get(key.lower())
        target = target or unit_fallbacks.get(value.unit)
        if target is None:
            warn(
                f"Could not map SDDS column {key!r} ({value.unit}) in {filename}; "
                "use column_map or a <field>_column keyword"
            )
            continue
        set_field(self, target, np.array(value.data), value.unit)


# ---------------------------------------------------------------------------
# Backwards compatibility: names renamed for PEP 8. Served lazily with a
# DeprecationWarning so downstream consumers (astec-stfc/simba) keep working.
# ---------------------------------------------------------------------------
from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "read_SDDS_field_file": "read_sdds_field_file",
        "write_SDDS_field_file": "write_sdds_field_file",
    },
)
