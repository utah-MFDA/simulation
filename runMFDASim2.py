
import argparse
import os
import shutil
import subprocess

import tarfile
import json
import re

import pandas as pd
import matplotlib.pyplot as plt


from SimulationXyce import SimulationXyce

local_file_path = os.path.dirname(os.path.realpath(__file__))

"""
Required inputs

- docker image (or) docker container name
- netlist location
- specification location


Steps
- convert to xyce netlist (.cir)
- upload to docker image
- wait for image to complete sim (or) get error
- pull completed file
- evaluate to spec

"""


# returns the date and time as a string for files
def timeString():
    from datetime import datetime
    return str(datetime.now()) \
        .replace(":", "") \
        .replace(" ", "") \
        .split(".")[0]


# ----------------------------------------------------
# main exec
# ----------------------------------------------------
"""
verilogFile
    - Verilog netlist
workDir
    - local directory for other files
libraryFile
    - file for list of components
cirConfig
    -
preRouteSim
    -
dockerContainer
    - simulation docker container name
dockerWD
    - working directory for simulation
xyceFiles
    - location for xyce files to be generated
"""


def runSimulation(
        design,
        verilogFile,
        sim_config,
        work_dir,
        libraryFile,
        isLocalXyce,
        cirConfigFile=None,
        length_file=None,
        preRouteSim=False,
        dockerContainer=None,
        dockerWD=None,
        verilog_2_xyce_extras_loc=None,
        verilog_2_xyce_relative=True,
        convert_v=True,
        output_dir=None,
        pcell_file=None,
        plot_results=False,
        evaluate_results=False,
        xyce_run_config_file=None,
        # extra_args={}
):

    xyceFiles = 'spice_files.csv'

    # Checks local_xyce value
    # if (isLocalXyce):
    _local_xyce = True
    _noarchive = True  # no docker archive created
    convert_basename = False

    # Convert to cir from v
    if convert_v:

        generate_cir_files_from_write_spice(
            design=design,
            verilog_file=verilogFile,
            wd=work_dir,
            sim_config=sim_config,
            length_file=length_file,
            pcell_file=pcell_file
        )

    if _local_xyce:
        local_xyce_run(
            design_name=design,
            verilogFile=verilogFile,
            sim_config=sim_config,
            workDir=work_dir,
            libraryFile=libraryFile,
            output_dir=output_dir,
            xyceFiles=xyceFiles,
            xyce_run_config=xyce_run_config_file,
            _eval_file=evaluate_results
        )
    else:
        raise Exception("Requires a local install of Xyce with ADMS support")


def local_xyce_run(
        design_name,
        verilogFile,
        sim_config,
        workDir,
        libraryFile,
        output_dir,
        xyceFiles,
        xyce_run_config,
        verilog_2_xyce_extras_loc=None,
        verilog_2_xyce_relative=True,
        _eval_file=False,
        _main_plt_results=False
):

    if verilog_2_xyce_relative:
        result_wd = workDir
    else:
        result_wd = verilog_2_xyce_extras_loc

    runLocalXyce(
        xyce_files=xyceFiles,
        workDir=result_wd,
        config_file=xyce_run_config
    )

    results_prn_wd = result_wd  # +'/results'
    load_wd = ''
    nodes_dir = ''

    generate_report(
        design_name=design_name,
        wd=workDir,
        load_wd=load_wd,
        nodes_dir=nodes_dir,
        prn_dir=results_prn_wd,
        sim_config=sim_config,
        output_dir=output_dir,
        _eval_file=_eval_file,
        _main_plt_results=_main_plt_results
    )


