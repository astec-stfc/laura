import shlex
from typing import Any, Dict, List


def _coerce(value: str) -> Any:
    value = value.strip()
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value.strip('"')


class TFSFile:
    """Minimal reader for MAD-X TFS-format tables (e.g. ``TWISS``/``SURVEY``
    output produced via ``SELECT`` + the corresponding command).

    TFS mirrors SDDS's own header/column/data shape closely enough that this
    follows the same pattern as
    :class:`~laura.translator.utils.SDDSFile.SDDSFile`, just for MAD-X's
    plain-text table format (``@`` header lines, a ``*`` column-name line, a
    ``$`` column-type line, then one whitespace-separated data row per
    element) instead of SDDS's binary one.
    """

    def __init__(self):
        self.headers: Dict[str, Any] = {}
        self.columns: List[str] = []
        self.data: Dict[str, List[Any]] = {}

    def read_file(self, filename: str) -> None:
        self.headers = {}
        self.columns = []
        rows = []
        with open(filename) as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                if line.startswith("@"):
                    parts = shlex.split(line[1:])
                    if len(parts) >= 2:
                        name = parts[0]
                        value = " ".join(parts[2:]) if len(parts) > 2 else parts[1]
                        self.headers[name.lower()] = _coerce(value)
                elif line.startswith("*"):
                    self.columns = [c.lower() for c in shlex.split(line[1:])]
                elif line.startswith("$"):
                    continue
                else:
                    rows.append(shlex.split(line))
        self.data = {col: [] for col in self.columns}
        for row in rows:
            for col, val in zip(self.columns, row):
                self.data[col].append(_coerce(val))

    def rows(self) -> List[Dict[str, Any]]:
        """Return the table as a list of ``{column_name: value}`` dicts, one per element."""
        n = len(self.data[self.columns[0]]) if self.columns else 0
        return [{col: self.data[col][i] for col in self.columns} for i in range(n)]
