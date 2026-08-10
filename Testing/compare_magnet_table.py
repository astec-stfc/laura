import sys
import os
import argparse
import numpy as np
from copy import deepcopy

# Add root to sys.path to allow imports from laura package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from laura.laura import LAURA
from laura.Importers.Magnet_Table import (
    add_magnet_table_parameters,
    magnet_table,
    magnet_table_filename,
)
from laura.Exporters.YAML import export_as_yaml

ZERO_LSC = "0,0,0,0,0,0,0"


def compare_coeffs(c1, c2, tol=1e-9):
    """Compare linear saturation coefficients."""
    keys = ["m", "I_max", "f", "a", "I0", "d", "L"]
    diffs = {}
    for k in keys:
        v1 = getattr(c1, k)
        v2 = getattr(c2, k)
        if abs(v1 - v2) > tol:
            diffs[k] = (v1, v2)
    return diffs


def lsc_is_nonzero(lsc):
    """Return True if any LSC coefficient is non-zero."""
    return any(getattr(lsc, k) != 0 for k in ["m", "I_max", "f", "a", "I0", "d", "L"])


def compare_and_report(name, elem, proposed_elem, header_width):
    """Compare original elem vs proposed and print diffs. Returns True if diffs found."""
    orig_coeffs = elem.magnetic.linear_saturation_coefficients
    orig_degauss = (
        list(elem.degauss.values)
        if hasattr(elem, "degauss") and elem.degauss is not None
        else []
    )
    orig_serial = (
        elem.manufacturer.serial_number
        if hasattr(elem, "manufacturer") and elem.manufacturer is not None
        else ""
    )
    orig_maxI = (
        elem.electrical.maxI
        if hasattr(elem, "electrical") and elem.electrical is not None
        else 0.0
    )

    has_diff = False

    # 1. Compare coefficients
    coeff_diffs = compare_coeffs(
        orig_coeffs, proposed_elem.magnetic.linear_saturation_coefficients
    )
    if coeff_diffs:
        has_diff = True
        for k, (v_old, v_new) in coeff_diffs.items():
            print(f"{name:<30} | {k:<10} | {v_old:<20g} | {v_new:<20g}")

    # 2. Compare serial number
    if (
        hasattr(proposed_elem, "manufacturer")
        and proposed_elem.manufacturer is not None
    ):
        if str(orig_serial) != str(proposed_elem.manufacturer.serial_number):
            has_diff = True
            print(
                f"{name:<30} | {'serial':<10} | {str(orig_serial):<20} | {str(proposed_elem.manufacturer.serial_number):<20}"
            )

    # 3. Compare max current
    if hasattr(proposed_elem, "electrical") and proposed_elem.electrical is not None:
        if abs(orig_maxI - proposed_elem.electrical.maxI) > 1e-6:
            has_diff = True
            print(
                f"{name:<30} | {'maxI':<10} | {orig_maxI:<20g} | {proposed_elem.electrical.maxI:<20g}"
            )

    # 4. Compare degauss values
    if hasattr(proposed_elem, "degauss") and proposed_elem.degauss is not None:
        proposed_degauss = list(proposed_elem.degauss.values)
        if len(orig_degauss) != len(proposed_degauss) or not np.allclose(
            orig_degauss, proposed_degauss, atol=1e-2
        ):
            has_diff = True
            print(
                f"{name:<30} | {'degauss':<10} | {str(orig_degauss[:2])}... | {str(proposed_degauss[:2])}..."
            )

    return has_diff


