
# ---------------------------------------------------------------------------
# Backwards compatibility: names renamed for PEP 8. Served lazily with a
# FutureWarning so downstream consumers (astec-stfc/simba) keep working.
# ---------------------------------------------------------------------------
from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "SimFrame_Conversion": "SimFrameConversion",
        "get_SimFrame_MachineArea": "get_simframe_machine_area",
        "get_SimFrame_PV": "get_simframe_pv",
        "get_SimFrame_YAML_filename": "get_simframe_yaml_filename",
        "interpret_SimFrame_Element": "interpret_simframe_element",
        "read_SimFrame_YAML": "read_simframe_yaml",
    },
)
