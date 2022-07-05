
import os, sys
#sys.path.append('./..')
sys.path.append('.')

#from ValveArray.simulation import valveArraySimulation
import netListParse
import simulation

#net1 = netListParse.main('./ValveArray/tests/testDev2')

# Output validated
#net1 = netListParse.main('./ValveArray/tests/testDev3')

# Output validated
#net1 = netListParse.main('./ValveArray/tests/testDev4')

# Output validated 
#net1 = netListParse.main('./ValveArray/tests/testDev5')

# Output validated 
#net1 = netListParse.main('./ValveArray/tests/testDev6')

# Output validated 
#net1 = netListParse.main('./ValveArray/tests/testDev7')

# Output validated 
net1 = netListParse.main('./ValveArray/tests/testDev8')

# Output validated not solving
#net1 = netListParse.main('./ValveArray/tests/testDev1')

net1.subForJunctions()

linSim = simulation.LinearSolver(net1)

linSim.setDebug(True)

linSim.generateEquations()

solutionVec = linSim.getFlowSolution()

print(solutionVec)
