#!/usr/bin/env python3
"""
Apply the whole PEP 8 naming migration from a clean checkout, in order.

Everything here is derived from the maps in ``tools/renames/`` plus the alias
tables below, so the migration is reproducible: revert the working tree, re-run
this, and you are back where you were. It is idempotent -- re-running on an
already-migrated tree is a no-op.

    python tools/apply_migration.py

Steps:
  0. the subdirectory guard in element.py, and the `seld` typo fixes
  1. round 1 -- translator/utils/ and translator/converters/codes/
  2. round 2 -- translator/converters/
  3. round 3 -- models/
  4. compat shims (module __getattr__ + method-alias mixins)
  5. round 4 -- module *filenames*, their imports, shims, and the Sphinx stubs
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

# --- step 0: hand edits that are not renames --------------------------------

GUARD_FN = '''def _identifies_same_type(class_name: str, hardware_type: str) -> bool:
    """
    Whether ``class_name`` and ``hardware_type`` name the same element type.

    ``hardware_type`` is a *wire value*: it is written into every saved lattice
    YAML and keys :data:`ELEMENT_REGISTRY`, so it is frozen for backwards
    compatibility. Python class names, by contrast, migrated to PEP 8 CapWords
    -- ``Beam_Position_Monitor`` became ``BeamPositionMonitor``.

    Comparing with underscores removed keeps the legacy wire value matching its
    renamed class, so :attr:`BaseElement.subdirectory` does not gain an extra
    path segment and move every element's file on disk. Exact matches are still
    matches, so this only loosens the comparison for names differing *solely*
    by underscores -- precisely what the rename changed.
    """
    return class_name.replace("_", "") == hardware_type.replace("_", "")


'''


def step0_hand_edits() -> None:
    element = ROOT / "laura/models/element.py"
    src = element.read_text()
    if "_identifies_same_type" not in src:
        src = src.replace("def _coerce_nested_model(", GUARD_FN + "def _coerce_nested_model(", 1)
        src = src.replace(
            "        if self.__class__.__name__ == self.hardware_type:",
            "        if _identifies_same_type(self.__class__.__name__, self.hardware_type):",
            1,
        )
        element.write_text(src)
        print("  element.py: subdirectory guard added")
    else:
        print("  element.py: guard already present")

    for rel in ("laura/translator/converters/model.py",
                "laura/translator/converters/section.py"):
        p = ROOT / rel
        s = p.read_text()
        if "def format_string(seld," in s:
            p.write_text(s.replace("def format_string(seld,", "def format_string(self,"))
            print(f"  {rel}: seld -> self")

    init = ROOT / "laura/translator/utils/elegant/__init__.py"
    if not init.exists():
        init.write_text(
            '"""\nelegant-specific SDDS helpers.\n\n'
            "This package was previously an implicit namespace package -- no\n"
            "``__init__.py`` in version control -- which made it invisible to ruff's\n"
            "module-name check and at risk of being dropped by setuptools'\n"
            '``packages = find:`` discovery.\n"""\n'
        )
        print("  elegant/__init__.py: created")


# --- step 4: compat shims ---------------------------------------------------

