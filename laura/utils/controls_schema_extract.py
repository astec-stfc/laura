"""
Extract a shared `controls->schema` template from a set of element YAML
files, and rewrite them to reference it plus their per-element overrides.

Elements of the same hardware type (e.g. every Quadrupole) typically define
near-identical `controls.variables` blocks, differing mainly in the
element's own name embedded in each `identifier`. This module finds, for
each (hardware_class, hardware_type) directory in a lattice tree, the
variable keys that really are shared across (nearly) every element there,
writes them out once as a `_schema.yaml` template (with the element's name
replaced by a `{name}` placeholder), and rewrites each element file down to
`controls: {schema: ..., variables: {<only the genuine per-element
overrides>}}`. See `laura.models.control.ControlsInformation` and
`laura.Importers.YAML_Loader.resolve_controls_schema` for how that reference
is expanded again when an element is loaded.

Elements sharing the same variable keyset but only ever using some of them
identically (`keyset` groups) are handled as a separate schema variant, so a
hardware type with two distinct control interfaces (e.g. a Screen that is
sometimes a single-axis unit and sometimes an H/V pair) gets one schema file
per shape rather than being forced into one.

Safety rule -- a variable key is only folded into the shared schema if every
element in its group has that key with *at least* the same fields as the
majority definition. A field may be added or have a different value (those
become per-element overrides), but never be *missing* relative to the
majority: `resolve_controls_schema`'s merge can only add or replace fields on
top of the schema, never remove one, so an element genuinely missing a field
the rest of the group has cannot be expressed as an override. Any variable
key that fails this check for even one element is left fully inline,
untouched, for every member of the group -- this is reported back as a
"kept inline" / outlier key, and is worth a manual look (it usually means
either a real per-element hardware difference, or a stray inconsistency in
the source data).

Usage:
    python -m laura.utils.controls_schema_extract <lattice_yaml_root> [--apply]

Without `--apply`, only a plan is printed (schema files and outlier keys that
would result, files that would be rewritten, and how much duplication is
removed) -- nothing is written. Run once without `--apply` first and read the
"kept inline" keys before committing to `--apply` on real lattice data.
"""

import argparse
import copy
import json
import os
from collections import Counter, defaultdict

import yaml
from yaml import CSafeLoader as Loader


def substitute_name_to_placeholder(value, name: str):
    """Inverse of `laura.Importers.YAML_Loader._substitute_schema_placeholders`:
    replace an element's own name with the `{name}` template placeholder,
    recursively through nested dicts/lists."""
    if isinstance(value, str):
        return value.replace(name, "{name}")
    if isinstance(value, dict):
        return {k: substitute_name_to_placeholder(v, name) for k, v in value.items()}
    if isinstance(value, list):
        return [substitute_name_to_placeholder(v, name) for v in value]
    return value


def _canon(value) -> str:
    return json.dumps(value, sort_keys=True)


def find_element_files(root: str):
    """Yield every YAML file under `root`, skipping underscore-prefixed files
    (schema templates, e.g. `_schema.yaml`) which are not elements."""
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.startswith("_"):
                continue
            if fn.endswith(".yaml") or fn.endswith(".yml"):
                yield os.path.join(dirpath, fn)


def load_controls_group(files):
    """Parse `files` and return `(path, data)` for those that are elements
    with an inline (not already schema-referencing) `controls.variables`
    block."""
    items = []
    for f in files:
        with open(f) as fh:
            data = yaml.load(fh, Loader=Loader)
        if not isinstance(data, dict) or "hardware_type" not in data:
            continue
        controls = data.get("controls")
        if not isinstance(controls, dict) or not controls.get("variables"):
            continue
        if controls.get("schema"):
            continue
        items.append((f, data))
    return items


def plan_schema_for_keyset_group(members):
    """
    `members`: a list of `(path, data)` all sharing the same set of
    `controls.variables` keys.

    Returns `(schema_variables, per_file_overrides, outlier_keys)`, or `None`
    if no key in this group is safe to share via a schema. `schema_variables`
    is the `{name}`-templated dict to write as the schema file;
    `per_file_overrides` is `{path: {var_key: override_fields}}`;
    `outlier_keys` is the set of variable keys that failed the safety check
    (see module docstring) and so are left fully inline for every member.
    """
    keyset = frozenset(members[0][1]["controls"]["variables"].keys())

    templated_by_key = defaultdict(dict)  # var_key -> {path: templated_dict}
    original_by_key = defaultdict(dict)   # var_key -> {path: literal, as-written dict}
    for path, data in members:
        name = data["name"]
        for var_key in keyset:
            original = data["controls"]["variables"][var_key]
            original_by_key[var_key][path] = original
            templated_by_key[var_key][path] = substitute_name_to_placeholder(original, name)

    schema_variables = {}
    outlier_keys = set()
    per_file_overrides = defaultdict(dict)

    for var_key, by_path in templated_by_key.items():
        counts = Counter(_canon(v) for v in by_path.values())
        majority_canon, _majority_count = counts.most_common(1)[0]
        majority = json.loads(majority_canon)

        missing_relative_to_majority = any(
            set(majority.keys()) - set(val.keys()) for val in by_path.values()
        )
        if missing_relative_to_majority:
            outlier_keys.add(var_key)
            continue

        schema_variables[var_key] = majority
        for path, templated_val in by_path.items():
            if templated_val == majority:
                continue
            # Diff on the templated form (so a difference that's purely the
            # element's own name doesn't count), but take the override's
            # actual values from the literal, as-written dict -- overrides
            # are not placeholder-substituted at load time, so they must
            # never contain a literal "{name}".
            literal = original_by_key[var_key][path]
            override = {
                k: literal[k] for k in templated_val if majority.get(k) != templated_val[k]
            }
            per_file_overrides[path][var_key] = override

    if not schema_variables:
        return None
    return schema_variables, per_file_overrides, outlier_keys


