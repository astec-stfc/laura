import functools
import json
import logging
import os
import pathlib
import re
from typing import List

import yaml
from pydantic import BaseModel, TypeAdapter, ValidationError
from yaml import CSafeLoader as Loader

from ..models.control import ControlVariable

# Import elements before building registry
from ..models.element import ELEMENT_REGISTRY

_log = logging.getLogger("laura.loader")

# Fast metadata extraction regex
_NAME_RE = re.compile(r'^\s*name:\s*["\'\s]?([^"\'\s#\n]+)["\'\s]?', re.MULTILINE)
_AREA_RE = re.compile(
    r'^\s*machine_area:\s*["\'\s]?([^"\'\s#\n]+)["\'\s]?', re.MULTILINE
)

COMBINED_SCHEMAS_KEY = "_schemas"


class ElementLoadError(Exception):
    """
    A single element could not be loaded from YAML.

    LAURA's loader is permissive by design: an element that cannot be parsed
    is logged and skipped, so a machine can load "successfully" while missing
    elements (see `patterns/debug-import-loading.md`). This is the default,
    but losses can be made visible
    """

    REASONS = (
        "no_hardware_type",
        "unregistered_hardware_type",
        "validation_error",
        "duplicate_name",
    )

    def __init__(
        self,
        name: str,
        reason: str,
        detail: str,
        hardware_type: str | None = None,
        filename: str | None = None,
    ):
        self.name = name
        self.reason = reason
        self.detail = detail
        self.hardware_type = hardware_type
        self.filename = filename
        hw = f" [{hardware_type}]" if hardware_type else ""
        where = f" in '{filename}'" if filename else ""
        super().__init__(f"Failed to load '{name}'{hw}{where}: {detail}")


class DuplicateElementError(ElementLoadError):
    """
    Two definitions declared the same element name; only one survives,
    later definitions win..

    Not a parse failure -- both definitions may be perfectly valid -- but
    elements are keyed by name all the way through LAURA, so the loser is
    simply absent from the machine.
    """

    def __init__(
        self,
        name: str,
        filename: str | None = None,
        superseded_by: str | None = None,
        hardware_type: str | None = None,
    ):
        self.superseded_by = superseded_by
        if superseded_by and superseded_by == filename:
            detail = "declared more than once in the same file"
        elif superseded_by:
            detail = f"superseded by the definition in '{superseded_by}'"
        else:
            detail = "superseded by a later definition of the same name"
        super().__init__(
            name,
            "duplicate_name",
            detail,
            hardware_type=hardware_type,
            filename=filename,
        )


def _record_load_failure(
    error: ElementLoadError, errors: list | None, strict: bool
) -> None:
    """
    Record *error* on the caller's ``errors`` list, and raise it when ``strict``.
    """
    if errors is not None:
        errors.append(error)
    if strict:
        raise error


def collect_unique_by_name(
    items, errors: list | None = None, strict: bool = False
) -> dict:
    """
    Build a ``{name: value}`` dict from ``(name, source, value)`` triples,
    recording each name that appears more than once. Later entries win.
    """
    result: dict = {}
    sources: dict = {}
    for name, source, value in items:
        if name in result:
            _record_load_failure(
                DuplicateElementError(
                    name,
                    filename=sources.get(name),
                    superseded_by=source,
                    hardware_type=getattr(value, "hardware_type", None),
                ),
                errors,
                strict,
            )
        result[name] = value
        sources[name] = source
    return result


def collect_unique_filenames(
    files, errors: list | None = None, strict: bool = False
) -> dict:
    """
    Map each element file's declared name to its path, reporting collisions.

    Note this catches two different data faults with one check: two files
    genuinely declaring the same ``name:``, and a file whose ``name:`` disagrees
    with its own filename and so collides with a *different* file's name.
    """
    return collect_unique_by_name(
        ((fast_get_element_metadata(fn)["name"], fn, fn) for fn in files),
        errors=errors,
        strict=strict,
    )


