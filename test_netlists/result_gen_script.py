
import os
import subprocess

this_directory = os.path.realpath(os.path.dirname(__file__))

def gen_config(config_path, test_name):
    with open(config_path, "+w") as cfg:
        cfg.write(f"""
export DESIGN_NAME     	= {test_name}
export VERILOG_FILES 	= $(dir $(DESIGN_CONFIG))../$(DESIGN_NAME).v
export SDC_FILE      	= $(dir $(DESIGN_CONFIG))constraint.sdc
export IO_CONSTRAINTS	= $(dir $(DESIGN_CONFIG))io_cfg.tcl
#export SIMULATION_CONFIG= $(dir $(DESIGN_CONFIG))simulation.config

#SCAD_ARGS += --dimm_file "$(DIMM_FILE)" 

""")

def gen_io_cfg(io_cfg_path, io_loc):
    if not isinstance(io_loc, list):
        raise ValueError("Expecting list of dict for io_loc")

    for itm in io_loc:
        if not isinstance(itm, dict):
            raise ValueError(f"Expecting list of dict for io_loc; io_loc type: {type(io_loc)}, itm type:{type(itm)}")
    
    print("writing to :" + io_cfg_path)
    with open(io_cfg_path, "w+") as io_w:
        
        rb = '}'
        lb = '{'
        
        used_ios = []

        for io in io_loc:
            io_w.write(f"place_pin -pin_name {io['name']} -layer {io['layer']} -location {lb} {io['pos'][0]} {io['pos'][1]} {rb}" + "\n")
            used_ios.append(io['pos'])

def gen_constraint(const_path, test_name):
    with open(const_path, "w+") as const_w:
        const_w.write(f"current_design {test_name}")


def hr33_pin_pos(x, y):
    if x <= 7 and x >= 0 and y <= 3 and y >=0:
        return [960 + 90*x, 930 + 90*y]
    else:
        raise ValueError(f"X and Y values invalid x must be within 0 and 7; y must be \
            within 0 and 3; Actual 'x:{x}, y:{y}' ")


def main(test_name, io_list, platform=None, flow_dir=None):

    src_path = f"{this_directory}/{test_name}/src"

    verilog_path = f"{src_path}/{test_name}.v"
    result_path = f"{this_directory}/{test_name}/results"
    
    if not os.path.exists(f"{this_directory}/{test_name}"):
        raise ValueError(f"Test '{test_name}' is not valid")

    if not os.path.exists(verilog_path):
        raise ValueError(f"Test '{test_name}' is not valid; no src verilog file")

    if not os.path.exists(f"{src_path}/cfg"):
        os.mkdir(f"{src_path}/cfg")

    config_path = f"{src_path}/cfg/config.mk"
    
    io_cfg_path = f"{src_path}/cfg/io_cfg.tcl"
    const_path  = f"{src_path}/cfg/constraint.sdc"

    if platform == 'h.r.3.3':
        for ind, port in enumerate(io_list):
            io_list[ind]['pos'] = hr33_pin_pos(port['pos'][0], port['pos'][1])
    
    if platform is not None:
        platform_arg = f'    -e PLATFORM={platform} '
    else:
        platform_arg = ''


    gen_config(config_path, test_name)
    gen_io_cfg(io_cfg_path, io_list)
    gen_constraint(const_path, test_name)

    if flow_dir is None:
        flow_dir = os.path.realpath('../../flow')

    if not os.path.exists(flow_dir):
        raise ValueError(f"Flow path does not exist: '{flow_dir}'")

    make_cmd = f"make pnr \
    -e DESIGN={test_name} \
    -e DESIGN_CONFIG={config_path} \
    -e RESULTS_DIR={result_path} \
    {platform_arg}-C {flow_dir}"

    print("Make command:\n" + make_cmd)

    subprocess.run(
        make_cmd, 
        check=True,
        shell=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--test', type=str)
    parser.add_argument('--platform', type=str)

    args = parser.parse_args()

    main(
        args.test,
        platform=args.platform
        )
