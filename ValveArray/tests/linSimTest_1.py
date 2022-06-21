
import os, sys
#sys.path.append('./..')
sys.path.append('.')

#from ValveArray.simulation import valveArraySimulation
import  netListParse
import simulation

#net1 = netListParse.main('./ValveArray/tests/testDev2')

# Output validated
#net1 = netListParse.main('./ValveArray/tests/testDev3')

# Output validated
#net1 = netListParse.main('./ValveArray/tests/testDev4')

# Output has a directional issue with 
net1 = netListParse.main('./ValveArray/tests/testDev5')

net1.subForJunctions()

linSim = simulation.LinearSolver(net1)

linSim.generateEquations()

solutionVec = linSim.getSolution()

print(solutionVec)
