

import os, sys
#sys.path.append('./..')
sys.path.append('.')

#from ValveArray.simulation import valveArraySimulation
import  netListParse

net1 = netListParse.main('./ValveArray/tests/testDev2')

print('Components:')
net1.printComponents()
print('Nodes:')
net1.printNodes()

net1.subForJunctions()

print('Components:')
net1.printComponents()
print('Nodes:')
net1.printNodes()