def fast_get_element_metadata(filename: str) -> dict:
    """Quickly extract metadata from a YAML file without full parsing."""
    metadata = {"name": None, "machine_area": None}
    try:
        with open(filename, "r") as f:
            # Metadata is usually in first 2000 chars
            content = f.read(2000)
            name_match = _NAME_RE.search(content)
            if name_match:
                metadata["name"] = name_match.group(1).strip()
            area_match = _AREA_RE.search(content)
            if area_match:
                metadata["machine_area"] = area_match.group(1).strip()
    except Exception:
        pass
    if not metadata["name"]:
        metadata["name"] = (
            os.path.basename(filename).replace(".yaml", "").replace(".yml", "")
        )
    return metadata


class LazyElementDict(dict):
    """
    Dictionary that loads elements from YAML files only when accessed.
    """

    def __init__(self, filenames, exclude_keys=None, strict=False, errors=None):
        # Initialise with keys but None values to satisfy tools that check keys()
        super().__init__({k: None for k in filenames.keys()})
        self._filenames = filenames  # Map of name: filename
        self._exclude_keys = exclude_keys
        self._metadata_cache = {}
        self._strict = strict
        self._failed = set()
        self.load_errors = [] if errors is None else errors

    def get_metadata(self, name):
        """Quickly get name/area without loading model."""
        if self.is_loaded(name):
            elem = super().__getitem__(name)
            if elem is None:
                return None
            return {
                "name": elem.name,
                "machine_area": getattr(elem, "machine_area", None),
            }
        if name in self._metadata_cache:
            return self._metadata_cache[name]
        if name in self._filenames:
            meta = fast_get_element_metadata(self._filenames[name])
            self._metadata_cache[name] = meta
            return meta
        return None

    def get_all_metadata(self):
        """Return all metadata for all files without loading."""
        return {name: self.get_metadata(name) for name in self._filenames}

    def is_loaded(self, name):
        """Check if an element has already been loaded via interpret_YAML_Element.

        NOTE: this answers about the *key*, and ``__init__`` seeds every key
        with a ``None`` placeholder, so it is True for an element that has
        never been read.
        """
        return super().__contains__(name)

    def __getitem__(self, key):
        if super().__contains__(key):
            val = super().__getitem__(key)
            if val is not None:
                return val
            if key in self._failed:
                return None
        if key in self._filenames:
            elem = read_YAML_Element_File(
                self._filenames[key],
                exclude_keys=self._exclude_keys,
                strict=self._strict,
                errors=self.load_errors,
            )
            if elem is None:
                self._failed.add(key)
            super().__setitem__(key, elem)
            return elem
        raise KeyError(key)

    def __contains__(self, key):
        return super().__contains__(key) or key in self._filenames

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return sorted(set(self._filenames.keys()) | set(super().keys()))

    def values(self):
        for k in self.keys():
            yield self[k]

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())


def get_all_subclasses(cls):
    subclasses = set()
    for sub in cls.__subclasses__():
        subclasses.add(sub)
        subclasses.update(get_all_subclasses(sub))
    return subclasses


_MODEL_REGISTRY = None


def get_model_registry():
    global _MODEL_REGISTRY
    if _MODEL_REGISTRY is None:
        ALL_MODELS = get_all_subclasses(BaseModel)
        _MODEL_REGISTRY = {cls.__name__: cls for cls in ALL_MODELS}
    return _MODEL_REGISTRY


class LazyAdapterDict(dict):
    def get(self, key, default=None):
        if key not in self:
            model = ELEMENT_REGISTRY.get(key)
            if model is None:
                return default
            self[key] = TypeAdapter(model)
        return super().get(key)


ADAPTERS = LazyAdapterDict()

# ── Optional JSON Schema validation ──────────────────────────────────────────

_SCHEMA_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "schema"
    / "generated"
    / "laura_element.schema.json"
)


@functools.cache
def _get_json_schema() -> dict:
    """Load and cache the generated LAURA JSON Schema."""
    if not _SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"LAURA JSON Schema not found at '{_SCHEMA_PATH}'.  "
            "Generate it with: gen-json-schema laura/schema/laura_schema.yaml "
            "--output laura/schema/generated/laura_element.schema.json"
        )
    with open(_SCHEMA_PATH, "r") as fh:
        return json.load(fh)


