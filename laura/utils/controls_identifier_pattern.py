"""
Second cleanup pass over a lattice already using `controls->schema` (see
`laura.utils.controls_schema_extract`): collapse per-variable `identifier`
overrides into a single `controls->identifier_pattern` wherever that's safe.

Some elements have `identifier`s that aren't actually prefixed with their own
name -- e.g. a diagnostic whose PVs are multiplexed through another unit's
electronics. After `controls_schema_extract`, that shows up as an explicit
`identifier` override on every affected variable. `identifier_pattern` (see
`laura.models.control.ControlsInformation.identifier_pattern`) lets a single
line substitute for all of them: whatever string it's set to replaces every
`{name}` in the schema, instead of the element's own name.

Safety rule -- `identifier_pattern` applies to the *whole* controls block,
not a single variable, so it is only introduced for an element if every
schema variable whose template contains `{name}` anywhere in a string field
is *already* overridden in that element, with values all consistent with one
substitution string. If even one such variable is left un-overridden (i.e.
still relying on the default own-name substitution), or the overrides imply
more than one distinct substitution, the element is left untouched --
otherwise turning on `identifier_pattern` would silently change a variable
that currently (correctly) resolves against the element's own name. This is
exactly why a BPM whose PVs are *partly* multiplexed through another unit and
*partly* its own (a mixed case) is correctly left with its per-variable
overrides rather than collapsed.

Usage:
    python -m laura.utils.controls_identifier_pattern <lattice_yaml_root> [--apply]

Without `--apply`, only prints what would change. Run once without `--apply`
and read the list before committing to `--apply` on real lattice data.
"""

import argparse
import copy
import os

import yaml
from yaml import CSafeLoader as Loader

from laura.Importers.YAML_Loader import get_controls_schema_variables


def _find_name_dependent_leaves(template, path=()):
    """Yield `(path, template_string)` for every string leaf in a schema
    variable's template dict/list that contains the `{name}` placeholder."""
    if isinstance(template, str):
        if "{name}" in template:
            yield path, template
    elif isinstance(template, dict):
        for k, v in template.items():
            yield from _find_name_dependent_leaves(v, path + (k,))
    elif isinstance(template, list):
        for i, v in enumerate(template):
            yield from _find_name_dependent_leaves(v, path + (i,))


def _get_by_path(d, path):
    cur = d
    for p in path:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        elif isinstance(cur, list) and isinstance(p, int) and 0 <= p < len(cur):
            cur = cur[p]
        else:
            return None, False
    return cur, True


def _del_by_path(d, path):
    if len(path) == 1:
        d.pop(path[0], None)
        return
    parent, ok = _get_by_path(d, path[:-1])
    if ok and isinstance(parent, dict):
        parent.pop(path[-1], None)


def _derive_pattern(template_str: str, actual_str: str):
    """If `template_str` has exactly one `{name}`, solve for what substituting
    it with `actual_str` requires; `None` if not solvable (0 or >1
    occurrences, or `actual_str` doesn't fit the template's fixed
    prefix/suffix around the placeholder)."""
    if template_str.count("{name}") != 1:
        return None
    prefix, suffix = template_str.split("{name}")
    if not actual_str.startswith(prefix) or not actual_str.endswith(suffix):
        return None
    core = actual_str[len(prefix): len(actual_str) - len(suffix) if suffix else None]
    if "{name}" in core:
        return None
    return core


