"""SDDSFile when the SDDS index it asks for is already taken."""

import numpy as np
import pytest

pytest.importorskip("sdds")

from laura.translator.utils.sdds_file import SDDS_Types, SDDSFile  # noqa: E402


def test_a_busy_index_falls_back_to_a_free_one(tmp_path):
    """The sdds package refuses a second object on one index ("Index 1 is already in
    use"); the fallback used to ask for the same slot again, so the file was left
    with no SDDS object and every read failed."""
    path = str(tmp_path / "x.sdds")
    written = SDDSFile(index=1)
    written.add_columns(["x"], [np.array([1.5, 2.5])], [SDDS_Types.SDDS_DOUBLE], ["m"], [""])
    written.write_file(path)  # `written` keeps index 1 busy

    read = SDDSFile(index=1)
    read.read_file(path, page=0)
    assert list(read.columns()["x"].data) == [1.5, 2.5]
