import re
import json
from pprint import pprint
from warnings import warn
from yaml import CSafeLoader as Loader
from pydantic import TypeAdapter, ValidationError

# Import elements before building registry
from ..models.element import *  # noqa

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

ALL_MODELS = get_all_subclasses(BaseModel)

MODEL_REGISTRY = {
    cls.__name__: cls
    for cls in ALL_MODELS
}

class LazyAdapterDict(dict):
    """
    Lazy lookup of TypeAdapters to avoid initializing all 100+ adapters on import.
    """
    def get(self, key, default=None):
        if key not in self:
            model = MODEL_REGISTRY.get(key)
            if model is None:
                return default
            self[key] = TypeAdapter(model)
        return super().get(key)

ADAPTERS = LazyAdapterDict()

def filter_top_level(elem: dict, exclude_keys: List[str] | None = None) -> dict:
    if isinstance(exclude_keys, list):
        return {k: v for k, v in elem.items() if k not in exclude_keys}
    return {k: v for k, v in elem.items()}

def interpret_YAML_Element(elem: dict, exclude_set=None):
    hw_type = elem.get("hardware_type")
    if not hw_type:
        warn(f"hardware_type not found in element {elem.get('name', 'unknown')}; returning None")
        return None

    adapter = ADAPTERS.get(hw_type)
    if adapter is None:
        warn(f"adapter not found in element {elem.get('name', 'unknown')}; returning None")
        return None

    if exclude_set:
        elem = {k: v for k, v in elem.items() if k not in exclude_set}

    try:
        return adapter.validate_python(elem)
    except ValidationError as e:
        pprint(e.errors(), width=200)
    warn(f"Could not interpret {elem.get('name', 'unknown')}; returning None")
    return None


def read_YAML_Element_File(filename: str, exclude_keys: List[str] | None = None):
    exclude_set = set(exclude_keys) if exclude_keys else None
    with open(filename, "r") as stream:
        data = yaml.load(stream, Loader=Loader)
    return interpret_YAML_Element(data, exclude_set=exclude_set)


def read_YAML_Element_Files(filenames: list):
    data = ""
    for file in filenames:
        data += "\n---\n"
        with open(file, "r") as stream:
            data += stream.read()
    gen = list(yaml.load_all(data, Loader=Loader))
    return gen, filenames


def read_YAML_Combined_File(filename: str, exclude_keys=None):
    exclude_set = set(exclude_keys) if exclude_keys else None

    if ".yaml" in filename.lower():
        with open(filename, "r") as stream:
            elements = yaml.load(stream, Loader=Loader)
    elif ".json" in filename.lower():
        with open(filename, "r") as stream:
            elements = json.load(stream)

    return [
        interpret_YAML_Element(element, exclude_set)
        for element in elements.values()
    ]