def _process_directory(dirpath: str, files, apply_changes: bool, report: dict):
    items = load_controls_group(files)
    if len(items) < 2:
        return  # nothing to deduplicate

    by_keyset = defaultdict(list)
    for path, data in items:
        by_keyset[frozenset(data["controls"]["variables"].keys())].append((path, data))

    # Largest group first, so the most common shape becomes `_schema.yaml`
    # and any secondary shapes get a numbered suffix.
    ordered_groups = sorted(by_keyset.values(), key=len, reverse=True)

    variant_index = 0
    for group in ordered_groups:
        if len(group) < 2:
            continue  # a shape used by only one element -- nothing to share
        result = plan_schema_for_keyset_group(group)
        if result is None:
            continue
        schema_variables, per_file_overrides, outlier_keys = result

        variant_index += 1
        schema_filename = "_schema.yaml" if variant_index == 1 else f"_schema_{variant_index}.yaml"
        schema_path = os.path.join(dirpath, schema_filename)
        report["schema_files"].append(
            (schema_path, len(group), sorted(schema_variables), sorted(outlier_keys))
        )
        if apply_changes:
            with open(schema_path, "w") as fh:
                yaml.safe_dump(
                    {"variables": schema_variables}, fh, sort_keys=True, default_flow_style=False
                )

        for path, data in group:
            overrides = per_file_overrides.get(path, {})
            new_variables = {}
            for var_key in data["controls"]["variables"]:
                if var_key in outlier_keys:
                    new_variables[var_key] = data["controls"]["variables"][var_key]
                elif var_key in overrides:
                    new_variables[var_key] = overrides[var_key]
                # else: fully covered by the schema, omit.

            new_controls = {k: v for k, v in data["controls"].items() if k != "variables"}
            new_controls["schema"] = schema_filename
            if new_variables:
                new_controls["variables"] = new_variables

            report["files_rewritten"].append(
                (path, len(new_variables), len(data["controls"]["variables"]))
            )
            if apply_changes:
                data = copy.deepcopy(data)
                data["controls"] = new_controls
                with open(path, "w") as fh:
                    yaml.safe_dump(data, fh, sort_keys=True, default_flow_style=False)


def extract_schemas(root: str, apply: bool = False) -> dict:
    """
    Walk every (hardware_class, hardware_type) directory under `root` and
    fold their elements' shared `controls.variables` into a `_schema.yaml`
    per directory (per distinct variable-keyset "shape", if more than one is
    found), rewriting each element to `{schema, variables: <overrides>}`.

    With `apply=False` (the default), nothing is written -- only the report
    is returned, describing what *would* happen.

    Returns a report dict:
        {
            "schema_files": [(path, n_elements, shared_keys, outlier_keys), ...],
            "files_rewritten": [(path, n_variables_left_inline, n_variables_before), ...],
        }
    """
    report = {"schema_files": [], "files_rewritten": []}
    by_directory = defaultdict(list)
    for path in find_element_files(root):
        by_directory[os.path.dirname(path)].append(path)

    for dirpath, files in sorted(by_directory.items()):
        _process_directory(dirpath, files, apply, report)
    return report


def print_report(report: dict, applied: bool) -> None:
    print(f"Schema files {'written' if applied else 'planned'}: {len(report['schema_files'])}")
    for path, n_elements, shared_keys, outlier_keys in report["schema_files"]:
        print(f"  {path}  ({n_elements} elements, {len(shared_keys)} shared keys, "
              f"{len(outlier_keys)} kept-inline keys)")
        if outlier_keys:
            print(f"      kept inline (unsafe to share): {outlier_keys}")

    n_files = len(report["files_rewritten"])
    total_before = sum(before for _, _, before in report["files_rewritten"])
    total_after = sum(after for _, after, _ in report["files_rewritten"])
    print(f"\nElement files {'rewritten' if applied else 'to be rewritten'}: {n_files}")
    print(f"  total variable entries before: {total_before}")
    print(f"  total variable entries left inline after (overrides + outlier keys): {total_after}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Root directory of the lattice's element YAML files")
    parser.add_argument(
        "--apply", action="store_true", help="Write changes (default: print a plan only)"
    )
    args = parser.parse_args()

    report = extract_schemas(args.root, apply=args.apply)
    print_report(report, applied=args.apply)


if __name__ == "__main__":
    main()
