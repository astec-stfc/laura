"""Read ImpactX inputs file ``argv[1]`` into JSON file ``argv[2]``.

Run in a subprocess by ``ImpactXLatticeImporter``, since AMReX starts once per
process."""

import json
import sys

if __name__ == "__main__":
    import amrex.space3d as amr
    import impactx

    sim = impactx.ImpactX()
    # run from the inputs file's folder, so keep init_grids off an existing diags/
    amr.ParmParse("diag").add("enable", False)
    sim.init_grids()
    sim.load_inputs_file(sys.argv[1])
    sim.init_lattice_elements_from_inputs()
    beam, given = amr.ParmParse("beam"), amr.ParmParse("").to_dict().get("beam", {})
    dicts = [
        {
            k: v.to_numpy().tolist() if hasattr(v, "to_numpy") else v
            for k, v in d.items()
        }
        for d in sim.lattice.to_dicts()
    ]
    with open(sys.argv[2], "w") as f:
        json.dump(
            {
                "kin_energy": beam.get_real("kin_energy")
                if "kin_energy" in given
                else None,
                "particle": beam.get_str("particle") if "particle" in given else None,
                "elements": dicts,
            },
            f,
        )
    sim.finalize()