def compare_positions(name, child_phys, parent_phys):
    """Compare physical position fields. Returns True if diffs found."""
    has_diff = False
    for field in ["middle", "datum"]:
        child_val = getattr(child_phys, field, None)
        parent_val = getattr(parent_phys, field, None)
        if child_val is None or parent_val is None:
            continue
        if list(child_val) != list(parent_val):
            has_diff = True
            print(
                f"{name:<30} | {field:<10} | {str(list(child_val)):<20} | {str(list(parent_val)):<20}"
            )
    if hasattr(child_phys, "length") and hasattr(parent_phys, "length"):
        if abs(child_phys.length - parent_phys.length) > 1e-9:
            has_diff = True
            print(
                f"{name:<30} | {'length':<10} | {child_phys.length:<20g} | {parent_phys.length:<20g}"
            )
    child_rot = getattr(child_phys, "rotation", None)
    parent_rot = getattr(parent_phys, "rotation", None)
    if child_rot is not None and parent_rot is not None:
        if list(child_rot) != list(parent_rot):
            has_diff = True
            print(
                f"{name:<30} | {'rotation':<10} | {str(list(child_rot)):<20} | {str(list(parent_rot)):<20}"
            )
    return has_diff


def update_element(elem, yaml_abs_path, updated_files):
    """Write a proposed element to its YAML file."""
    rel_path = elem.YAML_filename
    target_path = os.path.join(yaml_abs_path, rel_path)
    print(f"  -> Updating {target_path}...")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    export_as_yaml(target_path, elem)
    updated_files.add(target_path)


def copy_physical(source_phys, dest_phys):
    """Copy stored position data from source to dest physical model."""
    for field in ["middle", "datum"]:
        src = getattr(source_phys, field, None)
        if src is not None:
            dst = getattr(dest_phys, field)
            dst.x = src.x
            dst.y = src.y
            dst.z = src.z
    if hasattr(source_phys, "length"):
        dest_phys.length = source_phys.length
    src_rot = getattr(source_phys, "rotation", None)
    if src_rot is not None:
        dst_rot = getattr(dest_phys, "rotation", None)
        if dst_rot is not None:
            dst_rot.phi = src_rot.phi
            dst_rot.psi = src_rot.psi
            dst_rot.theta = src_rot.theta


