
import os
import sys
import shutil
from pathlib import Path

this_file = Path(os.path.abspath(os.path.dirname(__file__)))
# this is relative to the openmfda_flow 'flow' directory
this_file_rel = Path("../tools/simulation/testing_local/")

flow_root = Path(os.path.abspath("../../flow"))

# fmt: off
sys.path.append(os.path.abspath(flow_root / '..'))
from run_mfda_docker import run_mfdaflow_docker
# fmt: on

# important file locations

# verilog_file = this_file / "smart_toilet_test_config" / "smart_toilet.v"
#
# design_config = this_file_rel / "smart_toilet_test_config" / "openmfda_config.mk"
#
# design = "smart_toilet"
#
# run_mfdaflow_docker(
#     design,
#     "h.r.3.3",
#     "pnr scad",
#     docker_env_vars=[f"DESIGN_CONFIG={design_config}"]
# )
#
# src_results_dir = flow_root / "results" / design / "sim"
# dst_results_dir = this_file / "smart_toilet_test_config" / "results"
#
# # copy results over
# shutil.copyfile(
#     src_results_dir / "4_final.def",
#     dst_results_dir / "4_final.def"
# )
#
# shutil.copyfile(
#     src_results_dir / f"{design}_length.csv",
#     dst_results_dir / f"{design}_length.csv"
# )
#
# shutil.copyfile(
#     src_results_dir / f"{design}_route_nets.json",
#     dst_results_dir / f"{design}_route_nets.json"
# )

# base_dir is a relative path


def run_design_openmfda(
    base_dir,
    design,
    design_var="sim",
    platform="h.r.3.3",
    make_trgt="pnr scad"
):

    design_config = this_file_rel / base_dir / "openmfda_config.mk"

    run_mfdaflow_docker(
        design,
        platform,
        make_trgt,
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
    base_dir="mix_2_ht",
    design="mix_2_ht",
    design_var="sim"
)

run_design_openmfda(
    base_dir="mix_3_ht",
    design="mix_3_ht",
    design_var="sim"
)
