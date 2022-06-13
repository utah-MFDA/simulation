"""
This test validates the creation of a netlist from a file and confirms the 
the ability to switch valves
"""


import os, sys
#sys.path.append('./..')
sys.path.append('.')

from ValveArray.simulation import valveArraySimulation
import netListTest

net1 = netListTest.main()

sim1 = valveArraySimulation()

sim1.loadFromNetlistObj(net1)

# test valve states
state1 = {'v1': 0, 'v2':0, 'v3':0, 'v4':0}
state2 = {'v1': 0, 'v2':0, 'v3':1, 'v4':0}
state3 = {'v1': 0, 'v2':1, 'v3':0, 'v4':0}
state4 = {'v1': 1, 'v2':0, 'v3':0, 'v4':0}
state5 = {'v1': 0, 'v2':0, 'v3':0, 'v4':1}

sim1.loadValveStates(state1)
sim1.printValveStates()

sim1.loadValveStates(state2)
sim1.printValveStates()

sim1.loadValveStates(state3)
sim1.printValveStates()

sim1.loadValveStates(state4)
sim1.printValveStates()

sim1.loadValveStates(state5)
sim1.printValveStates()

