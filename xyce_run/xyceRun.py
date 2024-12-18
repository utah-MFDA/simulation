
import argparse
import json
import subprocess
import os

import pandas as pd

class xyceSimulator:

    def __init__(self):
        pass

    def __init__(self, configFile):

        if isinstance(configFile, list):
            configFile = configFile[0]
        print("config file", configFile)
        xyce_config = ''
        with open(configFile, 'r') as f:
            xyce_config = json.load(f)

        print("Xyce config", xyce_config)
        self.xyce_command = xyce_config["xyce_command"]

        self.xyce_libraries = []
        self.loadPlugins(xyce_config["library_files"], fromFile=False)

    def loadPlugins(self, config, fromFile=True):
        xyce_libs = None
        if fromFile:
            with open(config, 'r') as f:
                xyce_libs = json.load(f)["library_files"]
        else:
            xyce_libs = config

        print("Xyce libs", xyce_libs)

        self.xyce_libraries += xyce_libs

        pass

    def getPlugins(self):
        return self.xyce_libraries
    
    def genPluginStr(self):
        return ','.join(self.xyce_libraries) 

    def set_xyce_command(self, command):
        self.xyce_command = command

    def _hide_netlist_files(spice_dir):
        for f in os.listdir(spice_dir):
            if os.path.isfile(os.path.join(spice_dir, f)) and f[-4:]==".cir":
                os.rename(spice_dir+'/cir_files/'+f)


    def _move_results_files(self, spice_dir):
        for f in os.listdir(spice_dir):
            #if os.path.isdir(spice_dir):
                #os.remove(spice_dir+'/results')
            if os.path.isfile(os.path.join(spice_dir, f)) and f[-4:]==".prn":
                r_file = os.path.join(spice_dir, f)
                r_dir  = spice_dir#+'/results'
                # check for directory
                if not os.path.isdir(r_dir):
                    os.mkdir(r_dir)
                os.rename(r_file, r_dir+'/'+f)
                
    def replace_voltage_nodes(self, files, spList):
        for f in files:
            node_list_f = f+".str.nodes"
            result_f    = f+".prn"
            #result_f    = "/".join(f.split("/").insert(-2, "results"))+".prn"
            result_temp = result_f+".temp"

            #load spicelist
            print(spList)
            print(f.split("/")[-1])
            #chem_ind = spList.index[spList['OutputFile']==f.split("/")[-1]]

            chem_ind = spList.index[spList['spice_file']==f]
            print("chem ind:"+str(chem_ind))
            chem_name= list(spList.iloc[chem_ind]['Chemical'])[0]
            print(chem_name)

            replacement_list = {}
            n = json.load(open(node_list_f))

            for key, value in n.items():
                # autogenerated channel concetration keys end in c
                if key[-1] == 'c' or key[-1] == 'C':
                    replacement_list["V("+str(value)+")"] = chem_name+"("+"_".join(key.split("_")[:-1])+")"
                else:
                    replacement_list["V("+str(value)+")"] = "P("+"_".join(key.split("_")[:-1])+")"

            with open(result_f) as inFile, open(result_temp, 'w') as outFile:
                for line in inFile:
                    for src, target in replacement_list.items():
                        line = line.replace(src, target)
                    outFile.write(line)

            os.remove(result_f)
            os.rename(result_temp, result_f)
        # end f in files

    def run(self, files):
        
        # generate library string
        if self.xyce_libraries == None or self.xyce_libraries == '' or \
            len(self.xyce_libraries) == 1 and self.xyce_libraries[0] == '':
            xyce_lib_str = ''
        else:
            xyce_lib_str = ' -plugin '+self.genPluginStr()+' '

        xyce_run = self.xyce_command + xyce_lib_str

        for f in files:
            xyce_run_file = f"{xyce_run} {f}"
            print('---------------------------------')
            print("run Xyce: " + xyce_run_file)
            xyce_run_file = ' '.join(xyce_run_file.split())
            print(xyce_run_file)
            subprocess.run(xyce_run_file, shell=True)
        
        # TODO test
        #self._move_results_files(os.path.dirname(files[0]))

def parseFileList(ilist, wd):
    print("reading file: "+str(ilist))

    listDB = pd.read_csv(ilist)

    f_list = []

    for f in listDB.iterrows():
        #f_name = f[1]["OutputFile"]
        f_name = f[1]["spice_file"]
        f_list.append(f_name)

    return f_list

def setConfig(config):
    if args.config is None:
        config_file = "xyceConfig"
    else:
        config_file = args.config

    return config_file

def parseFiles(ifile, ilist, wd=None):
    if wd == None:
        wd = ''
    else:
        wd += '/'

    if ilist is not None and \
        ifile is not None:
        raise Exception("Pass either file or argument")
    elif ilist is not None:
        infiles = parseFileList(ilist, wd)
    elif ifile is not None:
        infiles = ifile.split(' ')
    else:
        raise Exception("No files passed")

    return infiles

if __name__ == "__main__":
    
    import os
    #configDefault     = "/mfda_simulation/xyce_docker_server/xyceConfig"
    configDefault = os.path.dirname(os.path.normpath(os.path.realpath(__file__)))+"/xyceConfig"
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--file', metavar="<files>", dest='ifile', type=str,
                        help="list of files", nargs='*')
    parser.add_argument('--list', metavar="<list_file>", dest='ilist', type=str,
                        help="list of files", nargs=1)
    parser.add_argument('--workdir', metavar='<working_dir>', dest='wd', type=str,
                        help="simulation working directory", default=None)
    parser.add_argument('--no_result_dir', dest='no_result_dir',
                        help="simulation working directory", action='store_true')

    parser.add_argument('--config', metavar="<config>", dest='config', type=str,
                        help="simulation configuration", nargs=1, default=configDefault)
    
    parser.add_argument('--debug', dest='debug', default=None)
    
    args = parser.parse_args()

    config_file = setConfig(args.config)
    sim = xyceSimulator(config_file)

    infiles = parseFiles(args.ifile, args.ilist[0], args.wd)
    if args.ilist is not None:
        spiceList = pd.read_csv(args.ilist[0])
    else:
        spiceList = None

    print("No results: "+str(args.no_result_dir))

    if(args.debug == None):
        sim.run(infiles)
        if spiceList is not None:
            sim.replace_voltage_nodes(infiles, spiceList)
        if not args.no_result_dir:
            print("Move results to "+os.path.dirname(infiles[0])+'/')
            sim._move_results_files(os.path.dirname(infiles[0]))