def validate_element_dict(elem: dict) -> None:
    """Validate *elem* against the LAURA LinkML-derived JSON Schema.

    Raises
    ------
    jsonschema.ValidationError
        If *elem* does not conform to the schema.
    ImportError
        If the *jsonschema* package is not installed.
    FileNotFoundError
        If the generated JSON Schema file has not been created yet.
    """
    try:
        import jsonschema  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "Install 'jsonschema' to enable YAML schema validation: "
            "pip install 'laura-accelerator[schema]'"
        ) from exc
    jsonschema.validate(instance=elem, schema=_get_json_schema())


def filter_top_level(elem: dict, exclude_keys: List[str] | None = None) -> dict:
    if isinstance(exclude_keys, list):
        return {k: v for k, v in elem.items() if k not in exclude_keys}
    return {k: v for k, v in elem.items()}


_CONTROLS_SCHEMA_CACHE: dict = {}


def resolve_controls_schema_path(path: str, base_dir: str | None) -> str:
    """
    Resolve a ``controls.schema`` reference to an actual file on disk.

    Tried in order: as given (absolute, or relative to the current working
    directory), then relative to ``base_dir`` -- the directory of the element
    YAML file that referenced it, which is the common case (a schema sitting
    alongside the element files it applies to).
    """
    if os.path.isabs(path):
        if os.path.exists(path):
            return path
    elif os.path.exists(path):
        return os.path.abspath(path)

    if base_dir:
        candidate = os.path.join(base_dir, path)
        if os.path.exists(candidate):
            return os.path.abspath(candidate)

    raise FileNotFoundError(
        f"controls schema '{path}' not found"
        + (f" (also tried relative to '{base_dir}')" if base_dir else "")
    )


def _load_controls_schema_variables(path: str) -> dict:
    if path not in _CONTROLS_SCHEMA_CACHE:
        with open(path, "r") as stream:
            data = yaml.load(stream, Loader=Loader) or {}
        variables = data.get("variables", data) if isinstance(data, dict) else {}
        _CONTROLS_SCHEMA_CACHE[path] = variables
    return _CONTROLS_SCHEMA_CACHE[path]


def get_controls_schema_variables(
    schema_ref: str, base_dir: str | None = None, schema_map: dict | None = None
) -> dict:
    """
    Look up the raw (still ``{name}``-templated) ``variables`` mapping named
    by a ``controls.schema`` reference.

    If ``schema_map`` is given and contains ``schema_ref``, that in-memory
    mapping is used directly -- this is how a combined file embeds its
    schemas (see ``read_YAML_Combined_File`` / ``export_machine_combined_file``)
    so it can be resolved without touching disk. Otherwise ``schema_ref`` is
    resolved to a file via :func:`resolve_controls_schema_path` and loaded
    (and cached) from there.
    """
    if schema_map is not None and schema_ref in schema_map:
        return schema_map[schema_ref]
    schema_path = resolve_controls_schema_path(schema_ref, base_dir)
    return _load_controls_schema_variables(schema_path)


def _substitute_schema_placeholders(value, name: str):
    """Replace the ``{name}`` placeholder with the owning element's name,
    recursively through nested dicts/lists (e.g. in `identifier`)."""
    if isinstance(value, str):
        return value.replace("{name}", name)
    if isinstance(value, dict):
        return {k: _substitute_schema_placeholders(v, name) for k, v in value.items()}
    if isinstance(value, list):
        return [_substitute_schema_placeholders(v, name) for v in value]
    return value


def resolve_controls_schema(
    controls: dict,
    element_name: str,
    base_dir: str | None = None,
    schema_map: dict | None = None,
) -> dict:
    """
    Expand a ``controls.schema`` reference into a full ``variables`` dict.

    ``controls['schema']`` names a schema (looked up via
    :func:`get_controls_schema_variables`) holding a template ``variables``
    mapping shared by every element of a given type; any ``{name}`` in its
    string fields (typically `identifier`) is replaced with ``element_name``,
    or with ``controls['identifier_pattern']`` instead if given.
    Any ``variables`` already present in ``controls`` are then layered on top
    of the template, one field at a time per variable key, so an element can
    override or add a single field without repeating the whole entry; a
    variable key not present in the schema is added as-is.

    Returns ``controls`` unchanged if it has no ``schema`` key.
    """
    schema_ref = controls.get("schema")
    if not schema_ref:
        return controls

    schema_variables = get_controls_schema_variables(schema_ref, base_dir, schema_map)
    substitution_name = controls.get("identifier_pattern") or element_name

    merged = {
        key: _substitute_schema_placeholders(var_def, substitution_name)
        for key, var_def in schema_variables.items()
    }

    for key, override in (controls.get("variables") or {}).items():
        if isinstance(merged.get(key), dict) and isinstance(override, dict):
            merged[key] = {**merged[key], **override}
        else:
            merged[key] = override

    resolved = {k: v for k, v in controls.items() if k != "variables"}
    resolved["variables"] = merged
    return resolved


