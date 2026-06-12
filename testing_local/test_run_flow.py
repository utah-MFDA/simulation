
#fmt: off
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.realpath(__file__) + '/../v_2_NX/'
    )
)

import runMFDASim2 as mfda_sim
#fmt: on


def test_run_smart_toilet_0():

    test_dir = 'testing_local/smart_toilet_test_config'
    omfda_result = f'{test_dir}/results_openmfda/'

    # inputs
    design_name = 'smart_toilet'
    verilog_file = f'{test_dir}/smart_toilet.v'
    sim_config = f'{test_dir}/simulation.config'
    length_file = f'{omfda_result}/smart_toilet_length.csv'

    # outputs
    sim_dir = f'{test_dir}/simulation_run_mfda'
    output_dir = sim_dir

    isLocalXyce = False

    x_config_file = 'testing_local/xyce_docker_config.json'

    mfda_sim.runSimulation(
        design=design_name,
        verilogFile=verilog_file,
        sim_config=sim_config,
        work_dir=sim_dir,
        libraryFile='',
        isLocalXyce=isLocalXyce,
        length_file=length_file,
        output_dir=output_dir,
        pcell_file=None,
        xyce_run_config_file=x_config_file,
    )


def test_run_smart_toilet_ht_0():

    test_dir = 'testing_local/smart_toilet_test_config'
    omfda_result = f'{test_dir}/results_openmfda/'

    # inputs
    design_name = 'smart_toilet_ht'
    verilog_file = f'{test_dir}/smart_toilet_ht.v'
    sim_config = f'{test_dir}/simulation_ht.config'
    length_file = f'{omfda_result}/smart_toilet_ht_length.csv'

    # outputs
    sim_dir = f'{test_dir}/simulation_run_mfda_ht'
    output_dir = sim_dir

    isLocalXyce = False

    x_config_file = 'testing_local/xyce_docker_config.json'

    mfda_sim.runSimulation(
        design=design_name,
        verilogFile=verilog_file,
        sim_config=sim_config,
        work_dir=sim_dir,
        libraryFile='',
        isLocalXyce=isLocalXyce,
        length_file=length_file,
        output_dir=output_dir,
        pcell_file=None,
        xyce_run_config_file=x_config_file,
    )


def test_run_smart_toilet_ht_temp_0():

    test_dir = 'testing_local/smart_toilet_test_config'
    omfda_result = f'{test_dir}/results_openmfda/'

    # inputs
    design_name = 'smart_toilet_ht'
    verilog_file = f'{test_dir}/smart_toilet_ht.v'
    sim_config = f'{test_dir}/simulation_ht_temp.config'
    length_file = f'{omfda_result}/smart_toilet_ht_length.csv'

    # outputs
    sim_dir = f'{test_dir}/simulation_run_mfda_ht_temp'
    output_dir = sim_dir

    isLocalXyce = False

    x_config_file = 'testing_local/xyce_docker_config.json'

    mfda_sim.runSimulation(
        design=design_name,
        verilogFile=verilog_file,
        sim_config=sim_config,
        work_dir=sim_dir,
        libraryFile='',
        isLocalXyce=isLocalXyce,
        length_file=length_file,
        output_dir=output_dir,
        pcell_file=None,
        xyce_run_config_file=x_config_file,
    )


# def test_run_mix2_ht_temp_0():
#
#     test_dir = 'testing_local/mix_2_ht'
#     omfda_result = f'{test_dir}/results_openmfda/'
#
#     # inputs
#     design_name = 'mix_2_ht'
#     verilog_file = f'{test_dir}/mix_2_ht.v'
#     sim_config = f'{test_dir}/simulation_ht_temp.config'
#     length_file = f'{omfda_result}/mix_2_ht_length.csv'
#
#     # outputs
#     sim_dir = f'{test_dir}/mix_2_ht_temp'
#     output_dir = sim_dir
#
#     isLocalXyce = False
#
#     x_config_file = 'testing_local/xyce_docker_config.json'
#
#     mfda_sim.runSimulation(
#         design=design_name,
#         verilogFile=verilog_file,
#         sim_config=sim_config,
#         work_dir=sim_dir,
#         libraryFile='',
#         isLocalXyce=isLocalXyce,
#         length_file=length_file,
#         output_dir=output_dir,
#         pcell_file=None,
#         xyce_run_config_file=x_config_file,
#     )
