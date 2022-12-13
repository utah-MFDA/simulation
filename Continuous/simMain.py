import subprocess
import sys

sys.path.append(__file__.replace('simMain.py', '') + 'V2Va_Parser')
sys.path.append('./Continuous/V2Va_Parser')

import V2Va_Parser.Verilog2VerilogA as Verilog2VerilogA
import V2Va_Parser.spiceExtract as spiceExtract

import pandas as pd

#
# file setting
#

# construct file path
#filePath = "./Continuous/V2Va_Parser/testFiles/PCR1"#.replace("./", "./V2Va_Parser/")
#fileName = "PCR1.v"

#filePath = "./Continuous/V2Va_Parser/testFiles/PCR_1"#.replace("./", "./V2Va_Parser/")
#fileName = "PCR1.v"

#
# Configuration strings
#

local_dir = __file__.replace('simMain.py', '') 

configFile = local_dir + "VMF_template.json"

library_csv= local_dir + "component_library/StandardCellLibrary.csv"

remoteComDir = local_dir + "remoteComFiles"

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

def sendFiles(filePath, fullPath, remotePath):
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
        sendFileArgs = [
            line.split('/')[-1], 
            fullPath + "/spiceFiles", 
            remotePath]
        sendFileCommand = remoteShellScript + " " + " ".join(str(arg) for arg in sendFileArgs)# + filePath.replace('./', '')
        #sendFileCommand = sendFileCommand     
        subprocess.call(sendFileCommand, shell=True)
    
    # send run sim script
    sendFileArgs = [
        "runSims.csh",
        fullPath + "/spiceFiles",
        remotePath
    ]
    sendFileCommand = remoteShellScript + " " + " ".join(str(arg) for arg in sendFileArgs)
    #sendFileCommand = sendFileCommand     
    subprocess.call(sendFileCommand, shell=True)

    print("\nend send files\n\n")

def runSimFiles(remotePath):
    print("\nrun simulations\n")

    runSimCommand = runSimScript + " " + remotePath #+ "/spiceFiles"

    subprocess.call(runSimCommand, shell=True)

    print("\nend run simulations\n\n")

def downloadFiles(filePath, fullPath, remotePath):
    
    # the spiceFiles is created by the V2Va parser
    spiceFilePath = fullPath + '/spiceFiles/spiceList'
    spiceListFile = pd.read_csv(spiceFilePath)
    
    print("\nRunning Download Commands\n")
    
    for line in spiceListFile.iterrows():
        # Construct command path
        line = line[1]['OutputFile']
        remotePathLine = remotePath + '/' + line.split('/')[-1].replace(".sp", "") + ""
        #remotePathLine = fullPath.replace('./', '') + '/' + line.split('/')[-1].replace(".sp", "") + ""
        sendFileArgs = [
            line.split('/')[-1].replace(".sp", "_o"), 
            remotePathLine, 
            fullPath + "/spiceFiles",
            fullPath + "/spiceFiles"]
        #getFileCommand = getFileScript + " " + line.split('/')[-1].replace(".sp", "_o") + " " + remotePath + " " + fullPath + "/spiceFiles " + fullPath + "/spiceFiles "# + filePath.replace('./', '')
        getFileCommand = getFileScript + " " + " ".join(sendFileArgs)
        #sendFileCommand = sendFileCommand     
        subprocess.call(getFileCommand, shell=True)

    print("Done getting files")

def extractChemData(fullPath, device):

    print("\nExtracting data\n\n")

    spiceExtract.parseSpiceOut(fullPath + '/spiceFiles/', "spiceList", device)

    print("\nDone extracting data\n\n")

def outputData(fullPath):

    pass

#
# main -------------------------------------------
#

def testing(platform=None, design=None, verilog_file=None, path=None, testCode=[1,1,1,1,1]):
    
    simulate(path, verilog_file, design=design, _buildSP=testCode[0], _sendFiles=testCode[1], _runSimScript=testCode[2], _downloadFiles=testCode[3], _extractData=testCode[4])


def simulate(path, fileName, design, _buildSP=True, _sendFiles=True, _runSimScript=True, _downloadFiles=True, _extractData=True):

    filePath     = path
    fullFilePath = path + "/" + fileName

    #solnFile   = "./V2Va_Parser/testFiles/smart_toilet_test2/solutionFile.csv"
    solnFile   = fullFilePath[:-2] + "_spec.csv"

    remoteTestPath = "~/Verilog_Tests/"

    # build sp file
    if _buildSP:
        buildSPfile(fullFilePath, configFile, solnFile, remoteTestPath)

    # send files to remote server
    # generate path relative to testfiles
    testpath_dir = filePath.split('/')
    testpath = ""
    for dir in testpath_dir[testpath_dir.index('testFiles'):]:
        testpath += dir + '/'
    testpath = testpath[:-1]
    if _sendFiles:
        sendFiles(filePath, filePath, testpath)
    
    # run simulation files
    if _runSimScript:
        runSimFiles(testpath)

    # get files from remote server
    if _downloadFiles:
        downloadFiles(filePath, filePath, testpath)

    # run file extraction
    if _extractData:
        extractChemData(filePath)

if __name__ == "__main__":
    
    #print(__file__.replace('simMain.py', '') + 'V2Va_Parser')

    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    ap.add_argument('--platform', metavar='<platform>', dest='platform', type=str,
                    help="Design platform.")
    ap.add_argument('--design', metavar='<design_name>', dest='design', type=str,
                    help="The design name.")
    ap.add_argument('--verilog_file', metavar='<verilog_file>', dest='verilog_file', type=str,
                    help='The name of the Verilog file')
    ap.add_argument('--path', metavar='test_path', dest='test_path', type=str,
                    help='Path to the test files')

    args = ap.parse_args()

    simulate(
        args.test_path, 
        args.verilog_file, 
        design=args.design_name)

    """
    fullPath     = filePath
    fullFilePath = fullPath + "/" + fileName

    #solnFile   = "./V2Va_Parser/testFiles/smart_toilet_test2/solutionFile.csv"
    solnFile   = fullFilePath[:-2] + "_spec.csv"

    remoteTestPath = "~/Verilog_Tests/"

    # build sp file
    buildSPfile(fullFilePath, configFile, solnFile, remoteTestPath)

    # send files to remote server
    # generate path relative to testfiles
    testpath_dir = fullPath.split('/')
    testpath = ""
    for dir in testpath_dir[testpath_dir.index('testFiles'):]:
        testpath += dir + '/'
    testpath = testpath[:-1]
    #sendFiles(filePath, fullPath, testpath)
    
    # run simulation files
    runSimFiles(testpath)

    # get files from remote server
    downloadFiles(filePath, fullPath, testpath)

    # run file extraction
    extractChemData(fullPath)
    """
