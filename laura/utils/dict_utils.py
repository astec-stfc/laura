"""
Dictionary and YAML utilities for LAURA models.

Flattening nested dicts, numpy scalar conversion and YAML representers.
"""

from collections.abc import MutableMapping
from typing import Dict

import numpy as np
import yaml

_LEAVES = (str, int, float, list, tuple, type(None), np.ndarray)


def flatten_dict(dictionary: Dict, parent_key: str = "", separator: str = "_") -> Dict:
    """
    Flatten a nested dictionary into a single level.

    Example:
        >>> flatten_dict({'a': {'b': 1, 'c': 2}})
        {'a_b': 1, 'a_c': 2}

    Args:
        dictionary: Dictionary to flatten
        parent_key: Base key prefix (used in recursion)
        separator: Separator between key levels

    Returns:
        Flattened dictionary
    """
    flat = {}
    for key, value in dictionary.items():
        if isinstance(key, str):
            new_key = parent_key + separator + key if parent_key else key
            if isinstance(value, dict) or (
                not isinstance(value, _LEAVES) and isinstance(value, MutableMapping)
            ):
                flat.update(flatten_dict(value, new_key, separator=separator))
            else:
                flat[new_key] = value
    return flat


def numpy_scalar_to_python(v):
    """Convert a numpy scalar to its native Python type; return `v` unchanged otherwise."""
    if isinstance(v, (np.float64, np.float32, np.float16)):
        return float(v)
    if isinstance(
        v,
        (
            np.int_,
            np.intc,
            np.intp,
            np.int8,
            np.int16,
            np.int32,
            np.int64,
            np.uint8,
            np.uint16,
            np.uint32,
            np.uint64,
        ),
    ):
        return int(v)
    return v


class StringWithQuotes(str):
    """String that will be represented with quotes in YAML output."""

    pass


class FlowList(list):
    """List that will be represented as a flow sequence in YAML output."""

    pass


def _quoted_presenter(dumper, data):
    """YAML representer for StringWithQuotes."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


def _flow_list_representer(dumper, data):
    """YAML representer for FlowList."""
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


# Register custom YAML representers
yaml.add_representer(StringWithQuotes, _quoted_presenter)
yaml.add_representer(FlowList, _flow_list_representer)
