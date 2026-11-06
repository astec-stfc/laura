"""
Legacy *module path* aliasing for previous non-PEP8-compliant code.

Module and package names were moved to lower_snake_case (``laura.models.RF`` ->
``laura.models.rf``, ``laura.Exporters`` -> ``laura.exporters``). This module
keeps every old import path working.

Registered from ``laura/__init__.py``. Because importing any submodule imports
its parent packages first, the finder is always installed before a legacy path
can be resolved.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.util
import sys
import warnings

__all__ = ["LEGACY_MODULES", "install"]

LEGACY_MODULES: dict[str, str] = {
    # --- packages -----------------------------------------------------------
    "laura.Exporters": "laura.exporters",
    "laura.Importers": "laura.importers",
    # --- laura/exporters ----------------------------------------------------
    "laura.Exporters.RDF": "laura.exporters.rdf_exporter",
    "laura.Exporters.SQL": "laura.exporters.sql_exporter",
    "laura.Exporters.YAML": "laura.exporters.yaml_exporter",
    "laura.exporters.RDF": "laura.exporters.rdf_exporter",
    "laura.exporters.SQL": "laura.exporters.sql_exporter",
    "laura.exporters.YAML": "laura.exporters.yaml_exporter",
    # --- laura/importers ----------------------------------------------------
    "laura.Importers.YAML_Loader": "laura.importers.yaml_loader",
    "laura.importers.YAML_Loader": "laura.importers.yaml_loader",
    # --- laura/models -------------------------------------------------------
    "laura.models.RF": "laura.models.rf",
    "laura.models.baseModels": "laura.models.base_models",
    "laura.models.elementList": "laura.models.element_list",
    # --- laura/translator ---------------------------------------------------
    "laura.translator.utils.SDDSFile": "laura.translator.utils.sdds_file",
    "laura.translator.utils.elegant.SDDSFile": "laura.translator.utils.elegant.sdds_file",
    "laura.translator.utils.elegant.sdds_classes_APS": "laura.translator.utils.elegant.sdds_classes_aps",
    "laura.translator.utils.fields.FieldParameter": "laura.translator.utils.fields.field_parameter",
}


class _LegacyLoader(importlib.abc.Loader):
    """Loader that returns the renamed module in place of the legacy one."""

    def __init__(self, legacy: str, current: str) -> None:
        self.legacy = legacy
        self.current = current

    def create_module(self, spec):
        warnings.warn(
            f"{self.legacy} was renamed to {self.current} for PEP 8 compliance. "
            f"The old import path still works but will be removed in a future "
            f"release; import from {self.current} instead.",
            FutureWarning,
            stacklevel=2,
        )
        return importlib.import_module(self.current)

    def exec_module(self, module) -> None:
        """No-op: the returned module was already executed under its real name."""


class _LegacyFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path=None, target=None):
        current = LEGACY_MODULES.get(fullname)
        if current is None:
            return None
        return importlib.util.spec_from_loader(
            fullname, _LegacyLoader(fullname, current)
        )


def _check_table() -> None:
    """A self-mapping entry would make the loader import itself forever."""
    for legacy, current in LEGACY_MODULES.items():
        if legacy == current:
            raise RuntimeError(
                f"LEGACY_MODULES maps {legacy!r} to itself, which would recurse."
            )


def install() -> None:
    """Register the finder. Idempotent."""
    _check_table()
    if not any(isinstance(f, _LegacyFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _LegacyFinder())
