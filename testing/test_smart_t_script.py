



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
    
def test_gen_simple_cir():
    import runMFDASim

    wd = "./testing/simpleChannelTest"
    vFile = "simple_channel.v"
    libFile="./testing/StandardCellLibrary.csv"
    cirConfig = "./V2Va_Parser/VMF_xyce.mfsp"

    runMFDASim.convertToCir(
        verilogFile=vFile,
        wd=wd,
        libFile=libFile,
        configFile=cirConfig,
        preRouteSim=False,
        overwrite=True)

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

def runXyceDocker(verilogFile, wd, libFile, configFile, prerouteSim, overwrite, 
                  docker_container, docker_WD, 
                  simRunTime, simDir, simStartFile, simArgs):
    import runMFDASim
    import os

    simTar = runMFDASim.convertToCir(
        verilogFile=verilogFile,
        wd=wd,
        libFile=libFile,
        configFile=configFile,
        preRouteSim=prerouteSim,
        overwrite=overwrite)

    runMFDASim.pushCir2Docker(
        simArchive=simTar,  
        dockerContainer=docker_container, 
        dockerWD=docker_WD)
    
    simDockerWDarg = "--workdir "+docker_WD+'/'+os.path.basename(simTar).replace('.tar','')

    runSimComm = simRunTime+' '+\
        simDir+'/'+simStartFile+' '+\
        simArgs+' '+simDockerWDarg

    runMFDASim.runRemoteXyce(runSimComm, docker_container, simDir)

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

def test_simplechannel_runXyceDocker():
    import runMFDASim

    import os

    wd        ="./testing/simpleChannelTest"
    vFile     ="simple_channel.v"
    libFile   ="./testing/StandardCellLibrary.csv"
    cirConfig ="./V2Va_Parser/VMF_xyce.mfsp"

    # Docker config
    simDir      = "/mfda_simulation/xyce_docker_server"
    simRunTime  = "python3"
    simStartFile= "xyceRun.py"
    simArgs     = "--list spiceList"
    

    dock_container = "vibrant_clarke"
    dock_WD        = "/mfda_simulation/local/simulations"
    
    

    runXyceDocker(verilogFile=vFile, 
                  wd=wd, 
                  libFile=libFile, 
                  configFile=cirConfig, 
                  prerouteSim=False, 
                  overwrite=True,  
                  docker_container=dock_container, 
                  docker_WD=dock_WD, 
                  simRunTime=simRunTime, 
                  simDir=simDir, 
                  simStartFile=simStartFile, 
                  simArgs=simArgs)
    
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
    
def test_simple_channel_pullFileFromDocker():

    #
    targetDir       = "testing/DockerPullTest"
    dockerContainer = "vibrant_clarke"
    dockerTargetDir = "/mfda_simulation/local/simulations/simple_channel_xyce_0"

    # 
    from runMFDASim import pullFromDocker

    # pullFromDocker(targetDirectory, dockerContainer, simDockerWD)
    pullFromDocker(targetDirectory=targetDir,
                   dockerContainer=dockerContainer,
                   simDockerWD=dockerTargetDir,
                   OR_fileExists=True)
    
def test_parse_simple_channel():

    from runMFDASim import load_xyce_results

    result_file = "simple_channel_H2O.cir.prn"
    result_wd   = "./testing/DockerPullTest/simple_channel_xyce_0"
    
    load_xyce_results(result_wd+"/"+result_file)

def test_plot_simple_channel():

    from runMFDASim import load_xyce_results
    from runMFDASim import plot_xyce_results

    result_file = "simple_channel_H2O.cir.prn"
    result_wd   = "./testing/DockerPullTest/simple_channel_xyce_0"
    
    df = load_xyce_results(result_wd+"/"+result_file)

    plot_xyce_results(df)

def test_full_simulation_simpleChannel():
    from runMFDASim import runSimulation

    verilogFile    ="simple_channel.v"
    workDir        ="./testing/simpleChannelTest"
    libraryFile    ="./testing/StandardCellLibrary.csv"
    cirConfigFile  ="./V2Va_Parser/VMF_xyce.mfsp"
    preRouteSim    =False
    dockerContainer="vibrant_clarke"
    dockerWD       ="/mfda_simulation/local/simulations"
    xyceFiles      ="spiceList"

    runSimulation(
        verilogFile=verilogFile, 
        workDir=workDir, 
        libraryFile=libraryFile,
        cirConfigFile=cirConfigFile,
        preRouteSim=preRouteSim,
        dockerContainer=dockerContainer,
        dockerWD=dockerWD,
        xyceFiles=xyceFiles)

if __name__ == "__main__":
    
    import sys

    import os
    sys.path.insert(1, os.getcwd())

    #from runMFDASim import runRemoteXyce
    
    #test_gen_simple_cir()
    #test_simplechannel_runXyceDocker()
    #test_parse_simple_channel()
    test_full_simulation_simpleChannel()