def generate_report(
        design_name,
        wd,
        load_wd,
        nodes_dir,
        prn_dir,
        sim_config,
        output_dir,
        _eval_file=False,
        _main_plt_results=False
):

    rfiles = pd.read_csv(wd+"/spice_files.csv")["OutputFile"]
    chem_list = pd.read_csv(wd+"/spice_files.csv")["Chemical"]

    for i, f in enumerate(rfiles):
        rfiles[i] = f  # +".prn"

    print("Result files")
    print(rfiles)

    print("Chemical list")
    print(chem_list)

    df = load_xyce_results(load_wd, nodes_dir, rfiles, chem_list)

    # export to csv
    if isinstance(df, list):
        csv_out = f"{prn_dir}/{design_name}_xyceOut.csv"
    elif isinstance(df, pd.DataFrame):
        csv_out = f"{prn_dir}/{design_name}_xyceOut.csv"
        print(prn_dir)
        print(f"Writing results to {csv_out}")
        df.to_csv(csv_out)
    else:
        raise ValueError(
            "devel error: results DF not of type list or pandas DataFrame")

    if _eval_file:
        # def evaluate_results(ev_file, wd, results_dir, design_name, sim_obj=None)
        evaluate_results(
            # ev_file=extra_args['eval_file'],
            sim_file=sim_config,
            wd=wd,
            results_dir=prn_dir,
            design_name=design_name)
        # if output_dir is not None:

    if output_dir is not None:
        print("Moving results to "+output_dir)
        os.makedirs(output_dir, exist_ok=True)
        shutil.move(csv_out, output_dir+'/'+os.path.basename(csv_out))
        if _eval_file:
            print("Moving eval to "+output_dir)
            shutil.move(f"{prn_dir}/Chem_Eval.csv",
                        f'{output_dir}/Chem_Eval.csv')

    if _main_plt_results:
        plot_xyce_results_list(df)


def generate_cir_files_from_write_spice(
    design,
    verilog_file,
    wd,
    sim_config=None,
    length_file=None,
    gen_output_dir=None,
    basename_only=False,
    pcell_file=None
):
    import writeSpice

    # output file
    if gen_output_dir == None:
        of = f"{wd}/{design}"
    else:
        os.makedirs(f"{wd}/{gen_output_dir}", exist_ok=True)
        of = f"{wd}/{gen_output_dir}/{design}"

    writeSpice.generate_cir_main(
        design=design,
        verilog_file=verilog_file,
        config_file=sim_config,
        length_file=length_file,
        out_file=of,
        basename_only=basename_only,
        pcell_file=pcell_file,
    )


local_file_path = os.path.dirname(os.path.realpath(__file__))


def runLocalXyce(
    xyce_files,
    workDir,
    xyce_run_location=f'{local_file_path}',
    config_file=None
):

    import xyceRun

    # def main(config, ifile, iList, wd, no_result_dir=False, debug=None):
    xyceRun.main(
        config=config_file,
        ifile=None,
        ilist=f'{xyce_files}',
        wd=workDir,
        no_result_dir=True
    )


# load the prn file into a dataframe
def load_xyce_results_file(rFile):

    r_df = pd.read_table(
        rFile,
        skipfooter=1,
        index_col=0,
        # delim_whitespace=True,
        sep=r'\s+',
        engine='python'
    )
    return r_df