def plan_identifier_pattern(data: dict, base_dir: str) -> tuple | None:
    """
    Check whether `data` (a parsed element, already using `controls.schema`)
    can safely have its per-variable `identifier` overrides collapsed into a
    single `controls.identifier_pattern`.

    Returns `(pattern, leaf_plan)` if so -- where `leaf_plan` is a list of
    `(var_key, path)` identifying exactly which override fields become
    redundant -- or `None` if unsafe or there is nothing to gain (see module
    docstring for the safety rule).
    """
    controls = data.get("controls")
    if not isinstance(controls, dict) or not controls.get("schema"):
        return None
    if controls.get("identifier_pattern"):
        return None  # already using it

    schema_variables = get_controls_schema_variables(controls["schema"], base_dir)
    overrides = controls.get("variables") or {}

    name_dependent_keys = {
        var_key: list(_find_name_dependent_leaves(var_def))
        for var_key, var_def in schema_variables.items()
        if list(_find_name_dependent_leaves(var_def))
    }
    if not name_dependent_keys:
        return None

    candidate_patterns = set()
    leaf_plan = []
    for var_key, leaves in name_dependent_keys.items():
        override = overrides.get(var_key)
        if not isinstance(override, dict):
            return None  # relies on default own-name substitution -- unsafe
        for path, template_str in leaves:
            actual, present = _get_by_path(override, path)
            if not present or not isinstance(actual, str):
                return None  # this leaf isn't overridden -- unsafe
            pattern = _derive_pattern(template_str, actual)
            if pattern is None:
                return None  # not a single consistent substitution -- unsafe
            candidate_patterns.add(pattern)
            leaf_plan.append((var_key, path))

    if len(candidate_patterns) != 1:
        return None  # multiple different foreign prefixes -- can't unify
    pattern = next(iter(candidate_patterns))
    if pattern == data["name"]:
        return None  # already matches the element's own name -- no gain
    return pattern, leaf_plan


def apply_identifier_pattern(data: dict, pattern: str, leaf_plan: list) -> dict:
    """Return a copy of `data` with `identifier_pattern` set and the
    now-redundant override fields in `leaf_plan` removed (dropping a variable
    override entirely if it becomes empty, and `variables` entirely if every
    override does)."""
    data = copy.deepcopy(data)
    controls = data["controls"]
    controls["identifier_pattern"] = pattern
    variables = controls["variables"]
    for var_key, path in leaf_plan:
        _del_by_path(variables[var_key], path)
        if not variables[var_key]:
            variables.pop(var_key)
    if not variables:
        controls.pop("variables", None)
    return data


def collapse_identifier_patterns(root: str, apply: bool = False) -> list:
    """
    Walk every element YAML file under `root` and, where safe (see
    `plan_identifier_pattern`), collapse its per-variable `identifier`
    overrides into a single `controls.identifier_pattern`.

    With `apply=False` (the default), nothing is written.

    Returns a list of `(relative_path, element_name, pattern, keys_touched)`
    describing what was (or would be) changed.
    """
    if not os.path.isdir(root):
        # os.walk silently yields nothing for a bad path, which would
        # otherwise look identical to "nothing here needs collapsing".
        raise NotADirectoryError(f"root '{root}' is not a directory")

    changes = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.startswith("_") or not fn.endswith(".yaml"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path) as fh:
                data = yaml.load(fh, Loader=Loader)
            if not isinstance(data, dict) or "hardware_type" not in data:
                continue

            try:
                result = plan_identifier_pattern(data, dirpath)
            except FileNotFoundError:
                continue  # schema not found here -- leave untouched
            if result is None:
                continue
            pattern, leaf_plan = result
            keys_touched = sorted({var_key for var_key, _ in leaf_plan})
            changes.append((os.path.relpath(path, root), data["name"], pattern, keys_touched))

            if apply:
                new_data = apply_identifier_pattern(data, pattern, leaf_plan)
                with open(path, "w") as fh:
                    yaml.safe_dump(new_data, fh, sort_keys=True, default_flow_style=False)
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Root directory of the lattice's element YAML files")
    parser.add_argument(
        "--apply", action="store_true", help="Write changes (default: print a plan only)"
    )
    args = parser.parse_args()

    try:
        changes = collapse_identifier_patterns(args.root, apply=args.apply)
    except NotADirectoryError as exc:
        parser.error(str(exc))
    for rel_path, name, pattern, keys_touched in changes:
        print(f"{rel_path}: name={name} -> identifier_pattern={pattern!r} (keys: {keys_touched})")
    verb = "Applied" if args.apply else "Would apply"
    print(f"\n{verb} identifier_pattern to {len(changes)} elements")


if __name__ == "__main__":
    main()
