
import argparse
import os
import shutil

import docker
import tarfile
import json

import pandas as pd
import matplotlib.pyplot as plt

# local imports
from V2Va_Parser import Verilog2Xyce



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
class SimulationXyce:
        
    class Node:    
        def __init__(self, name, args):
                self.name = name
                self.args = args

        def getName(self):
            return self.name
        
        def getArgs(self):
            return self.args
    
    class Inlet(Node):
        def __init__(self, name, args):
            super.__init__(name, args)

    class Outlet(Node):
        def __init__(self, name, args):
            super.__init__(name, args)

    class Eval:
        def __init__(self, chem, node, value):
            self.node = node
            self.value= value
            
        def getNode(self):
            return self.node
        
        def getValue(self):
            return self.value

    # this will need some more generic definitions
    class Dev:
        def __init__(self, node, type, args):
            self.type = type
            self.node = node
            self.args = args

        def getType(self):
            return self.type

        def getNode(self):
            return self.node
        
        def getArgs(self):
            return self.args
        
        def addArgument(self, arg):
            self.args.append(arg)
    
    class ChemInput:
        def __init__(self, chem, node, in_value):
            self.chem = chem
            self.node = node
            self.value=in_value
            
        def getInValue(self):
            return self.value
        
        def getNode(self):
            return self.node
        
        def getChem(self):
            return self.chem

    def __init__(self):
        self.netListFiles = []
        self.inlets = {}
        self.eval   = {}
        self.dev    = {}
        self.chem   = {}
        self.times  = {}
        
    def parse_config_file(self, file):
        in_conf_f = open(file)
        for line in in_conf_f:
            # remove comments
            if '#' in line:
                line = line.split('#')[0]
            line = ' '.join(line.lstrip().split()) # removes leading and extra WS
            
            if len(line) == 0:
                continue
            
            params = line.split(' ')
            key = params[0]
            
            if key == 'input':
                self.dev[params[1]] = self.Dev(params[1], params[2], params[3:])
            if key == 'chem':
                if params[2] in self.dev:
                    self.chem[params[1]] = self.ChemInput(params[1], params[2], params[3])
                    if params[1] in self.eval:
                        self.eval[params[1]].append(self.Eval(params[1], params[4], params[5]))
                    else:
                        self.eval[params[1]] = [self.Eval(params[1], params[4], params[5])]
                else:
                    pass
            
            # key for timing
            if key == 'transient':
                if 'transient' in self.times:
                    self.times['transient'].append(params)
                else:
                    self.times['transient'] = [params]
            # untested method
            # would need to use DC simulations
            if key == 'static':
                pass
            
            
            
    def addNetlistFile(self, nFile):
        self.netListFiles.append(nFile)

    def removeNelistFile(self):
        # find file that matches key

        # remove file
        pass

    def clearNetlistFile(self):
        self.netListFiles = []

    def addInlet(self, inletName, inletArgs):
        #' '.join(str.split()) reduces multispaces to single space
        inletArgs = ' '.join(inletArgs.split()).split(' ')
        self.inlets[inletName] = {'args':inletArgs}

    def removeInlet(self):
        pass

    def addEval(self, evalNode, evalArgs):
        evalArgs = ' '.join(evalArgs.split()).split(' ')
        self.eval[evalNode] = {'args':evalArgs}

    def removeEval(self):
        pass

    def addDev(self, dev, node, args):
        self.dev[node] = {'dev':dev, 'args':args}
        
    def getDeviceList(self):
        return self.dev
    
    def getDevice(self, port):
        return self.dev[port]
    
    def getEvaluation(self, chem):
        eval = self.eval[chem]
        e_out = {}
        for e in eval:
            e_out[e.getNode()] = e.getValue()
        
        return e_out
    
    def getInputChemList(self):
        return self.chem
    
    def getInputChem(self, chem):
        return self.chem[chem].getNode(), self.chem[chem].getValue()
    
    def getSimulationTimes(self):
        return self.times

    
    

