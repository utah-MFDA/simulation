
import os, sys
#sys.path.append('./..')
sys.path.append('.')

from numpy import test
from ValveArray.netlist import Netlist
import netListParse

def main():
    testString = open('./ValveArray/tests/testDev1')

    # initialize Netlist
    net1 = Netlist()

    '''
    for line in testString:
        data = line.replace('\n', '').split(' ')
        try:
            data.remove('')
        except ValueError:
            pass
        #print(data)
        param = []

        for val in data:
            #print(val)
            if val.find('=') != -1:
                param.append(val)
            else:
                pass

        paramTemp = param
        param = []

        for val in paramTemp:
            data.remove(val)
            param.append(val.split('=')[1])


        if len(data) == 0:
            pass
        elif data[0] == '':
            pass
        else:
            compType = data[0]
            compKey = data[1]
            nodeKeys = data[2:]
            net1.addComponent(compType, compKey, nodeKeys, param)

            '''

    net1 = netListParse.main('./ValveArray/tests/testDev1')
    
            
    print('Components:')
    net1.printComponents()
    print('Nodes:')
    net1.printNodes()

    # Test getComponentList

    print(net1.getComponentList())

    return net1

if __name__ == "__main__":
    net1 = main()
    net1.generateGraph('dev1Graph', 'dev1Test')