# This also removes
def change_results_node_ref(df, node_file, chem):

    node_mod = r'([VIvi])\(\s*(\d+|\w+)\s*\)'
    # node_parse = r'(?:(\w+)_(\w+)_comp_chem|(\w+)_(\w+)_chem|(\w+)_(\w+))'
    node_parse = r'(?:(\w+)_(\w+)_comp_chem|(\w+)_(\w+)_chem|(\w+)_(\w+)_comp_heat|(\w+)_(\w+)_heat|(\w+)_(\w+))'
    # regular_reg = [r'(\w+)_(\w+)']
    # chem_reg = [
    #     r'(\w+)_(\w+)_comp_chem',
    #     r'(\w+)_(\w+)_chem'
    # ]
    # heat_reg = [
    #     r'(\w+)_(\w+)_comp_heat',
    #     r'(\w+)_(\w+)_heat'
    # ]
    # node_parse = r'(?:' + '|'.join(
    #     chem_reg + heat_reg + regular_reg
    # ) + ')'
    node_flow_parse = r'VFL_(\w+)_(\w+)'

    df_nodes = list(df)
    node_dict = json.load(open(node_file))

    print(df_nodes)
    for node in df_nodes:
        print("---"+node+"---")
        node_name = ""
        if node == 'TIME':
            continue
        else:
            node_match = re.match(node_mod, node)
            if node_match is None:
                raise ValueError(f"Unable to parse '{node}'.")
            node_num = node_match[2]
            node_type = node_match[1]
            if node_type == 'I':
                print('Flow node ', node_num)
                parsed_node = re.match(node_flow_parse, node_num)
                if parsed_node is not None:
                    node_name = parsed_node[1]
                    node_dev = parsed_node[2]
                else:
                    raise Exception(f"Unable to parse {node_num}")
                node_key = node_name+'_'+node_dev

            elif node_type == 'V':
                # node_num = node.replace('V(', '').replace(')', '')
                print("Node #:", node_num, "Node T:", node_type)
                node_key = list(node_dict.keys())[list(
                    node_dict.values()).index(int(node_num))]

                is_chem_node = False
                is_temp_node = False

                parsed_node = re.match(node_parse, node_key)
                print(parsed_node.groups())
                # the type of node is determined by group position
                if parsed_node is not None:
                    # chemistry nodes
                    if parsed_node[1] is not None:
                        node_name = parsed_node[1]
                        node_dev = parsed_node[2]
                        is_chem_node = True
                    elif parsed_node[3] is not None:
                        node_name = parsed_node[3]
                        node_dev = parsed_node[4]
                        is_chem_node = True
                    # heat transfer nodes
                    elif parsed_node[5] is not None:
                        node_name = parsed_node[5]
                        node_dev = parsed_node[6]
                        is_temp_node = True
                    elif parsed_node[7] is not None:
                        node_name = parsed_node[7]
                        node_dev = parsed_node[8]
                        is_temp_node = True
                    # flow nodes
                    elif parsed_node[9] is not None:
                        node_name = parsed_node[9]
                        node_dev = parsed_node[10]
                    else:
                        raise ValueError(
                            f'Node {node_key} is not correctly formated, reg: {parsed_node.groups()}')
                else:
                    raise Exception(f"Unable to parse {node_num}")

            # node_name = '_'.join(node_key.split('_')[:-1])
            # if '_' in node_name_k:
                # node_name_k = node_key.split('_')[-1]
            if '_' in node_name:
                node_name_k = node_key.split('_')[-1]
            else:
                node_name_k = node_key

            print(node_name + ' : ' + node_name_k)

            # We assume chem node end in '_chem'
            if node_type == 'V':
                # if len(node_name_k) >= 4 and node_name_k.lower() == 'chem':
                if is_chem_node:
                    # to be supported later
                    # new_node = f'C_{str(chem)}({node_dev}-{node_name})'
                    new_node = f'C_{str(chem)}({node_name})'
                # may be an old implementation for output nodes
                elif node_name_k[-2:] == 'c0':
                    new_node = 'C_'+str(chem)+'('+node_name+')'
                elif is_temp_node:
                    new_node = f'T_({node_name})'
                # all else are pressure nodes
                else:
                    new_node = f'P({node_dev}-{node_name})'
            elif node_type == 'I':
                new_node = f'Q({node_dev}-{node_name})'

            print('  new node: '+new_node)

            df = df.rename(columns={node: new_node})

            # df = df.rename(columns={node:new_node})

    return df


def load_xyce_results(rDir, nodes_dir, rlist=None, chem_list=None):

    if rDir != '':
        rDir += '/'
    if nodes_dir != '':
        nodes_dir += '/'

    if rlist is None:
        return load_xyce_results_file(rDir)
    else:
        r_df = []

        # we assume in list generation the indexes did not shift
        for ind, rFile in enumerate(rlist):

            full_result_fpath = rDir+rFile
            full_node_fpath = nodes_dir+rFile
            print(full_result_fpath)
            temp_df = load_xyce_results_file(full_result_fpath)

            if chem_list is not None:
                temp_df = change_results_node_ref(
                    temp_df,
                    full_node_fpath.replace('.prn', '.str.nodes'),
                    chem_list[ind]
                )

            # remove duplicate columns
            if ind > 0:
                for t_col in temp_df.columns.tolist():
                    if t_col in r_df[0].columns.tolist():
                        temp_df = temp_df.drop(t_col, axis=1)
            if not ind:
                r_df.append(temp_df)
            else:
                r_df.append(temp_df)

        r_df = pd.concat(r_df, axis=1)

        return r_df