def collapse_controls_schema(
    controls: dict,
    element_name: str,
    schema_variables: dict,
    live_variables: dict | None = None,
) -> dict:
    """
    Inverse of the merge step in :func:`resolve_controls_schema`.

    Given a ``controls`` dict whose ``variables`` are fully resolved (as
    produced by serialising a ``ControlsInformation``, e.g. via
    ``ele.base_model_dump()``) and which still names its ``schema``, re-derive
    the minimal per-field ``variables`` override needed to reconstruct it
    against ``schema_variables`` (that schema's raw, still ``{name}``-templated
    content -- see :func:`get_controls_schema_variables`).

    ``live_variables`` (``{key: ControlVariable}``, typically ``ele.controls.
    variables``), if given, is used for a value-exact comparison via
    :meth:`~laura.models.control.ControlVariable.unstripped_dump` rather than
    the already-defaults-stripped dicts in ``controls['variables']``.

    Used by exporters that want to write elements back out referencing a
    shared schema rather than in the fully expanded form. Returns ``controls``
    unchanged if it has no ``schema`` key.
    """
    schema_ref = controls.get("schema")
    if not schema_ref:
        return controls

    substitution_name = controls.get("identifier_pattern") or element_name
    expected = {
        key: _substitute_schema_placeholders(var_def, substitution_name)
        for key, var_def in schema_variables.items()
    }

    collapsed = {}
    for key, actual in (controls.get("variables") or {}).items():
        exp = expected.get(key)
        if exp is None:
            collapsed[key] = actual
            continue

        if live_variables is not None and key in live_variables:
            try:
                expected_cv = ControlVariable(**exp)
            except ValidationError:
                expected_cv = None
            if expected_cv is not None:
                actual_full = live_variables[key].unstripped_dump()
                expected_full = expected_cv.unstripped_dump()
                override = {
                    k: v for k, v in actual_full.items() if expected_full.get(k) != v
                }
                if override:
                    collapsed[key] = override
                continue

        if actual == exp:
            continue  # fully covered by the schema, omit
        override = {k: v for k, v in actual.items() if exp.get(k) != v}
        if override:
            collapsed[key] = override

    resolved = {k: v for k, v in controls.items() if k != "variables"}
    if collapsed:
        resolved["variables"] = collapsed
    return resolved


def interpret_YAML_Element(
    elem: dict,
    exclude_set=None,
    base_dir: str | None = None,
    schema_map: dict | None = None,
    *,
    strict: bool = False,
    errors: list | None = None,
    filename: str | None = None,
):
    """Parse one raw element dict into its registered model class.

    Returns ``None`` when the element cannot be loaded. Every such failure
    is appended to ``errors`` as an :class:`ElementLoadError`; when
    ``strict`` the error is raised.
    """
    hw_type = elem.get("hardware_type")
    if not hw_type:
        name = elem.get("name", "<unknown>")
        _log.warning("Skipping element '%s': no hardware_type field", name)
        _record_load_failure(
            ElementLoadError(
                name, "no_hardware_type", "no hardware_type field", filename=filename
            ),
            errors,
            strict,
        )
        return None

    adapter = ADAPTERS.get(hw_type)
    if adapter is None:
        name = elem.get("name", "<unknown>")
        _log.warning(
            "Skipping element '%s': unregistered hardware_type '%s'", name, hw_type
        )
        _record_load_failure(
            ElementLoadError(
                name,
                "unregistered_hardware_type",
                f"unregistered hardware_type '{hw_type}'",
                hardware_type=hw_type,
                filename=filename,
            ),
            errors,
            strict,
        )
        return None

    controls = elem.get("controls")
    if isinstance(controls, dict) and controls.get("schema"):
        elem = {
            **elem,
            "controls": resolve_controls_schema(
                controls, elem.get("name", ""), base_dir, schema_map
            ),
        }

    if exclude_set:
        elem = {k: v for k, v in elem.items() if k not in exclude_set}

    try:
        result = adapter.validate_python(elem)
        _log.debug("Loaded %s (%s)", elem.get("name", "?"), hw_type)
        return result
    except Exception as exc:
        name = elem.get("name", "<unknown>")
        _log.error(
            "Failed to parse '%s' [%s]: %s",
            name,
            hw_type,
            exc,
        )
        _log.debug("Validation error detail for '%s':", name, exc_info=True)
        error = ElementLoadError(
            name, "validation_error", str(exc), hardware_type=hw_type, filename=filename
        )
        error.__cause__ = exc
        _record_load_failure(error, errors, strict)
        return None