def main():
    parser = argparse.ArgumentParser(
        description="Compare Magnet Table with YAML lattice for CLARA (laura-lattices)"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update YAML files with values from Excel",
    )
    parser.add_argument(
        "--yaml_dir",
        default=None,
        help="Path to YAML directory (default: laura-lattices CLARA/YAML)",
    )
    parser.add_argument("--excel", help="Path to alternative Magnet Table Excel file")
    args = parser.parse_args()

    # If an alternative Excel file is provided, reload the magnet_table
    global magnet_table
    if args.excel:
        if not os.path.exists(args.excel):
            print(f"Error: Excel file not found at {args.excel}")
            return
        print(f"Loading alternative magnet table from {args.excel}...")
        try:
            import pandas
        except ImportError as _err:
            raise ImportError(
                "pandas is not installed. "
                "Install with: pip install pandas"
            ) from _err
        import laura.Importers.Magnet_Table as mt

        mt.magnet_table = pandas.read_excel(
            args.excel,
            sheet_name="Table",
            skiprows=2,
            index_col=(2, 3, 5, 6),
            dtype={"serial number": "str"},
        ).fillna(0)
        magnet_table = mt.magnet_table
    else:
        print(f"Using magnet table from: {magnet_table_filename}")

    # Load the CLARA lattice via laura-lattices
    try:
        import laura_lattices.CLARA as CLARA
    except ImportError:
        print("Error: laura_lattices package not found. Install it with:")
        print("  pip install -e path/to/laura-lattices")
        return

    # Determine YAML directory
    if args.yaml_dir:
        yaml_abs_path = os.path.abspath(args.yaml_dir)
    else:
        yaml_abs_path = os.path.dirname(CLARA.element_list)

    print(f"Loading lattice from {yaml_abs_path}...")

    try:
        machine = LAURA(lattice=CLARA)
    except Exception as e:
        print(f"Error loading machine: {e}")
        return

    magnets_checked = 0
    diffs_found = 0
    updated_files = set()

    # Track HCOR/VCOR elements already handled via their parent HVCOR
    handled_via_hvcor = set()

    header = f"{'Magnet Name':<30} | {'Field':<10} | {'YAML Value':<20} | {'Excel Value':<20}"
    print("\n" + header)
    print("-" * len(header))

    for name, elem in machine.elements.items():
        # Only process elements that have magnetic data with LSC
        if not hasattr(elem, "magnetic") or elem.magnetic is None:
            continue
        if elem.magnetic.linear_saturation_coefficients is None:
            continue

        # Skip HCOR/VCOR elements that were already processed via their parent HVCOR
        if name in handled_via_hvcor:
            continue

        magnets_checked += 1

        # --- HVCOR special handling ---
        is_hvcor = (
            getattr(elem, "hardware_type", None) == "Combined_Corrector"
            and getattr(elem, "Horizontal_Corrector", None) is not None
            and getattr(elem, "Vertical_Corrector", None) is not None
            and (elem.Horizontal_Corrector != name or elem.Vertical_Corrector != name)
        )
        if is_hvcor:
            hvcor_has_diff = False

            # (a) HVCOR should have zeroed LSC — flag if non-zero
            if lsc_is_nonzero(elem.magnetic.linear_saturation_coefficients):
                hvcor_has_diff = True
                lsc = elem.magnetic.linear_saturation_coefficients
                for k in ["m", "I_max", "f", "a", "I0", "d", "L"]:
                    v = getattr(lsc, k)
                    if v != 0:
                        print(f"{name:<30} | {k:<10} | {v:<20g} | {'0 (HVCOR)':<20}")

            # (b) Update child HCOR/VCOR from the magnet table
            for child_attr in ["Horizontal_Corrector", "Vertical_Corrector"]:
                child_name = getattr(elem, child_attr, None)
                if not child_name or child_name not in machine.elements:
                    continue
                child_elem = machine.elements[child_name]
                handled_via_hvcor.add(child_name)
                magnets_checked += 1

                if not hasattr(child_elem, "magnetic") or child_elem.magnetic is None:
                    continue
                if child_elem.magnetic.linear_saturation_coefficients is None:
                    continue

                proposed_child = deepcopy(child_elem)
                try:
                    add_magnet_table_parameters(child_name, proposed_child, child_name)
                except Exception:
                    continue

                child_has_diff = compare_and_report(
                    child_name, child_elem, proposed_child, len(header)
                )

                # (c) Compare position data — child should match parent HVCOR
                if (
                    hasattr(elem, "physical")
                    and elem.physical is not None
                    and hasattr(child_elem, "physical")
                    and child_elem.physical is not None
                ):
                    pos_diff = compare_positions(
                        child_name, child_elem.physical, elem.physical
                    )
                    if pos_diff:
                        child_has_diff = True
                        # Copy parent position to proposed child
                        copy_physical(elem.physical, proposed_child.physical)

                if child_has_diff:
                    diffs_found += 1
                    if args.update:
                        update_element(proposed_child, yaml_abs_path, updated_files)

            # Update HVCOR itself if its LSC was non-zero
            if hvcor_has_diff:
                diffs_found += 1
                if args.update:
                    proposed_hvcor = deepcopy(elem)
                    proposed_hvcor.magnetic.linear_saturation_coefficients.update_from_string(
                        ZERO_LSC
                    )
                    update_element(proposed_hvcor, yaml_abs_path, updated_files)

            continue

        # --- Normal magnet handling ---
        proposed_elem = deepcopy(elem)
        try:
            add_magnet_table_parameters(name, proposed_elem, name)
        except Exception:
            continue

        magnet_has_diff = compare_and_report(name, elem, proposed_elem, len(header))

        if magnet_has_diff:
            diffs_found += 1
            if args.update:
                update_element(proposed_elem, yaml_abs_path, updated_files)

    print("-" * len(header))
    print(f"Checked {magnets_checked} magnets.")
    print(f"Found differences in {diffs_found} magnets.")
    if args.update:
        print(f"Updated {len(updated_files)} YAML files.")
    else:
        print("Run with --update to apply changes.")


if __name__ == "__main__":
    main()