def evaluate_results(wd, results_dir, design_name, sim_obj=None, ev_file=None, sim_file=None):

    # setup
    if ev_file is not None:
        sim_obj = load_eval_file(wd+'/'+ev_file, sim_obj=sim_obj)
    elif sim_file is not None:
        sim_obj = SimulationXyce()
        # sim_obj.parse_config_file(sim_file)
        sim_obj.load_analysis_file(sim_file)

    if not isinstance(sim_obj, SimulationXyce):
        raise ValueError(f"{sim_obj} is not a SimulationXyce object")

    ev_chem_list = sim_obj.getEvaluation()
    # print("EVALS", ev_chem_list)
    eval_df_coln = ['Chemical', 'Time', 'Node',
                    'Error', 'Expected Conc', 'Eval Conc']
    eval_df = pd.DataFrame(columns=eval_df_coln)

    # load results
    for ev_chem in ev_chem_list:

        rFile = f"{results_dir}/{design_name}_xyceOut.csv"
        temp_df = pd.read_csv(rFile)
        if len(ev_chem_list[ev_chem]) == 0:
            continue

        for eval_obj in ev_chem_list[ev_chem]:
            if eval_obj.getTime() in temp_df['TIME']:

                # get time coln index
                row_time_ind = temp_df['TIME'][temp_df['TIME']
                                               == eval_obj.getTime()].index[0]
            # check for illegal values
            elif eval_obj.get_time() < 0:
                raise ValueError(f"{eval_obj.get_time()} is not a valid time")
            else:
                print('Cannot evaluate time: '+str(eval_obj.getTime())+' for chem: ' +
                      str(eval_obj.getChem())+'('+str(eval_obj.getNode())+')')
                print('attempting to get closest time step')
                if eval_obj.get_time() > max(temp_df['TIME']):
                    row_time_ind = temp_df['TIME'][-1]
                else:
                    for ti, t in enumerate(temp_df['TIME']):
                        if t < eval_obj.get_time():
                            if ti == 0:
                                continue
                            if abs(t - eval_obj.get_time()) < abs(temp_df["TIME"][ti-1] - eval_obj.get_time()):
                                row_time_ind = ti
                            else:
                                row_time_ind = ti - 1

            # get chemical value
            chem_name = 'C_'+eval_obj.getChem()+'('+eval_obj.getNode()+')'
            print("evaluating: "+chem_name)
            # chem_name = eval_obj.getChem()+'('+eval_obj.getNode()+')'
            # print(temp_df.columns.tolist())
            prn_val = temp_df[chem_name][row_time_ind]

            exp_val = eval_obj.getValue()
            # Calculate error
            err_val = abs((prn_val - exp_val)/exp_val)

            # add to data frame
            new_data = pd.DataFrame([[
                eval_obj.getChem(),
                eval_obj.getTime(),
                eval_obj.getNode(),
                err_val,
                eval_obj.getValue(),
                prn_val
            ]], columns=eval_df_coln)

            eval_df = pd.concat([eval_df, new_data])

    eval_df.to_csv(results_dir+'/Chem_Eval.csv')


# input is the results dataframe
def plot_xyce_results_list(r_df):

    if isinstance(r_df, list):
        for df in r_df:
            plot_xyce_results(df)
    elif isinstance(r_df, pd.DataFrame):
        plot_xyce_results(r_df)


def plot_xyce_results(r_df):

    x = r_df["TIME"]
    y = {}

    for col in r_df.keys():
        if col == "TIME":
            continue
        else:
            y[col] = r_df[col]

    fig, ax = plt.subplots()

    for p in y:
        ax.plot(x, y[p], label=p)

    ax.legend()
    plt.show()


