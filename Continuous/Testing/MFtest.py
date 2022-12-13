
import sys

sys.path.append(__file__.replace('Testing/MFtest.py', ''))

import simMain


def smartToiletPreRoute():
    # add file path
    filePath = "./Continuous/V2Va_Parser/testFiles/smart_toilet_test2"
    fileName = "smart_toilet2.v"

    # run simulation
    simMain.testing(verilog_file=fileName, 
        path=filePath, 
        design=fileName.replace('.v', ''),
        testCode=[1,0,0,0,0])

def smartToiletPostRoute():
    # add file path
    filePath = "./Continuous/V2Va_Parser/testFiles/smart_toilet_test1"
    fileName = "smart_toilet.v"

    # run simulation
    simMain.testing(verilog_file=fileName, 
        path=filePath, 
        design=fileName.replace('.v', ''),
        testCode=[0,0,0,0,1])

def smartToilet3():
    # add file path
    filePath = "./Continuous/V2Va_Parser/testFiles/smart_toilet_test3"
    fileName = "smart_toilet3.v"

    # run simulation
    simMain.testing(verilog_file=fileName, 
        path=filePath, 
        design=fileName.replace('.v', ''),
        testCode=[0,0,0,0,1])

def PCR1():

    # add file path
    filePath = "./Continuous/V2Va_Parser/testFiles/mfda_30px/PCR1"
    fileName = "PCR1.v"

    # run simulation
    simMain.testing(verilog_file=fileName, 
        path=filePath, 
        design='PCR1',
        testCode=[0,0,0,0,1])

    # check results

if __name__ == '__main__':
    
    # smart toilet
    smartToiletPreRoute()
    #smartToiletPostRoute()
    #smartToilet3()
    
    # PCR device
    #PCR1()