MODULE_ALIASES: dict[str, dict[str, str]] = {
    "laura/translator/converters/codes/astra.py": {
        "astra_header": "AstraHeader", "astra_newrun": "AstraNewRun",
        "astra_output": "AstraOutput", "astra_charge": "AstraCharge",
        "astra_errors": "AstraErrors",
        "section_header_text_ASTRA": "section_header_text_astra"},
    "laura/translator/converters/codes/csrtrack.py": {
        "csrtrack_element": "CsrTrackElement", "csrtrack_forces": "CsrTrackForces",
        "csrtrack_monitor": "CsrTrackMonitor", "csrtrack_particles": "CsrTrackParticles",
        "csrtrack_track_step": "CsrTrackTrackStep", "csrtrack_tracker": "CsrTrackTracker"},
    "laura/translator/converters/codes/gpt.py": {
        "gpt_Zminmax": "GptZMinMax", "gpt_accuracy": "GptAccuracy", "gpt_ccs": "GptCcs",
        "gpt_charge": "GptCharge", "gpt_csr1d": "GptCsr1D", "gpt_dtmaxt": "GptDtMaxT",
        "gpt_dtmint": "GptDtMinT", "gpt_element": "GptElement",
        "gpt_forwardscatter": "GptForwardScatter", "gpt_scatterplate": "GptScatterPlate",
        "gpt_setfile": "GptSetFile", "gpt_setreduce": "GptSetReduce",
        "gpt_spacecharge": "GptSpaceCharge", "gpt_tout": "GptTout",
        "gpt_writefloorplan": "GptWriteFloorPlan"},
    "laura/translator/converters/codes/ocelot.py": {
        "type_conversion_rules_Ocelot": "type_conversion_rules_ocelot"},
    "laura/translator/converters/codes/opal.py": {
        "opal_beam": "OpalBeam", "opal_distribution": "OpalDistribution",
        "opal_fieldsolver": "OpalFieldSolver", "opal_header": "OpalHeader",
        "opal_option": "OpalOption", "opal_run": "OpalRun", "opal_track": "OpalTrack"},
    "laura/translator/utils/sdds_file.py": {"SDDS_Types": "SddsTypes"},
    "laura/translator/utils/elegant/sdds_classes_aps.py": {
        "SDDS_Floor": "SddsFloor", "SDDS_Params": "SddsParams"},
    "laura/translator/utils/fields/__init__.py": {"field": "FieldMap"},
    "laura/translator/utils/fields/hdf5.py": {
        "read_HDF5_field_file": "read_hdf5_field_file",
        "write_HDF5_field_file": "write_hdf5_field_file"},
    "laura/translator/utils/fields/sdds.py": {
        "read_SDDS_field_file": "read_sdds_field_file",
        "write_SDDS_field_file": "write_sdds_field_file"},
    "laura/translator/utils/functions.py": {"checkValue": "check_value"},
    "laura/translator/converters/__init__.py": {
        "elements_Elegant": "elements_elegant", "elements_Genesis": "elements_genesis",
        "elements_Ocelot": "elements_ocelot", "elements_Cheetah": "elements_cheetah",
        "elements_Opal": "elements_opal", "elements_Madx": "elements_madx",
        "type_conversion_rules_Elegant": "type_conversion_rules_elegant",
        "type_conversion_rules_Genesis": "type_conversion_rules_genesis",
        "type_conversion_rules_Opal": "type_conversion_rules_opal",
        "type_conversion_rules_Madx": "type_conversion_rules_madx",
        "type_conversion_rules_Names": "type_conversion_rules_names"},
    "laura/models/base_models.py": {"objectList": "ObjectList"},
    "laura/models/element.py": {
        "baseElement": "BaseElement",
        "Beam_Position_Monitor": "BeamPositionMonitor",
        "Beam_Arrival_Monitor": "BeamArrivalMonitor",
        "Bunch_Length_Monitor": "BunchLengthMonitor",
        "Wall_Current_Monitor": "WallCurrentMonitor",
        "Faraday_Cup_Monitor": "FaradayCupMonitor",
        "Photon_Monitor": "PhotonMonitor",
        "Integrated_Current_Transformer": "IntegratedCurrentTransformer",
        "Horizontal_Corrector": "HorizontalCorrector",
        "Vertical_Corrector": "VerticalCorrector",
        "Combined_Corrector": "CombinedCorrector",
        "Low_Level_RF": "LowLevelRF"},
    "laura/models/magnetic.py": {
        "Dipole_Magnet": "DipoleMagnet", "Quadrupole_Magnet": "QuadrupoleMagnet",
        "Sextupole_Magnet": "SextupoleMagnet", "Octupole_Magnet": "OctupoleMagnet",
        "Solenoid_Magnet": "SolenoidMagnet", "Corrector_Magnet": "CorrectorMagnet",
        "Wiggler_Magnet": "WigglerMagnet", "NonLinearLens_Magnet": "NonLinearLensMagnet",
        "Power": "power", "Sqrt": "sqrt",
        "solenoidFields": "solenoid_fields",
        "solenoidFieldsData": "solenoid_fields_data"},
    "laura/models/diagnostic.py": {
        "Beam_Position_Monitor_Diagnostic": "BeamPositionMonitorDiagnostic",
        "Beam_Arrival_Monitor_Diagnostic": "BeamArrivalMonitorDiagnostic",
        "Bunch_Length_Monitor_Diagnostic": "BunchLengthMonitorDiagnostic",
        "Photon_Intensity_Monitor_Diagnostic": "PhotonIntensityMonitorDiagnostic",
        "Camera_Diagnostic": "CameraDiagnostic", "Screen_Diagnostic": "ScreenDiagnostic",
        "Charge_Diagnostic": "ChargeDiagnosticElement",
        "Camera_Sensor": "CameraSensor", "Camera_Mask": "CameraMask",
        "Camera_Pixel_Results_Indices": "CameraPixelResultsIndices",
        "Camera_Pixel_Results_Names": "CameraPixelResultsNames",
        "Camera_Diagnostic_Type": "camera_diagnostic_type",
        "Manta_Camera_Diagnostic": "manta_camera_diagnostic",
        "Manta_Camera_Sensor": "manta_camera_sensor",
        "PCO_Camera_Diagnostic": "pco_camera_diagnostic",
        "PCO_Camera_Sensor": "pco_camera_sensor"},
    "laura/models/rf_elements.py": {
        "Low_Level_RF_Element": "LowLevelRFElement",
        "llrftimingsCATAPnames": "llrf_timings_catap_names"},
}

