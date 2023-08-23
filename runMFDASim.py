
import argparse


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

def runSimulation(verilogFile, workDir):
    

    # Convert to cir from v
    convertToCir(verilogFile, workDir)

    # transfer to docker image

    # wait for simulator

    # load extracted data

    # generate report

    pass

def convertToCir(verilogFile, wd):

    # locate nessary files
    specFile  = wd+verilogFile[:-2]+"_spec.csv"
    lengthFile= wd+verilogFile[:-2]+"_length.xlsx"
    devFile   = wd+"/devices.csv"
    timeFile  = wd+"/simTime.csv" 

def getSimFiles(verilogFile, wd):

    files = {}
    # locate nessary files
    files['specFile']  = wd+"/"+verilogFile[:-2]+"_spec.csv"
    files['lengthFile']= wd+"/"+verilogFile[:-2]+"_length.xlsx"
    files['devFile']   = wd+"/devices.csv"
    files['timeFile']  = wd+"/simTime.csv"

    return files

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
    