# returns the date and time as a string for files
def timeString():
    from datetime import datetime
    return str(datetime.now()) \
        .replace(":","") \
        .replace(" ","") \
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
        verilogFile, 
        workDir, 
        libraryFile,
        cirConfigFile,
        length_file=None,
        preRouteSim=False,
        dockerContainer=None,
        dockerWD=None,
        xyceFiles="spiceList",
        convert_v=True,
        extra_args={}):
    
    # hard coded simulation directory in docker image
    docker_PyWD    = "/mfda_simulation/xyce_docker_server"

    simRunComm     = "python3 "+docker_PyWD+"/xyceRun.py --list "+xyceFiles

    sim_config     = workDir+"/simulation.config"

    ###### extra argument handling #####
    
    # default definitions
    _main_plot_results = False
    
    
    if ('plot' in extra_args) and (extra_args['plot'].lower() in ['true', '1']):
        _main_plot_results = True


    #####

    # Convert to cir from v
    if convert_v:
        """
        verilogFile,
        sim_config,
        wd, 
        libFile, 
        configFile,
        length_file=None,
        preRouteSim=False, 
        overwrite=False
        """
        arcName = convertToCir_from_config(
            verilogFile =verilogFile,
            sim_config  =sim_config,
            wd          =workDir, 
            libFile     =libraryFile, 
            configFile  =cirConfigFile,
            length_file =length_file,
            preRouteSim =preRouteSim)
    
    # default result directory
    result_wd = workDir+"/"+os.path.basename(arcName).replace('.tar','')
    result_wd = workDir+"/results"

    # transfer files to docker image
    pushCir2Docker(arcName, dockerContainer, dockerWD)

    simRunComm += " --workdir "+dockerWD+'/'+os.path.basename(arcName).replace('.tar','')

    # wait for simulator
    runRemoteXyce(simStartComm=simRunComm, 
                  dockerContainer=dockerContainer, 
                  simDockerPyWD=dockerWD)

    # move old results directory
    if os.path.isdir(result_wd):
        # create tar file
        old_result_path = result_wd+"_old"
        if not os.path.isdir(old_result_path):
            os.makedirs(old_result_path)
        result_old_tar = old_result_path+"/result_"+timeString()+".tar"
        #result_old_tar = result_wd+"_old/result_"+timeString()+".tar"
        r_tar = tarfile.open(result_old_tar, 'x')
        r_tar.add(result_wd)
        # remove old results
        shutil.rmtree(result_wd)
        

    # load extracted data
    pullFromDocker(targetDirectory=result_wd,
                   dockerContainer=dockerContainer,
                   simDockerWD=dockerWD+'/'+os.path.basename(arcName).replace('.tar',''),
                   # overwrite pervious tar
                   OR_fileExists=True)

    # generate report
    rfiles    = pd.read_csv(result_wd+"/spiceList")["OutputFile"]
    chem_list = pd.read_csv(result_wd+"/spiceList")["Chemical"]


    for i, f in enumerate(rfiles):
        rfiles[i] = f+".prn"

    print("Result files")
    print(rfiles)

    df = load_xyce_results(result_wd+"/results", rfiles, chem_list)

    # export to csv
    if isinstance(df, list):
        pass
    elif isinstance(df, pd.DataFrame):
        df.to_csv(result_wd+"/results/"+verilogFile[:-2]+'_chemOut.csv')
    else:
        throw()
    if _main_plot_results:    
        plot_xyce_results_list(df)

    pass

def parseMFDAFile(mfda_file):
    
    iFile = open(mfda_file, "r")

    xyceSimObj = SimulationXyce()

    for line in iFile:

        lineWSSplit = ' '.join(line.lstrip().split())

        lineKey = lineWSSplit[0]
        lineArgs = lineWSSplit[1:]

        if lineKey == "NETLIST" and lineArgs[0] == "file":
            xyceSimObj.addNetlistFile(lineArgs[1])
        elif lineKey == "inlet":
            xyceSimObj.addInlet(lineArgs[0], lineArgs[1:])
        elif lineKey == "eval":
            xyceSimObj.addEval(lineArgs[0], lineArgs[1:])
        elif lineKey == "dev":
            xyceSimObj
        
        

        pass

def convertToCir(verilogFile, wd, libFile, configFile, preRouteSim, overwrite=False):

    # locate nessary files
    files = getSimFiles(verilogFile, wd)

    Verilog2Xyce.Verilog2Xyce_from_csv(
        inputVerilogFile=files['verilogFile'],
        configFile=configFile,
        solnFile=files['specFile'],
        remoteTestPath="",
        libraryFile=libFile,
        devFile=files["devFile"],
        length_file=files["lengthFile"],
        timeFile=files["timeFile"],
        preRouteSim=preRouteSim,
        outputVerilogFile=None,
        runScipt=True)
    
    # create archive
    arcNameBase = files['verilogFile'][:-2]+"_xyce"

    xyceTar, arcName = createXyceArchive(arcNameBase, Overwrite=overwrite)

    srcDir = wd+"/spiceFiles"
    xyceTar.add(srcDir, arcname=os.path.basename(srcDir.replace("spiceFiles",arcName.replace('.tar',''))))

    xyceTar.close()

    print("--------------------")
    print("created archive: " + arcName)
    print("--------------------")

    return arcName

