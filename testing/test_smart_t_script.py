



def test_file_load():

    import runMFDASim

    wd = "./testing/smart_toilet_test"
    vFile = "smart_toilet.v"

    files = runMFDASim.getSimFiles(verilogFile=vFile,
                            wd=wd)

    specFile   = wd+"/smart_toilet_spec.csv"
    lengthFile = wd+"/smart_toilet_length.xlsx"
    devFile    = wd+"/devices.csv"
    timeFile   = wd+"/simTime.csv"

    assert files['specFile'] == specFile
    assert files['lengthFile'] == lengthFile
    assert files['devFile'] == devFile
    assert files['timeFile']== timeFile
