
import subprocess


def test_run_local_simple_channel():

    python_cmd = 'python3 ./runMFDASim.py'

    arg_netlsit    = '--netlist simple_channel.v'
    arg_sim_file   = '--sim_file ./simpleChannelTest_full_config/simulation.config'
    arg_sim_dir    = '--sim_dir ./simpleChannelTest_full_config'
    arg_lib        = '--lib ./../testing/StandardCelLibrary.csv'
    arg_cir_config = '--cir_config ./../V2Va_Parser/VMF_xyce.mfsp'
    arg_length_file= '--length_file ./simpleChannelTest_full_config/simple_channel_lengths.xlsx'

    arg_eval_file  = '--eval_file ./simpleChannelTest_full_config/eval.config'
    arg_local_xyce = '--local_xyce'

    cmd_w_args = ' '.join([
        python_cmd,
        arg_netlsit,
        arg_sim_file, 
        arg_sim_dir,
        arg_lib,
        arg_cir_config,
        arg_length_file,
        arg_eval_file,
        arg_local_xyce])

    print("Running: "+cmd_w_args)

    subprocess.run(cmd_w_args)

def test_run_local_smart_toilet():

    python_cmd = 'python3 ./runMFDASim.py'

    arg_netlsit    = '--netlist smart_toilet.v'
    arg_sim_file   = '--sim_file ./smart_toilet_test_config/simulation.config'
    arg_sim_dir    = '--sim_dir ./smart_toilet_test_config'
    arg_lib        = '--lib ./../testing/StandardCelLibrary.csv'
    arg_cir_config = '--cir_config ./../V2Va_Parser/VMF_xyce.mfsp'
    arg_length_file= '--length_file ./smart_toilet_test_config/smart_toilet_lengths.xlsx'

    arg_eval_file  = '--eval_file ./smart_toilet_test_config/eval.config'
    arg_local_xyce = '--local_xyce'

    cmd_w_args = ' '.join([
        python_cmd,
        arg_netlsit,
        arg_sim_file, 
        arg_sim_dir,
        arg_lib,
        arg_cir_config,
        arg_length_file,
        arg_eval_file,
        arg_local_xyce])

    print("Running: "+cmd_w_args)

    subprocess.run(cmd_w_args)