def convertToCir_from_config(
        verilogFile,
        sim_config,
        wd, 
        libFile, 
        configFile,
        length_file=None,
        preRouteSim=False, 
        overwrite=False):

    # locate nessary files
    #files = getSimFiles(verilogFile, wd)
    
    vFile = wd+"/"+verilogFile
    
    if length_file is None:
        len_file = wd+"/"+verilogFile[:-2]+"_lengths.xlsx"
    else:
        len_file = length_file
    
    # create Sim class
    _sim = SimulationXyce()
    _sim.parse_config_file(sim_config)
    

    Verilog2Xyce.Verilog2Xyce_from_config(
        inputVerilogFile  = vFile,
        configFile        = configFile,
        solnInputList     = _sim.getInputChemList(),
        #simEvalList       = _sim.getEvaluation(),
        remoteTestPath    = "",
        libraryFile       = libFile,
        devList           = _sim.getDeviceList(),
        length_file       = len_file,
        simTimesList      = _sim.getSimulationTimes(),
        preRouteSim       = preRouteSim,
        outputVerilogFile = None,
        runScipt          = True)
    
    # create archive
    arcNameBase = vFile[:-2]+"_xyce"

    xyceTar, arcName = createXyceArchive(arcNameBase, Overwrite=overwrite)

    srcDir = wd+"/spiceFiles"
    xyceTar.add(srcDir, arcname=os.path.basename(srcDir.replace("spiceFiles",arcName.replace('.tar',''))))

    xyceTar.close()

    print("--------------------")
    print("created archive: " + arcName)
    print("--------------------")

    return arcName

def createXyceArchive(arcName, Overwrite=True, attempt=0):
    newName = arcName+"_"+str(attempt)+".tar"
    try:
        xyceTar = tarfile.open(newName, 'x')
        return xyceTar, newName
    except FileExistsError:
        if Overwrite:
            os.remove(newName)
            xyceTar = tarfile.open(newName, 'x')
            return xyceTar, newName
        else:
            return createXyceArchive(arcName, attempt=attempt+1)

def getSimFiles(verilogFile, wd):

    files = {}
    files['verilogFile']=wd+"/"+verilogFile
    # locate necessary files
    files['specFile']  = wd+"/"+verilogFile[:-2]+"_spec.csv"
    files['lengthFile']= wd+"/"+verilogFile[:-2]+"_lengths.xlsx"
    files['devFile']   = wd+"/devices.csv"
    files['timeFile']  = wd+"/simTime.csv"

    return files

def pushCir2Docker(simArchive, dockerContainer, dockerWD):

    client = docker.from_env()

    # check for running image
    is_docker_container_running(client, dockerContainer)
    
    # create archive
    #tarfile.open()

    xyceContainer = client.containers.get(dockerContainer)

    with open(simArchive, 'rb') as fd:
        ok = xyceContainer.put_archive(dockerWD, data=fd)
        if not ok:
            raise Exception('Put file failed')
        else:
            print("Files transfer success")

def runRemoteXyce(simStartComm, dockerContainer, simDockerPyWD):
    
    client = docker.from_env()

    # check for running image
    is_docker_container_running(client, dockerContainer)

    xyceContainer = client.containers.get(dockerContainer)

    print("------------------------------")
    print("send command: "+simStartComm)
    print("to directory: " + dockerContainer+":"+simDockerPyWD )

    _, stream = xyceContainer.exec_run(cmd=simStartComm, 
                                       workdir=simDockerPyWD, 
                                       stream=True,
                                       #stream=False,
                                       )
    for data in stream:
        print(data.decode())

def pullFromDocker(targetDirectory, dockerContainer, simDockerWD, OR_fileExists=False):

    client = docker.from_env()

    is_docker_container_running(client, dockerContainer)

    xyceContainer = client.containers.get(dockerContainer)

    if not os.path.exists(targetDirectory):
        os.makedirs(targetDirectory)
    else:
        pass # directory exists
    
    targetFileAbs = targetDirectory+'/result.tar'

    try:
        f = open(targetFileAbs, 'xb')
    except FileExistsError:
        if OR_fileExists:
            f = open(targetFileAbs, 'wb')
        else:
            attempt = 0
            while True:
                try:
                    targetFileAbs = targetDirectory+'/result'+attempt+'.tar'
                    f = open(targetFileAbs, 'xb')
                    break
                except FileExistsError:
                    attempt += 1
                
    bits, stat = xyceContainer.get_archive(simDockerWD)
    print(stat)

    for chunk in bits:
        f.write(chunk)
    f.close

    # unpack archive
    local_arc = tarfile.open(targetFileAbs, 'r')
    local_arc.extractall(path=targetDirectory)
    os.remove(targetFileAbs)

    # move files to results
    for f1 in os.listdir(targetDirectory):
        f1_ = targetDirectory+"/"+f1
        if os.path.isdir(f1_):
            for f2 in os.listdir(f1_):
                
                os.rename(f1_+"/"+f2, targetDirectory+"/"+f2)
            os.removedirs(f1_)

