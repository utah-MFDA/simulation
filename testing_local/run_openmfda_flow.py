
import os
import sys
import shutil
from pathlib import Path

this_file = Path(os.path.abspath(os.path.dirname(__file__)))
# this is relative to the openmfda_flow 'flow' directory
this_file_rel = Path("../tools/simulation/testing_local/")

flow_root = this_file / "../../../flow"

# fmt: off
sys.path.append(os.path.abspath(flow_root / '..'))
from run_mfda_docker import run_mfdaflow_docker
# fmt: on


def run_design_openmfda(
    base_dir,
    design,
    design_var="sim",
    platform="h.r.3.3",
    make_trgt="pnr scad",
    force_deps=False,
):

    design_config = this_file_rel / base_dir / "openmfda_config.mk"

    run_mfdaflow_docker(
        design,
        platform,
        make_trgt,
        run_deps=force_deps,
        docker_env_vars=[f"DESIGN_CONFIG={design_config}"]
    )

    src_results_dir = flow_root / "results" / design / design_var
    dst_results_dir = this_file / base_dir / "results_openmfda"

    # copy results over
    shutil.copyfile(
        src_results_dir / "4_final.def",
        dst_results_dir / "4_final.def"
    )

    shutil.copyfile(
        src_results_dir / f"{design}_length.csv",
        dst_results_dir / f"{design}_length.csv"
    )

    shutil.copyfile(
        src_results_dir / f"{design}_route_nets.json",
        dst_results_dir / f"{design}_route_nets.json"
    )
# end run_design_openmfda


run_design_openmfda(
    "smart_toilet_test_config",
    "smart_toilet",
    design_var="sim"
)

run_design_openmfda(
    "smart_toilet_test_config_cnode",
    "smart_toilet",
    design_var="sim_cnode"
)

run_design_openmfda(
    "smart_toilet_test_config_pcell",
    "smart_toilet",
    design_var="sim_pcell"
)

run_design_openmfda(
    base_dir="smart_toilet_test_subcir",
    design="smart_toilet_subcir",
    force_deps=True,
    design_var="sim"
)

#   has bugs
# run_design_openmfda(
#     base_dir="mix_2_ht",
#     design="mix_2_ht",
#     design_var="sim"
# )
#
# run_design_openmfda(
#     base_dir="mix_3_ht",
#     design="mix_3_ht",
#     design_var="sim"
# )
