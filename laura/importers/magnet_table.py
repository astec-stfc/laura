import logging
import os
from math import ceil

_log = logging.getLogger("laura.loader.magnet_table")

try:
    import pandas
except ImportError as _err:
    raise ImportError(
        "pandas is not installed. Install with: pip install pandas"
    ) from _err

magnet_table_filename = os.path.join(
    os.path.dirname(__file__), "CLARA Magnet Table v6.xlsx"
)
magnet_table = pandas.read_excel(
    magnet_table_filename,
    sheet_name="Table",
    skiprows=2,
    index_col=(2, 3, 5, 6),
    dtype={"serial number": "str"},
).fillna(0)


def create_degauss_values(maxI): # noqa N806
    if maxI < 10.0:
        maxI = 10.0 # noqa N806
    return [
        round(ceil(maxI) / 10.0 * v, 2)
        for v in [9.98, -9.98, 6.0, -6.0, 4.0, -4.0, 2.0, -2.0, 1.0, -1.0, 0.0]
    ]


def add_magnet_table_parameters(n, e, magnetPV): # noqa N806
    try:
        mag_pv_split = magnetPV.split("-")
        magnet = (
            mag_pv_split[0].replace("EBT", "CLA"),
            mag_pv_split[1].replace("HRG1", "GUN"),
            mag_pv_split[3],
            int(mag_pv_split[4]),
        )
        table = magnet_table.loc[
            magnet,
            [
                "slope [units/A]",
                "max current [A]",
                "f [units/A³]",
                "a [units/A²]",
                "I0 [A]",
                "d [units]",
                "magnetic length [mm]",
                "current [A]",
                "magnet type",
                "serial number",
            ],
        ]
        m, i_max, f, a, i0, d, l, i_degauss, manufacturer, serial_number = table
        e.magnetic.linear_saturation_coefficients.update_from_string(
            ",".join(list(map(str, [m, i_max, f, a, i0, d, l])))
        )
        e.degauss.values = create_degauss_values(float(i_degauss))
        e.manufacturer.manufacturer = manufacturer
        e.manufacturer.serial_number = serial_number
        e.electrical.max_i = ceil(i_degauss)
        e.electrical.min_i = -1.0 * ceil(i_degauss)
    except Exception:
        _log.warning("Magnet '%s' not found in magnet table", magnet)