# load the prn file into a dataframe
def load_xyce_results_file(rFile):
    r_df = pd.read_table(rFile, skipfooter=1, index_col=0, delim_whitespace=True)
    #print(str(r_df))
    return r_df

def change_r_node_ref(df, rFile, chem):
    
    df_nodes = list(df)

    node_dict = json.load(open(rFile.replace('.prn','.nodes')))

    for node in df_nodes:
        if node == 'TIME':
            continue
        else:
            if node[0] == 'V':
                node_num = node.replace('V(', '').replace(')', '')
                node_key = list(node_dict.keys())[list(node_dict.values()).index(int(node_num))]

                node_name = '_'.join(node_key.split('_')[:-1])
                node_name_k = node_key.split('_')[-1]

                print(node_name+' : '+node_name_k)

                if node_name_k.lower()[-1] == 'c':
                    new_node = 'C_'+str(chem)+'('+node_name+')'
                else:
                    new_node = 'P('+node_name+')'

                print('  new node: '+new_node)

            elif node[0] == 'I':
                pass

            df = df.rename(columns={node:new_node})

    return df



def load_xyce_results(rDir, rlist=None, chem_list=None):
    if rlist is None:
        return load_xyce_results_file(rDir)
    else:
        r_df = []
        #r_df = pd.DataFrame()
        # we assume in list generation the indexes did not shift
        for ind, rFile in enumerate(rlist):

            print(rDir+"/"+rFile)
            temp_df = pd.read_table(rDir+"/"+rFile, skipfooter=1, index_col=0, delim_whitespace=True)
            
            if chem_list is not None:
                temp_df = change_r_node_ref(temp_df, rDir+"/../"+rFile, chem_list[ind])

            #r_df = pd.append([temp_df])
            if not ind:
                r_df.append(temp_df)
            else:
                r_df.append(temp_df.drop('TIME', axis=1))
            #print(str(r_df))
        r_df = pd.concat(r_df, axis=1)
        
        return r_df

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

def export_xyce_results_to_csv(design, chem_list, result_dir):
    pass

def evaluate_results():
    pass


def is_docker_container_running(client, container):
    if container not in [x.name for x in client.containers.list()]:
        #print(client.containers.list())
        raise ValueError('Container not in list (is it running?)' + "\n"+\
                         "Running images: " + str([x.name for x in client.containers.list()]))
    return True


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        prog="MFDASimulation",
        description="",
        epilog=""
    )

    parser.add_argument('--netlist',   metavar='<netlist_file>', type=str, required=True)
    parser.add_argument('--sim_file',  metavar='<sim_file>', type=str, required=True)
    parser.add_argument('--sim_dir',   metavar='<sim_dir>' , type=str, required=True)
    parser.add_argument('--lib',       metavar='<lib>'       , type=str, required=True)
    
    # included with the parser
    parser.add_argument('--cir_config',metavar='<cir_config>', type=str, required=True)
    
    
    parser.add_argument('--design', metavar='<design>', type=str)
    parser.add_argument('--length_file', metavar='<length_file>', type=str, default=None)

    parser.add_argument('--docker_image', metavar='<image>', type=str)
    parser.add_argument('--docker_container', metavar='<container>', type=str)
    parser.add_argument('--docker_wd', metavar='<docker_wd>', 
            type=str, default="/mfda_simulation/local/simulations")
    
    parser.add_argument('--preRoute', metavar='<preRoute>', type=str, default='False')
    parser.add_argument('--convert_verilog', metavar='<convert_verilog>', type=str, default='True')
    
    parser.add_argument('--plot', type=str, default='False')
    
    args = parser.parse_args()
    
    ex_args = {
        'plot':args.plot
        }
    
    runSimulation(
        verilogFile    = args.netlist, 
        workDir        = args.sim_dir, 
        libraryFile    = args.lib,
        cirConfigFile  = args.cir_config,
        length_file    = args.length_file,
        preRouteSim    = args.preRoute.lower() in ['true', '1'],
        dockerContainer= args.docker_container,
        dockerWD       = args.docker_wd,
        xyceFiles      = "spiceList",
        convert_v      = args.convert_verilog.lower() in ['true', '1'],
        extra_args     = ex_args)
    
    """
    runSimulation(
        verilogFile, 
        workDir, 
        libraryFile,
        cirConfigFile,
        length_file=None,
        preRouteSim=False,
        dockerContainer=None,
        dockerWD=None,
        xyceFiles="spiceList",
        convert_v=True)
    """
    
    
    
