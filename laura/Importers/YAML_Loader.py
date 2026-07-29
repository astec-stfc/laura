import re
from typing import List
import json
import logging
import yaml
import os
import pathlib
import functools
from yaml import CSafeLoader as Loader
from pydantic import TypeAdapter, BaseModel
from typing import List

# Import elements before building registry
from ..models.element import ELEMENT_REGISTRY

_log = logging.getLogger("laura.loader")

# Fast metadata extraction regex
_NAME_RE = re.compile(r'^\s*name:\s*["\'\s]?([^"\'\s#\n]+)["\'\s]?', re.MULTILINE)
_AREA_RE = re.compile(r'^\s*machine_area:\s*["\'\s]?([^"\'\s#\n]+)["\'\s]?', re.MULTILINE)

def fast_get_element_metadata(filename: str) -> dict:
    """Quickly extract metadata from a YAML file without full parsing."""
    metadata = {"name": None, "machine_area": None}
    try:
        with open(filename, 'r') as f:
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
        metadata["name"] = os.path.basename(filename).replace('.yaml', '').replace('.yml', '')
    return metadata


class LazyElementDict(dict):
    """
    Dictionary that loads elements from YAML files only when accessed.
    """
    def __init__(self, filenames, exclude_keys=None):
        # Initialise with keys but None values to satisfy tools that check keys()
        super().__init__({k: None for k in filenames.keys()})
        self._filenames = filenames  # Map of name: filename
        self._exclude_keys = exclude_keys
        self._metadata_cache = {}

    def get_metadata(self, name):
        """Quickly get name/area without loading model."""
        if self.is_loaded(name):
            elem = super().__getitem__(name)
            if elem is None:
                return None
            return {"name": elem.name, "machine_area": getattr(elem, "machine_area", None)}
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
        """Check if an element has already been loaded via interpret_YAML_Element."""
        return super().__contains__(name)

    def __getitem__(self, key):
        if super().__contains__(key):
            val = super().__getitem__(key)
            if val is not None:
                return val
        if key in self._filenames:
            # Only load when needed
            elem = read_YAML_Element_File(self._filenames[key], exclude_keys=self._exclude_keys)
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
        # We MUST return the full models if someone calls .values() 
        # but we can detect if it's MachineModel building indexes and return stubs instead
        # However, it's safer to just let indexing call its own metadata lookup.
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

def interpret_YAML_Element(elem: dict, exclude_set=None):
    hw_type = elem.get("hardware_type")
    if not hw_type:
        name = elem.get("name", "<unknown>")
        _log.warning("Skipping element '%s': no hardware_type field", name)
        return None

    adapter = ADAPTERS.get(hw_type)
    if adapter is None:
        name = elem.get("name", "<unknown>")
        _log.warning("Skipping element '%s': unregistered hardware_type '%s'", name, hw_type)
        return None

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
            name, hw_type, exc,
        )
        _log.debug("Validation error detail for '%s':", name, exc_info=True)
        return None


def read_YAML_Element_File(
    filename: str,
    exclude_keys: List[str] | None = None,
    validate: bool = False,
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
    """
    exclude_set = set(exclude_keys) if exclude_keys else None
    with open(filename, "r") as stream:
        data = yaml.load(stream, Loader=Loader)
    if validate:
        validate_element_dict(data)
    return interpret_YAML_Element(data, exclude_set=exclude_set)


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

    _log.debug("Parsing %d elements from '%s'", len(elements), filename)
    results = [
        interpret_YAML_Element(element, exclude_set)
        for element in elements.values()
    ]
    loaded = sum(1 for r in results if r is not None)
    failed = len(results) - loaded
    _log.info(
        "Loaded %d/%d elements from '%s'%s",
        loaded, len(results), filename,
        f" ({failed} failed — enable DEBUG for details)" if failed else "",
    )
    return results