def read_YAML_Element_File(
    filename: str,
    exclude_keys: List[str] | None = None,
    validate: bool = False,
    *,
    strict: bool = False,
    errors: list | None = None,
):
    """Read a single-element YAML file and return the parsed model.

    Parameters
    ----------
    filename:
        Path to the YAML file.
    exclude_keys:
        Top-level keys to strip before parsing (e.g., legacy fields).
    validate:
        When ``True``, validate the raw YAML dict against the LinkML-derived
        JSON Schema *before* Pydantic parsing.  Requires both the
        *jsonschema* package and a previously generated schema file.
    strict:
        When ``True``, raise :class:`ElementLoadError` instead of returning
        ``None`` for an element that cannot be loaded.
    errors:
        List to append each :class:`ElementLoadError` to, so a non-strict
        caller can see what was skipped.
    """
    exclude_set = set(exclude_keys) if exclude_keys else None
    with open(filename, "r") as stream:
        data = yaml.load(stream, Loader=Loader)
    if validate:
        validate_element_dict(data)
    return interpret_YAML_Element(
        data,
        exclude_set=exclude_set,
        base_dir=os.path.dirname(os.path.abspath(filename)),
        strict=strict,
        errors=errors,
        filename=filename,
    )


def read_YAML_Element_Files(filenames: list):
    data = ""
    for file in filenames:
        data += "\n---\n"
        with open(file, "r") as stream:
            data += stream.read()
    gen = list(yaml.load_all(data, Loader=Loader))
    return gen, filenames


def read_YAML_Combined_File(
    filename: str,
    exclude_keys=None,
    validate: bool = False,
    *,
    strict: bool = False,
    errors: list | None = None,
):
    """Read a combined (multi-element) YAML or JSON file and return parsed models.

    Parameters
    ----------
    filename:
        Path to the YAML or JSON file containing multiple element definitions.
    exclude_keys:
        Top-level keys to strip from each element before parsing.
    validate:
        When ``True``, validate each element dict against the LinkML-derived
        JSON Schema *before* Pydantic parsing.
    strict:
        When ``True``, raise :class:`ElementLoadError` on the first element
        that cannot be loaded, instead of skipping it.
    errors:
        List to append each :class:`ElementLoadError` to, so a non-strict
        caller can see what was skipped.
    """
    exclude_set = set(exclude_keys) if exclude_keys else None

    if ".yaml" in filename.lower():
        with open(filename, "r") as stream:
            elements = yaml.load(stream, Loader=Loader)
    elif ".json" in filename.lower():
        with open(filename, "r") as stream:
            elements = json.load(stream)

    if validate:
        for element in elements.values():
            validate_element_dict(element)

    schema_map = elements.pop(COMBINED_SCHEMAS_KEY, None)

    base_dir = os.path.dirname(os.path.abspath(filename))

    _log.debug("Parsing %d elements from '%s'", len(elements), filename)
    results = [
        interpret_YAML_Element(
            element,
            exclude_set,
            base_dir=base_dir,
            schema_map=schema_map,
            strict=strict,
            errors=errors,
            filename=filename,
        )
        for element in elements.values()
    ]
    loaded = sum(1 for r in results if r is not None)
    failed = len(results) - loaded
    _log.info(
        "Loaded %d/%d elements from '%s'%s",
        loaded,
        len(results),
        filename,
        f" ({failed} failed — enable DEBUG for details)" if failed else "",
    )
    return results
