
import argparse
import os

import docker
import tarfile

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

    class Eval(Node):
        def __init__(self, name, args):
            super.__init__(name, args)

    # this will need some more generic definitions
    class Dev:
        def __init__(self, type, node, args):
            self.type = type
            self.node = node
            self.args = args

        def getType(self):
            return self.type

        def getNode(self):
            return self.node
        
        def getArgs(self):
            return self.args

    def __init__(self):
        self.netListFiles = []
        self.inlets = {}
        self.eval   = {}
        self.dev    = {}

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

def runSimulation(
        verilogFile, 
        workDir, 
        libraryFile,
        cirConfigFile,
        preRouteSim=False,
        dockerContainer=None,
        dockerWD=None,
        xyceFiles="spiceList"):
    
    simRunComm = "python xyceRun.py --file "+xyceFiles

    # Convert to cir from v
    arcName = convertToCir(verilogFile, workDir, libraryFile, cirConfigFile, preRouteSim)

    # transfer files to docker image
    pushCir2Docker(arcName, simRunComm, dockerContainer, dockerWD)

    simRunComm += "--workdir "+dockerWD+'/'+os.path.basename(arcName).replace('.tar','')

    # wait for simulator

    # load extracted data

    # generate report

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

    Verilog2Xyce.Verilog2Xyce(
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

    xyceContainer.exec_run(cmd=simStartComm, workdir=simDockerPyWD)

def pullFromDocker(targetDirectory, dockerContainer, simDockerWD, OR_fileExists=False):

    client = docker.from_env()

    is_docker_container_running(client, dockerContainer)

    xyceContainer = client.containers.get(dockerContainer)

    if not os.path.exists(targetDirectory):
        os.makedirs(targetDirectory)
    else:
        pass # directory exists
    
    targetFileAbs = targetDirectory+'/reults.tar'

    try:
        f = open(targetFileAbs, 'xb')
    except FileExistsError:
        if OR_fileExists:
            f = open(targetFileAbs, 'wb')
        else:
            attempt = 0
            while True:
                try:
                    targetFileAbs = targetDirectory+'/reults'+attempt+'.tar'
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


def load_xyce_results(rFile):
    r_df = pd.read_table(rFile, skipfooter=2, index_col=0, delim_whitespace=True)
    #print(str(r_df))
    return r_df


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

    parser.add_argument('--file', metavar='<verilog_file>', type=str, required=True)
    parser.add_argument('--spec', metavar='<spec_file>', type=str, required=True)

    parser.add_argument('--docker_image', metavar='<image>', type=str)
    parser.add_argument('--docker_container', metavar='<container>', type=str)
    