SHIM = '''

# ---------------------------------------------------------------------------
# Backwards compatibility: names renamed for PEP 8. Served lazily with a
# DeprecationWarning so downstream consumers (astec-stfc/simba) keep working.
# ---------------------------------------------------------------------------
from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
%s    },
)
'''

# class -> (module, {legacy: current}); the mixin is inserted on the class.
METHOD_ALIASES: dict[str, tuple[str, dict[str, str]]] = {
    "AstraHeader": ("laura/translator/converters/codes/astra.py",
                    {"write_ASTRA": "write_astra"}),
    "CsrTrackElement": ("laura/translator/converters/codes/csrtrack.py",
                        {"write_CSRTrack": "write_csrtrack", "CSRTrack_str": "csrtrack_str"}),
    "GptElement": ("laura/translator/converters/codes/gpt.py", {"write_GPT": "write_gpt"}),
    "GptCcs": ("laura/translator/converters/codes/gpt.py", {"M": "rotation_matrix"}),
    "OpalHeader": ("laura/translator/converters/codes/opal.py", {"write_Opal": "write_opal"}),
    "BaseElementTranslator": ("laura/translator/converters/base.py", {
        "_write_ASTRA": "_write_astra",
        "_write_ASTRA_Common": "_write_astra_common",
        "_write_ASTRA_Circular": "_write_astra_circular",
        "_write_ASTRA_Planar": "_write_astra_planar",
        "_write_ASTRA_dictionary": "_write_astra_dictionary",
        "_write_ASTRA_dipole": "_write_astra_dipole",
        "_write_ASTRA_quadrupole": "_write_astra_quadrupole",
        "_write_ASTRA_solenoid": "_write_astra_solenoid",
        "_write_CSRTrack": "_write_csrtrack",
        "_convertKeyword_Elegant": "_convert_keyword_elegant",
        "_convertKeyword_Genesis": "_convert_keyword_genesis",
        "_convertKeyword_Ocelot": "_convert_keyword_ocelot",
        "_convertKeyword_Cheetah": "_convert_keyword_cheetah",
        "_convertKeyword_Opal": "_convert_keyword_opal",
        "_convertKeyword_Madx": "_convert_keyword_madx",
        "_convertKeyword_WakeT": "_convert_keyword_wake_t",
        "_convertKeyword_Xsuite": "_convert_keyword_xsuite",
        "_convertType_Elegant": "_convert_type_elegant",
        "_convertType_Genesis": "_convert_type_genesis",
        "_convertType_Ocelot": "_convert_type_ocelot",
        "_convertType_Cheetah": "_convert_type_cheetah",
        "_convertType_Opal": "_convert_type_opal",
        "_convertType_Madx": "_convert_type_madx"}),
    "BaseElement": ("laura/models/element.py", {"YAML_filename": "yaml_filename"}),
    "SectionLattice": ("laura/models/element_list.py", {"createDrifts": "create_drifts"}),
    "LAURA": ("laura/laura.py", {"createDrifts": "create_drifts"}),
    "MagneticElement": ("laura/models/magnetic.py", {
        "KToCurrent": "k_to_current", "KLToCurrent": "kl_to_current",
        "currentToK": "current_to_k", "currentToAngle": "current_to_angle"}),
    "FieldIntegral": ("laura/models/magnetic.py", {"currentToK": "current_to_k"}),
    "LinearSaturationFit": ("laura/models/magnetic.py", {
        "KToCurrent": "k_to_current", "KLToCurrent": "kl_to_current",
        "currentToK": "current_to_k"}),
    "LowLevelRFElement": ("laura/models/rf_elements.py",
                          {"_create_LLRFChannels_Model": "_create_llrf_channels_model"}),
}

