import json
import yaml
from yaml import CSafeLoader as Loader
from pydantic import TypeAdapter

from ..models.element import *  # noqa

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

ADAPTERS = {
    name: TypeAdapter(model)
    for name, model in MODEL_REGISTRY.items()
}

def filter_top_level(elem: dict, exclude_keys: List[str] | None = None) -> dict:
    if isinstance(exclude_keys, list):
        return {k: v for k, v in elem.items() if k not in exclude_keys}
    return {k: v for k, v in elem.items()}

def interpret_YAML_Element(elem: dict, exclude_set=None):
    hw_type = elem.get("hardware_type")
    if not hw_type:
        return None

    adapter = ADAPTERS.get(hw_type)
    if adapter is None:
        return None

    if exclude_set:
        elem = {k: v for k, v in elem.items() if k not in exclude_set}

    try:
        return adapter.validate_python(elem)
    except Exception:
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