def plot_xyce_results_2(design, results_directory):

    # generate report
    rfiles = pd.read_csv(results_directory+"/spiceList")["OutputFile"]

    for i, f in enumerate(rfiles):
        rfiles[i] = f+".prn"

    print("Result files")
    print(rfiles)

    df = load_xyce_results(results_directory+"/results", rfiles)

    plot_xyce_results_list(df)

    pass


def load_eval_file(ev_file, sim_obj=None):

    if sim_obj == None:
        sim_obj = SimulationXyce()

    sim_obj.parse_eval_file(ev_file)

    return sim_obj


def is_docker_container_running(client, container):
    if container not in [x.name for x in client.containers.list()]:
        # print(client.containers.list())
        raise ValueError('Container not in list (is it running?). Looking for ' + container + "\n" +
                         "Running images: " + str([x.name for x in client.containers.list()]))
    return True


def docker_clean_result_dir(client, container, device):
    pass


def export_xyce_results_to_csv(design, chem_list, result_dir):
    pass


if __name__ == "__main__":

    def is_str_true(var):
        if (isLocalXyce.lower() in ['true', '1']):
            return True
        elif (isLocalXyce.lower() in ['false', '0']):
            return False
        else:
            raise InputError("--local_xyce much be false or true (0 or 1)")
    parser = argparse.ArgumentParser(
        prog="MFDASimulation",
        description="",
        epilog=""
    )

    parser.add_argument(
        '--netlist',   metavar='<netlist_file>', type=str, required=True)
    parser.add_argument(
        '--sim_config', metavar='<sim_config>', type=str, required=True)
    parser.add_argument('--sim_dir',   metavar='<sim_dir>',
                        type=str, required=True)
    parser.add_argument('--lib',       metavar='<lib>',
                        type=str, required=True)

    # included with the parser
    parser.add_argument(
        '--cir_config', metavar='<cir_config>', type=str, required=True)

    parser.add_argument(
        '--output_dir', metavar='<output_dir>', type=str, default=None)
    parser.add_argument(
        '--pcell_file', metavar='<pcell_file>', type=str, default=None)

    parser.add_argument('--design', metavar='<design>',
                        type=str, required=True)
    parser.add_argument(
        '--length_file', metavar='<length_file>', type=str, default=None)

    parser.add_argument('--docker_image', metavar='<image>', type=str)
    parser.add_argument('--docker_container', metavar='<container>', type=str)
    parser.add_argument('--docker_wd', metavar='<docker_wd>',
                        type=str, default="/mfda_simulation/local/simulations")

    parser.add_argument('--preRoute', action="store_true", default=False)
    parser.add_argument('--convert_verilog',
                        action="store_false", default=True)

    parser.add_argument('--plot', action='store_true', default=False)
    parser.add_argument('--eval_result', action='store_true', default=False)
    parser.add_argument('--local_xyce', action='store_true', default=False)

    parser.add_argument('--dont_move_results',
                        action="store_true", default=False)

    parser.add_argument('--xyce_run_config', type=str, default=None)
    parser.add_argument('--xyce_write_loc', type=str, default=None)

    args = parser.parse_args()

    runSimulation(
        design=args.design,
        verilogFile=args.netlist,
        sim_config=args.sim_config,
        work_dir=args.sim_dir,
        libraryFile=args.lib,
        isLocalXyce=args.local_xyce,
        cirConfigFile=args.cir_config,
        length_file=args.length_file,
        preRouteSim=args.preRoute,
        dockerContainer=args.docker_container,
        dockerWD=args.docker_wd,
        convert_v=args.convert_verilog,
        output_dir=args.output_dir,
        pcell_file=args.pcell_file,
        verilog_2_xyce_extras_loc=args.xyce_write_loc,
        plot_results=args.plot,
        evaluate_results=args.eval_result,
        xyce_run_config_file=args.xyce_run_config,
    )
