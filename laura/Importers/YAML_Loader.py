import yaml
from yaml import CSafeLoader as Loader

from ..models.element import *  # noqa


def interpret_YAML_Element(elem: dict, filename: str | None = None):
    if "hardware_type" in elem and elem["hardware_type"] in globals():
        try:
            felem = globals()[elem["hardware_type"]]
            elemmodel = felem(**elem)
            return elemmodel
        except Exception as e:
            print("interpret_YAML_Element - Error", e, "with element:", elem["name"])
    else:
        if filename is not None:
            print("Could not interpret element:", filename)


def read_YAML_Element_File(filename):
    with open(filename, "r") as stream:
        data = yaml.load(stream, Loader=Loader)
    return interpret_YAML_Element(data, filename=filename)


def read_YAML_Element_Files(filenames: list):
    data = ""
    for file in filenames:
        data += "\n---\n"
        with open(file, "r") as stream:
            data += stream.read()
    gen = list(yaml.load_all(data, Loader=Loader))
    return gen, filenames


def read_YAML_Combined_File(filename):
    with open(filename, "r") as stream:
        elements = yaml.load(stream, Loader=Loader)
    return [interpret_YAML_Element(element) for element in elements.values()]
