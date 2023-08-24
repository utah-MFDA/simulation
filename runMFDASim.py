
import argparse
import os

import docker
import tarfile

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

def runSimulation(
        verilogFile, 
        workDir, 
        libraryFile,
        cirConfigFile,
        preRouteSim=False,
        dockerContainer=None,
        dockerWD=None):
    
    simRunComm = ""

    # Convert to cir from v
    arcName = convertToCir(verilogFile, workDir, libraryFile, cirConfigFile, preRouteSim)

    # transfer files to docker image
    pushCir2Docker(arcName, simRunComm, dockerContainer, dockerWD)

    # wait for simulator

    # load extracted data

    # generate report

    pass

def convertToCir(verilogFile, wd, libFile, configFile, preRouteSim):

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

    xyceTar, arcName = createXyceArchive(arcNameBase)

    srcDir = wd+"/spiceFiles"
    xyceTar.add(srcDir, arcname=os.path.basename(srcDir.replace("spiceFiles",arcName.replace('.tar',''))))

    xyceTar.close()

    print("--------------------")
    print("created archive: " + arcName)
    print("--------------------")

    return arcName

def createXyceArchive(arcName, attempt=0):
    newName = arcName+"_"+str(attempt)+".tar"
    try:
        xyceTar = tarfile.open(newName, 'x')
        return xyceTar, newName
    except FileExistsError:
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
    if dockerContainer not in [x.name for x in client.containers.list()]:
        #print(client.containers.list())
        raise ValueError('Container not in list (is it running?)' + "\n"+\
                         "Running images: " + str([x.name for x in client.containers.list()]))
    
    # create archive
    #tarfile.open()

    xyceContainer = client.containers.get(dockerContainer)

    with open(simArchive, 'rb') as fd:
        ok = xyceContainer.put_archive(dockerWD, data=fd)
        if not ok:
            raise Exception('Put file failed')
        else:
            print("Files transfer success")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        prog="MFDASimulation",
        description="",
        epilog=""
    )

    parser.add_argument('--file', metavar='verilog_file', type=ascii, required=True)
    parser.add_argument('--spec', metavar='spec_file', type=ascii, required=True)

    parser.add_argument('--docker_image', metavar='image', type=ascii)
    parser.add_argument('--docker_container', metavar='container', type=ascii)
    