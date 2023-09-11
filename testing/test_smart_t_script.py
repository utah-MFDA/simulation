



def test_file_load():

    import runMFDASim

    wd = "./testing/smart_toilet_test"
    vFile = "smart_toilet.v"

    files = runMFDASim.getSimFiles(verilogFile=vFile,
                            wd=wd)

    verilogFile= wd+"/"+vFile
    specFile   = wd+"/smart_toilet_spec.csv"
    lengthFile = wd+"/smart_toilet_lengths.xlsx"
    devFile    = wd+"/devices.csv"
    timeFile   = wd+"/simTime.csv"

    assert files['verilogFile'] == verilogFile
    assert files['specFile']    == specFile
    assert files['lengthFile']  == lengthFile
    assert files['devFile']     == devFile
    assert files['timeFile']    == timeFile

def test_gen_cir():
    import runMFDASim

    wd = "./testing/smart_toilet_test"
    vFile = "smart_toilet.v"
    libFile="./testing/StandardCellLibrary.csv"
    cirConfig = "./V2Va_Parser/VMF_xyce.mfsp"

    runMFDASim.convertToCir(
        verilogFile=vFile,
        wd=wd,
        libFile=libFile,
        configFile=cirConfig,
        preRouteSim=False)

def test_push2Docker():

    import runMFDASim

    wd = "./testing/smart_toilet_test"
    vFile = "smart_toilet.v"
    libFile="./testing/StandardCellLibrary.csv"
    cirConfig = "./V2Va_Parser/VMF_xyce.mfsp"

    # Docker config
    runSimComm = ""

    dock_container = "vibrant_clarke"
    dock_WD = "/mfda_simulation/local/simulations"

    simTar = runMFDASim.convertToCir(
        verilogFile=vFile,
        wd=wd,
        libFile=libFile,
        configFile=cirConfig,
        preRouteSim=False,
        overwrite=True)

    runMFDASim.pushCir2Docker(
        simArchive=simTar,  
        dockerContainer=dock_container, 
        dockerWD=dock_WD)
        
def test_runXyceDocker():
    import runMFDASim

    import os

    wd = "./testing/smart_toilet_test"
    vFile = "smart_toilet.v"
    libFile="./testing/StandardCellLibrary.csv"
    cirConfig = "./V2Va_Parser/VMF_xyce.mfsp"

    # Docker config
    simDir      = "/mfda_simulation/xyce_docker_server"
    simRunTime  = "python3"
    simStartFile= "xyceRun.py"
    simArgs     = "--list spiceList"
    

    dock_container = "vibrant_clarke"
    dock_WD        = "/mfda_simulation/local/simulations"

    simTar = runMFDASim.convertToCir(
        verilogFile=vFile,
        wd=wd,
        libFile=libFile,
        configFile=cirConfig,
        preRouteSim=False,
        overwrite=True)

    runMFDASim.pushCir2Docker(
        simArchive=simTar,  
        dockerContainer=dock_container, 
        dockerWD=dock_WD)
    
    simDockerWDarg = "--workdir "+dock_WD+'/'+os.path.basename(simTar).replace('.tar','')

    runSimComm = simRunTime+' '+\
        simDir+'/'+simStartFile+' '+\
        simArgs+' '+simDockerWDarg

    runMFDASim.runRemoteXyce(runSimComm, dock_container, simDir)

    
def test_pullFileFromDocker():

    #
    targetDir       = "testing/DockerPullTest"
    dockerContainer = "vibrant_clarke"
    dockerTargetDir = "/mfda_simulation/local/simulations/smart_toilet_xyce_0"

    # 
    from runMFDASim import pullFromDocker

    # pullFromDocker(targetDirectory, dockerContainer, simDockerWD)
    pullFromDocker(targetDirectory=targetDir,
                   dockerContainer=dockerContainer,
                   simDockerWD=dockerTargetDir,
                   OR_fileExists=True)
    
