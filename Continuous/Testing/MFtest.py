
import sys

sys.path.append(__file__.replace('Testing/MFtest.py', ''))

import simMain


def PCR1():

    # add file path
    filePath = "./Continuous/V2Va_Parser/testFiles/mfda_30px/PCR1"
    fileName = "PCR1.v"

    # run simulation
    simMain.testing(verilog_file=fileName, path=filePath, testCode=[False,False,False,False,True])

    # check results

if __name__ == '__main__':
    
    PCR1()