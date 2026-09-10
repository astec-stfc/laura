from ..sdds_file import SDDSFile as _SDDSFile, SddsTypes, read_sdds_file  # noqa: F401


class SDDSFile(_SDDSFile):
    """SDDSFile with per-instance indexed SDDS slots, for concurrent elegant writes."""

    def __init__(self, index=1, ascii=False):
        super().__init__(index=index, ascii=ascii, indexed=True)
