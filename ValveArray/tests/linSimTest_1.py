
import os, sys
#sys.path.append('./..')
sys.path.append('.')

#from ValveArray.simulation import valveArraySimulation
import netListParse
import simulation

#net1 = netListParse.main('./ValveArray/tests/testDev2')
net1 = netListParse.main('./ValveArray/tests/testDev2Ch')

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
# order of node effect the solver ability to converge
#net1 = netListParse.main('./ValveArray/tests/testDev7.1.1')

# Output not solving as intended
#net1 = netListParse.main('./ValveArray/tests/testDev8')

# Output validated care with nodes
#net1 = netListParse.main('./ValveArray/tests/testDev1')

#net1 = netListParse.main('./ValveArray/tests/testDev1.1')

net1.subForJunctions()

linSim = simulation.LinearSolver(net1)

linSim.setDebug(True)

linSim.generateEquations()

solutionVec = linSim.getFlowSolution()

linSim.generateChemicalSolutions()

chemSoln = linSim.getChemicalSolution()

print(solutionVec)

print(chemSoln)
