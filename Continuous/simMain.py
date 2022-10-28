import subprocess
import sys

sys.path.append('./V2Va_Parser')
sys.path.append('./Continuous/V2Va_Parser')

import V2Va_Parser.Verilog2VerilogA as Verilog2VerilogA
import V2Va_Parser.spiceExtract as spiceExtract

import pandas as pd

#
# file setting
#

# construct file path
filePath = "./Continuous/V2Va_Parser/testFiles/smart_toilet_test2"#.replace("./", "./V2Va_Parser/")
fileName = "smart_toilet2.v"

#
# Configuration strings
#

configFile = "./Continuous/VMF_template.json"

library_csv= "./Continuous/component_library/StandardCellLibrary.csv"

remoteComDir = "./Continuous/remoteComFiles"

remoteShellScript = remoteComDir + "/sendFileHSpice.bash"
runSimScript = remoteComDir + "/runSimsRemote.bash"
getFileScript = remoteComDir + "/getFileHSpice.bash"

#
# methods --------------------------------------------------------------------------------
#

def buildSPfile(fullFilePath, configFile, solnFile, remoteTestPath):
    print("\n\nstart builing sp file\n")

    Verilog2VerilogA.Verilog2VerilogA(fullFilePath, configFile, solnFile, remoteTestPath, library_csv)

    print("\nend building sp file\n\n")

def sendFiles(filePath, fullPath):
    # execute shell script
    #remoteShellScript = remoteComDir + "/sendFileHSpice.bash"

    # read list file
    # the spiceFiles is created by the V2Va parser
    spiceFilePath = fullPath + '/spiceFiles/spiceList'
    spiceListFile = pd.read_csv(spiceFilePath)

    # Construct command path
    #sendFileCommand = remoteShellScript + " " + fileName + " " + filePath
    #sendFileCommand = sendFileCommand.replace("./", localPathRoute)

    print("start send file\n")
    for line in spiceListFile.iterrows():
        # Construct command path
        line = line[1]['OutputFile']
        sendFileCommand = remoteShellScript + " " + line.split('/')[-1] + " " + fullPath + "/spiceFiles "# + filePath.replace('./', '')
        #sendFileCommand = sendFileCommand     
        subprocess.call(sendFileCommand, shell=True)
    
    sendFileCommand = remoteShellScript + " runSims.csh " + fullPath + "/spiceFiles " + filePath.replace('./', '')
    #sendFileCommand = sendFileCommand     
    subprocess.call(sendFileCommand, shell=True)

    print("\nend send files\n\n")

def runSimFiles(filePath):
    print("\nrun simulations\n")

    runSimCommand = runSimScript + " " + filePath.replace('./', '') + "/spiceFiles"

    subprocess.call(runSimCommand, shell=True)

    print("\nend run simulations\n\n")

def downloadFiles(filePath, fullPath):
    
    # the spiceFiles is created by the V2Va parser
    spiceFilePath = fullPath + '/spiceFiles/spiceList'
    spiceListFile = pd.read_csv(spiceFilePath)
    
    print("\nDownloading file\n")
    
    for line in spiceListFile.iterrows():
        # Construct command path
        line = line[1]['OutputFile']
        remotePath = fullPath.replace('./', '') + "/spiceFiles/" + line.split('/')[-1].replace(".sp", "") + ""
        getFileCommand = getFileScript + " " + line.split('/')[-1].replace(".sp", "_o") + " " + remotePath + " " + fullPath + "/spiceFiles " + fullPath + "/spiceFiles "# + filePath.replace('./', '')
        #sendFileCommand = sendFileCommand     
        subprocess.call(getFileCommand, shell=True)

    print("Done getting files")

def extractChemData(fullPath):

    print("\nExtracting data\n\n")

    spiceExtract.parseSpiceOut(fullPath + '/spiceFiles/', "spiceList")

    print("\nDone extracting data\n\n")

#
# main -------------------------------------------
#

if __name__ == "__main__":
    

    fullPath     = filePath
    fullFilePath = fullPath + "/" + fileName

    #solnFile   = "./V2Va_Parser/testFiles/smart_toilet_test2/solutionFile.csv"
    solnFile   = fullFilePath[:-2] + "_spec.csv"

    remoteTestPath = "~/Verilog_Tests/"

    # build sp file
    buildSPfile(fullFilePath, configFile, solnFile, remoteTestPath)

    # send files to remote server
    sendFiles(filePath, fullPath)
    
    # run simulation files
    runSimFiles(fullPath)

    # get files from remote server
    downloadFiles(filePath, fullPath)

    # run file extraction
    extractChemData(fullPath)
    
