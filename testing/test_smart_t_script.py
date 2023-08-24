



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
        preRouteSim=False)

    runMFDASim.pushCir2Docker(
        simArchive=simTar, 
        simRunComm=runSimComm, 
        dockerContainer=dock_container, 
        dockerWD=dock_WD)
        
