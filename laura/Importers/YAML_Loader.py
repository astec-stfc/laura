from typing import List
import yaml
from yaml import CSafeLoader as Loader
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import os

from ..models.element import *  # noqa


def filter_top_level(elem: dict, exclude_keys: List[str] | None = None) -> dict:
    if isinstance(exclude_keys, list):
        return {k: v for k, v in elem.items() if k not in exclude_keys}
    return {k: v for k, v in elem.items()}

def interpret_YAML_Element(
        elem: dict,
        filename: str | None = None,
        exclude_keys: List[str] | None = None,
):
    if "hardware_type" not in elem:
        print("Missing hardware_type:", filename)
        return None

    hw_type = elem["hardware_type"]

    if hw_type not in globals():
        if filename:
            print("Unknown hardware_type:", filename)
        return None

    felem = globals()[hw_type]

    try:
        if isinstance(exclude_keys, list):
            filtered_elem = {k: v for k, v in elem.items() if k not in exclude_keys}
            return felem(**filtered_elem)
        return felem(**elem)

    except Exception as e:
        print("interpret_YAML_Element - Error", e, "with element:", elem.get("name"))
        return None

def load_and_interpret_yaml(filename, exclude_keys: List[str] | None = None):
    try:
        with open(filename, "r") as stream:
            data = yaml.load(stream, Loader=Loader)

        if exclude_keys:
            data = {k: v for k, v in data.items() if k not in exclude_keys}

        return interpret_YAML_Element(data, filename=filename)

    except Exception as e:
        print("Failed to load:", filename, e)
        return None

def load_elements_parallel(files, exclude_keys=None, max_workers=None):
    if max_workers is None:
        max_workers = os.cpu_count()
    worker = partial(load_and_interpret_yaml, exclude_keys=exclude_keys)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        elems = list(executor.map(worker, files))

    return [e for e in elems if e is not None]


def read_YAML_Element_File(filename: str, exclude_keys: List[str] | None = None):
    with open(filename, "r") as stream:
        data = yaml.load(stream, Loader=Loader)
    return interpret_YAML_Element(data, filename=filename, exclude_keys=exclude_keys)


def read_YAML_Element_Files(filenames: list):
    data = ""
    for file in filenames:
        data += "\n---\n"
        with open(file, "r") as stream:
            data += stream.read()
    gen = list(yaml.load_all(data, Loader=Loader))
    return gen, filenames


def read_YAML_Combined_File(filename: str, exclude_keys: List[str] | None = None):
    with open(filename, "r") as stream:
        elements = yaml.load(stream, Loader=Loader)
    return [interpret_YAML_Element(element, exclude_keys=exclude_keys) for element in elements.values()]