#: Classes that already inherit DeprecatedMethodAliases through a base
#: (BaseElementTranslator -> PhysicalBaseElement -> ... -> BaseElement).
#: Re-declaring the mixin on these makes the MRO inconsistent.
INHERITS_MIXIN = {"BaseElementTranslator"}

CLASS_RE_TMPL = r"^class {name}\((?P<bases>[^)]*)\):\n(?P<doc>    (?P<q>\"\"\"|''')(?:.|\n)*?(?P=q)\n)?"


def add_module_shims() -> None:
    for rel, aliases in MODULE_ALIASES.items():
        p = ROOT / rel
        src = p.read_text()
        if "deprecated_aliases" in src or "Deprecated module path" in src:
            continue
        body = "".join(f'        "{o}": "{n}",\n' for o, n in sorted(aliases.items()))
        p.write_text(src.rstrip("\n") + SHIM % body)
        print(f"  shim: {rel} ({len(aliases)})")


def _already_has_aliases(src: str, cls: str) -> bool:
    """
    Whether *cls* already declares _DEPRECATED_METHOD_ALIASES.

    Parsed rather than string-sliced: a fixed-width window around the class
    header overflows on long docstrings, and the guard then silently fails,
    double-applying the mixin and breaking the MRO on re-run.
    """
    import ast

    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls:
            for stmt in node.body:
                targets = getattr(stmt, "targets", []) or []
                if any(isinstance(t, ast.Name) and t.id == "_DEPRECATED_METHOD_ALIASES"
                       for t in targets):
                    return True
    return False


def add_method_aliases() -> None:
    for cls, (rel, aliases) in METHOD_ALIASES.items():
        p = ROOT / rel
        src = p.read_text()
        pat = re.compile(CLASS_RE_TMPL.format(name=re.escape(cls)), re.MULTILINE)
        m = pat.search(src)
        if not m:
            print(f"  !! {rel}: class {cls} not found")
            continue
        if _already_has_aliases(src, cls):
            continue
        body = "".join(f'        "{o}": "{n}",\n' for o, n in sorted(aliases.items()))
        bases = m.group("bases") if cls in INHERITS_MIXIN else \
            f"DeprecatedMethodAliases, {m.group('bases')}"
        # docstring first, then the alias table -- otherwise the docstring is
        # demoted to a stray expression and __doc__ becomes None.
        replacement = (
            f"class {cls}({bases}):\n"
            + (m.group("doc") or "")
            + "\n    # Legacy names, served with a DeprecationWarning by the mixin,\n"
            "    # which also warns if a subclass overrides one under its old name.\n"
            f"    _DEPRECATED_METHOD_ALIASES = {{\n{body}    }}\n"
        )
        src = src[: m.start()] + replacement + src[m.end():]
        if cls not in INHERITS_MIXIN and "from laura._compat import DeprecatedMethodAliases" not in src:
            lines = src.splitlines(keepends=True)
            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    lines.insert(i, "from laura._compat import DeprecatedMethodAliases\n")
                    break
            src = "".join(lines)
        p.write_text(src)
        print(f"  method aliases: {rel} :: {cls} ({len(aliases)})")


def run_codemod(mapfile: str) -> None:
    print(f"\n== codemod {mapfile} ==")
    subprocess.run(
        [PY, str(ROOT / "tools/pep8_rename.py"), "--map", str(ROOT / "tools/renames" / mapfile),
         "--docstrings", "--apply"],
        check=True, cwd=ROOT,
    )


def main() -> int:
    print("== step 0: hand edits ==")
    step0_hand_edits()
    for mapfile in ("01-leaf-modules.toml", "02-converters.toml", "03-models.toml",
                    "05-importers-exporters.toml"):
        run_codemod(mapfile)
    # Module renames run before the name-alias shims: the alias tables below
    # name post-rename files, and step 5 leaves a module-path shim at each old
    # path. Appending a name-alias block onto one of those shims produces a
    # __getattr__ over the wrong globals() and breaks every alias in it.
    print("\n== step 4: module filenames + docs ==")
    subprocess.run([PY, str(ROOT / "tools/rename_modules.py"), "--apply"],
                   check=True, cwd=ROOT)
    print("\n== step 5: compat shims ==")
    add_module_shims()
    add_method_aliases()
    print("\ndone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
